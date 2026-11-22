# Égide

Tout ce à quoi on a droit avec ses cartes bancaires, sa mutuelle et ses assurances, rangé par situation : « Il t'arrive
quoi ? ». Pour savoir enfin ce que t'apportent tes contrats, garantie par garantie.

- Page : http://localhost:3009, et sur tes appareils par Tailscale (`tailscale serve --https=10004`).
- Service Muninn `egide`, démarré avec WSL. Données : `data/egide.db` (SQLite, hors git). Rien ne sort du PC.

## La page

- **Les tampons :** 21 situations (je pars en voyage, panne de voiture, lunettes, dégât des eaux, litige…). En
  presser un ouvre le dossier.
- **Le dossier :** le bon réflexe, puis chaque garantie concernée, tous contrats confondus. Pour chacune : le
  plafond, la franchise, la condition, comment faire, qui appeler, le délai pour déclarer, et d'où vient
  l'information. Un cachet dit si c'est couvert, sous condition, à vérifier, une piste, vérifié ou non couvert.
- **La recherche :** par mot (franchise, avocat, lentilles…).
- **Le trousseau :** les contrats sous forme de cartes et d'attestations. En toucher un montre tout ce qu'il couvre,
  avec sa référence, ses notes, son échéance et l'ajout d'une garantie.
- **Les échéances :** pour chaque contrat, une date (renouvellement, fin du contrat, expiration de la carte) et un
  préavis de résiliation en jours. La section les range par jour où agir, c'est-à-dire l'échéance moins le préavis,
  avec un compte à rebours. Elle met en évidence le mois qui vient, et le trousseau affiche un badge dans les 60 jours.
  « Ajouter à mon agenda » télécharge un fichier `.ics` (`/api/contrats/<id>/echeance.ics`), que l'agenda du
  téléphone ou d'Outlook importe. Il crée un événement le jour où agir, avec un rappel un mois puis une semaine avant,
  répété chaque année pour un renouvellement.
- **En double, et ce qui manque :**
  - les doublons : plusieurs contrats pour le même besoin, avec le plus haut des plafonds ;
  - les trous : garantie achats, prévoyance, protection juridique.
- **Les numéros à garder,** rassemblés depuis toutes les garanties.
- **À vérifier dans tes contrats :** les garanties à confirmer dans les conditions particulières.
- **Profils :** un par personne. Au premier démarrage, un dossier vide, « Mon dossier », est créé : ajoute tes cartes
  et tes contrats depuis le catalogue, ou décris-les toi-même.

## Le catalogue ([`src/egide/catalogue.py`](src/egide/catalogue.py))

Chaque garantie porte son origine. Je l'ai écrite moi-même à partir des documents ci-dessous, sans IA dans
l'application :

| Contrat | Source | Fiabilité |
|---|---|---|
| Visa Ultim (BoursoBank) | Notice Chubb FRBOTY03361 au 1er janvier 2026 | lu dans la notice |
| Visa Classic (BRED) | Notice BRED non lisible : chiffres de comparateurs (Milesopedia, HelloSafe) et de la notice 2023 | à vérifier |
| CAMIEG | Tableau des garanties en vigueur au 1er juillet 2026 | lu dans la notice |
| sanergi ieg (CSM des IEG, Crédit Agricole Assurances) | Mémos options et garanties, assistance (Europ Assistance), FAQ mars 2026 | lu, sauf les renforts par option (à vérifier) |
| Assurance habitation (BRED) | Aucun document trouvé : garanties habituelles d'une multirisque habitation | à vérifier |
| Auto AXA via SATEC (contrat groupe CCAS) | Conditions générales 05/2025 et page ccas.satecassur.com/auto | lu ; garanties de formule à vérifier |
| Statut IEG | Activités sociales CCAS/CMCAS, tarif agent | piste |

Les délais de déclaration de l'habitation et de l'auto (5 jours ouvrés, 2 pour un vol, 30 jours après un arrêté de
catastrophe naturelle) sont les délais légaux minimum. Le contrat peut prévoir plus long.

Pour ajouter un produit connu : une entrée dans `PRODUITS`, des réflexes dans `REFLEXES`, et la source. Les tests
vérifient que chaque garantie est rangée dans une situation, sourcée, et que ses numéros ont le bon nombre de chiffres.

## Commandes

```
egide serve     # la page, sur le port 3009 (Muninn la lance)
egide list      # les profils, leurs contrats, les garanties à vérifier
```

Tests : `.venv/bin/pytest -q`.
