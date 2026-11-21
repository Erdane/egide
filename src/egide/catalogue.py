"""Le catalogue d'Égide : les produits connus (cartes, régimes, mutuelles, assurances) et leurs garanties.

Chaque garantie dit d'où elle vient (`statut`) :
- « notice »        : lue dans la notice ou le tableau officiel cité en source ;
- « source-tierce » : relevée chez un comparateur ou un résumé, la notice officielle n'ayant pas pu être lue ;
- « typique »       : garantie habituelle de ce genre de contrat, à confirmer dans les conditions particulières ;
- « piste »         : un droit probable, lié au statut (IEG), à confirmer.
On peut ensuite marquer chaque garantie « vérifiée » ou « absente » de son contrat, ou en ajouter.

`theme` regroupe les garanties qui se recouvrent d'un contrat à l'autre (les doublons) ; `valeur` (en euros) sert à
dire laquelle est la plus haute. Rien ici n'est le contrat lui-même : les montants sont à jour à la date de la source.
"""
from __future__ import annotations

SITUATIONS = [
    ("voyage", "Je pars en voyage", "valise"),
    ("sante-etranger", "Malade ou blessé à l'étranger", "croix"),
    ("annulation", "Je dois annuler ou écourter un voyage", "calendrier"),
    ("bagages", "Bagages perdus, volés ou en retard", "bagage"),
    ("retard", "Vol ou train en retard", "horloge"),
    ("location", "Je loue une voiture", "cle"),
    ("ski", "Je pars au ski", "flocon"),
    ("panne", "Panne ou accident de voiture", "voiture"),
    ("maison", "Dégât des eaux, incendie, cambriolage", "maison"),
    ("dommage-cause", "J'ai causé un dommage à quelqu'un", "main"),
    ("optique", "Lunettes ou lentilles", "lunettes"),
    ("dentaire", "Dentiste, prothèse, orthodontie", "dent"),
    ("audition", "Appareils auditifs", "oreille"),
    ("soins", "Médecin, pharmacie, analyses", "stethoscope"),
    ("hospitalisation", "Hospitalisation ou opération", "lit"),
    ("convalescence", "Besoin d'aide à la maison après une maladie", "coeur"),
    ("juridique", "Un litige, besoin d'un avocat", "balance"),
    ("carte", "Carte perdue, volée, paiement frauduleux", "carte"),
    ("naissance", "Naissance ou adoption", "berceau"),
    ("coup-dur", "Coup dur : décès, difficultés financières", "parapluie"),
    ("loisirs", "Vacances, loisirs, réductions", "soleil"),
]
CLES_SITUATIONS = {s[0] for s in SITUATIONS}
STATUTS = {"notice", "source-tierce", "typique", "piste", "verifie", "absent", "perso"}

CEAM = "Emporte la carte européenne d'assurance maladie (CEAM, à demander sur ameli.fr) pour les voyages en Europe."
OPPOSITION = "0 892 705 705 (centre d'opposition interbancaire, 7j/7, 24h/24) ou l'appli de la banque"

SOURCE_ULTIM = "https://www.boursobank.com/ultim/"
DATE_ULTIM = "notice Chubb FRBOTY03361, applicable au 1er janvier 2026"
SOURCE_BRED_CARTE = "https://www.bred.fr/medias/pdf/informations-reglementaires/notice-carte-visa-classique.pdf"
SOURCE_CAMIEG = "https://www.camieg.fr/fileadmin/05-Garanties-Soins/Garanties/Tableau-garanties-camieg.pdf"
DATE_CAMIEG = "tableau des garanties CAMIEG en vigueur au 1er juillet 2026"
SOURCE_SANERGI = "https://infos-sanergi-ieg.ca-assurances.com/memo-3dc7ot-4bgxkTQW/memo-options-et-garanties.pdf"
SOURCE_SANERGI_ASSIST = "https://infos-sanergi-ieg.ca-assurances.com/memo-2P09As-4bqHggpY/memo-assistance.pdf"
SOURCE_AXA = "https://ccas.satecassur.com/uploads/documents/Assurance-automobile-Conditions-generales-05-2025-2025-05-15.pdf"
DATE_AXA = "conditions générales AXA – CCAS 05/2025 et page ccas.satecassur.com/auto"

CHUBB = "Chubb Assistance : +33 1 70 39 12 17, choix 1 (24h/24)"
CHUBB_SINISTRE = "Déclaration sur bour.so/assurances-voyages, ou +33 1 70 39 12 17, choix 3"
BRED_ASSIST = "Assistance de la carte : +33 9 69 32 10 03 (24h/24) ou votre-assistance.fr"
AXA_ASSIST = "AXA Assistance : 01 55 92 19 85 (24h/24, 7j/7)"
AXA_SINISTRE = "Service sinistres AXA – CCAS : 0 970 809 669 (lun-ven 8h30-18h), service.ccas@axa.fr"
CAMIEG_TEL = "CAMIEG : 08 06 06 93 00 (service gratuit + prix d'appel), camieg.fr"
SANERGI_TEL = "sanergi ieg : 09 69 39 29 38 (orientation), appli « sanergi ieg Ma Santé »"


def d(cle, titre, categorie, situations, resume, *, plafond="", franchise="", conditions="", demarche="", contact="",
      delai="", statut="notice", theme="", valeur=None):
    return {"cle": cle, "titre": titre, "categorie": categorie, "situations": situations, "resume": resume,
            "plafond": plafond, "franchise": franchise, "conditions": conditions, "demarche": demarche,
            "contact": contact, "delai": delai, "statut": statut, "theme": theme, "valeur": valeur}


ULTIM_VOYAGE = "Voyage à l'étranger, ou en France à plus de 100 km de chez toi"
ULTIM_PAYE = "Voyage payé au moins pour moitié (transport ou hébergement) avec la carte Ultim, avant le sinistre ; 180 premiers jours du déplacement"
ULTIM_ASSIST = "90 premiers jours du déplacement ; titulaire, conjoint et enfants"

PRODUITS: dict[str, dict] = {
    "boursobank-ultim": {
        "nom": "Carte Visa Ultim", "fournisseur": "BoursoBank", "type": "carte", "couleur": "nuit-rose",
        "source_url": SOURCE_ULTIM, "source_date": DATE_ULTIM,
        "droits": [
            d("ultim-frais-medicaux", "Frais médicaux à l'étranger", "assistance", ["sante-etranger", "voyage"],
              "Hospitalisation, médecin et médicaments à l'étranger, après la Sécurité sociale et la mutuelle.",
              plafond="155 000 € par personne et par sinistre", franchise="Aucune", conditions=ULTIM_ASSIST,
              demarche="Appelle Chubb Assistance avant d'engager des frais : sinon, ce qui aurait pu être évité est déduit.",
              contact=CHUBB, theme="frais-medicaux-etranger", valeur=155000),
            d("ultim-dentaire", "Soins dentaires d'urgence à l'étranger", "assistance", ["sante-etranger"],
              "Une rage de dents ou une dent cassée pendant le voyage.", plafond="700 €", franchise="50 €",
              conditions=ULTIM_ASSIST, contact=CHUBB),
            d("ultim-rapatriement", "Rapatriement médical", "assistance", ["sante-etranger", "voyage"],
              "Retour en France organisé par l'assistance, et retour des accompagnants assurés.",
              plafond="Frais réels", conditions=ULTIM_ASSIST, contact=CHUBB, theme="rapatriement"),
            d("ultim-secours", "Secours et recherche en montagne", "assistance", ["ski", "sante-etranger"],
              "Frais de premiers secours, et frais de recherche et de secours en montagne.",
              plafond="Secours : 2 500 € ; recherche en montagne : frais réels", conditions=ULTIM_ASSIST, contact=CHUBB),
            d("ultim-proches", "Un proche à ton chevet, garde des enfants", "assistance", ["sante-etranger"],
              "Si tu es hospitalisée : voyage d'un proche, hébergement, retour anticipé, garde des enfants de moins de 15 ans.",
              plafond="Hébergement 125 €/nuit (10 nuits) ; garde d'enfants 200 €/jour (5 jours)", conditions=ULTIM_ASSIST,
              contact=CHUBB),
            d("ultim-juridique", "Avance de caution et d'avocat à l'étranger", "juridique", ["juridique", "voyage"],
              "Poursuites pour une infraction non intentionnelle hors de France : l'assistance avance la caution et l'avocat.",
              plafond="Avances jusqu'à 16 000 € chacune (à rembourser) ; avocat pris en charge jusqu'à 3 100 €",
              conditions=ULTIM_ASSIST, contact=CHUBB, theme="caution-penale", valeur=16000),
            d("ultim-avance", "Avance d'argent et papiers perdus", "assistance", ["voyage", "carte"],
              "Avance de frais sur place si tu perds tes moyens de paiement, aide pour refaire passeport ou carte d'identité.",
              plafond="Avance jusqu'à 2 000 €", conditions=ULTIM_ASSIST, contact=CHUBB),
            d("ultim-annulation", "Annulation ou modification du voyage", "voyage", ["annulation", "voyage"],
              "Remboursement des frais non utilisés si tu dois annuler pour une raison couverte (maladie, accident…).",
              plafond="5 000 € par personne et par an", franchise="Aucune", conditions=ULTIM_PAYE,
              demarche="Déclare en ligne dès que tu sais que tu dois annuler.", contact=CHUBB_SINISTRE,
              delai="Immédiatement, ou dans les 30 jours", theme="annulation", valeur=5000),
            d("ultim-interruption", "Interruption de voyage", "voyage", ["annulation", "sante-etranger"],
              "Les nuits et prestations non utilisées si tu dois rentrer plus tôt, et les frais supplémentaires.",
              plafond="5 000 € par personne et par an", conditions=ULTIM_PAYE, contact=CHUBB_SINISTRE,
              delai="Dans les 30 jours"),
            d("ultim-retard", "Retard de transport, correspondance manquée", "voyage", ["retard", "voyage"],
              "Vol ou train retardé de plus de 4 heures, ou correspondance manquée : repas, hôtel, achats de première nécessité.",
              plafond="400 € par retard", conditions=ULTIM_PAYE, demarche="Garde les justificatifs du retard et les tickets.",
              contact=CHUBB_SINISTRE, delai="Dans les 30 jours", theme="retard-transport", valeur=400),
            d("ultim-depart-manque", "Départ manqué", "voyage", ["retard", "voyage"],
              "Frais d'hébergement et de transport pour poursuivre le voyage si tu rates ton départ.",
              plafond="400 € par personne et par an", conditions=ULTIM_PAYE, contact=CHUBB_SINISTRE, delai="Dans les 30 jours"),
            d("ultim-bagages", "Bagages perdus, volés ou abîmés", "voyage", ["bagages", "voyage"],
              "Tes affaires perdues, volées ou abîmées pendant le voyage.",
              plafond="800 € par sinistre ; 300 € par objet ; objets précieux 250 €", conditions=ULTIM_PAYE,
              demarche="Signale le vol dans les 24 h à la police locale ou à l'hôtel, et demande un rapport.",
              contact=CHUBB_SINISTRE, delai="Dans les 30 jours", theme="bagages", valeur=800),
            d("ultim-bagages-retard", "Bagages en retard", "voyage", ["bagages", "retard"],
              "Bagages livrés plus de 4 heures après ton arrivée : achats de première nécessité.",
              plafond="400 € par sinistre", conditions=ULTIM_PAYE, demarche="Garde le rapport de la compagnie et les tickets.",
              contact=CHUBB_SINISTRE, delai="Dans les 30 jours"),
            d("ultim-location", "Franchise de la voiture de location", "voyage", ["location", "voyage"],
              "Si la voiture louée est volée ou abîmée, la franchise demandée par le loueur est remboursée.",
              plafond="50 000 € par sinistre, 2 sinistres par an", conditions=ULTIM_PAYE,
              demarche="Tu peux refuser le rachat de franchise du loueur. Garde le contrat de location et le constat.",
              contact=CHUBB_SINISTRE, delai="Dans les 30 jours", theme="location-voiture", valeur=50000),
            d("ultim-accident-transport", "Accident pendant le voyage", "voyage", ["voyage"],
              "Capital en cas de décès accidentel ou d'invalidité permanente pendant le voyage.",
              plafond="310 000 € en transport public ; 46 000 € en véhicule loué ou privé", conditions="Titre de transport payé avec la carte Ultim",
              contact=CHUBB_SINISTRE, theme="deces-voyage", valeur=310000),
            d("ultim-rc", "Responsabilité civile à l'étranger", "voyage", ["dommage-cause", "voyage"],
              "Les dommages que tu causes à quelqu'un pendant un voyage.",
              plafond="Corporels 4,5 M€ ; matériels 1,525 M€", conditions=ULTIM_PAYE, contact=CHUBB_SINISTRE,
              delai="Dans les 30 jours", theme="rc"),
            d("ultim-ski", "Sports d'hiver", "voyage", ["ski"],
              "Forfait ou cours non utilisés, ton équipement ou celui loué cassé ou volé, frais médicaux en France.",
              plafond="Forfait 800 € ; équipement 800 € ; frais médicaux en France 2 300 €",
              franchise="Équipement : 150 € (le tien), 50 € (loué) ; frais médicaux : 30 €", conditions=ULTIM_PAYE,
              contact=CHUBB_SINISTRE, delai="Dans les 30 jours", theme="ski"),
            d("ultim-frais", "Paiements et retraits à l'étranger", "avantage", ["voyage", "loisirs"],
              "Paiements gratuits partout, retraits en euros gratuits ; retraits en devises : 3 gratuits par mois, puis 1,69 %.",
              conditions="Carte gratuite si tu fais au moins un paiement par mois (sinon 9 € ce mois-là)",
              statut="notice"),
            d("ultim-fraude", "Paiements frauduleux remboursés", "banque", ["carte"],
              "Après une perte, un vol ou un paiement que tu n'as pas fait, la banque doit te rembourser (Code monétaire et financier).",
              franchise="Au plus 50 € avant l'opposition (rien pour un achat en ligne frauduleux), sauf négligence grave",
              demarche="Fais opposition tout de suite, puis conteste les opérations auprès de BoursoBank.",
              contact=OPPOSITION, delai="Le plus vite possible ; contestation jusqu'à 13 mois", theme="fraude-carte"),
        ],
    },
    "bred-visa-classic": {
        "nom": "Carte Visa Classic", "fournisseur": "BRED", "type": "carte", "couleur": "bleu",
        "source_url": SOURCE_BRED_CARTE, "source_date": "notice BRED (version 2023) et comparateurs, notice en vigueur non lue",
        "droits": [
            d("bred-frais-medicaux", "Frais médicaux à l'étranger", "assistance", ["sante-etranger", "voyage"],
              "Frais médicaux d'urgence à l'étranger, après la Sécurité sociale et la mutuelle.",
              plafond="11 000 € par personne", franchise="50 €", conditions="90 premiers jours du déplacement",
              contact=BRED_ASSIST, statut="source-tierce", theme="frais-medicaux-etranger", valeur=11000),
            d("bred-rapatriement", "Rapatriement médical", "assistance", ["sante-etranger"],
              "Retour en France organisé par l'assistance de la carte.", plafond="Frais réels",
              conditions="90 premiers jours du déplacement", contact=BRED_ASSIST, statut="source-tierce", theme="rapatriement"),
            d("bred-deces", "Décès ou invalidité en voyage", "voyage", ["voyage"],
              "Capital en cas d'accident pendant un voyage.", plafond="46 000 €",
              conditions="Voyage payé avec la carte Visa Classic", statut="source-tierce", theme="deces-voyage", valeur=46000),
            d("bred-juridique", "Caution pénale et avocat à l'étranger", "juridique", ["juridique", "voyage"],
              "Avance de la caution et prise en charge d'un avocat si tu es poursuivie à l'étranger.",
              plafond="Caution 7 770 € (avance) ; avocat 3 100 €", contact=BRED_ASSIST, statut="source-tierce",
              theme="caution-penale", valeur=7770),
            d("bred-fraude", "Paiements frauduleux remboursés", "banque", ["carte"],
              "Après une perte, un vol ou un paiement que tu n'as pas fait, la banque doit te rembourser (Code monétaire et financier).",
              franchise="Au plus 50 € avant l'opposition (rien pour un achat en ligne frauduleux), sauf négligence grave",
              demarche="Fais opposition tout de suite, puis conteste les opérations auprès de la BRED.",
              contact=OPPOSITION, delai="Le plus vite possible ; contestation jusqu'à 13 mois", theme="fraude-carte"),
        ],
    },
    "camieg": {
        "nom": "Régime santé des IEG", "fournisseur": "CAMIEG", "type": "regime", "couleur": "vert",
        "source_url": SOURCE_CAMIEG, "source_date": DATE_CAMIEG,
        "droits": [
            d("camieg-soins", "Consultations, pharmacie, analyses", "sante", ["soins"],
              "Médecin : 120 % de la base de remboursement (70 % obligatoire + 50 % complémentaire). Médicaments remboursés à 100 %. Analyses et kiné : 120 %.",
              contact=CAMIEG_TEL, demarche="Carte Vitale et carte de tiers payant CAMIEG chez le médecin et en pharmacie."),
            d("camieg-hospi", "Hospitalisation", "sante", ["hospitalisation"],
              "Frais d'hospitalisation pris en charge à 100 % ; honoraires pendant le séjour jusqu'à 300 % de la base.",
              contact=CAMIEG_TEL, demarche="Présente la carte de tiers payant à l'admission.", theme="hospitalisation"),
            d("camieg-optique", "Lunettes et lentilles", "sante", ["optique"],
              "Panier 100 % Santé : rien à payer. Hors panier, adultes : monture 35 €, verres 50 € (simples), 124 € (complexes), 185 € (très complexes). Moins de 18 ans : monture 77 €, verres 43 à 197 €.",
              plafond="Lentilles remboursées : 705 % de la base ; non remboursées : 92,30 €/an (151,20 € avant 18 ans)",
              contact=CAMIEG_TEL, theme="optique"),
            d("camieg-dentaire", "Dentaire", "sante", ["dentaire"],
              "Prothèses 100 % Santé : rien à payer. Prothèses à tarifs maîtrisés ou libres : 495 % de la base. Orthodontie acceptée : 360 %.",
              demarche="Demande un devis au dentiste avant les soins.", contact=CAMIEG_TEL, theme="dentaire"),
            d("camieg-audition", "Appareils auditifs", "sante", ["audition"],
              "Classe I (100 % Santé) : pris en charge intégralement. Classe II : jusqu'à 1 700 € par oreille.",
              contact=CAMIEG_TEL, theme="audition"),
            d("camieg-cures", "Cures thermales", "sante", ["soins"],
              "Soins médicaux et thermaux : 120 %. Hébergement et transport selon tes ressources.", contact=CAMIEG_TEL),
            d("camieg-layette", "Prime de layette", "famille", ["naissance"],
              "Une somme pour l'arrivée d'un enfant.", plafond="341 €", contact=CAMIEG_TEL,
              demarche="Demande-la à la CAMIEG (rubrique « Préparer l'arrivée d'un enfant »)."),
            d("camieg-obseques", "Frais d'obsèques", "famille", ["coup-dur"],
              "Une allocation forfaitaire en cas de décès.", plafond="682 €", contact=CAMIEG_TEL),
            d("camieg-aides", "Aides et accompagnements", "famille", ["coup-dur", "soins"],
              "Aide financière selon ta situation, aide psychologique, aide au sevrage tabagique, vaccin contre la grippe.",
              contact=CAMIEG_TEL, statut="piste", demarche="Rubriques « Demander une aide financière » et garanties sur camieg.fr."),
        ],
    },
    "sanergi-ieg": {
        "nom": "Couverture supplémentaire maladie (CSM)", "fournisseur": "sanergi ieg", "type": "mutuelle", "couleur": "turquoise",
        "source_url": SOURCE_SANERGI, "source_date": "mémos sanergi ieg (Crédit Agricole Assurances), tarifs 2025",
        "droits": [
            d("sanergi-base", "Le complément de la CAMIEG", "sante", ["soins", "hospitalisation", "optique", "dentaire", "audition"],
              "La CSM s'ajoute aux remboursements de la CAMIEG, sans délai de carence. Trois options facultatives la renforcent : Select, Medium, Premium.",
              plafond="Options par mois : Select 4,95 € (8,16 € famille), Medium 19,49 € (32,16 €), Premium 27,98 € (46,17 €)",
              demarche="Pour changer d'option : avant le 31 octobre, effet au 1er janvier. Ajouter un enfant ou un conjoint : dans les 30 jours.",
              contact=SANERGI_TEL),
            d("sanergi-chambre", "Chambre particulière", "sante", ["hospitalisation"],
              "La chambre seule à l'hôpital, maternité comprise (8 jours au plus).",
              plafond="Base CSM : 3 % du plafond mensuel de la Sécurité sociale par nuit (environ 118 € en 2025) ; ambulatoire 1,12 % par jour ; plus avec les options",
              demarche="Demande-la à l'admission et présente ta carte sanergi ieg.", contact=SANERGI_TEL, theme="chambre-particuliere", valeur=118),
            d("sanergi-honoraires", "Dépassements d'honoraires à l'hôpital", "sante", ["hospitalisation"],
              "Pour un chirurgien hors OPTAM, la CAMIEG rembourse 300 % de la base ; la base CSM n'ajoute rien, les options de +80 à +220 %.",
              conditions="Selon l'option souscrite", contact=SANERGI_TEL),
            d("sanergi-renforts", "Optique, dentaire, audition : les renforts", "sante", ["optique", "dentaire", "audition"],
              "En plus de la CAMIEG : une grille de remboursement des verres selon ta correction, des forfaits dentaires (orthodontie, couronnes provisoires) et un complément pour l'audition, plus élevés avec les options.",
              conditions="Montants selon l'option : voir le tableau des garanties du mémo", statut="source-tierce", contact=SANERGI_TEL),
            d("sanergi-garde", "Garde d'enfants et aide à domicile", "assistance", ["convalescence", "hospitalisation"],
              "Si tu es malade ou accidentée : garde des enfants, livraison de médicaments, recherche d'un médecin ou d'une infirmière, aide en cas d'immobilisation.",
              plafond="Garde d'enfants : 20 heures au plus ; livraison de médicaments : frais réels",
              conditions="Toi (salariée), ton conjoint et tes enfants", contact=SANERGI_TEL + " ; numéro d'assistance dans l'appli, rubrique Contact",
              theme="aide-domicile"),
            d("sanergi-deplacement", "Malade en déplacement en France", "assistance", ["sante-etranger", "ski", "voyage"],
              "En France métropolitaine : transport sanitaire, prolongation d'hôtel, secours sur les pistes de ski.",
              plafond="Hôtel 80 €/nuit, 10 nuits ; secours sur piste 460 €", contact=SANERGI_TEL),
            d("sanergi-emploi", "Retour à l'emploi après une maladie", "assistance", ["convalescence", "coup-dur"],
              "Après un accident, une maladie ou une ALD : entretiens d'orientation, aide au retour à l'emploi, accompagnement à la reconversion.",
              plafond="Programme de 3 entretiens ; jusqu'à 10 heures pour une reconversion", contact=SANERGI_TEL),
            d("sanergi-fonds-social", "Fonds social", "famille", ["coup-dur"],
              "Une aide financière ponctuelle si tu fais face à certaines dépenses de santé.", contact=SANERGI_TEL,
              statut="piste", demarche="Demande le dossier au centre de gestion sanergi ieg."),
        ],
    },
    "bred-habitation": {
        "nom": "Assurance habitation", "fournisseur": "BRED", "type": "assurance", "couleur": "bleu",
        "source_url": "https://www.bred.fr", "source_date": "garanties habituelles d'une multirisque habitation : à confirmer avec tes conditions particulières",
        "droits": [
            d("hab-eau", "Dégât des eaux, incendie, tempête", "maison", ["maison"],
              "Les dommages à ton logement et à tes meubles après une fuite, un incendie ou une tempête.",
              demarche="Coupe l'eau, protège ce qui peut l'être, prends des photos, garde les factures. Fais un constat amiable dégât des eaux avec le voisin.",
              delai="5 jours ouvrés (délai légal minimum)", statut="typique", theme="habitation"),
            d("hab-catnat", "Catastrophe naturelle", "maison", ["maison"],
              "Inondation, sécheresse, coulée de boue… reconnue par un arrêté publié au Journal officiel : garantie obligatoire de toute assurance habitation.",
              delai="30 jours après la publication de l'arrêté", statut="typique"),
            d("hab-vol", "Vol et vandalisme", "maison", ["maison"],
              "Cambriolage, objets volés, dégradations.", conditions="Selon ta formule (souvent avec conditions de serrures)",
              demarche="Porte plainte, puis envoie le récépissé à l'assureur.", delai="2 jours ouvrés (délai légal minimum)", statut="typique"),
            d("hab-rc", "Responsabilité civile vie privée", "maison", ["dommage-cause"],
              "Les dommages que toi, tes enfants ou tes animaux causez à quelqu'un dans la vie de tous les jours. Souvent incluse, souvent oubliée.",
              statut="typique", theme="rc"),
            d("hab-assistance", "Assistance habitation", "maison", ["maison"],
              "Envoi d'un plombier ou d'un serrurier en urgence, relogement si le logement est inhabitable.",
              conditions="Selon ta formule", statut="typique", theme="assistance-maison"),
            d("hab-pj", "Protection juridique", "juridique", ["juridique"],
              "Un litige avec un voisin, un artisan, un vendeur : informations juridiques, frais d'avocat.",
              conditions="Souvent en option", statut="typique", theme="protection-juridique"),
        ],
    },
    "axa-ccas-auto": {
        "nom": "Assurance auto (contrat groupe CCAS)", "fournisseur": "AXA, par SATEC", "type": "assurance", "couleur": "rouge",
        "source_url": SOURCE_AXA, "source_date": DATE_AXA,
        "droits": [
            d("axa-assistance", "Assistance panne et accident dès 0 km", "auto", ["panne"],
              "Dépannage ou remorquage même devant chez toi, panne de carburant comprise.",
              conditions="Toutes les formules : assistance accident et panne sans franchise kilométrique",
              demarche="Appelle l'assistance avant tout dépannage : elle l'organise et le prend en charge.", contact=AXA_ASSIST,
              theme="assistance-auto"),
            d("axa-personnes", "Assistance aux personnes", "auto", ["panne", "sante-etranger"],
              "Rapatriement, hôtel, retour des passagers après un accident ou une panne loin de chez toi.",
              franchise="30 km du domicile", contact=AXA_ASSIST),
            d("axa-conducteur", "Sécurité du conducteur", "auto", ["panne"],
              "Ton préjudice corporel indemnisé si tu es blessée en conduisant, même si l'accident est de ta faute.",
              plafond="450 000 € (1 000 000 € avec l'option ou le pack Excellence) ; décès du conducteur 10 000 €",
              contact=AXA_SINISTRE, delai="5 jours ouvrés"),
            d("axa-juridique", "Protection juridique et informations par téléphone", "juridique", ["juridique", "panne"],
              "Défense pénale et recours après un accident, protection juridique, et un juriste au téléphone.",
              contact="Informations juridiques : 01 30 09 97 26 (lun-ven 9h30-19h30) ; " + AXA_SINISTRE,
              theme="protection-juridique"),
            d("axa-dommages", "Vol, incendie, bris de glace, dommages", "auto", ["panne"],
              "Formule 2 : vol, incendie, événements climatiques, catastrophes naturelles, bris de glace sans franchise. Formule 3 : en plus, dommages tous accidents et valeur à neuf 12 mois.",
              conditions="Selon ta formule : regarde tes conditions particulières", demarche="Vol : porte plainte et déclare-le.",
              contact=AXA_SINISTRE, delai="5 jours ouvrés ; vol : 2 jours ouvrés", statut="source-tierce"),
            d("axa-remplacement", "Véhicule de remplacement", "auto", ["panne"],
              "Une voiture prêtée pendant l'immobilisation de la tienne.",
              plafond="7 jours après une panne, 15 jours après un accident, 30 jours après un vol",
              conditions="Avec le pack « Ma mobilité » ou l'option véhicule de remplacement", contact=AXA_ASSIST, statut="source-tierce"),
            d("axa-sinistralite", "Pas de résiliation après des sinistres", "avantage", ["panne"],
              "Le contrat groupe des IEG n'est pas résilié parce que tu as eu des sinistres.", statut="source-tierce"),
        ],
    },
    "statut-ieg": {
        "nom": "Avantages du statut IEG", "fournisseur": "CCAS, CMCAS, employeur", "type": "statut", "couleur": "laiton",
        "source_url": "https://www.ccas.fr", "source_date": "pistes liées au statut des industries électriques et gazières, à confirmer",
        "droits": [
            d("ieg-activites", "Activités sociales CCAS et CMCAS", "avantage", ["loisirs", "naissance", "coup-dur"],
              "Séjours de vacances, colonies pour les enfants, culture, sport, aides : les activités sociales des IEG, financées par le 1 % des ventes d'énergie.",
              demarche="Connecte-toi à ton espace CCAS ou va voir ta CMCAS.", statut="piste"),
            d("ieg-tarif-agent", "Tarif agent pour l'électricité et le gaz", "avantage", ["loisirs"],
              "Les agents statutaires des IEG paient l'énergie de leur logement principal à un tarif réduit.",
              conditions="Agent statutaire (actif ou retraité)", statut="piste"),
        ],
    },
}

# Ce que chaque situation demande de savoir d'abord. Le premier réflexe dont tous les produits sont présents est retenu.
REFLEXES: dict[str, list[tuple[set[str], str]]] = {
    "voyage": [({"boursobank-ultim"}, "Paie au moins la moitié du voyage (billets ou hôtel) avec la carte Ultim : c'est elle qui active l'annulation (5 000 €), les bagages, les retards et la franchise de location. Enregistre le +33 1 70 39 12 17 et pense à la CEAM pour l'Europe.")],
    "sante-etranger": [({"boursobank-ultim", "bred-visa-classic"}, "Appelle d'abord Chubb Assistance (carte Ultim, +33 1 70 39 12 17, choix 1) avant d'engager des frais : elle couvre jusqu'à 155 000 € de frais médicaux, contre 11 000 € avec la Visa Classic BRED."),
                       ({"boursobank-ultim"}, "Appelle d'abord Chubb Assistance (+33 1 70 39 12 17, choix 1) avant d'engager des frais.")],
    "annulation": [({"boursobank-ultim"}, "L'annulation n'est couverte que si le voyage a été payé au moins pour moitié avec la carte Ultim. Déclare-la en ligne dès que tu sais que tu ne pourras pas partir.")],
    "bagages": [({"boursobank-ultim"}, "Fais un rapport auprès de la compagnie (ou de la police en cas de vol, dans les 24 h), garde les tickets de tes achats de dépannage, puis déclare sous 30 jours.")],
    "retard": [({"boursobank-ultim"}, "Au-delà de 4 heures de retard, la carte Ultim rembourse jusqu'à 400 € de frais : garde l'attestation de retard et les tickets.")],
    "location": [({"boursobank-ultim"}, "Paie la location avec la carte Ultim et refuse le rachat de franchise du loueur : la franchise est remboursée jusqu'à 50 000 € (2 fois par an).")],
    "ski": [({"boursobank-ultim", "sanergi-ieg"}, "Avec l'Ultim : forfait non utilisé et matériel jusqu'à 800 €, frais médicaux en France jusqu'à 2 300 €. Sanergi paie aussi les secours sur piste jusqu'à 460 €.")],
    "panne": [({"axa-ccas-auto"}, "Appelle AXA Assistance (01 55 92 19 85) avant tout dépanneur, même devant chez toi : l'assistance marche dès 0 km. Déclare ensuite le sinistre sous 5 jours ouvrés (2 en cas de vol).")],
    "maison": [({"bred-habitation"}, "Coupe l'eau ou l'électricité, prends des photos, garde les factures et déclare à l'assurance habitation BRED sous 5 jours ouvrés (2 jours en cas de vol, après la plainte).")],
    "dommage-cause": [({"bred-habitation", "boursobank-ultim"}, "En France, c'est la responsabilité civile de l'assurance habitation (à vérifier) ; en voyage, la carte Ultim te couvre aussi. Ne reconnais pas ta responsabilité par écrit avant d'en parler à l'assureur.")],
    "optique": [({"camieg", "sanergi-ieg"}, "Le panier 100 % Santé ne te coûte rien. Hors panier, la CAMIEG rembourse un forfait (monture 35 €, verres 50 à 185 €) et sanergi ieg complète selon ton option : demande un devis à l'opticien.")],
    "dentaire": [({"camieg", "sanergi-ieg"}, "Demande un devis : les prothèses 100 % Santé sont sans reste à charge ; sinon CAMIEG 495 % de la base, plus sanergi ieg selon ton option.")],
    "audition": [({"camieg"}, "Classe I (100 % Santé) : rien à payer. Classe II : jusqu'à 1 700 € par oreille. Compare les deux avec l'audioprothésiste.")],
    "soins": [({"camieg"}, "Carte Vitale et carte de tiers payant CAMIEG : tu n'avances presque rien chez le médecin ni en pharmacie.")],
    "hospitalisation": [({"camieg", "sanergi-ieg"}, "Présente les cartes CAMIEG et sanergi ieg à l'admission et demande la chambre particulière (3 % du plafond Sécurité sociale par nuit avec la base). Après, l'assistance sanergi peut garder les enfants ou livrer les médicaments.")],
    "convalescence": [({"sanergi-ieg"}, "L'assistance sanergi ieg (Europ Assistance) peut garder les enfants jusqu'à 20 heures et livrer les médicaments : le numéro est dans l'appli Ma Santé, rubrique Contact.")],
    "juridique": [({"axa-ccas-auto"}, "Un juriste répond au 01 30 09 97 26 (informations juridiques du contrat auto AXA – CCAS). À l'étranger, la carte Ultim avance caution et avocat jusqu'à 16 000 €.")],
    "carte": [({"boursobank-ultim"}, "Fais opposition tout de suite (0 892 705 705 ou l'appli). Les paiements frauduleux te sont remboursés, avec au plus 50 € à ta charge avant l'opposition, sauf négligence grave.")],
    "naissance": [({"camieg", "sanergi-ieg"}, "Demande la prime de layette de la CAMIEG (341 €) et ajoute l'enfant à sanergi ieg dans les 30 jours.")],
    "coup-dur": [({"camieg", "sanergi-ieg"}, "CAMIEG : allocation obsèques de 682 € et aides financières selon ta situation. sanergi ieg : un fonds social pour une aide ponctuelle.")],
    "loisirs": [({"statut-ieg"}, "En tant qu'agent des IEG, regarde les séjours et activités de la CCAS et de ta CMCAS.")],
}

# Ce qui manque souvent : affiché si aucune garantie de ce thème n'est dans le profil.
TROUS = [
    ("achats", "Garantie des achats et casse du téléphone", "Aucune de tes cartes ne couvre la casse ou le vol d'un téléphone. BoursoBank propose Bourso Protect en option (0,99 €/mois)."),
    ("prevoyance", "Arrêt de travail, invalidité", "Ni les cartes ni la mutuelle ne versent de revenu en cas d'arrêt long : vérifie ce que prévoient le statut IEG et ton employeur."),
    ("protection-juridique", "Protection juridique générale", "Hors voiture, rien ne couvre un litige (voisin, artisan, achat) : regarde si l'assurance habitation a l'option."),
]
THEMES_DES_TROUS = {"achats", "prevoyance"}       # thèmes sans garantie dans le catalogue : toujours des trous, sauf ajout


def produits_publics() -> list[dict]:
    return [{"cle": k, "nom": p["nom"], "fournisseur": p["fournisseur"], "type": p["type"], "garanties": len(p["droits"])}
            for k, p in PRODUITS.items()]
