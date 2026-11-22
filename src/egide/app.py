"""La page d'Égide et son API, sur http://localhost:3009 (et le tailnet par « tailscale serve »)."""
from __future__ import annotations

import ipaddress
import json
import re
import threading
import time
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from . import catalogue
from .base import ECHEANCES, Base, amorcer

RACINE = Path(__file__).resolve().parents[2]
STATIQUE = Path(__file__).parent / "static"
TAILSCALE = (ipaddress.ip_network("100.64.0.0/10"), ipaddress.ip_network("fd7a:115c:a1e0::/48"))


def _source(entetes) -> str:
    premiere = (entetes.get("x-forwarded-for") or "").split(",")[0].strip()
    try:
        return "tailscale" if premiere and any(ipaddress.ip_address(premiere) in r for r in TAILSCALE) else "local"
    except ValueError:
        return "local"


class Profil(BaseModel):
    nom: str = Field(min_length=1, max_length=60)


class NouveauContrat(BaseModel):
    profil: int
    produit: str = Field("", max_length=60)
    nom: str = Field("", max_length=80)
    fournisseur: str = Field("", max_length=80)
    type: str = Field("assurance", max_length=20)


class ReglageContrat(BaseModel):
    nom: str | None = Field(None, max_length=80)
    fournisseur: str | None = Field(None, max_length=80)
    reference: str | None = Field(None, max_length=80)
    notes: str | None = Field(None, max_length=2000)
    echeance: str | None = Field(None, pattern=r"^(\d{4}-\d{2}-\d{2})?$")     # vide : pas d'échéance
    echeance_sorte: Literal["renouvellement", "fin", "carte", "autre", ""] | None = None
    preavis: int | None = Field(None, ge=0, le=365)


def _ics(texte: str) -> str:
    return texte.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def agenda(c: dict) -> str:
    """Un événement d'agenda (iCalendar) pour l'échéance d'un contrat : le jour où il faut agir, avec deux rappels."""
    jour = date.fromisoformat(c["echeance"])
    sorte = ECHEANCES.get(c["echeance_sorte"] or "autre", "Échéance")
    action = jour - timedelta(days=c["preavis"] or 0)
    qui = f"{c['fournisseur']} · {c['nom']}" if c["fournisseur"] else c["nom"]
    if c["preavis"]:
        titre = f"Dernier jour pour résilier ou renégocier : {qui}"
        texte = f"{sorte} le {jour:%d/%m/%Y}, préavis de {c['preavis']} jours."
    else:
        titre = f"{sorte} : {qui}"
        texte = f"{sorte} le {jour:%d/%m/%Y}."
    if c["reference"]:
        texte += f" Référence : {c['reference']}."
    lignes = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Egide//echeances//FR", "CALSCALE:GREGORIAN", "BEGIN:VEVENT",
              f"UID:egide-contrat-{c['id']}-{jour:%Y%m%d}@egide.local",
              f"DTSTAMP:{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}",
              f"DTSTART;VALUE=DATE:{action:%Y%m%d}", f"DTEND;VALUE=DATE:{action + timedelta(days=1):%Y%m%d}",
              f"SUMMARY:{_ics(titre)}", f"DESCRIPTION:{_ics(texte)}"]
    if c["echeance_sorte"] == "renouvellement":
        lignes.append("RRULE:FREQ=YEARLY")                     # une reconduction revient chaque année
    for avance, mot in (("P30D", "dans un mois"), ("P7D", "dans une semaine")):
        lignes += ["BEGIN:VALARM", "ACTION:DISPLAY", f"TRIGGER:-{avance}", f"DESCRIPTION:{_ics(titre + ', ' + mot)}", "END:VALARM"]
    lignes += ["END:VEVENT", "END:VCALENDAR"]
    return "\r\n".join(lignes) + "\r\n"


def _fichier(nom: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode().lower()).strip("-") or "contrat"


class Garantie(BaseModel):
    titre: str | None = Field(None, max_length=120)
    categorie: str | None = Field(None, max_length=30)
    situations: list[str] | None = None
    resume: str | None = Field(None, max_length=2000)
    plafond: str | None = Field(None, max_length=300)
    franchise: str | None = Field(None, max_length=300)
    conditions: str | None = Field(None, max_length=600)
    demarche: str | None = Field(None, max_length=1000)
    contact: str | None = Field(None, max_length=300)
    delai: str | None = Field(None, max_length=200)
    statut: str | None = Field(None, max_length=20)
    notes: str | None = Field(None, max_length=2000)


class NouvelleGarantie(Garantie):
    contrat: int
    titre: str = Field(min_length=1, max_length=120)


def analyse(contrats: list[dict]) -> dict:
    """Les doublons (un même besoin couvert par plusieurs contrats) et les trous (ce qui ne l'est par aucun)."""
    themes: dict[str, list] = {}
    for c in contrats:
        for g in c["droits"]:
            if g["theme"] and g["statut"] != "absent":
                themes.setdefault(g["theme"], []).append({"contrat": c["nom"], "fournisseur": c["fournisseur"], "titre": g["titre"],
                                                          "plafond": g["plafond"], "valeur": g["valeur"], "statut": g["statut"]})
    doublons = []
    for theme, liste in themes.items():
        contrats_distincts = {(x["fournisseur"], x["contrat"]) for x in liste}
        if len(contrats_distincts) < 2:
            continue
        chiffres = [x for x in liste if x["valeur"]]
        meilleur = max(chiffres, key=lambda x: x["valeur"]) if chiffres else None
        doublons.append({"theme": theme, "titre": liste[0]["titre"], "offres": liste,
                         "meilleur": f"{meilleur['fournisseur']} {meilleur['contrat']}" if meilleur else None})
    trous = [{"theme": t, "titre": titre, "texte": texte} for t, titre, texte in catalogue.TROUS if t not in themes]
    return {"doublons": doublons, "trous": trous}


def reflexes(contrats: list[dict]) -> dict:
    presents = {c["produit"] for c in contrats if c["produit"]}
    sortie = {}
    for situation, options in catalogue.REFLEXES.items():
        for requis, texte in options:
            if requis <= presents:
                sortie[situation] = texte
                break
    return sortie


def creer_app(dossier: Path = RACINE, amorce: bool = True) -> FastAPI:
    base = Base(dossier / "data" / "egide.db")
    if amorce:
        amorcer(base)
    journal = dossier / "logs" / "acces.jsonl"
    ecriture = threading.Lock()
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.base = base

    @app.middleware("http")
    async def noter_acces(requete: Request, suite):
        debut = time.perf_counter()
        reponse = await suite(requete)
        if requete.url.path != "/api/sante":
            ligne = {"t": round(time.time(), 3), "m": requete.method, "p": requete.url.path[:200], "src": _source(requete.headers),
                     "s": reponse.status_code, "ms": round((time.perf_counter() - debut) * 1000)}
            try:
                journal.parent.mkdir(parents=True, exist_ok=True)
                with ecriture, journal.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(ligne) + "\n")
            except OSError:
                pass
        return reponse

    def profil_ou_404(ident: int) -> dict:
        p = next((p for p in base.profils() if p["id"] == ident), None)
        if p is None:
            raise HTTPException(404, "Profil inconnu")
        return p

    @app.get("/")
    def page():
        return FileResponse(STATIQUE / "index.html", headers={"Cache-Control": "no-cache"})

    @app.get("/icone.svg")
    def icone():
        return FileResponse(STATIQUE / "icone.svg", media_type="image/svg+xml")

    @app.get("/api/sante")
    def sante():
        return {"ok": True}

    @app.get("/api/etat")
    def etat(profil: int | None = None):
        profils = base.profils()
        if not profils:
            return {"profils": [], "profil": None, "contrats": [], "situations": catalogue.SITUATIONS, "reflexes": {},
                    "catalogue": catalogue.produits_publics(), "analyse": {"doublons": [], "trous": []}}
        courant = next((p for p in profils if p["id"] == profil), profils[0])
        contrats = base.contrats(courant["id"])
        return {"profils": profils, "profil": courant, "contrats": contrats, "situations": catalogue.SITUATIONS,
                "reflexes": reflexes(contrats), "catalogue": catalogue.produits_publics(), "analyse": analyse(contrats)}

    @app.post("/api/profils")
    def nouveau_profil(p: Profil):
        return {"id": base.ajouter_profil(p.nom)}

    @app.patch("/api/profils/{ident}")
    def renommer(ident: int, p: Profil):
        profil_ou_404(ident)
        base.renommer_profil(ident, p.nom)
        return {"ok": True}

    @app.delete("/api/profils/{ident}")
    def supprimer_profil(ident: int):
        profil_ou_404(ident)
        base.supprimer_profil(ident)
        return {"ok": True}

    @app.post("/api/contrats")
    def nouveau_contrat(c: NouveauContrat):
        profil_ou_404(c.profil)
        if c.produit and c.produit not in catalogue.PRODUITS:
            raise HTTPException(422, "Produit inconnu du catalogue")
        if not c.produit and not c.nom.strip():
            raise HTTPException(422, "Donne un nom au contrat")
        champs = {} if c.produit else {"nom": c.nom.strip(), "fournisseur": c.fournisseur.strip(), "type": c.type}
        return {"id": base.ajouter_contrat(c.profil, c.produit, **champs)}

    @app.patch("/api/contrats/{ident}")
    def regler_contrat(ident: int, r: ReglageContrat):
        if not base.contrat(ident):
            raise HTTPException(404, "Contrat inconnu")
        if r.echeance:
            try:
                date.fromisoformat(r.echeance)
            except ValueError:
                raise HTTPException(422, "Date d'échéance impossible") from None
        base.modifier_contrat(ident, **r.model_dump(exclude_none=True))
        return {"ok": True}

    @app.get("/api/contrats/{ident}/echeance.ics")
    def echeance_agenda(ident: int):
        c = base.contrat(ident)
        if not c:
            raise HTTPException(404, "Contrat inconnu")
        if not c["echeance"]:
            raise HTTPException(404, "Ce contrat n'a pas d'échéance")
        return Response(agenda(c), media_type="text/calendar; charset=utf-8",
                        headers={"Content-Disposition": f'attachment; filename="echeance-{_fichier(c["nom"])}.ics"'})

    @app.delete("/api/contrats/{ident}")
    def supprimer_contrat(ident: int):
        base.supprimer_contrat(ident)
        return {"ok": True}

    @app.post("/api/garanties")
    def nouvelle_garantie(g: NouvelleGarantie):
        if not base.contrat(g.contrat):
            raise HTTPException(404, "Contrat inconnu")
        champs = g.model_dump(exclude_none=True, exclude={"contrat"})
        champs["statut"] = "perso"
        return {"id": base.ajouter_droit(g.contrat, **champs)}

    @app.patch("/api/garanties/{ident}")
    def regler_garantie(ident: int, g: Garantie):
        if not base.droit(ident):
            raise HTTPException(404, "Garantie inconnue")
        champs = g.model_dump(exclude_none=True)
        if "statut" in champs and champs["statut"] not in catalogue.STATUTS:
            raise HTTPException(422, "Statut inconnu")
        base.modifier_droit(ident, **champs)
        return base.droit(ident)

    @app.delete("/api/garanties/{ident}")
    def supprimer_garantie(ident: int):
        base.supprimer_droit(ident)
        return {"ok": True}

    return app
