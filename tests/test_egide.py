"""Tests d'Égide : le catalogue est cohérent, l'amorce crée le profil, l'API recopie, règle et analyse."""
from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from egide import catalogue
from egide.app import analyse, creer_app, reflexes


# --- le catalogue ------------------------------------------------------------------------
def test_chaque_garantie_est_rangee_et_sourcee():
    for cle, p in catalogue.PRODUITS.items():
        assert p["droits"] and p["source_url"].startswith("https://") and p["source_date"], cle
        for g in p["droits"]:
            assert g["situations"] and set(g["situations"]) <= catalogue.CLES_SITUATIONS, g["cle"]
            assert g["statut"] in {"notice", "source-tierce", "typique", "piste"}, g["cle"]
            assert g["titre"] and g["resume"], g["cle"]
    cles = [g["cle"] for p in catalogue.PRODUITS.values() for g in p["droits"]]
    assert len(cles) == len(set(cles))


def test_reflexes_et_situations_coherents():
    assert set(catalogue.REFLEXES) <= catalogue.CLES_SITUATIONS
    for options in catalogue.REFLEXES.values():
        for requis, texte in options:
            assert requis <= set(catalogue.PRODUITS) and texte


def test_les_numeros_sont_bien_formes():
    # un numéro mal recopié est pire qu'aucun : chaque numéro du catalogue a 10 chiffres (ou +33 et 9 chiffres)
    for p in catalogue.PRODUITS.values():
        for g in p["droits"]:
            for n in re.findall(r"(\+33\s?\d(?:[\s.]?\d{2}){4}|0\s?\d{3}(?:\s?\d{3}){2}|0\d(?:\s?\d{2}){4})", g["contact"]):
                chiffres = re.sub(r"\D", "", n)
                assert len(chiffres) == (11 if n.startswith("+33") else 10), (g["cle"], n)


# --- l'analyse -----------------------------------------------------------------------------
def contrats_de(*produits):
    sortie = []
    for i, k in enumerate(produits):
        p = catalogue.PRODUITS[k]
        sortie.append({"id": i, "produit": k, "nom": p["nom"], "fournisseur": p["fournisseur"],
                       "droits": [dict(g) for g in p["droits"]]})
    return sortie


def test_doublons_et_trous():
    c = contrats_de("bred-visa-classic", "boursobank-ultim", "bred-habitation")
    a = analyse(c)
    medical = next(d for d in a["doublons"] if d["theme"] == "frais-medicaux-etranger")
    assert medical["meilleur"] == "BoursoBank Carte Visa Ultim"
    assert {d["theme"] for d in a["doublons"]} >= {"rc", "fraude-carte", "caution-penale"}
    assert {t["theme"] for t in a["trous"]} == {"achats", "prevoyance"}    # la protection juridique est dans l'habitation
    # une garantie marquée absente ne compte plus
    for g in c[2]["droits"]:
        g["statut"] = "absent"
    assert "protection-juridique" in {t["theme"] for t in analyse(c)["trous"]}


def test_le_reflexe_depend_des_contrats():
    seul = reflexes(contrats_de("boursobank-ultim"))
    deux = reflexes(contrats_de("boursobank-ultim", "bred-visa-classic"))
    assert "11 000 €" in deux["sante-etranger"] and "11 000 €" not in seul["sante-etranger"]
    assert "panne" not in seul


# --- l'API ---------------------------------------------------------------------------------
@pytest.fixture
def client_vide(tmp_path):
    return TestClient(creer_app(tmp_path))


@pytest.fixture
def client(client_vide):
    """Le dossier de départ, rempli avec tout le catalogue."""
    pid = client_vide.get("/api/etat").json()["profils"][0]["id"]
    for produit in catalogue.PRODUITS:
        client_vide.post("/api/contrats", json={"profil": pid, "produit": produit})
    return client_vide


def test_amorce_et_etat(client_vide):
    client = client_vide
    e = client.get("/api/etat").json()
    assert [p["nom"] for p in e["profils"]] == ["Mon dossier"] and e["contrats"] == []     # un dossier vide
    pid = e["profils"][0]["id"]
    for produit in catalogue.PRODUITS:
        assert client.post("/api/contrats", json={"profil": pid, "produit": produit}).status_code == 200
    e = client.get(f"/api/etat?profil={pid}").json()
    assert {c["produit"] for c in e["contrats"]} == set(catalogue.PRODUITS)
    assert sum(len(c["droits"]) for c in e["contrats"]) == sum(len(p["droits"]) for p in catalogue.PRODUITS.values())
    assert "voyage" in e["reflexes"] and e["analyse"]["doublons"]


def test_verifier_absent_annuler(client):
    e = client.get("/api/etat").json()
    g = next(g for c in e["contrats"] for g in c["droits"] if g["cle"] == "hab-rc")
    assert g["statut"] == "typique" and g["statut_origine"] == "typique"
    assert client.patch(f"/api/garanties/{g['id']}", json={"statut": "verifie", "notes": "page 12"}).json()["statut"] == "verifie"
    assert client.patch(f"/api/garanties/{g['id']}", json={"statut": "n'importe"}).status_code == 422
    retour = client.patch(f"/api/garanties/{g['id']}", json={"statut": "typique"}).json()
    assert retour["statut"] == "typique" and retour["notes"] == "page 12"


def test_profil_contrat_et_garantie_ajoutes(client):
    pid = client.post("/api/profils", json={"nom": "Moi"}).json()["id"]
    assert client.post("/api/contrats", json={"profil": pid, "produit": "inconnu"}).status_code == 422
    cid = client.post("/api/contrats", json={"profil": pid, "nom": "Carte Gold", "fournisseur": "Banque test", "type": "carte"}).json()["id"]
    client.post("/api/garanties", json={"contrat": cid, "titre": "Garantie achats", "situations": ["carte", "pas-une-situation"],
                                        "plafond": "1 500 €"})
    client.post("/api/contrats", json={"profil": pid, "produit": "camieg"})
    e = client.get(f"/api/etat?profil={pid}").json()
    assert e["profil"]["nom"] == "Moi" and len(e["contrats"]) == 2
    perso = e["contrats"][0]["droits"][0]
    assert perso["statut"] == "perso" and perso["situations"] == ["carte"]
    client.delete(f"/api/contrats/{cid}")
    assert len(client.get(f"/api/etat?profil={pid}").json()["contrats"]) == 1
