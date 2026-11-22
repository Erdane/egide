"""La base SQLite d'Égide : les profils (une personne, un foyer), leurs contrats et les garanties de chaque contrat.

Ajouter un contrat du catalogue y recopie ses garanties : la personne peut ensuite les marquer vérifiées ou absentes,
les corriger, en ajouter. Rien ne sort du PC.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path

from . import catalogue

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS profils (id INTEGER PRIMARY KEY, nom TEXT NOT NULL, cree_le REAL NOT NULL);
CREATE TABLE IF NOT EXISTS contrats (
    id INTEGER PRIMARY KEY,
    profil INTEGER NOT NULL REFERENCES profils(id) ON DELETE CASCADE,
    produit TEXT NOT NULL DEFAULT '',          -- clé du catalogue, vide pour un contrat ajouté à la main
    nom TEXT NOT NULL, fournisseur TEXT NOT NULL DEFAULT '', type TEXT NOT NULL DEFAULT 'assurance',
    couleur TEXT NOT NULL DEFAULT '', reference TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT '',
    source_url TEXT NOT NULL DEFAULT '', source_date TEXT NOT NULL DEFAULT '', ajoute_le REAL NOT NULL,
    echeance TEXT NOT NULL DEFAULT '',         -- AAAA-MM-JJ : renouvellement, fin de contrat, expiration de la carte
    echeance_sorte TEXT NOT NULL DEFAULT '', preavis INTEGER NOT NULL DEFAULT 0   -- jours pour résilier avant l'échéance
);
CREATE TABLE IF NOT EXISTS droits (
    id INTEGER PRIMARY KEY,
    contrat INTEGER NOT NULL REFERENCES contrats(id) ON DELETE CASCADE,
    cle TEXT NOT NULL DEFAULT '', theme TEXT NOT NULL DEFAULT '', titre TEXT NOT NULL, categorie TEXT NOT NULL DEFAULT '',
    situations TEXT NOT NULL DEFAULT '[]', resume TEXT NOT NULL DEFAULT '', plafond TEXT NOT NULL DEFAULT '',
    franchise TEXT NOT NULL DEFAULT '', conditions TEXT NOT NULL DEFAULT '', demarche TEXT NOT NULL DEFAULT '',
    contact TEXT NOT NULL DEFAULT '', delai TEXT NOT NULL DEFAULT '', statut TEXT NOT NULL DEFAULT 'perso',
    statut_origine TEXT NOT NULL DEFAULT 'perso',  -- d'où vient la garantie, pour revenir en arrière après « vérifié » ou « absent »
    valeur REAL, notes TEXT NOT NULL DEFAULT '', ordre INTEGER NOT NULL DEFAULT 0
);
"""
CHAMPS_CONTRAT = {"nom", "fournisseur", "type", "reference", "notes", "echeance", "echeance_sorte", "preavis"}
ECHEANCES = {"renouvellement": "Renouvellement", "fin": "Fin du contrat", "carte": "Expiration de la carte", "autre": "Échéance"}
CHAMPS_DROIT = {"titre", "categorie", "situations", "resume", "plafond", "franchise", "conditions", "demarche", "contact",
                "delai", "statut", "notes", "theme"}


class Base:
    def __init__(self, chemin: Path):
        chemin.parent.mkdir(parents=True, exist_ok=True)
        self.cx = sqlite3.connect(chemin, check_same_thread=False, isolation_level=None)
        self.cx.row_factory = sqlite3.Row
        self.verrou = threading.RLock()
        with self.verrou:
            self.cx.executescript(SCHEMA)
            colonnes = {l[1] for l in self.cx.execute("PRAGMA table_info(contrats)")}
            for nom, type_ in (("echeance", "TEXT NOT NULL DEFAULT ''"), ("echeance_sorte", "TEXT NOT NULL DEFAULT ''"),
                               ("preavis", "INTEGER NOT NULL DEFAULT 0")):
                if nom not in colonnes:                       # base créée avant les échéances
                    self.cx.execute(f"ALTER TABLE contrats ADD COLUMN {nom} {type_}")

    def _x(self, sql, params=()):
        with self.verrou:
            return self.cx.execute(sql, params).lastrowid

    def _tous(self, sql, params=()):
        with self.verrou:
            return [dict(l) for l in self.cx.execute(sql, params).fetchall()]

    # --- profils ---------------------------------------------------------------------
    def profils(self):
        return self._tous("SELECT * FROM profils ORDER BY id")

    def ajouter_profil(self, nom: str) -> int:
        return self._x("INSERT INTO profils(nom, cree_le) VALUES (?, ?)", (nom.strip()[:60] or "Moi", time.time()))

    def renommer_profil(self, ident: int, nom: str) -> None:
        self._x("UPDATE profils SET nom = ? WHERE id = ?", (nom.strip()[:60], ident))

    def supprimer_profil(self, ident: int) -> None:
        self._x("DELETE FROM profils WHERE id = ?", (ident,))

    # --- contrats --------------------------------------------------------------------
    def contrats(self, profil: int):
        contrats = self._tous("SELECT * FROM contrats WHERE profil = ? ORDER BY ajoute_le, id", (profil,))
        droits = self._tous("SELECT d.* FROM droits d JOIN contrats c ON c.id = d.contrat WHERE c.profil = ? ORDER BY d.ordre, d.id", (profil,))
        par_contrat: dict[int, list] = {}
        for x in droits:
            x["situations"] = json.loads(x["situations"] or "[]")
            par_contrat.setdefault(x["contrat"], []).append(x)
        for c in contrats:
            c["droits"] = par_contrat.get(c["id"], [])
        return contrats

    def contrat(self, ident: int):
        lignes = self._tous("SELECT * FROM contrats WHERE id = ?", (ident,))
        return lignes[0] if lignes else None

    def ajouter_contrat(self, profil: int, produit: str = "", **champs) -> int:
        modele = catalogue.PRODUITS.get(produit)
        if modele:
            champs = {"nom": modele["nom"], "fournisseur": modele["fournisseur"], "type": modele["type"],
                      "couleur": modele["couleur"], "source_url": modele["source_url"], "source_date": modele["source_date"], **champs}
        ident = self._x("INSERT INTO contrats(profil, produit, nom, fournisseur, type, couleur, reference, notes, source_url, source_date, ajoute_le) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (profil, produit if modele else "", (champs.get("nom") or "Contrat")[:80], champs.get("fournisseur", "")[:80],
                         champs.get("type", "assurance"), champs.get("couleur", ""), champs.get("reference", "")[:80],
                         champs.get("notes", ""), champs.get("source_url", ""), champs.get("source_date", ""), time.time()))
        for i, g in enumerate(modele["droits"] if modele else []):
            self.ajouter_droit(ident, ordre=i, **g)
        return ident

    def modifier_contrat(self, ident: int, **champs) -> None:
        champs = {k: v for k, v in champs.items() if k in CHAMPS_CONTRAT}
        if champs:
            self._x(f"UPDATE contrats SET {', '.join(f'{k} = ?' for k in champs)} WHERE id = ?", (*champs.values(), ident))

    def supprimer_contrat(self, ident: int) -> None:
        self._x("DELETE FROM contrats WHERE id = ?", (ident,))

    # --- garanties -----------------------------------------------------------------
    def ajouter_droit(self, contrat: int, ordre: int = 999, **g) -> int:
        return self._x("INSERT INTO droits(contrat, cle, theme, titre, categorie, situations, resume, plafond, franchise, conditions, "
                       "demarche, contact, delai, statut, statut_origine, valeur, notes, ordre) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (contrat, g.get("cle", ""), g.get("theme", ""), g.get("titre", "Garantie")[:120], g.get("categorie", ""),
                        json.dumps([s for s in g.get("situations", []) if s in catalogue.CLES_SITUATIONS]), g.get("resume", ""),
                        g.get("plafond", ""), g.get("franchise", ""), g.get("conditions", ""), g.get("demarche", ""),
                        g.get("contact", ""), g.get("delai", ""), g.get("statut", "perso"), g.get("statut", "perso"), g.get("valeur"),
                        g.get("notes", ""), ordre))

    def droit(self, ident: int):
        lignes = self._tous("SELECT * FROM droits WHERE id = ?", (ident,))
        if lignes:
            lignes[0]["situations"] = json.loads(lignes[0]["situations"] or "[]")
        return lignes[0] if lignes else None

    def modifier_droit(self, ident: int, **champs) -> None:
        champs = {k: v for k, v in champs.items() if k in CHAMPS_DROIT}
        if "situations" in champs:
            champs["situations"] = json.dumps([s for s in champs["situations"] if s in catalogue.CLES_SITUATIONS])
        if champs:
            self._x(f"UPDATE droits SET {', '.join(f'{k} = ?' for k in champs)} WHERE id = ?", (*champs.values(), ident))

    def supprimer_droit(self, ident: int) -> None:
        self._x("DELETE FROM droits WHERE id = ?", (ident,))


def amorcer(base: Base) -> None:
    """Au premier démarrage : un dossier vide, à remplir depuis le catalogue (une base existante n'est pas touchée)."""
    if base.profils():
        return
    base.ajouter_profil("Mon dossier")
