"""Égide : commandes. `egide serve` lance la page (Muninn s'en charge)."""
from __future__ import annotations

import argparse
import sys


def main() -> None:
    parseur = argparse.ArgumentParser(prog="egide", description=__doc__)
    sous = parseur.add_subparsers(dest="commande", required=True)
    s = sous.add_parser("serve", help="Lance la page sur http://localhost:3009")
    s.add_argument("--port", type=int, default=3009)
    sous.add_parser("list", help="Les profils, leurs contrats et le nombre de garanties")
    args = parseur.parse_args()
    if args.commande == "serve":
        import uvicorn

        from .app import creer_app
        uvicorn.run(creer_app(), host="127.0.0.1", port=args.port, log_level="warning", access_log=False)
        return
    from .app import RACINE
    from .base import Base
    base = Base(RACINE / "data" / "egide.db")
    for p in base.profils():
        print(p["nom"])
        for c in base.contrats(p["id"]):
            a_verifier = sum(1 for g in c["droits"] if g["statut"] in ("source-tierce", "typique", "piste"))
            print(f"  {c['fournisseur']} {c['nom']} : {len(c['droits'])} garanties, {a_verifier} à vérifier")
    sys.exit(0)
