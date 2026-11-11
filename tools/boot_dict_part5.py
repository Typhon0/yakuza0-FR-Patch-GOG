# -*- coding: utf-8 -*-
"""
tools/boot_dict_part5.py
-------------------------
Traduction française des 195 chaînes UI restantes de string_tbl.bin_c dans boot.par:
- Menus principaux (Nouvelle partie, Charger, Difficulté Légende)
- Descriptions des styles de combat (Bagarreur, Fonceur, Brute, Voyou, Danseur, Batteur)
- Zones de l'Immobilier (Roi des médias, Roi du jeu, etc.)
- Zones du Cabaret (Club Mars, Club Jupiter, Club Mercury, Club Venus, Club Moon)
- Interactions système, coffre, inventaire et sanctuaire CP
"""

P5 = {
    # Navigation & Boutons
    'Back': 'Retour',
    'Close': 'Fermer',
    'OK    Back': 'OK    Retour',
    'Cancel': 'Annuler',
    'Money': 'Argent',
    'Price': 'Prix',
    'Area': 'Zone',
    'Status': 'Statut',
    'Style': 'Style',
    'Style:': 'Style :',
    'Playing Style': 'Style de jeu',
    'Coliseum Style': 'Style du Colisée',
    'Style Features': 'Spécificités du style',
    'Heat Actions': 'Actions Heat',
    'Dodge Enemy Attacks': 'Esquiver les attaques ennemies',
    'OPTIONS button': 'Touche OPTIONS',
    'Touch pad button': 'Touche pavé tactile',
    'SELECT button': 'Touche SELECT',
    'Return to Title': 'Écran titre',
    'Return to title screen?': 'Retourner à l\'écran titre ?',
    'Return to the main menu?': 'Retourner au menu principal ?',
    'Unsaved data will be lost. Are you sure?': 'Les données non sauvegardées seront perdues. Confirmer ?',
    'Save the game?': 'Sauvegarder la partie ?',
    'Cancel saving?': 'Annuler la sauvegarde ?',
    'Cancel loading?': 'Annuler le chargement ?',
    'Cancel Changes?': 'Annuler les modifications ?',
    'Are you sure?': 'Êtes-vous sûr ?',
    'Are you sure you want to skip?': 'Voulez-vous vraiment passer ?',
    'Chapter Result': 'Bilan du chapitre',
    'Result': 'Résultat',
    'Result Table': 'Tableau des résultats',
    'Defeat': 'Défaite',
    'Complete': 'Terminé',
    'Attack': 'Attaque',
    'Store': 'Boutique',
    'Training': 'Entraînement',
    'Special Training': 'Entraînement spécial',
    'Special Training Info': 'Infos entraînement spécial',
    'Club Status': 'Statut du club',
    'Club Status Info': 'Infos statut du club',

    # Expédition des agents
    'Dispatch Cost': 'Coût d\'envoi',
    "Agent's Fee": "Honoraires de l'agent",
    'Select a destination.': 'Choisir une destination.',
    'Dispatch agent?': 'Envoyer l\'agent ?',
    'Destination Settings': 'Choix destination',
    'Remove destination?': 'Retirer la destination ?',

    # Inventaire, coffre & exploration
    'Item Box': 'Coffre',
    'Inventory': 'Inventaire',
    'Use': 'Utiliser',
    'Sell': 'Vendre',
    'Discard': 'Jeter',
    'Look': 'Examiner',
    'Use item?': 'Utiliser l\'objet ?',
    'Use this item?': 'Utiliser cet objet ?',
    'Discard item?': 'Jeter l\'objet ?',
    'Buy Item?': 'Acheter l\'objet ?',
    'Give this item?': 'Donner cet objet ?',
    'Your item box is also full. Discard item?': 'Le coffre est également plein. Jeter l\'objet ?',
    "Don't have anything I can use.": "Je n'ai rien d'utilisable.",
    'What should I use?': 'Que devrais-je utiliser ?',
    '(What should I eat?)': '(Que devrais-je manger ?)',
    'Are you sure you want to eat it?': 'Voulez-vous vraiment manger ceci ?',
    "(Haven't got anything to give it.)": "(Je n'ai rien à lui donner.)",
    '(Anything to make it feel better?)': '(Un truc pour le soulager ?)',
    "You can't carry any more items.": "Vous ne pouvez plus porter d'objets.",
    "(I'm carrying too much stuff.)": "(Je porte trop de choses.)",
    "(Can't carry any more stuff.)": "(Je ne peux rien porter de plus.)",
    'Use the left stick to look around.': 'Utilisez le stick gauche pour regarder autour.',

    # Sanctuaire CP
    'Exchange CP for this item?': 'Échanger des CP contre cet objet ?',
    "(I don't have enough CP.)": "(Je n'ai pas assez de CP.)",
    "(Ain't got enough CP for this.)": "(J'ai pas assez de CP pour ça.)",
    "(Guess I can't do this in Kamurocho.)": "(Impossible de faire ça à Kamurocho.)",

    # Immobilier sous cloche (Cinq Rois)
    'Media King Area': 'Zone du Roi des médias',
    'Gambling King Area': 'Zone du Roi du jeu',
    'Leisure King Area': 'Zone du Roi des loisirs',
    'Electronics King Area': 'Zone du Roi de l\'électronique',
    'Pleasure King Area': 'Zone du Roi des plaisirs',
    'Area share increased.': 'Part de marché augmentée.',
    'Area share decreased.': 'Part de marché diminuée.',
    'Purchased %s': 'Bien acquis : %s',
    'Share': 'Part',
    'Share Gained': 'Part acquise',
    'Share Bonus': 'Bonus de part',
    '%u\xef\xbc\x85': '%u%%',
    '\xc3\x97%u\xef\xbc\x85': '×%u%%',
    '%d\xef\xbc\x85': '%d%%',
    'Profit Forecast': 'Bénéfices estimés',
    'Economy': 'Économie',
    'Safety Rank': 'Sécurité',
    'Property Rank': 'Rang du bien',
    'Rank': 'Rang',
    'Management Skills': 'Gestion',
    'Troubleshooting': 'Dépannage',
    'Strength': 'Force',
    'Battle Assist Rate': 'Taux de soutien',
    'Property Skills': 'Compétences du bien',
    'Investment': 'Investissement',
    'Profile': 'Profil',
    'Salary': 'Salaire',
    'Role': 'Rôle',
    'Manage areas.': 'Gérer les zones.',
    'View properties.': 'Voir les propriétés.',
    "Opponent's Strength": "Force adverse",
    "Media King's Turf": "Territoire du Roi des médias",
    "Gambling King's Turf": "Territoire du Roi du jeu",
    "Leisure King's Turf": "Territoire du Roi des loisirs",
    "Electronics King's Turf": "Territoire du Roi de l'électronique",
    "Pleasure King's Turf": "Territoire du Roi des plaisirs",
    'Weak': 'Faible',
    'Medium': 'Moyen',
    'Strong': 'Fort',
    'Payout Ready': 'Paiement prêt',
    'Collecting Payout': 'Encaissement en cours',
    'Manager Salary': 'Salaire du gérant',
    'Security Salary': 'Salaire du vigile',
    'Total': 'Total',
    'Recover': 'Récupérer',
    '%s obtained.': '%s obtenu.',

    # Cabaret Club Sunshine
    'Target Club Mars Area Customers': 'Cibler la clientèle de la zone Club Mars',
    'Target Club Jupiter Area Customers': 'Cibler la clientèle de la zone Club Jupiter',
    'Target Club Mercury Area Customers': 'Cibler la clientèle de la zone Club Mercury',
    'Target Club Venus Area Customers': 'Cibler la clientèle de la zone Club Venus',
    'Target Club Moon Area Customers': 'Cibler la clientèle de la zone Club Moon',

    # Styles de combat (Descriptions)
    "Kiryu's basic battle style. Unleash dynamic fighting moves effective in any situation.": "Style de combat de base de Kiryu. Déchaînez des mouvements dynamiques efficaces en toute situation.",
    'A battle style focused on speed. Pummel enemies into submission with a flurry of blows and quick evasions.': "Un style axé sur la vitesse. Rouez les ennemis de coups et esquivez rapidement.",
    "Majima's basic battle style. Launch precise attacks that exploit enemy weaknesses in any situation.": "Style de combat de base de Majima. Lancez des attaques précises exploitant les faiblesses adverses.",
    'A battle style focused on speed. Deal massive combo damage with whirling attacks based on breakdancing.': "Un style axé sur la vitesse. Infligez d'importants dégâts tournoyants inspirés du breakdance.",
    'A battle style focused on power. Wield a bat to gain a crushing advantage and an iron defense.': "Un style axé sur la puissance. Maniez une batte pour un avantage écrasant et une défense de fer.",
    'Enable Dragon of Dojima': 'Activer Dragon de Dojima',
    'Disable Dragon of Dojima': 'Désactiver Dragon de Dojima',

    # Menu principal & Niveaux de difficulté
    'Start a new game.': 'Commencer une nouvelle partie.',
    'Load a saved game.': 'Charger une partie sauvegardée.',
    'Explore the game world without following the main story.': 'Explorer le monde sans suivre l\'histoire principale.',
    'View information about online features.': 'Consulter les infos sur les fonctionnalités en ligne.',
    'View previously seen story events.': 'Revoir les cinématiques de l\'histoire déjà vues.',
    'Read before starting the game.': 'À lire avant de commencer le jeu.',
    'New game using game clear data': 'Nouvelle partie avec données de fin de jeu',
    'New game without using game clear data': 'Nouvelle partie sans données de fin de jeu',
    'Start a new game retaining all clear data except certain elements. You cannot play on LEGEND difficulty when carrying over data.': 'Commencer en conservant les données de fin, sauf certains éléments. Mode LÉGENDE impossible avec transfert.',
    'Start a new game from scratch without using game clear data.': 'Commencer une nouvelle partie à zéro sans données de fin de jeu.',
    'This is the standard difficulty level.': 'Niveau de difficulté standard.',
    'Recommended for players who are skilled at action games.': 'Recommandé aux habitués des jeux d\'action.',
    'The highest difficulty setting, with no data carried over and no continues. For true yakuza only!': 'Difficulté maximale, sans transfert ni continus. Réservé aux vrais yakuzas !',
    'Start using game clear data': 'Démarrer avec données de fin de jeu',
    'Start without using game clear data': 'Démarrer sans données de fin de jeu',
    'Retain clear data and explore the game world without following the story.': 'Conserver les données de fin et explorer sans suivre l\'histoire.',
    'Start a new game from scratch and explore the game world without following the story.': 'Commencer à zéro et explorer sans suivre l\'histoire.',

    # Chapitres
    'CHAPTER 2: The Real Estate Broker in the Shadows': 'CHAPITRE 2 : L\'agent immobilier de l\'ombre',
    'CHAPTER 6: The Yakuza Way': 'CHAPITRE 6 : La voie du yakuza',
    '-The End-': '-Fin-',

    # Mini-jeux (Pocket Circuit, Fléchettes, Mahjong)
    'Cost Limit': 'Coût limite',
    'Total Cost': 'Coût total',
    'Parts Cost': 'Coût pièces',
    'Cost: %d': 'Coût : %d',
    'Select Circuit': 'Choisir circuit',
    'Select a circuit.': 'Choisir un circuit.',
    'Buy custom circuit.': 'Acheter circuit personnalisé.',
    'Exit circuit editor?': 'Quitter l\'éditeur de circuit ?',
    'Select a challenge.': 'Choisir un défi.',
    'Select stakes': 'Choisir la mise',
    'Select difficulty.': 'Choisir la difficulté.',
    'Select direction   Camera controls   Shooting mode': 'Direction   Caméra   Mode de tir',
    'Throw 1': 'Tir 1',
    'Throw 2': 'Tir 2',
    'Throw 3': 'Tir 3',
    'Triple Throw': 'Triple tir',
    'Advanced difficulty unlocked.': 'Difficulté Avancé débloquée.',
    'Expert difficulty unlocked.': 'Difficulté Expert débloquée.',
    'Top-Grade Bait': 'Appât de premier choix',
    'Green Dragon': 'Dragon Vert',
    'Red Dragon': 'Dragon Rouge',
    'Sacred Discard': 'Défausse sacrée',
    'Wind Discard Draw': 'Tirage défausse du vent',
    'Climax Battles item opened.': 'Combat Climax débloqué.',
    'Exit Scarecrow Hall?': 'Quitter la Salle de l\'épouvantail ?',
    'Street Goons': 'Racailles de rue',
    'Powerful enemy approaching': 'Un puissant ennemi approche',
    'Dime Store': 'Bazar',
    'Udon Shop': 'Restaurant d\'udon',
    'Chapter Completion Bonus': 'Bonus de fin de chapitre',

    # Boutons avec balises et invites de navigation
    '<Sign:C> Back': '<Sign:C> Retour',
    '<Sign:D> OK  <Sign:C> Back': '<Sign:D> OK  <Sign:C> Retour',
    '<Sign:D> OK    <Sign:C> Back': '<Sign:D> OK    <Sign:C> Retour',
    '<Sign:D> Next': '<Sign:D> Suivant',
    '<Sign:55>Dodge Enemy Attacks<Sign:55>': '<Sign:55>Esquiver les attaques ennemies<Sign:55>',
    '<Sign:30> Select direction\n<Sign:29> Camera controls\n<Sign:0> Shooting mode': '<Sign:30> Choisir direction\n<Sign:29> Contrôles caméra\n<Sign:0> Mode tir',

    # Descriptions des styles de combat
    "Kiryu's basic battle style.\nUnleash dynamic fighting moves\neffective in any situation.":
        "Style de combat de base de Kiryu.\nAttaques dynamiques et efficaces\nen toute situation.",
    'A battle style focused on speed.\nPummel enemies into submission with a\nflurry of blows and quick evasions.':
        'Un style axé sur la vitesse.\nSubmergez les ennemis sous un déluge\nde coups et d\'esquives rapides.',
    'A battle style focused on power.\nWield a bat to gain a crushing\nadvantage and an iron defense.':
        'Un style axé sur la puissance.\nArmé d\'une batte pour un avantage\nécrasant et une défense de fer.',
    "Majima's basic battle style.\nLaunch precise attacks that exploit\nenemy weaknesses in any situation.":
        "Style de combat de base de Majima.\nAttaques précises ciblant les faiblesses\nennemies en toute situation.",
    'A battle style focused on speed. Deal\nmassive combo damage with whirling\nattacks based on breakdancing.':
        'Un style axé sur la vitesse. Infligez\nde lourds combos tourbillonnants inspirés\ndu breakdance.',

    # Menus système et modes de jeu
    'Unsaved data will be lost.\nAre you sure?':
        'Les données non sauvegardées seront perdues.\nConfirmer ?',
    'Explore the game world without\nfollowing the main story.':
        'Explorez librement le monde sans\nsuivre l\'histoire principale.',
    'I can go wherever I want and do whatever\nI wanna do.':
        'Je peux aller où je veux et faire tout\nce dont j\'ai envie.',
    'I can go wherever I want and do whatever\nI want to do.':
        'Je peux aller où je veux et faire tout\nce dont j\'ai envie.',
    'Recommended for players who are skilled at\naction games.':
        'Recommandé pour les joueurs aguerris\naux jeux d\'action.',
    'The highest difficulty setting, with no data carried\nover and no continues. For true yakuza only!':
        'La difficulté ultime, sans transfert de données\nni continuations. Pour les vrais yakuzas !',
    'Retain clear data and explore the game world\nwithout following the story.':
        'Conservez vos données et explorez librement\nle monde sans suivre l\'histoire.',
    'Start a new game from scratch and explore the\ngame world without following the story.':
        'Commencez une nouvelle partie et explorez\nlibrement le monde sans suivre l\'histoire.',
    'Start a new game from scratch without\nusing game clear data.':
        'Commencer une nouvelle partie de zéro sans\nutiliser de données de fin de jeu.',
    'Start a new game retaining all clear\ndata except certain elements.\nYou cannot play on LEGEND difficulty when carrying over data.':
        'Commencer une partie en conservant les données\nvalidées (hors exceptions).\nDifficulté LÉGENDE indisponible avec transfert.',

    # Mini-jeux et tournois
    'Keio Mahjong Cup: Dragon Series': 'Coupe de mahjong Keio : Série Dragon',
    'Mahjong Revolution Cup: Dragon Series': 'Révolution du mahjong : Série Dragon',
    'Total points x rate': 'Total points x taux',
    'Result %d pts.': 'Résultat : %d pts',
    'Select %s?': 'Sélectionner %s ?',

    # Dialogues et interjections courtes
    'Hello.': 'Bonjour.',
    'Hello!': 'Bonjour !',
    'Okay.': "D'accord.",
    'Okay...': "D'accord...",
    'Oh, okay.': "Oh, d'accord.",
    'Oh, okay...': "Oh, d'accord...",
    'Uh, okay.': "Euh, d'accord.",
    'Uh, okay?': "Euh, d'accord ?",
    'Sorry.': 'Désolé.',
    'Sorry, heh.': 'Désolé, hé.',
    'Sorry, pal!': "Désolé, l'ami !",
    "Heh, that's okay.": 'Hé, pas de souci.',
    "Maybe I'll order takeout.": 'Je vais peut-être commander à emporter.',
    'Awright!/Oh, yeah.': 'Super !/Oh oui.',
    'Defeat stings...': 'La défaite est amère...',
    'Heh, sorry guys.': 'Hé, désolé les gars.',
    'Hell yeah!': 'Carrément !',
    'Hello, handsome.': 'Salut, beau gosse.',
    'Oh yeah!': 'Oh oui !',
    'Oh yeah./Sweet.': 'Oh oui./Génial.',
    'Oh, yeah!/Woo-hoo!': 'Oh oui !/Youhou !',
    'Oh, yeah!/Yes!': 'Oh oui !/Oui !',
    'Oh, yeah./Sweet.': 'Oh oui./Génial.',
    'Okay, okay./Phew...': "D'accord, d'accord./Ouf...",
    'Thanks a bunch!': 'Merci infiniment !',
    'Welcome!': 'Bienvenue !',
    'Yeah!': 'Ouais !',
}
