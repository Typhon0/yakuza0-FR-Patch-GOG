# -*- coding: utf-8 -*-
"""
tools/calibrate_stay_tables.py
------------------------------
Calibrated in-place translations for stay.par tables.
Guarantees for every string:
1. len(fr.encode('latin1')) <= len(en.encode('latin1'))
2. Space-padded with b' ' * (len(en) - len(fr)) before the single null terminator
3. Bit-exact file length and bit-exact column null counts (zero row shifts, zero 0x30ED crash)
4. Preservation of uncompressed raw flags (0x0) for cabaret_island_area & battle_result (zero 0x1400EB0CF crash)
"""

# ===========================================================================
# 1. CABARET ISLAND AREA (cabaret_island_area.bin_c - flags=0x0)
# ===========================================================================
CABARET_AREA_CALIBRATED = {
    # name
    "Mars Area": "Zone Mars",
    "Jupiter Area": "Zone Jupiter",
    "Mercury Area": "Zone Mercure",
    "Venus Area": "Zone Venus",
    "Moon Area": "Zone Moon",

    # explanation
    "Uses money to hire high\nquality girls. Has a bad\nreputation for squeezing\nmoney from customers.":
        "Utilise son argent pour recruter\ndes hôtesses d'élite. Réputé pour\nescroquer ses clients.",

    "Club owned by Kizuka, an\nex-con. Involved in many\nother shady businesses\nto generate profits.":
        "Club tenu par Kizuka, ex-taulard.\nLié à des commerces louches\npour générer des profits.",

    "An established club that\nused to be a cabaret,\nbut its reputation has\nsuffered in recent days.":
        "Un établissement réputé, ancien cabaret,\ndont la renommée a récemment\ncommencé à décliner.",

    "The No. 2 club of the\nFive Stars, it tricks\ngirls and takes\nadvantage of them.":
        "Club n°2 des 5 Étoiles.\nManipule les filles et en tire\nprofit sans scrupule.",

    "The top cabaret club in\nSotenbori. Its hostesses\nand service are second\nto none.":
        "Le cabaret club n°1 de Sotenbori.\nSes hôtesses et son service\nsont sans égaux.",

    # battle_name
    "Battle vs. Club Mars": "Duel vs Club Mars",
    "Battle vs. Club Jupiter": "Duel vs Club Jupiter",
    "Battle vs. Club Mercury": "Duel vs Club Mercure",
    "Battle vs. Club Venus": "Duel vs Club Venus",
    "Battle vs. Club Moon": "Duel vs Club Moon",

    # battle_detail
    "Cabaret club battle against Hino from\nClub Mars.":
        "Bataille de cabaret contre Hino\ndu Club Mars.",

    "Cabaret club battle against Kizuka from\nClub Jupiter.":
        "Bataille de cabaret contre Kizuka\ndu Club Jupiter.",

    "Cabaret club battle against Mizumura from\nClub Mercury.":
        "Bataille de cabaret contre Mizumura\ndu Club Mercure.",

    "Cabaret club battle against Kanehara from\nClub Venus.":
        "Bataille de cabaret contre Kanehara\ndu Club Venus.",

    "Cabaret club battle against Tsukiyama from\nClub Moon.":
        "Bataille de cabaret contre Tsukiyama\ndu Club Moon.",
}

# ===========================================================================
# 2. BATTLE RESULT (battle_result.bin_c - flags=0x0)
# ===========================================================================
BATTLE_RESULT_CALIBRATED = {
    # name (col 1)
    "Enemy Down": "Au sol",
    "The Brawler": "Bagarreur",
    "The Rusher": "Le Foncent",
    "The Beast": "La Brute",
    "The Thug": "Le Voyou",
    "The Breaker": "Le Danseur",
    "The Slugger": "Le Batteur",
    "Running Man": "En course",
    "Tormentor": "Bourreau",
    "Finishing Blow": "Coup de grâce",
    "Heat Explosion": "Explosion Heat",
    "Counter Master": "Maître Contre",
    "BOOM!": "BOUM!",
    "My Bad, Sorry": "Oups, pardon",
    "Collateral Damage": "Dégât collatéral",
    "Grappler": "Lutteur",
    "Curb Stomper": "Piétinement",
    "Now You See Me": "Prise à revers",
    "Guard Breaker": "Brise-garde",
    "Lightning Fast": "Fulgurant",
    "Untouchable": "Intouchable",
    "Combo Takedown": "K.-O. combo",
    "Double Takedown": "Double K.-O.",
    "Triple Takedown": "Triple K.-O.",
    "Quadruple Takedown": "Quadruple K.-O.",
    "Mass Takedown": "K.-O. massif",
    "Empty Tank": "À sec",
    "Top Gear": "À fond",
    "Indomitable": "Indomptable",
    "Legend in the Making": "Légende vivante",

    # detail (col 3)
    "Defeat an enemy.":
        "Battez 1 ennemi.",
    "Defeat enemy with a counterattack in Brawler style.":
        "Battez l'ennemi en contre en style Bagarreur.",
    "Defeat enemy after weaving in Rush style.":
        "Battez l'ennemi esquivé, style Foncent.",
    "Defeat enemy with a weapon in Beast style.":
        "Battez l'ennemi armé en style Brute.",
    "Defeat enemy with a counterattack in Thug style.":
        "Battez l'ennemi en contre en style Voyou.",
    "Defeat enemy after a freeze in Breaker style.":
        "Battez l'ennemi après freeze, style Danseur.",
    "Defeat enemy with a charged attack in Slugger style.":
        "Battez l'ennemi d'un coup chargé, style Batteur.",
    "Defeat enemy with a running attack.":
        "Battez l'ennemi en pleine course.",
    "Defeat enemy with an attack unleashed after evading.":
        "Battez l'ennemi avec une attaque après esquive.",
    "Defeat enemy with a Finishing Blow.":
        "Battez l'ennemi d'un coup de grâce.",
    "Defeat enemy with a Heat Action.":
        "Battez l'ennemi d'un coup Heat.",
    "Defeat enemy with a counterattack.":
        "Battez l'ennemi en contre-attaque.",
    "Defeat enemy with an explosion.":
        "Battez l'ennemi via explosion.",
    "Defeat enemy when taking out a weapon.":
        "Battez l'ennemi en sortant une arme.",
    "Defeat enemy by throwing or knocking another into them.":
        "Battez l'ennemi en projetant un autre sur lui.",
    "Defeat enemy with a grabbing attack.":
        "Battez l'ennemi avec une prise.",
    "Defeat enemy while they are lying on the ground.":
        "Battez l'ennemi pendant qu'il est au sol.",
    "Defeat enemy that has lost track of you.":
        "Battez l'ennemi qui vous a perdu de vue.",
    "Defeat enemy immediately after breaking their guard.":
        "Battez l'ennemi juste après avoir brisé sa garde.",
    "Defeat enemy within 5 seconds of first damaging them.":
        "Battez l'ennemi en 5 sec après le 1er coup porté.",
    "Defeat enemy before taking any damage in a battle.":
        "Battez l'ennemi sans subir de dégâts en combat.",
    "Defeat a second enemy within 3 seconds of a first.":
        "Battez un second ennemi en 3 sec après le premier.",
    "Defeat 2 enemies within 1 second.":
        "Battez 2 ennemis en une seconde.",
    "Defeat 3 enemies within 1 second.":
        "Battez 3 ennemis en une seconde.",
    "Defeat 4 enemies within 1 second.":
        "Battez 4 ennemis en une seconde.",
    "Defeat 5 or more enemies within 1 second.":
        "Battez 5 ennemis ou plus en une seconde.",
    "Defeat enemy when your Heat Gauge is empty.":
        "Battez l'ennemi avec la jauge Heat vide.",
    "Defeat enemy when your Heat Gauge is full.":
        "Battez l'ennemi avec la jauge Heat pleine.",
    "Defeat enemy when your health is red and flashing.":
        "Battez l'ennemi avec la santé qui clignote.",
    "Defeat enemy with your remaining health at 1.":
        "Battez l'ennemi alors qu'il vous reste 1 PV.",
}

# ===========================================================================
# 3. CABARET CAST INFO (caba_cast_info.bin_c - flags=0x80000000)
# ===========================================================================
CABA_CAST_CALIBRATED = {
    "The star of this club.\nShe's a diamond in the\nrough who could shine.":
        "L'étoile du club.\nUn diamant brut qui ne\ndemande qu'à briller.",

    "One of Sotenbori's top\ngirls, her customer care\nskills are unparalleled.":
        "L'une des reines de Sotenbori.\nSon art de recevoir est\nsans égal.",

    "Club Moon's ex-No. 1.\nHer skills and unexpected\nvulnerability bewitch men.":
        "Ex-numéro 1 du Club Moon.\nSon charme et sa fragilité\nenvoûtent les hommes.",

    "Cheerful and energetic,\nher earnestness captures\nthe hearts of men.":
        "Joyeuse et dynamique,\nsa sincérité touche le\ncoeur des hommes.",

    "A girl with maturity,\nher skills make older\nmen swoon.":
        "Hôtesse mûre dont le\nsavoir-faire charme les aînés.",

    "A tough girl with a\ngreat work ethic, she\nhas a bright personality.":
        "Une fille dévouée et travailleuse,\nà la personnalité radieuse.",

    "Sotenbori's disco queen.\nHer partying abilities\nare second to none.":
        "La reine disco de Sotenbori.\nSon sens de la fête est\nsans pareil.",

    "A mature lady from Osaka,\nshe loves to gossip and\nwill talk up a storm!":
        "Une dame mûre d'Osaka,\nelle adore les potins et\nparle sans s'arrêter !",

    "Doll Girl's mother. Many\nmen are struck by her\ndevotion to her daughter.":
        "La mère de Doll Girl.\nLes hommes sont touchés par\nson amour maternel.",

    "Introduced by Simon the\nMystery Man, she's\nshrouded in mystery.":
        "Présentée par Simon l'inconnu,\nelle reste un vrai mystère.",

    "A girl with lots of\npotential, she is great\nat romantic talk.":
        "Une fille à fort potentiel,\ntrès douée pour le romantisme.",

    "Straight as an arrow, she\nworked at a bank and is\nwell-liked by older men.":
        "Droite et sérieuse, ex-banquière\net très appréciée des hommes\nd'âge mûr.",

    "A short-haired girl with\na sunny personality, she\nlikes strange talk.":
        "Une fille aux cheveux courts et\nsouriante, fan de sujets insolites.",

    "Rumors say this cool\nbeauty used to date a\nmember of a biker gang.":
        "On dit que cette beauté froide\nsortait avec un chef de gang.",

    "Erran-kun is smitten by her.\nHer skills need work, but\nshe might shine bright.":
        "Erran-kun est sous son charme.\nEncore novice, mais elle\npourrait rayonner.",

    "She worked at a club shut\ndown by the Five Stars.\nShe's delicate, but eager.":
        "Officiait dans un club fermé\npar les Cinq Étoiles.\nFragile mais motivée.",

    "Formerly of Club Moon.\nShe wants to take down\nTsukiyama, who fired her.":
        "Ancienne du Club Moon.\nElle veut faire tomber Tsukiyama,\nson ex-patron.",

    "An aspiring news reporter,\nshe works here because of\nher poor speaking skills.":
        "Aspirante journaliste, elle est\nici pour améliorer son aisance\nà l'oral.",

    "The number of men she's\nslept with is in triple\ndigits!? She's a maneater.":
        "Ses conquêtes se comptent à trois\nchiffres !? Vraie croqueuse\nd'hommes.",

    "She loves to talk and\ncan't stop talking, but\nshe lacks stamina.":
        "Très bavarde, elle ne s'arrête\njamais mais manque d'endurance.",

    "A girl with a laid-back\npersonality, she went to\nthe same school as Yuki.":
        "Une jeune fille décontractée,\nqui était dans la même école\nque Yuki.",

    "A college student in a\nscience field, her smarts\nare her charm point.":
        "Étudiante en sciences,\nson intelligence fait tout\nson charme.",

    "A veteran with refined\nskills who used to work at\na high-end club.":
        "Vétérane au savoir-faire\néprouvé ayant exercé dans un\ngrand club.",

    "She works here because she\nloves to drink. She's good\nat livening things up.":
        "Elle travaille ici pour boire.\nElle sait toujours mettre de\nl'ambiance.",

    "The way she talks is sexy.\nLoves to go to the clubs\nand loves to party.":
        "Une voix très sensuelle.\nAdore sortir en boîte et faire\nla fête.",

    "She says not being unique\nis her unique trait. Her\nfavorite word is \"safe.\"":
        "Elle affirme que sa banalité est sa\nforce. Son mot favori est\n\"prudence\".",

    "A mysterious girl who\ndemands to go by Marilyn.\nHer real name is Mariko.":
        "Fille mystérieuse voulant qu'on\nl'appelle Marilyn. Nom réel :\nMariko.",

    "She's looking for her\npurpose in life. Perhaps\nshe can find it here!":
        "Elle cherche sa voie dans la vie.\nPeut-être la trouvera-t-elle\nici !",

    "A student from Korea, her\nfluent Japanese is one of\nher charms.":
        "Étudiante de Corée,\nson japonais parfait fait tout\nson charme.",

    "Her husband cheated on\nher, so she chose this job\nout of despair.":
        "Son mari l'ayant trompée, elle a\nchoisi ce travail par désespoir.",
}

# ===========================================================================
# 4. MONEY ISLAND TARENT (money_island_tarent.bin_c - flags=0x80000000)
# ===========================================================================
MONEY_ISLAND_TARENT_CALIBRATED = {
    # post
    "Manager": "Gérant",
    "Guard": "Garde",
    "Advisor": "Conseil",

    # comment
    "I'm just an average guy, but I'll do my best!":
        "Gars ordinaire, mais je ferai de mon mieux !",

    "I'm all about keeping things the same as they\nalways are. Leave it to me.":
        "Mon crédo : maintenir la stabilité habituelle.\nFais-moi confiance.",

    "I know Kamurocho's underbelly inside out.\nIt'll be easy for me to keep business humming.":
        "Je connais les bas-fonds de Kamurocho par coeur.\nLes affaires vont tourner rond.",

    "Cluck cluck cluuuck!":
        "Cot cot cooot !",

    "I'll make good use of the management skills\nI learned from my burusera business.":
        "Je mettrai à profit mes compétences acquises\ndans mon commerce de burusera.",

    "I'll show you the good luck that got me my fortune\nin pachinko. Life's full of ups and downs.":
        "Je vais te montrer ma chance insolente du pachinko.\nLa vie a des hauts et des bas.",

    "I'm not a people person. But with my intellect,\nthis job's a cinch.":
        "Pas très sociable. Mais avec mon esprit,\nce job est facile.",

    "Management is like gambling. Don't overthink\nthings and let me handle everything!":
        "Gérer, c'est comme le jeu. Ne cogite pas trop\net laisse-moi tout piloter !",

    "Managing businesses is easy compared to the\nTV industry. Let's do this! Cha-ching!":
        "Gérer des affaires est facile comparé à la télé.\nC'est parti ! Jackpot !",

    "If you leave it to me, I promise to deliver\nnever-before-seen results.":
        "Si tu me fais confiance, je promets d'obtenir\ndes résultats inédits.",

    "These aren't muscles. I just have a big chest.":
        "Ce ne sont pas des muscles. Juste du coffre.",

    "I got mugged last time I was in Mongolia.\nI'm good at arguing.":
        "Agressé lors de mon séjour en Mongolie.\nJe suis bon débatteur.",

    "I'm going to get stronger and get that girl to\nnotice me!":
        "Je serai plus fort pour que cette fille me remarque !",

    "Kiryu-san says new employees should get a feel for\nthe streets, so I'm starting as security staff!":
        "Kiryu-san dit que les recrues doivent arpenter la rue,\nje débute en sécurité !",

    "Thanks for bringing me on along with the Leisure\nKing. I'll take point on security.":
        "Merci de m'engager avec le Roi des Loisirs.\nJe serai en pointe sur la sécurité.",

    "The Electronics King and you are about the only\nones who can beat me. I got this.":
        "Le Roi de l'Élec et toi êtes les seuls à pouvoir me battre. Je gère.",

    "I have experience dealing with problematic\ncustomers, so I'm sure I can help you out.":
        "Habitué aux clients pénibles, je saurai\nparfaitement vous épauler.",

    "This will give me the practice I need to do things\nother than stop-and-searches.":
        "Cela m'entraînera à faire autre chose que\ndes fouilles corporelles.",

    "Hehehe. Don't worry, I do good work to earn\nmy pay.":
        "Héhéhé. T'inquiète pas, je bosse dur pour\nma paye.",

    "I'll show you the depths of the mafia's power.\nDeath to those who get in our way.":
        "Je vous montrerai la puissance de la mafia.\nMort à quiconque nous barre la route.",

    "I work in the cosmetics corner at a department\nstore. I wonder if my input will be useful...":
        "Je vends des cosmétiques en grand magasin.\nJ'espère que mon avis sera utile...",

    "I help create unique interior designs.\nMy focus is on artistic and modern designs.":
        "Je crée des décors intérieurs uniques.\nMon crédo : le moderne et l'artistique.",

    "I hope to provide useful advice from a masochist's\npoint of view.":
        "J'espère donner de bons avis du point\nde vue d'un masochiste.",

    "My band is crazy popular in its niche for some\nreason, so that might help me help you.":
        "Mon groupe cartonne dans sa niche, ça pourra\nsûrement vous être profitable.",

    "I get all the gossip at Earth Angel! I'll put it\nall to good use for you, Kiryu-chanâ\x9d¤":
        "J'ai tous les ragots à l'Earth Angel ! Tout pour toi, Kiryu-chan !",

    "I owe you, Kiryu-san, so I'll do anything I can\nto help. Within the bounds of the law, of course.":
        "J'ai une dette envers vous, Kiryu-san. J'aiderai dans le respect des lois.",

    "You can depend on me for insights on adult\nestablishments. I'm the Pleasure King, after all.":
        "Comptez sur moi pour les clubs adultes.\nJe suis le Roi des Plaisirs, après tout.",

    "Yeah! Let's party tonight!":
        "Ouais ! Fêtons ça ce soir!",

    "I can see the future... My advice is never wrong,\nthough it is expensive.":
        "Je vois l'avenir... Mes avis sont infaillibles,\nmais ils sont chers.",

    "Take my strong advice! Woo!":
        "Suis mon conseil ! Wouhou !",
}

# ===========================================================================
# 5. ULTIMATE BATTLES (ultimate.bin_c - flags=0x80000000)
# ===========================================================================
ULTIMATE_CALIBRATED = {
    # NAME
    "Proving Grounds 1": "Épreuve 1",
    "Proving Grounds 2": "Épreuve 2",
    "Proving Grounds 3": "Épreuve 3",
    "Proving Grounds 4": "Épreuve 4",
    "Proving Grounds 5": "Épreuve 5",
    "Proving Grounds 6": "Épreuve 6",
    "Proving Grounds 7": "Épreuve 7",
    "Proving Grounds 8": "Épreuve 8",
    "Proving Grounds 9": "Épreuve 9",
    "Proving Grounds 10": "Épreuve 10",
    "Melee Battle 1": "Mêlée 1",
    "Melee Battle 2": "Mêlée 2",
    "Melee Battle 3": "Mêlée 3",
    "Melee Battle 4": "Mêlée 4",
    "Melee Battle 5": "Mêlée 5",
    "Melee Battle 6": "Mêlée 6",
    "Melee Battle 7": "Mêlée 7",
    "Melee Battle 8": "Mêlée 8",
    "Melee Battle 9": "Mêlée 9",
    "Melee Battle 10": "Mêlée 10",
    "Millionaire Battle 1": "Duel de Millions 1",
    "Millionaire Battle 2": "Duel de Millions 2",
    "Millionaire Battle 3": "Duel de Millions 3",
    "Millionaire Battle 4": "Duel de Millions 4",
    "Millionaire Battle 5": "Duel de Millions 5",
    "Millionaire Battle 6": "Duel de Millions 6",
    "Ultimate Battle 1": "Combat Ultime 1",
    "Ultimate Battle 2": "Combat Ultime 2",
    "Ultimate Battle 3": "Combat Ultime 3",
    "Ultimate Battle 4": "Combat Ultime 4",
    "Ultimate Battle 5": "Combat Ultime 5",
    "Ultimate Battle 6": "Combat Ultime 6",

    # EXPLANATION
    "Use weapons to beat enemies. Bare-handed attacks don't count.":
        "Utilisez des armes. Mains nues interdites pour ce défi.",

    "Withstand the enemy assault and defeat all foes.":
        "Résistez aux assauts et battez tous les ennemis.",

    "Survive as long as you can without dealing or sustaining damage.":
        "Survivez le plus longtemps sans frapper ni subir de dégâts.",

    "Overcome all armed attackers.":
        "Battez les assaillants armés.",

    "Overcome all these attackers!":
        "Battez tous les assaillants !",

    "Get \\30,000,000 within the time limit.":
        "Obtenez 30 000 000 ¥ dans le temps.",

    "Beat all enemies while fighting in an altered state.":
        "Battez tous les ennemis dans un état altéré.",

    "Defeat all foes using Dragon of Dojima style without taking damage.":
        "Battez tout ennemi en Dragon de Dojima sans subir de dégâts.",

    "Beat all enemies using Mad Dog of Shimano style without taking damage.":
        "Battez tout ennemi en Chien Enragé de Shimano sans dégâts.",

    "Defeat your foes within the time limit.":
        "Battez vos ennemis dans le temps.",

    "Beat all enemies within the time limit.":
        "Battez les ennemis dans le temps.",

    "Defeat your foe to get money.":
        "Battez l'ennemi pour du cash.",

    "Beat your enemy to get money.":
        "Battez l'ennemi pour du cash.",

    "Get \\10,000,000 within the time limit.":
        "Obtenez 10 000 000 ¥ dans le temps.",

    "Get \\30,000,000 without losing any money.":
        "Obtenez 30 000 000 ¥ sans en perdre.",

    "Defeat your foes to get money.":
        "Battez-les pour avoir du cash.",

    "Beat the enemies to get money.":
        "Battez l'ennemi pour du magot.",

    "Beat three brutal enemies. You recover 10% of your HP between battles.":
        "Battez 3 brutes. Vous récupérez 10 % de santé entre chaque duel.",

    "Vanquish five adversaries. You recover 10% of your HP between battles.":
        "Battez 5 ennemis. Vous récupérez 10 % de santé entre chaque duel.",

    "Defeat ten fearsome foes. You recover 10% of your HP between battles.":
        "Battez 10 ennemis. Vous récupérez 10 % de santé entre chaque duel.",

    # LEVEL_DISP & LEVEL
    "Weak Kiryu": "Kiryu doux",
    "Weak Majima": "Majima doux",
    "Strong Kiryu": "Kiryu fort",
    "Strong Majima": "Majima fort",
    "Weakest": "Faible",
    "Strongest": "Robuste",
}

# ===========================================================================
# 6. SEARCH ARMS RESULT PICTURE (search_arms_result_picture.bin_c - 0x80000000)
# ===========================================================================
SEARCH_ARMS_PICTURE_CALIBRATED = {
    "Sudden setback!\nInterference from the locals.":
        "Revers soudain !\nInterférence des locaux.",

    "Hair-raising encounter!\nAttacked by a wild beast.":
        "Péril sauvage !\nAttaque d'une bête féroce.",

    "Unforeseen difficulties!\nNegotiation partners get too inquisitive.":
        "Imprévu de taille !\nPartenaires de négociation trop curieux.",

    "Caught in the crossfire!\nSupplier's foes launch a surprise attack.":
        "Pris entre deux feux !\nAttaque surprise des ennemis du contact.",

    "Things get awkward!\nNegotiation partner's mom steps in.":
        "Malaise imprévu !\nLa mère du partenaire s'interpose.",

    "Language barrier!\nNo choice but to rely on signs and gestures.":
        "Barrière de la langue !\nContraint de communiquer par gestes.",

    "Tight spot!\nSurrounded by men who look like bad news.":
        "Mauvaise passe !\nCerné par des types patibulaires.",

    "In luck we trust!\nNegotiations come down to a coin toss.":
        "Coup de chance !\nNégociations jouées à pile ou face.",

    "Twins or clones!?\nNegotiation partner's doppelganger appears.":
        "Jumeaux ou clones !?\nLe sosie du partenaire apparaît.",

    "Dangerous temptations!\nApproached by a third party with a side deal.":
        "Tentation risquée !\nUn tiers propose un marché parallèle.",

    "Good reception!\nGreeted in a very promising way.":
        "Accueil chaleureux !\nReçu de façon prometteuse.",

    "It's too spicy!\nTreated to a hellishly hot meal.":
        "C'est trop épicé !\nRepas diaboliquement pimenté.",

    "Can't read maps!\nMission successful, but got lost on the way home.":
        "Perdu en route !\nMission réussie, mais égaré au retour.",

    "Crazy unbelievable success!\nMission went swimmingly and treasure was found!":
        "Succès incroyable !\nMission parfaite et trésor découvert !",

    "Resounding success!\nMission went even better than hoped.":
        "Succès total !\nMission au-delà de toute espérance.",

    "Yarr, thar be treasure!\nMiraculously stumbled upon treasure.":
        "Trésor en vue !\nTrésor déniché par pur miracle.",

    "Success!\nMission went reasonably well.":
        "Succès !\nMission menée à bien.",
}

# ===========================================================================
# 7. SEARCH ARMS AGENT (search_arms_agent.bin_c - flags=0x80000000)
# ===========================================================================
SEARCH_ARMS_AGENT_CALIBRATED = {
    'A Eastern European weapon smuggler.\nUsed to deal in antique weapons and\narmors, but the business was too\nslow. Carries around a great number\nof items, passing himself as a\ntraveling antique salesman.':
        "Contrebandier d'Europe de l'Est. Écoulait jadis des antiquités\navant de passer aux armes lourdes. Utilise une vieille malle.",
    'A Middle Eastern prince, 50th in\nline to the throne. In order to\nactually live like a prince, he had\nto take up some sort of work and\ndecided to be an arms agent. Travels\nwith a king-sized suitcase.':
        "Prince du Moyen-Orient, 50e dans l'ordre de succession. Pour financer\nson train de vie, revend des armes rares. Malle princière.",
    'A South American shaman guided in\nher weapon searches by the spirits.\nOpinions are divided on how\neffective that is. Physically frail,\nshe can only carry a small bag.':
        'Chamane sud-américaine guidée dans ses recherches par\nles esprits ancestraux. Trouve des matériaux mystiques.\nVoyage avec un sac artisanal tissé.',
    "A beautiful dancer in an attention-\ngrabbing costume. Having grown up in\nthe slums, she has many friends in\nthe South American criminal\nunderworld. Her travel bag is much\nlarger than you'd expect.":
        'Danseuse magnifique au costume étincelant. Son charme\nsensoriel désarme les vendeurs les plus coriaces.\nVoyage avec une malle de spectacle colorée.',
    "A big shot in the Latin American\nunderworld. Though he normally pulls\nstrings from the shadows, as an\nexception he'll work for you\ndirectly. Likes sushi. An underling\ncarries a large travel bag for him.":
        "Un ponte de la pègre latino-américaine. Bien qu'il vende\ncher, ses filières sont d'une fiabilité absolue.\nVoyage avec une valise blindée.",
    'A cunning spy who puts her charisma\nto a good use. Her travel bag is\na standard size.':
        'Espionne rusée mettant son charisme à\nprofit. Sa valise est de taille\nstandard.',
    "A famous adventurer who knows any\ncountry in the world like the back\nof his hand. With great negotiation\nskills, travel expertise, and an\nenormous suitcase, he's the guy to\nsend out when you need equipment.":
        "Aventurier réputé connaissant le monde comme sa\npoche. S'enfonce dans les recoins les plus hostiles.\nÉquipé d'un sac à dos d'exploration.",
    "A globetrotting street performer.\nDoesn't know much about weaponry,\nbut has a good eye for finding\nparts. Carries a spacious travel\nbag.":
        "Un artiste de rue globe-trotteur. S'y connaît\npeu en armes, mais a l'oeil pour trouver des\npièces rares. Porte un grand sac de voyage.",
    "A greatly feared pirate operating in\nthe waters off Africa's eastern\ncoastline. Plunders only top-quality\ngoods shipments. Has access to many\nexcellent smuggling routes.":
        "Capitaine pirate redouté des côtes somaliennes. Arraisonne les cargos d'armes\npour revendre leur cargaison. Coffre marin cerclé de fer.",
    'A high-ranking official who deals in\nweapons and gear to fund his\npolitical activities. He has a lot\nof pull in important places and can\nget you top-grade stuff. Carries a\nlarge, expensive-looking suitcase.':
        'Haut fonctionnaire corrompu revendant des prototypes militaires secrets\npour garnir ses comptes suisses. Attaché-case officiel.',
    "A homeless man based in the\nSotenbori area. He and his buddies\nhave their own intelligence-\ngathering network. His bag isn't\nparticularly large, though.":
        "Un sans-abri basé à Sotenbori. Ses compères et lui\nparcourent le Japon à la recherche d'équipements.\nUtilise un grand sac à dos usé.",
    'A mercenary who makes a living in\nvarious internal conflict zones in\nAfrica. Given his day job, he is\nadept at sourcing weapons and gear.\nHis bag is quite large.':
        "Mercenaire vétéran monnayant ses talents dans les guerres civiles africaines.\nRécupère les meilleures armes de guerre. Sac militaire d'assaut.",
    'A pilot who flies international\nroutes. Deals in weapons on the side\nto earn foreign currency and help\nhis poverty-stricken homeland. Has\nlots of space in his suitcase.':
        'Pilote sur les lignes internationales. Transporte des\narmes entre les continents en évitant les contrôles.\nUtilise sa valise de pilote de ligne.',
    'A political thinker and ideologue\nworking as an agent to fund his\nactivities, he is surprisingly\neffective at finding good weapons\nand gear. Has a large suitcase.':
        "Penseur politique et idéologue finançant son mouvement par le trafic\nd'équipements de combat. Voyage avec un sac en toile sobre.",
    'A professional swindler who makes\nfull use of her personal charm in\nnegotiations. Her travel bag is a\nregular size, but she hates to carry\nheavy weapons and prefers to focus\non parts instead.':
        'Une arnaqueuse professionnelle qui use de tout\nson charme pour dégoter des armes rares. Voyage\navec une petite valise chic.',
    "A quiz show presenter who travels\nall over Japan and abroad. Can\neasily transport various goods by\npassing them as quiz show prizes.\nDoesn't have too much spare space in\nhis suitcase.":
        "Présentateur de jeu télévisé parcourant le Japon\net l'étranger. Se sert de ses tournages pour dégoter\ndes armes. Porte une valise de luxe.",
    'A retired marine who finds civilian\nlife just too boring. He started\nworking as an agent, making use of\nold connections in the military and\ntransport routes open only to those\nin the know.':
        "Un marine à la retraite trouvant la vie civile bien\ntrop fade. Cherche l'adrénaline en quête d'armes.\nUtilise son ancien paquetage militaire.",
    'A smooth-talking swindler who gets\nthe best from any deal. Can be very\nuseful, but may not be entirely\ntrustworthy. Likes to travel light,\nwith a small and compact suitcase.':
        'Un escroc à la langue bien pendue qui tire le\nmeilleur de chaque affaire. Transporte ses trouvailles\ndans un sac en cuir.',
    "A soldier who has seen many a\nbattlefield across the world. It's\nnot clear whether his unique combat\nmethods have much practical value.\nCarries a sizeable travel suitcase.":
        'Un soldat aguerri qui a écumé les champs de bataille\ndu monde entier. Déniche le matériel le plus létal.\nVoyage avec un paquetage de survie.',
    "A weapon craftsman who's much\nhappier in his workshop, but is\nsometimes forced by his wife to take\non assignments as a weapons agent.\nUses a large travel bag.":
        "Artisan d'armes bien plus heureux dans son\natelier, mais parfois forcé par sa femme de faire\ndes missions d'agent. Voyage avec un grand sac.",
    "A world-class spy who supplements\nhis income procuring weapons for\nanyone who's willing to pay. He\nwon't let you down. The only\ndrawback is that his travel bag\nisn't that big.":
        'Un espion de classe mondiale qui arrondit ses fins\nde mois en fournissant des armes. Voyage léger avec\nun sac de créateur discret.',
    'A wrestler with a huge following in\nthe US. Works as an agent to save up\nfor medical treatment for a\nseriously ill friend who helped him\nout in the past. His travel suitcase\ncan hold a lot of items.':
        'Catcheur adulé aux États-Unis. Travaille comme agent\npour se payer des extras. Sa carrure intimide les vendeurs.\nUtilise un sac polochon géant.',
    "A youth from a jungle-dwelling\ntribe. Deals in weapons and parts to\nearn some cash. Doesn't own a\nsuitcase, so he can only bring as\nmuch as he can carry in his hands.":
        "Jeune chasseur d'une tribu de la jungle. Excelle à dénicher des matériaux\net poisons rares dans la canopée. Carquois et besace en peau.",
    'Adventure':
        'Aventure',
    'Adventurer':
        'Aventurier',
    'Africa':
        'Africa',
    'An Asian crime syndicate. The\norganization has a wide reach and\ncan easily source weapons and gear,\nbut some members are less reliable\nand may keep goods for themselves.':
        "Syndicat du crime asiatique tentaculaire. Leurs filières d'approvisionnement\nsont quasi illimitées. Transport par container scellé.",
    "An anti-government activist who has\ntraveled far and wide, making\ncountless connections across many\ncountries. Carries a large suitcase,\nbut there's no telling what's\nalready inside.":
        "Militant anti-gouvernemental ayant beaucoup voyagé.\nSes réseaux clandestins lui permettent d'obtenir des\narmes. Voyage avec un sac militaire kaki.",
    "An earnest, honest man who sweats\naway in forests when he's not busy\nsearching for weapons. Doesn't\nrealize that the arms trade is\nillegal. His travel bag is\nsurprisingly small.":
        'Un homme honnête et travailleur qui bûche dur dans\nles forêts. Sa force colossale lui permet de ramener\ndes pièces lourdes dans sa hotte en bois.',
    'An enthusiastic young backpacker who\nwill work for cheap, but arms are\nnot his strong suit. He has an\noversized backpack, but most of the\nspace is already taken by his\npersonal stuff.':
        'Un jeune routard enthousiaste qui travaille pour\npas cher, mais dont les compétences sont limitées.\nVoyage avec un sac à dos de randonnée.',
    'An oil trader who makes even more\nmoney by smuggling weapons as he\ntravels the world on business. His\nemployees carry a large suitcase for\nhim.':
        'Négociant en pétrole brassant des millions en trafiquant des armes\navec les magnats locaux. Voyage avec une mallette dorée.',
    'Athlete':
        'Athlète',
    'Backpacker':
        'Routard',
    "Based in North America, he procures\nweapons and parts on the side to\nearn extra money. His bag is already\nalmost full with his athletic gear,\nso he can't bring you much.":
        'Basé en Amérique du Nord, il négocie des armes en\nparallèle de ses tournois. Robuste et endurant.\nVoyage avec un grand sac de sport.',
    'Bassist from a hot new American rock\nband. Wants to live fast and die\nyoung, and working as a weapons\nagent will surely help him achieve\nthat. Can carry loads of weapons and\ngear in his huge guitar case.':
        "Bassiste d'un nouveau groupe de rock américain en vogue.\nVit à cent à l'heure et aime les armes extravagantes.\nTransporte son butin dans son étui de basse.",
    "Can obtain the best weapons out\nthere, but for a hefty price. It's\nstill a good deal when you think\nabout it. A veteran in the business,\nhe has access to varied smuggling\nroutes.":
        "Peut fournir les armes les plus dévastatrices du marché, mais à un prix\nexorbitant. Sa réputation n'est plus à faire. Valise en titane.",
    'Chinese Chef':
        'Chef chinois',
    'Claims to be a devil with a\nfiendishly good eye for weapons. She\nmight be a little crazy, but is an\nexcellent agent. Carries a large bag\nwith a somewhat disturbing design.':
        "Affirme être un démon doté d'un flair diabolique pour les armes.\nNégocie sans scrupule pour rafler les meilleurs contrats.\nVoyage avec une sacoche sombre en cuir.",
    'Claims to be an angel blessed with\nthe ability to source all types of\nweaponry and gear. While odd, she\ncan certainly deliver. Carries a\nlarge and fancy travel suitcase.':
        'Prétend être un ange béni capable de localiser toutes les\narmes terrestres. Ses méthodes restent mystérieuses mais efficaces.\nVoyage avec un sac blanc immaculé.',
    'Con Artist':
        'Escroc',
    'Decided he no longer wanted to be a\nterrorist, but ran into money\nproblems and became a weapons agent\ninstead. He has access to good\nsmuggling routes.':
        'Terroriste repenti ayant fui son groupe, qui met ses connaissances des\narmes au service du plus offrant. Sac à dos de combat.',
    "Even though he left the yakuza, he\ncouldn't shake off old habits and\noffers his services as a weapons\nagent on the side. Has a large bag.":
        "Retiré des yakuzas, il n'a pu oublier\nleurs méthodes et négocie des armes\nà l'occasion. Utilise une sacoche noire.",
    'Ex-Investigator':
        'Ex-enquêteur',
    'Ex-Mafia':
        'Ex-mafia',
    'Ex-Marine':
        'Ex-marine',
    'Ex-Police Officer':
        'Ex-policier',
    'Ex-Special Agent':
        'Ex-agent spécial',
    'Ex-Yakuza':
        'Ex-yakuza',
    'Fei Hu':
        'Fei Hu',
    'Government Official':
        'Haut fonctionnaire',
    "Grew up in a remote mountain\nvillage. Knows next to nothing about\nthe world and doesn't even realize\nhow dangerous the goods he's\nsmuggling are. His travel bag is\nsmall.":
        "A grandi dans un village montagnard isolé. Ignore tout du monde moderne,\nmais ressent l'énergie des armes forgées. Baluchon en toile.",
    "Had to leave the force after his\nshady dealings were exposed. Uses\nhis old connections to procure\nweapons and gear. His suitcase isn't\nparticularly large.":
        'A dû quitter la police après la découverte de ses\ntrafics. A gardé ses contacts dans la pègre.\nUtilise un attaché-case discret.',
    'He retired from the mafia, but could\nnever quite get used to the life of\nan ordinary, law-abiding citizen.\nHe now makes his living as an arms\nagent. Travels with a standard size\nbusiness suitcase.':
        "Retiré de la mafia, il n'a jamais pu s'habituer\nà la vie de citoyen ordinaire. Il gagne sa vie\ncomme agent. Voyage avec une valise d'affaires.",
    'Homeless Man':
        'Sans-abri',
    'Information Dealer':
        'Informateur',
    'International Spy':
        'Espion du monde',
    'Japan':
        'Japon',
    'Japanese Mercenary':
        'Mercenaire nippon',
    'Long-Haul Fisherman':
        'Pêcheur hauturier',
    'Made many friends in various\ncriminal organizations during his\nworld tours, making it easy for him\nto obtain info about weapons. Never\ngoes anywhere without his favorite\nlarge travel bag.':
        "S'est fait de nombreux contacts parmi les mafias lors de\nses tournées internationales. Cache des armes dans ses partitions.\nVoyage avec une malle d'instruments.",
    'Martial Artist':
        'Karatéka',
    'Mercenary':
        'Soldat',
    'Merchant of Death':
        'Marchand de mort',
    'Negotiator':
        'Médiateur',
    'Oil Trader':
        'Pétrolier',
    'Once a top agent working to keep his\nnation secure, he retired after\ngetting caught up in political\nupheaval. Can easily locate and\ntransport large amounts of goods.':
        'Jadis agent secret de premier ordre, retiré du service.\nA conservé ses accès aux arsenaux gouvernementaux.\nVoyage avec une valise diplomatique sécurisée.',
    'Orchestra Conductor':
        "Chef d'orchestre",
    'Owner of the Dragon & Tiger.':
        'Patron du Dragon & Tigre.',
    'Pilot':
        'As',
    'Pirate Captain':
        'Capitaine',
    'Plays an electronic keyboard and\nwrites songs for his band. Loves\nmusic, instruments and all sorts of\ncontraptions, including the deadly\nillegal ones. Has a huge suitcase,\nsupposedly for musical instruments.':
        'Claviériste et compositeur électro. Déniche des gadgets et\narmes high-tech au fil de ses concerts nocturnes.\nVoyage avec une housse de synthétiseur.',
    'Political Activist':
        'Militant politique',
    'Political Theorist':
        'Théoricien',
    "Popular TV show host from North\nAmerica, frequently traveling on\nbusiness all over the country. What\nhis millions of fans aren't aware of\nis that he's a weapons fanatic. Uses\na large travel suitcase.":
        'Animateur populaire en Amérique du Nord, toujours en\ndéplacement. Profite de ses pauses pour chiner.\nVoyage avec un bagage cabine élégant.',
    'Prince':
        'Prince',
    'Professional Wrestler':
        'Catcheur pro',
    'Reformed Terrorist':
        'Terroriste repenti',
    'Retired Army Officer':
        'Officier en retraite',
    'Retired when national politics took\na turn in a direction he very much\ndid not agree with. A Japanophile\nwith a stunning collection of prized\nkatana and a large suitcase.':
        "Officier retiré après un coup d'État manqué. Connaît les surplus\nmilitaires comme sa poche. Voyage avec une cantine d'officier.",
    'Rock Musician':
        'Rockeur',
    'Samba Dancer':
        'Danseuse',
    'Secret Syndicate':
        'Syndicat secret',
    'Self-Proclaimed Angel':
        'Ange autoproclamé',
    'Self-Proclaimed Devil':
        'Démon autoproclamé',
    'Sexy Swindler':
        'Séductrice',
    'Shaman':
        'Chaman',
    'Smuggler':
        'Passeur',
    'Smuggles weapons and gear in a huge\ncello case. Apparently the cello is\nnot just for show--he can play it\nvery well, too.':
        "Passe des armes dans un étui de\nvioloncelle. Sa couverture est idéale\net n'éveille aucun soupçon.",
    'Spy':
        'As',
    'Store Owner':
        'Boutiquier',
    'Swindler':
        'Escroc',
    'TV Host':
        'Hôte TV',
    'TV Personality':
        'Célébrité télé',
    'Techno Musician':
        'Musicien techno',
    'This guy has got a way with words.\nHe can persuade almost anyone to\ngive him what he wants, and brings\nback lots of good items in his large\nsuitcase.':
        "Ce type a un vrai don pour les mots. Il peut\npersuader presque n'importe qui de négocier.\nVoyage avec une mallette diplomatique.",
    'Traveling Cellist':
        'Violoncelliste',
    'Traveling Entertainer':
        'Artiste nomade',
    'Tribesman':
        'Indigène',
    'Used to be a top investigator\nworking high-profile cases, but had\nto quit due to a character flaw--the\ninability to refuse when asked for\nhelp, even if it involved breaking\nthe law. Has a large suitcase.':
        "Ancien enquêteur d'élite ayant traité de gros dossiers.\nSait où creuser pour trouver des armes sous scellés.\nVoyage avec un porte-documents en cuir.",
    "Used to be a triad member and even\nnow engages in shady dealings on the\nside. His travel bag isn't very big.":
        'Ex-membre des triades ayant gardé de\nbons contacts louches. Déniche de super\nobjets, mais petit sac.',
    'Used to be a weapons fanatic, but\nattained complete mastery of all\ntypes of weapons and is now an\naccomplished and deadly fighter.\nTravels with a large suitcase.':
        "Autrefois simple passionné, devenu un maître d'armes\naccompli capable d'obtenir des pièces de légende.\nVoyage avec une caisse de transport renforcée.",
    'Weapon Master':
        "Maître d'arme",
    'Weapons Dealer':
        'Armurier',
    'Weapons Fanatic':
        "Fana d'armes",
    'With an excellent network of\ninformants, he knows where to find\nanything, from weapons to parts.\nHis big travel suitcase can fit a\nlot of interesting items.':
        "Grâce à son vaste réseau d'informateurs, il sait\noù dénicher les pièces rares. Utilise une valise\nd'affaires de taille moyenne.",
    'Woodcutter':
        'Bûcheron',
    'Works on ships frequently going in\nand out of the country. Can easily\ntransport large quantities of parts,\nbut concealing weapons on the ship\nwould be a little difficult.':
        "Travaille sur des navires sillonnant les mers du\nglobe. Peut ramener des armes des ports d'escale.\nUtilise un grand sac marin robuste.",
    'Wrestler':
        'Catcheur',
    'Young, but extremely knowledgeable\nabout weapons and gear. He creates\nhis own designs as well, some of\nwhich have found their way to the\nblack market. Rumored to have a twin\nbrother. Carries a very large bag.':
        'Jeune, mais incollable sur les armes et armures.\nMet sa passion à profit pour dénicher du matériel.\nVoyage avec un sac à dos urbain.',
}

# ===========================================================================
# 8. SEARCH ARMS LOCATION (search_arms_location.bin_c - flags=0x80000000)
# ===========================================================================
SEARCH_ARMS_LOCATION_CALIBRATED = {
    '"Famous big cities and tourist\ndestinations with mafia families\npulling strings from the shadows.':
        '"Métropoles et sites touristiques où la mafia\ntire les ficelles dans l\'ombre.',
    '"Kak Dela"':
        '"Kak Dela"',
    '"The Jackal"':
        '"Le Chacal"',
    '5JC':
        '5JC',
    'A Central American criminal group\nknown for ruthless robberies and\nexcessively vicious blackmail.':
        "Cartel d'Amérique centrale réputé pour ses braquages\nimpitoyables et ses chantages vicieux.",
    'A Moscow bar popular among army\nofficers. The name is Russian\nfor "How\'s it going?"':
        'Bar moscovite prisé des officiers.\nSon nom signifie "Comment ça va ?" en russe.',
    'A Native American village that\nretains traditional methods of\nmaking spears and crafts.':
        "Village amérindien perpétuant la fabrication\ntraditionnelle de lances et d'artisanat.",
    'A Siberian general store selling\ndeadly weapons to the drunk, rowdy\nclientele.':
        'Bazar sibérien vendant des armes mortelles\nà des clients ivres et turbulents.',
    'A continent with a rich natural\nenvironment. Some areas suffer\nfrom internal conflicts.':
        'A continent with a rich natural\nenvironment. Some areas suffer\nfrom internal conflicts.',
    'A continent with lush natural\nenvironments. Some areas suffer\nfrom instability and crime.':
        'A continent with lush natural\nenvironments. Some areas suffer\nfrom instability and crime.',
    'A criminal group heavily involved in\nassassinations. They also trade in\ndecorative items for trendy killers.':
        "Réseau criminel spécialisé dans les contrats d'assassinat,\ntrafiquant aussi des parures pour tueurs stylés.",
    'A densely-populated slum that has\ngrown and expanded to resemble a\ncastle, where money is king.':
        "Bidonville tentaculaire devenu une véritable\nforteresse urbaine où seul l'argent fait la loi.",
    'A group known for its cruelty and a\nparticular fondness for knives and\nbrass knuckles.':
        'Gang cruel ayant un goût prononcé pour les couteaux\net les poings américains.',
    "A huge military research facility\nin the middle of the desert. No one\nknows what they're doing there.":
        "Une immense base militaire au milieu du désert.\nPersonne ne sait ce qui s'y trame réellement.",
    'A karate dojo. The master may be\npersuaded to part with his precious\ntonfa and nunchaku, for a price.':
        'Un dojo de karaté. Le maître pourrait céder\nses précieux tonfas et nunchakus, moyennant finances.',
    'A karate master from Okinawa. Easy-\ngoing and booze-loving. Knows where\nto get high quality weapons quickly.':
        "Maître de karaté d'Okinawa, bon vivant et buveur.\nSait où trouver vite des armes de haute volée.",
    'A large yakuza group based in the\nKansai area. Not at war with any\nother families... for now.':
        "Puissant clan yakuza du Kansai.\nEn paix avec les autres familles... pour l'instant.",
    'A lively market with some stalls\nselling all kinds of illegal goods.':
        'Marché animé dont des échoppes vendent\ndes marchandises illicites.',
    'A long-forgotten shrine deep in\na black forest, where even the\nbravest locals fear to tread.':
        "Sanctuaire au coeur d'une forêt sombre,\noù même les plus braves craignent d'aller.",
    'A market in a South American city--\nthe place to go to for weapons and\ngear not available via legal means.':
        'Un marché sud-américain : le lieu idéal pour dégoter\ndes armes et pièces introuvables par voies légales.',
    'A market open only at night,\nwhere the stalls are lined with\nweaponry from sundown to sunrise.':
        "Un marché nocturne dont les étals regorgent d'armes\ndu coucher au lever du soleil.",
    'A powerful criminal organization.\nGet on their bad side and you\ncould wind up dead... or worse.':
        "Puissante triade criminelle. S'attirer leurs\nfoudres peut vous coûter la vie... ou pire encore.",
    'A roadside marketplace. You never\nknow what you might find there.':
        "Marché de route. On ne sait jamais ce qu'on\npeut y dégoter.",
    'A run-down dive bar by a highway.\nThey sell more shotguns than shots.':
        "Bar miteux d'autoroute.\nOn y vend plus de fusils que de verres.",
    'A small settlement of the Inuit\npeople who make a living hunting.':
        'Un petit campement inuit vivant principalement de la chasse.',
    "A small village in the cold north,\nwhere it's possible to purchase\nequipment and weapons for hunting.":
        "Un petit village du grand nord où l'on peut\nacheter de l'équipement et des armes de chasse.",
    'A suburban sushi bar owned by a\nJapanophile who deals in many\nimported Japanese items.':
        'Bar à sushis tenu par un nippophile\nécoulant divers produits japonais importés.',
    'A terrifying criminal organization\nknown for large-scale robberies\nand mass extortions.':
        'Terrifiant réseau criminel réputé pour ses\nbraquages armés et ses extorsions massives.',
    'A very old mafia family based\nin a picturesque seaside town.':
        "Ancienne famille mafieuse d'une belle\nbourgade côtière.",
    'A village renowned for its weapon\ncraftsmen, whose skills have been\npassed on for many generations.':
        "Village réputé pour ses forgerons d'élite,\ndont l'art se transmet depuis des générations.",
    'Africa':
        'Africa',
    'An English soccer stadium and a\nbattlefield for overzealous fans.':
        'Stade de foot anglais, arène de combat\npour hooligans survoltés.',
    'An Indian nobleman who lost big on\ngambling is now selling his ancient\nfamily heirlooms to make ends meet.':
        'Un noble indien ruiné par le jeu qui brade les précieux\nhéritages familiaux pour joindre les deux bouts.',
    'An anti-government group is carrying\nout "liberation" attacks in an attempt\nto destabilize the current regime.':
        'Un groupe rebelle menant des attaques de " libération "\npour tenter de déstabiliser le pouvoir en place.',
    'An anti-government organization\ngrowing in strength day by day.':
        'Faction clandestine dont la force grandit\nde jour en jour.',
    'An auction house frequented by the\nrich who wish to purchase the best\nweapons and gear money can buy.':
        "Maison de vente courue des fortunés désireux de s'offrir\nle meilleur matériel de combat à prix d'or.",
    'An average yakuza family of medium\nsize and influence, offering a\nstandard assortment of guns, etc.':
        "Clan yakuza moyen d'influence modeste,\noffrant un éventail classique d'armes à feu.",
    "An elderly, passionate inventor\nwho'd rather not draw too much\nattention to himself or his work.":
        "Vieil inventeur passionné qui préfère ne pas\ntrop attirer l'attention sur lui ou ses créations.",
    'An old man claiming to have been\nborn at the end of the samurai era.\nCollects antique Japanese swords.':
        "Un vieillard prétendant être né à la fin de l'ère samurai.\nCollectionne les sabres japonais anciens.",
    'An old mountain temple. The monks\nliving there are very skilled in\nthe use of various pole weapons.':
        "Vieux temple montagnard. Ses moines sont\npassés maîtres dans le maniement des armes d'hast.",
    'An opulent bar in the capital,\nfrequented by politicians. They\nchoose their clientele carefully.':
        "Bar opulent de la capitale fréquenté par l'élite.\nLe tri à l'entrée y est impitoyable.",
    'Arab Mafia':
        'Clan arabe',
    'Arab Royalty':
        'Émirs arabes',
    'Areas known for oil, extreme\nwealth, and abject poverty.\nTravel can be dangerous.':
        'Areas known for oil, extreme\nwealth, and abject poverty.\nTravel can be dangerous.',
    'Balkan Mafia':
        'Clan Balkans',
    'Black Market':
        'Marché noir',
    'Black Market Auction':
        'Enchères noires',
    "Blacksmiths' Village":
        'Village forgerons',
    'Brazilian Mafia':
        'Mafia brésil.',
    'Can purchase shotguns to "ward off\nbears" from the foresters living at\nthe foot of the mountain range.':
        'On peut acheter des fusils pour " chasser l\'ours "\nauprès des forestiers au pied des montagnes.',
    'Cold climates can make travel\nchallenging. Local crime groups\nare good suppliers of weapons.':
        'Cold climates can make travel\nchallenging. Local crime groups\nare good suppliers of weapons.',
    'Colombian Cartels':
        'Cartels colombie',
    'Corporate Research Lab':
        'Labo de recherche',
    'Corsican Mafia':
        'Mafia corse',
    'Difficult to get to, with\nsupposedly nothing to see apart\nfrom miles of snow and ice... ':
        "Difficile d'accès, avec pour ainsi\ndire rien que de la neige et glace...",
    'Dispatch agents to locations in\nJapan. Expenses are lower when\ncompared to dispatching overseas.':
        "Envoyez des agents au Japon.\nLes frais sont moins élevés que pour\nun départ à l'étranger.",
    'E. Asia':
        'Asie E.',
    'E. Europe':
        'Europe E.',
    'Elusive village where to this day,\nninja undergo their secret training.\nGood source of traditional weapons.':
        "Village insaisissable où les ninjas s'entraînent encore.\nExcellente source d'armes traditionnelles.",
    'Entered the premises, gave the password, and was ushered\ninto a back room! How will the negotiations go!?':
        "Infiltré, mot de passe donné, conduit dans\nl'arrière-boutique ! Comment vont se passer les négo !?",
    'Families with exceptionally loyal\nmembers who know to keep their\nmouths shut about mafia business.':
        "Des familles aux membres loyalistes jurant l'omerta absolue\nsur les affaires du milieu.",
    'Famous big cities and tourist\ndestinations with mafia families\npulling strings from the shadows.':
        "Métropoles et sites touristiques où la mafia\ntire les ficelles dans l'ombre.",
    'Famous ruins constantly scoured\nby archaeologists and thieves.\nThey still have their secrets.':
        'Célèbres ruines fouillées par archéologues\net pilleurs. Elles gardent bien des secrets.',
    'Feared for their brutality, these\npowerful organizations have broad\ninfluence and a very long reach.':
        'Redoutés pour leur brutalité, ces cartels ont\nune vaste influence et un réseau tentaculaire.',
    'Ganges Delta':
        'Delta Gange',
    'Giza: Ancient Ruins':
        'Ruines de Gizeh',
    'Grand Canyon':
        'Grand Canyon',
    'Headquarters of a secret group aimed\nat overthrowing the government.\nKnown to possess illegal weapons.':
        "QG d'un groupe secret visant à renverser le pouvoir.\nConnu pour détenir des armes illégales.",
    'Hercules Sporting Goods':
        'Sports Hercules',
    'Hidden Ninja Village':
        'Village ninja secret',
    "Hunters' Village":
        'Bourg chasseur',
    'Incan Ruins':
        'Site inca',
    'Independent Inventor':
        'Inventeur indép.',
    'Indian Nobility':
        "Nobles d'Inde",
    'Inuit Village':
        'Village inuit',
    'It seems hammers are their weapons\nof choice when torturing victims.':
        'Le marteau est leur arme favorite\npour torturer leurs victimes.',
    "It's cold here. Very, very cold.":
        'Il fait très, très froid ici.',
    'Japan':
        'Japon',
    'Jungle':
        'Jungle',
    'Just a regular sporting goods shop.\nSells baseball bats and golf clubs.':
        'Boutique de sport classique.\nVend battes de baseball et clubs de golf.',
    'Kanto Yakuza Family':
        'Clan yakuza Kanto',
    'Karate Master':
        'Maître Karaté',
    'Kinki Gokumonkai':
        'Gokumonkai Kinki',
    'Kowloon Walled City':
        'Cité de Kowloon',
    'Liberation Army Camp':
        'Camp de libération',
    'Local Dojo':
        'Dojo local',
    "Looks like a normal office, but it's\na branch of a secret organization\nplanning to overthrow the government.":
        "On dirait un bureau normal, mais c'est la branche\nd'une organisation secrète visant à renverser l'État.",
    'Lubao Teahouse':
        'Thé de Lubao',
    'Mafia EL-38':
        'Mafia EL-38',
    'Managed to sneak into the store despite\nsuspicious looks from the shoppers!':
        'Faufilé en douce dans la boutique malgré\nles regards méfiants des clients !',
    'Many nations have been gaining\neconomic momentum but some areas\nare still unstable.':
        'Many nations have been gaining\neconomic momentum but some areas\nare still unstable.',
    'Marketplace':
        'Marché',
    'Mexican Mafia':
        'Mafia mexic.',
    'Modern Samurai':
        'Samouraï mod.',
    'N. America':
        'Amér. Nord',
    'NYC Mafia':
        'Mafia NYC',
    'Neo Japan HQ':
        'QG Néo-Japon',
    'Neo Japan Kinki Branch':
        'Néo-Japon (Kinki)',
    'Night Market':
        'Marché nuit',
    'Nomad Camp':
        'Campement',
    'North Pole':
        'Pôle Nord',
    'Offers a wide range of locations,\nranging from the cold north to\nthe jungles of Central America.':
        "Offre un large choix de lieux,\ndes glaces du grand nord jusqu'aux\njungles d'Amérique centrale.",
    'One':
        'Un',
    'Rocky Mountains':
        'Rocheuses',
    'Ruined Shrine':
        'Vieux temple',
    'Ruins of a lost city built high in\nthe mountains by an ancient empire.':
        "Ruines d'une cité perdue des sommets,\nbâtie par un antique empire.",
    'Ruins where you may find interesting\ndecorative objects, half-forgotten\nrelics, and ancient apparel.':
        'Ruines regorgeant de parures fascinantes, de reliques\noubliées et de parures millénaires.',
    'S. America':
        'Amér. Sud',
    'Secret Base in Nevada':
        'Base du Nevada',
    "Secret lab of a large corporation,\nwhere they conduct research they\ndon't want the public to know about.":
        "Laboratoire secret d'une grande corporation,\nmenant des recherches tenues secrètes du grand public.",
    'Sicilian Union':
        'Union Sicile',
    'Small-fry yakuza from the Tohoku\nregion. Quite friendly for a\ncriminal organization.':
        'Yakuzas de bas étage du Tohoku.\nPlutôt affables pour un clan criminel.',
    'Soccer Stadium':
        'Stade de foot',
    'Somali Coast':
        'Côte somalie',
    'Sunny Sicily is known for its\noranges, culture, and ruthless\nbut well-dressed mafia.':
        'La Sicile est réputée pour ses oranges,\nsa culture et sa mafia impitoyable et chic.',
    'Sushi Bar BANZAI':
        'Bar BANZAI',
    'The Arctic':
        'Arctique',
    'The Guild':
        'La Guilde',
    'The Hanafubuki Family':
        'Famille Hanafubuki',
    'The Napolitano Family':
        'Famille Napolitano',
    'The coastal waters are ruled by\npirates who attack fishing vessels\nand freighters without mercy.':
        'Eaux côtières sous la coupe de pirates pillant\nsans pitié chalutiers et cargos marchands.',
    'The infamous gangs of New York.':
        'Les célèbres gangs de New York.',
    'The nomads have varied odds and ends\nfor sale, but also offer other, more\ndangerous goods "to keep you safe."':
        'Les nomades vendent des babioles, mais aussi des biens bien\nplus dangereux " pour assurer votre protection ".',
    'They take great pride in their\ncollections of weapons and gear, but\nare willing to part with some of it.':
        "Fiers de leur grande collection d'armes,\nils acceptent toutefois d'en céder quelques pièces.",
    'This charming little dim sum\nrestaurant is just the cover for\na shop with weapons on the menu.':
        'Ce charmant restaurant de dim sum sert de\nfaçade à un arsenal complet sous le comptoir.',
    'This small village near the Ganges\nRiver is a good place to acquire\nhand-made, pole-type weapons.':
        "Ce petit village près du Gange est réputé pour ses\narmes d'hast artisanales de qualité.",
    'Tianlin Temple':
        'Temple Tianlin',
    'Underground Market':
        'Marché souterrain',
    'Underground Organization':
        'Réseau clandestin',
    'Used to be a trade union, but\nnowadays the guild members are\nselling secret intelligence.':
        'Jadis syndicat, les membres de la guilde\nvendent désormais des renseignements secrets.',
    'Variety Shop Khorosho':
        'Bazar Khorosho',
    'W. Asia':
        'Asie O.',
    'W. Europe':
        'Europe O.',
    'Washington D.C. Bar':
        'Bar de Washington',
    'We were suddenly surrounded by threatening shadows!\nWill the negotiations go smoothly!?':
        'Soudain cerné par des ombres menaçantes !\nLes négociations vont-elles bien se passer !?',
    "With piranhas in the rivers and huge\nsnakes in the forest, it's a holiday\nspot only for the most adventurous.":
        "Entre piranhas et serpents géants,\nce lieu n'attend que les aventuriers les plus intrépides.",
    'Zimbabwe: Ancient Ruins':
        'Ruines du Zimbabwe',
}

# ===========================================================================
# 9. ACTIVITY LIST / CP CHALLENGES (activity_list.bin_c - flags=0x80000000)
# ===========================================================================
ACTIVITY_LIST_CALIBRATED = {
    '\x01\x01\x01\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1a\x1a\x1a\x1b\x1b\x1b\x1b\x1c\x1c\x1c\x1d\x1d\x1d\x1e\x1e\x1e\x1f\x1f\x1f   !!!!!!""""""####$$$$$$%%%&&&&\'\'\'((()))***+++,,,---...///000001112334554556777788888999999:::;;;;<<<<===>?@ABCDDDDEFFGGGHHHIIIJJJKKLMMNNOOPQRSTUVWXYZZZZ[\\]^_`aaabbbcccdddeeefffgggghijklllmmmnnnooopppqrstuvwxyz{{{{{|||||}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa0\xa0¡¡¡¢¢¢£££¤¥¦§¨©ª«¬¬¬\xad®¯°±±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÃÄÅÆÇÈÉÊÊËËÌÍÎÏÐÑÎÏÐ':
        '\x01\x01\x01\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1a\x1a\x1a\x1b\x1b\x1b\x1b\x1c\x1c\x1c\x1d\x1d\x1d\x1e\x1e\x1e\x1f\x1f\x1f   !!!!!!""""""####$$$$$$%%%&&&&\'\'\'((()))***+++,,,---...///000001112334554556777788888999999:::;;;;<<<<===>?@ABCDDDDEFFGGGHHHIIIJJJKKLMMNNOOPQRSTUVWXYZZZZ[\\]^_`aaabbbcccdddeeefffgggghijklllmmmnnnooopppqrstuvwxyz{{{{{|||||}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa0\xa0¡¡¡¢¢¢£££¤¥¦§¨©ª«¬¬¬\xad®¯°±±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÃÄÅÆÇÈÉÊÊËËÌÍÎÏÐÑÎÏÐ',
    '\x01\x01\x01\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1a\x1a\x1a\x1b\x1b\x1b\x1b\x1c\x1c\x1c\x1d\x1d\x1d\x1e\x1e\x1e\x1f\x1f\x1f   !!!!!!""""""####$$$$$$%%%&&&&\'\'\'((()))***+++,,,---...///000001112334554556777788888999999:::;;;;<<<<===>?@ABCDDDDEFFGGGHHHIIIJJJKKLMMNNOOPQRSTUVWXYZZZZ[\\]^_`abcdefghijklmnopqrsssstuvwxxxyyyzzz{{{|||}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x87\x87\x87\x87\x88\x88\x88\x88\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬¬¬\xad\xad\xad®®®¯¯¯°±²³´µ¶·¸¸¸¹º»¼½½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÏÐÑÒÓÔÕÖÖ××ØÙÚÛÜÝÚÛÜ':
        '\x01\x01\x01\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1a\x1a\x1a\x1b\x1b\x1b\x1b\x1c\x1c\x1c\x1d\x1d\x1d\x1e\x1e\x1e\x1f\x1f\x1f   !!!!!!""""""####$$$$$$%%%&&&&\'\'\'((()))***+++,,,---...///000001112334554556777788888999999:::;;;;<<<<===>?@ABCDDDDEFFGGGHHHIIIJJJKKLMMNNOOPQRSTUVWXYZZZZ[\\]^_`abcdefghijklmnopqrsssstuvwxxxyyyzzz{{{|||}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x87\x87\x87\x87\x88\x88\x88\x88\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬¬¬\xad\xad\xad®®®¯¯¯°±²³´µ¶·¸¸¸¹º»¼½½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÏÐÑÒÓÔÕÖÖ××ØÙÚÛÜÝÚÛÜ',
    'Acquire %d different accessories for Ai':
        'Obtenir %d accessoires diff. pour Ai',
    'Acquire %d different accessories for Chika':
        'Obtenir %d accessoires diff. pour Chika',
    'Acquire %d different accessories for Hibiki':
        'Obtenir %d accessoires diff. pour Hibiki',
    'Acquire %d different accessories for Mana':
        'Obtenir %d accessoires diff. pour Mana',
    'Acquire %d different accessories for Saki':
        'Obtenir %d accessoires diff. pour Saki',
    'Acquire %d different accessories for Yuki':
        'Obtenir %d accessoires diff. pour Yuki',
    'Acquire %d different gear items':
        'Obtenir %d armures diff.',
    'Acquire %d different gear or accessory items':
        'Obtenir %d armures ou accessoires',
    'Acquire %d different prizes':
        'Obtenir %d prix différents',
    'Acquire %d different prizes from the UFO Catcher':
        'Obtenir %d prix différents au UFO Catcher',
    'Acquire %d different weapons':
        'Obtenir %d armes différentes',
    "Ai's accessory collection 1":
        "Accessoires d'Ai 1",
    "Ai's accessory collection 2":
        "Accessoires d'Ai 2",
    "Ai's accessory collection 3":
        "Accessoires d'Ai 3",
    'Befriend Ayaka':
        'Ami avec Ayaka',
    'Befriend Ayaka through the telephone club':
        'Ami avec Ayaka via le club de rencontre',
    'Befriend Doll Girl':
        'Ami avec Doll Girl',
    'Befriend Emiri':
        'Ami avec Emiri',
    'Befriend Haruki':
        'Ami avec Haruki',
    'Befriend Haruki through the telephone club':
        'Ami avec Haruki via le club de rencontre',
    'Befriend Kitajima the Shroomer':
        'Ami avec Kitajima le cueilleur',
    'Befriend Kyoko':
        'Ami avec Kyoko',
    'Befriend Luka':
        'Ami avec Luka',
    'Befriend Miho':
        'Ami avec Miho',
    'Befriend Mr. Libido - Akimoto':
        'Ami avec M. Libido - Akimoto',
    'Befriend Mr. Libido - Habu':
        'Ami avec M. Libido - Habu',
    'Befriend Mr. Moneybags - Fukushima':
        'Ami avec M. Crésus - Fukushima',
    'Befriend Mr. Moneybags - Tanioka':
        'Ami avec M. Crésus - Tanioka',
    'Befriend Officer Kikuchi':
        "Ami avec l'agent Kikuchi",
    'Befriend Pocket Circuit Fighter':
        'Ami avec le Pocket Fighter',
    'Befriend Riku':
        'Ami avec Riku',
    'Befriend Riku through the telephone club':
        'Ami avec Riku via le club de rencontre',
    'Befriend Simon the Mystery Man':
        "Ami avec Simon l'homme mystère",
    'Befriend the Gandhara staff member':
        "Ami avec l'employé du Gandhara",
    'Befriend the Sushi Gin chef':
        'Ami avec chef Sushi Gin',
    'Befriend the barkeep':
        'Ami avec le barman',
    'Befriend the boss at Komian':
        'Ami avec le chef du Komian',
    'Bowl %d strikes':
        '%d strikes',
    'Bowl %d strikes in bowling':
        '%d strikes au bowling',
    'Break %d objects during battles\n*Excluding those broken by throwing or kicking':
        'Détruire %d objets au combat\n*Sans compter les lancers ou coups de pied',
    'Break %d objects in battle':
        'Détruire %d objets au duel',
    'Buy %d Electronics King properties':
        'Achat %d biens Roi Élec.',
    'Buy %d Gambling King properties':
        'Achat %d biens Roi du Jeu',
    'Buy %d Leisure King properties':
        'Achat %d biens Roi Loisirs',
    'Buy %d Leisure King property':
        'Achat %d bien Roi Loisirs',
    'Buy %d Media King properties':
        'Achat %d biens Roi Médias',
    'Buy %d Pleasure King properties':
        'Achat %d biens Roi Plaisir',
    'Buy %d properties in the Electronics King area':
        "%d biens achetés (zone Roi de l'Élec.)",
    'Buy %d properties in the Gambling King area':
        '%d biens achetés (zone Roi du Jeu)',
    'Buy %d properties in the Leisure King area':
        '%d biens achetés (zone Roi Loisirs)',
    'Buy %d properties in the Media King area':
        '%d biens achetés (zone Roi Médias)',
    'Buy %d properties in the Pleasure King area':
        '%d biens achetés (zone Roi Plaisir)',
    'Buy %d property in the Leisure King area':
        '%d bien acheté (zone Roi Loisirs)',
    'Buy from Dream Machines %d times':
        'Achat distributeurs %d fois',
    'Buy items from Dream Machines %d times':
        'Acheter aux distributeurs %d fois',
    'Catch %d different freshwater fish':
        'Catch %d different freshwater fish',
    'Catch %d different freshwater fish while fishing':
        "Pêcher %d poissons d'eau douce différents",
    'Catch %d different saltwater fish':
        'Catch %d different saltwater fish',
    'Catch %d different saltwater fish while fishing':
        "Pêcher %d poissons d'eau de mer différents",
    "Chika's accessory collection 1":
        'Accessoires de Chika 1',
    "Chika's accessory collection 2":
        'Accessoires de Chika 2',
    "Chika's accessory collection 3":
        'Accessoires de Chika 3',
    'Collect %d different frames':
        'Collecter %d châssis diff.',
    'Collect %d different frames in Pocket Circuit':
        'Collecter %d châssis diff. en Pocket Circuit',
    'Collect %d different gears':
        'Trouver %d engrenages',
    'Collect %d different gears in Pocket Circuit':
        'Trouver %d engrenages en Pocket Circuit',
    'Collect %d different motors':
        'Collecter %d moteurs diff.',
    'Collect %d different motors in Pocket Circuit':
        'Collecter %d moteurs diff. en Pocket Circuit',
    'Collect %d different tires':
        'Collecter %d pneus diff.',
    'Collect %d different tires in Pocket Circuit':
        'Collecter %d pneus diff. en Pocket Circuit',
    'Collect %d telephone cards':
        'Trouver %d cartes tél.',
    'Collect total proceeds of %s':
        'Recettes totales de %s',
    'Collected total proceeds of %s':
        'Recettes totales de %s',
    'Compete in Pocket Circuit races %d times':
        '%d courses disputées en Pocket Circuit',
    'Compete in races %d times':
        '%d courses disputées',
    'Complete %d Kiryu substories':
        'Finir %d Kiryu substories',
    'Complete %d Majima substories':
        'Finir %d Majima substories',
    "Complete Ai's special training and substory":
        "Finir Ai's special training and substory",
    "Complete Ai's substory":
        "Finir Ai's substory",
    'Complete Akaushimaru':
        'Finir Akaushimaru',
    'Complete Cafe Alps':
        'Finir Cafe Alps',
    "Complete Chika's special training and substory":
        "Finir Chika's special training and substory",
    "Complete Chika's substory":
        "Finir Chika's substory",
    'Complete Earth Angel':
        'Finir Earth Angel',
    'Complete Fuji Soba':
        'Finir Fuji Soba',
    'Complete Ganko Sushi':
        'Finir Ganko Sushi',
    'Complete Gindaco':
        'Finir Gindaco',
    'Complete Heroine':
        'Finir Heroine',
    "Complete Hibiki's special training and substory":
        "Finir Hibiki's special training and substory",
    "Complete Hibiki's substory":
        "Finir Hibiki's substory",
    'Complete Kani Douraku':
        'Finir Kani Douraku',
    'Complete Kanrai':
        'Finir Kanrai',
    'Complete Kinryu Ramen':
        'Finir Kinryu Ramen',
    'Complete Komian':
        'Finir Komian',
    'Complete Kushikatsu Daruma':
        'Finir Kushikatsu Daruma',
    'Complete Maharaja':
        'Finir Maharaja',
    "Complete Mana's special training and substory":
        "Finir Mana's special training and substory",
    "Complete Mana's substory":
        "Finir Mana's substory",
    'Complete Ringer Hut':
        'Finir Ringer Hut',
    "Complete Saki's special training and substory":
        "Finir Saki's special training and substory",
    "Complete Saki's substory":
        "Finir Saki's substory",
    'Complete Shellac':
        'Finir Shellac',
    'Complete Shot Bar STIJL':
        'Finir Shot Bar STIJL',
    'Complete Smile Burger':
        'Finir Smile Burger',
    'Complete Sushi Gin':
        'Finir Sushi Gin',
    'Complete Tengokuken':
        'Finir Tengokuken',
    'Complete Tsuruhashi Fugetsu':
        'Finir Tsuruhashi Fugetsu',
    'Complete Utahime':
        'Finir Utahime',
    'Complete Vincent':
        'Finir Vincent',
    'Complete Yoronotaki':
        'Finir Yoronotaki',
    "Complete Yuki's special training and substory":
        "Finir Yuki's special training and substory",
    "Complete Yuki's substory":
        "Finir Yuki's substory",
    'Complete Zuboraya':
        'Finir Zuboraya',
    'Deepen your friendship with Doll Girl':
        "Approfondir l'amitié avec Doll Girl",
    'Deepen your friendship with Emiri the Mach Bowl employee':
        "Approfondir l'amitié avec Emiri, employée du Mach Bowl",
    'Deepen your friendship with Kitajima the Shroomer':
        "Approfondir l'amitié avec Kitajima le cueilleur",
    'Deepen your friendship with Kyoko the SEGA HI-TECH LAND\nSotenbori employee':
        "Approfondir l'amitié avec Kyoko du SEGA HI-TECH LAND\nde Sotenbori",
    'Deepen your friendship with Luka the SEGA HI-TECH LAND\nNakamichi St. employee':
        "Approfondir l'amitié avec Luka du SEGA HI-TECH LAND\nde la rue Nakamichi",
    'Deepen your friendship with Miho the Poppo Tenkaichi St.\nemployee':
        'Ami avec Miho du Poppo Tenkaichi',
    'Deepen your friendship with Mr. Libido Akimoto':
        "Approfondir l'amitié avec M. Libido Akimoto",
    'Deepen your friendship with Mr. Libido Habu':
        "Approfondir l'amitié avec M. Libido Habu",
    'Deepen your friendship with Mr. Moneybags Fukushima':
        "Approfondir l'amitié avec M. Crésus Fukushima",
    'Deepen your friendship with Mr. Moneybags Tanioka':
        "Approfondir l'amitié avec M. Crésus Tanioka",
    'Deepen your friendship with Officer Kikuchi':
        "Approfondir l'amitié avec l'agent Kikuchi",
    'Deepen your friendship with Simon the Mystery Man':
        "Approfondir l'amitié avec Simon l'homme mystère",
    'Deepen your friendship with the Gandhara staff member':
        "Approfondir l'amitié avec l'employé du Gandhara",
    'Deepen your friendship with the Pocket Circuit Fighter':
        "Approfondir l'amitié avec le Pocket Circuit Fighter",
    'Deepen your friendship with the Sushi Gin chef':
        "Approfondir l'amitié avec le chef du Sushi Gin",
    'Deepen your friendship with the barkeep at\nShot Bar STIJL':
        "Approfondir l'amitié avec le barman du\nShot Bar STIJL",
    'Deepen your friendship with the boss at Komian':
        "Approfondir l'amitié avec le chef du Komian",
    'Defeat %d coliseum opponents':
        'Battre %d rivaux au Colisée',
    'Defeat %d enemies in Beast style':
        'Battre %d ennemis en style Brute',
    'Defeat %d enemies in Brawler style':
        'Battre %d ennemis en Bagarreur',
    'Defeat %d enemies in Breaker style':
        'Battre %d ennemis en style Danseur',
    'Defeat %d enemies in Dragon style':
        'Battre %d ennemis en style Dragon',
    'Defeat %d enemies in Mad Dog style':
        'Battre %d ennemis en Chien enragé',
    'Defeat %d enemies in Rush style':
        'Battre %d ennemis en Foncent',
    'Defeat %d enemies in Slugger style':
        'Battre %d ennemis en style Batteur',
    'Defeat %d enemies in Thug style':
        'Battre %d ennemis en Voyou',
    'Defeat %d enemies on the street':
        'Battre %d ennemis en rue',
    'Defeat %d enemies that attack you on the street':
        'Battre %d ennemis qui vous agressent en rue',
    'Defeat %d enemies using the Dragon of Dojima style':
        'Battre %d ennemis en Dragon de Dojima',
    'Defeat %d enemies using the Mad Dog of Shimano style':
        'Battre %d ennemis en Chien de Shimano',
    'Defeat %d enemies using the beast style':
        'Battre %d ennemis en style Brute',
    'Defeat %d enemies using the brawler style':
        'Battre %d ennemis en style Bagarreur',
    'Defeat %d enemies using the breaker style':
        'Battre %d ennemis en style Danseur',
    'Defeat %d enemies using the rush style':
        'Battre %d ennemis en style Foncent',
    'Defeat %d enemies using the slugger style':
        'Battre %d ennemis en style Batteur',
    'Defeat %d enemies using the thug style':
        'Battre %d ennemis en style Voyou',
    'Defeat %d enemies using weapons':
        'Battre %d ennemis armé',
    'Defeat %d nouveau riche enemies':
        'Battre %d ennemis richards',
    'Defeat %d nouveau riche enemy':
        'Battre %d ennemi richard',
    'Defeat Mr. Shakedown %d time':
        'Battre M. Shakedown %d fois',
    'Defeat Mr. Shakedown %d times':
        'Battre M. Shakedown %d fois',
    'Defeat Sega %d time':
        'Battre Sega %d fois',
    'Defeat an enemy with the last name "Sega" %d time':
        'Terrasser un ennemi nommé " Sega " %d fois',
    'Defeat the Electronics King':
        "Battre le Roi de l'Élec.",
    'Defeat the Gambling King':
        'Battre le Roi du Jeu',
    'Defeat the Leisure King':
        'Battre Roi des Loisirs',
    'Defeat the Media King':
        'Battre le Roi Médias',
    'Defeat the Pleasure King':
        'Battre Roi du Plaisir',
    'Dine at eateries %d times':
        'Manger au resto %d fois',
    'Earn %d fans in Jupiter area':
        '%d fans zone Jupiter',
    'Earn %d fans in Mars area':
        '%d fans en zone Mars',
    'Earn %d fans in Mercury area':
        '%d fans zone Mercure',
    'Earn %d fans in Moon area':
        '%d fans en zone Moon',
    'Earn %d fans in Venus area':
        '%d fans zone Venus',
    'Earn %d fans in the Jupiter area':
        '%d fans dans zone Jupiter',
    'Earn %d fans in the Mars area':
        '%d fans dans la zone Mars',
    'Earn %d fans in the Mercury area':
        '%d fans dans zone Mercure',
    'Earn %d fans in the Moon area':
        '%d fans dans la zone Moon',
    'Earn %d fans in the Venus area':
        '%d fans dans la zone Venus',
    'Earn a total of %s':
        'Gagner %s au total',
    'Earn a total of %s by batting':
        'Gagner %s au batting center',
    'Earn a total of %s in Catfights':
        'Gagner %s aux combats de catch',
    'Earn a total of %s in baccarat':
        'Gagner %s au baccara',
    'Earn a total of %s in battle':
        'Gagner %s au duel',
    'Earn a total of %s in blackjack':
        'Gagner %s au blackjack',
    'Earn a total of %s in cee-lo':
        'Gagner %s au cee-lo',
    'Earn a total of %s in cho-han':
        'Gagner %s au cho-han',
    'Earn a total of %s in darts':
        'Gagner %s aux fléchettes',
    'Earn a total of %s in koi-koi':
        'Gagner %s au koi-koi',
    'Earn a total of %s in mahjong':
        'Gagner %s au mahjong',
    'Earn a total of %s in oicho-kabu':
        "Gagner %s à l'oicho-kabu",
    'Earn a total of %s in poker':
        'Gagner %s au poker',
    'Earn a total of %s in pool':
        'Gagner %s au billard',
    'Earn a total of %s in roulette':
        'Gagner %s à la roulette',
    'Earn a total of %s in sales':
        'Gagner %s de ventes',
    'Earn a total of %s in split games':
        'Gagner %s au split game',
    'Earned a total of %s':
        'Gagné %s au total',
    'Earned a total of %s at the batting center':
        'Gagner %s au batting center',
    'Earned a total of %s in Catfights':
        'Gagner %s aux combats de catch',
    'Earned a total of %s in baccarat':
        'Gagner %s au baccara',
    'Earned a total of %s in battle':
        'Gagner %s au combat en tout',
    'Earned a total of %s in blackjack':
        'Gagner %s au blackjack',
    'Earned a total of %s in cee-lo':
        'Gagner %s au cee-lo',
    'Earned a total of %s in cho-han':
        'Gagner %s au cho-han',
    'Earned a total of %s in darts':
        'Gagner %s aux fléchettes',
    'Earned a total of %s in koi-koi':
        'Gagner %s au koi-koi',
    'Earned a total of %s in mahjong':
        'Gagner %s au mahjong',
    'Earned a total of %s in oicho-kabu':
        "Gagner %s à l'oicho-kabu",
    'Earned a total of %s in poker':
        'Gagner %s au poker',
    'Earned a total of %s in pool':
        'Gagner %s au billard',
    'Earned a total of %s in roulette':
        'Gagner %s à la roulette',
    'Earned a total of %s in sales':
        'Gagner %s de ventes',
    'Earned a total of %s in split game bowling':
        'Gagner %s au split game du bowling',
    'Eat %d food items':
        'Manger %d plats',
    'Enjoy yourself at an entertainment venue %d times':
        "Profiter d'un lieu de divertissement %d fois",
    'Entertain yourself %d times':
        'Se divertir %d fois',
    'Finish all bouts with Komeki':
        'Finir les duels de Komeki',
    'Friday Night 1':
        'Friday Night 1',
    'Friday Night 2':
        'Friday Night 2',
    'Friday Night 3':
        'Friday Night 3',
    'Get %d points in Fantasy Zone':
        '%d points à Fantasy Zone',
    'Get %d points in Out Run':
        '%d points à Out Run',
    'Get %d points in Space Harrier':
        '%d points à Space Harrier',
    'Get %d points in Super Hang-On':
        '%d points à Super Hang-On',
    'Get 90 or more in 24-hour Cinderella at karaoke':
        '90 pts ou plus à 24-hour Cinderella au karaoké',
    'Get 90 or more in Bakamitai at karaoke':
        '90 pts ou plus à Bakamitai au karaoké',
    'Get 90 or more in Heartbreak Mermaid at karaoke':
        '90 pts ou plus à Heartbreak Mermaid au karaoké',
    'Get 90 or more in Judgement -Shinpan- at karaoke':
        'Obtenir 90 points ou plus à Judgement au karaoké',
    'Get 90 or more in Rouge of Love at karaoke':
        '90 pts ou plus à Rouge of Love au karaoké',
    'Get 90 or more in x3 SHINE at karaoke':
        '90 pts ou plus à x3 SHINE au karaoké',
    'Get 90+ in 24-hour Cinderella':
        'Get 90+ in 24-hour Cinderella',
    'Get 90+ in Bakamitai':
        'Get 90+ in Bakamitai',
    'Get 90+ in Heartbreak Mermaid':
        'Get 90+ in Heartbreak Mermaid',
    'Get 90+ in Judgement -Shinpan-':
        'Get 90+ in Judgement -Shinpan-',
    'Get 90+ in Rouge of Love':
        'Get 90+ in Rouge of Love',
    'Get 90+ in x3 SHINE':
        'Get 90+ in x3 SHINE',
    'Get the highest score in\nFriday Night (EASY) at the disco':
        'Meilleur score dans\nFriday Night (FACILE) au disco',
    'Get the highest score in\nFriday Night (HARD) at the disco':
        'Meilleur score dans\nFriday Night (DIFF.) au disco',
    'Get the highest score in\nFriday Night (NORMAL) at the disco':
        'Meilleur score dans\nFriday Night (NORMAL) au disco',
    'Get the highest score in\nI Wanna Take You Home (EASY) at the disco':
        'Meilleur score dans\nI Wanna Take You Home (FACILE) au disco',
    'Get the highest score in\nI Wanna Take You Home (HARD) at the disco':
        'Meilleur score dans\nI Wanna Take You Home (DIFF.) au disco',
    'Get the highest score in\nI Wanna Take You Home (NORMAL) at the disco':
        'Meilleur score dans\nI Wanna Take You Home (NORMAL) au disco',
    "Get the highest score in\nI'm Gonna Make Her Mine (EASY) at the disco":
        "Meilleur score dans\nI'm Gonna Make Her Mine (FACILE) au disco",
    "Get the highest score in\nI'm Gonna Make Her Mine (HARD) at the disco":
        "Meilleur score dans\nI'm Gonna Make Her Mine (DIFF.) au disco",
    "Get the highest score in\nI'm Gonna Make Her Mine (NORMAL) at the disco":
        "Meilleur score dans\nI'm Gonna Make Her Mine (NORMAL) au disco",
    'Get the highest score in\nKoi no DISCO QUEEN (EASY) at the disco':
        'Meilleur score dans\nKoi no DISCO QUEEN (FACILE) au disco',
    'Get the highest score in\nKoi no DISCO QUEEN (HARD) at the disco':
        'Meilleur score dans\nKoi no DISCO QUEEN (DIFF.) au disco',
    'Get the highest score in\nKoi no DISCO QUEEN (NORMAL) at the disco':
        'Meilleur score dans\nKoi no DISCO QUEEN (NORMAL) au disco',
    'Get the highest score in\nQueen of Passion (EASY) at the disco':
        'Meilleur score dans\nQueen of Passion (FACILE) au disco',
    'Get the highest score in\nQueen of Passion (HARD) at the disco':
        'Meilleur score dans\nQueen of Passion (DIFF.) au disco',
    'Get the highest score in\nQueen of Passion (NORMAL) at the disco':
        'Meilleur score dans\nQueen of Passion (NORMAL) au disco',
    'Go out %d times':
        'Gagner %d fois',
    'Go out in mahjong %d times':
        'Gagner au mahjong %d fois',
    'Go out in mahjong with Full Straight':
        'Gagner au mahjong avec Grande Suite',
    'Go out in mahjong with Haneman %d time':
        'Gagner au mahjong en Haneman %d fois',
    'Go out in mahjong with Mangan %d times':
        'Gagner au mahjong en Mangan %d fois',
    'Go out in mahjong with Riichi Ippatsu':
        'Gagner au mahjong en Riichi Ippatsu',
    'Go out with Full Straight':
        'Go out with Full Straight',
    'Go out with Haneman %d time':
        'Gagner en Haneman %d fois',
    'Go out with Mangan %d times':
        'Gagner en Mangan %d fois',
    'Go out with Riichi Ippatsu':
        'Go out with Riichi Ippatsu',
    'Help %d attack victims around town':
        'Aider %d victimes en ville',
    'Help %d people who are being attacked around town':
        'Secourir %d personnes agressées en ville',
    "Hibiki's accessory collection 1":
        "Accessoires d'Hibiki 1",
    "Hibiki's accessory collection 2":
        "Accessoires d'Hibiki 2",
    "Hibiki's accessory collection 3":
        "Accessoires d'Hibiki 3",
    'I Wanna Take You Home 1':
        'I Wanna Take You Home 1',
    'I Wanna Take You Home 2':
        'I Wanna Take You Home 2',
    'I Wanna Take You Home 3':
        'I Wanna Take You Home 3',
    "I'm Gonna Make Her Mine 1":
        "I'm Gonna Make Her Mine 1",
    "I'm Gonna Make Her Mine 2":
        "I'm Gonna Make Her Mine 2",
    "I'm Gonna Make Her Mine 3":
        "I'm Gonna Make Her Mine 3",
    'Increase advisory staff to %d':
        'Monter les conseils à %d',
    'Increase management staff to %d':
        'Monter la direction à %d',
    'Increase security staff to %d':
        'Monter la sécurité à %d',
    'Koi no DISCO QUEEN 1':
        'Koi no DISCO QUEEN 1',
    'Koi no DISCO QUEEN 2':
        'Koi no DISCO QUEEN 2',
    'Koi no DISCO QUEEN 3':
        'Koi no DISCO QUEEN 3',
    "Learn all of Areshi's moves":
        "Apprendre tout d'Areshi",
    "Learn all of Bacchus's moves":
        'Apprendre tout de Bacchus',
    "Learn all of Fei Hu's moves":
        'Apprendre tout de Fei Hu',
    "Learn all of Kamoji's moves":
        'Apprendre tout de Kamoji',
    "Learn all of Miss Tatsu's moves":
        'Apprendre tout de Miss Tatsu',
    'Make the Jupiter area your turf':
        'Conquérir la zone Jupiter',
    'Make the Mars area your turf':
        'Conquérir la zone Mars',
    'Make the Mercury area your turf':
        'Conquérir la zone Mercure',
    'Make the Moon area your turf':
        'Conquérir la zone Moon',
    'Make the Venus area your turf':
        'Conquérir la zone Venus',
    "Mana's accessory collection 1":
        'Accessoires de Mana 1',
    "Mana's accessory collection 2":
        'Accessoires de Mana 2',
    "Mana's accessory collection 3":
        'Accessoires de Mana 3',
    'Occupy %d% of the Electronics King area':
        "Occuper %d% zone Roi de l'Élec.",
    'Occupy %d% of the Gambling King area':
        'Occuper %d% de la zone du Roi du Jeu',
    'Occupy %d% of the Leisure King area':
        'Occuper %d% zone Roi Loisirs',
    'Occupy %d% of the Media King area':
        'Occuper %d% zone Roi Médias',
    'Occupy %d% of the Pleasure King area':
        'Occuper %d% zone Roi Plaisir',
    'Order everything on the menu at Akaushimaru':
        'Tout commander chez Akaushimaru',
    'Order everything on the menu at Cafe Alps':
        'Tout commander chez Cafe Alps',
    'Order everything on the menu at Earth Angel':
        'Tout commander chez Earth Angel',
    'Order everything on the menu at Fuji Soba':
        'Tout commander chez Fuji Soba',
    'Order everything on the menu at Ganko Sushi':
        'Tout commander chez Ganko Sushi',
    'Order everything on the menu at Gindaco':
        'Tout commander chez Gindaco',
    'Order everything on the menu at Heroine Karaoke Bar':
        'Tout commander chez Heroine Karaoke Bar',
    'Order everything on the menu at Kani Douraku':
        'Tout commander chez Kani Douraku',
    'Order everything on the menu at Kanrai':
        'Tout commander chez Kanrai',
    'Order everything on the menu at Kinryu Ramen':
        'Tout commander chez Kinryu Ramen',
    'Order everything on the menu at Komian':
        'Tout commander chez Komian',
    'Order everything on the menu at Kushikatsu Daruma':
        'Tout commander chez Kushikatsu Daruma',
    'Order everything on the menu at Maharaja':
        'Tout commander chez Maharaja',
    'Order everything on the menu at Ringer Hut':
        'Tout commander chez Ringer Hut',
    'Order everything on the menu at Shellac':
        'Tout commander chez Shellac',
    'Order everything on the menu at Shot Bar STIJL':
        'Tout commander chez Shot Bar STIJL',
    'Order everything on the menu at Smile Burger':
        'Tout commander chez Smile Burger',
    'Order everything on the menu at Sushi Gin':
        'Tout commander chez Sushi Gin',
    'Order everything on the menu at Tengokuken':
        'Tout commander chez Tengokuken',
    'Order everything on the menu at Tsuruhashi Fugetsu':
        'Tout commander chez Tsuruhashi Fugetsu',
    'Order everything on the menu at Utahime Karaoke Bar':
        'Tout commander chez Utahime Karaoke Bar',
    'Order everything on the menu at Vincent':
        'Tout commander chez Vincent',
    'Order everything on the menu at Yoronotaki':
        'Tout commander chez Yoronotaki',
    'Order everything on the menu at Zuboraya':
        'Tout commander chez Zuboraya',
    'Partner with %d shops in Jupiter area':
        '%d commerces partenaires (Jupiter)',
    'Partner with %d shops in Mars area':
        '%d commerces partenaires (Mars)',
    'Partner with %d shops in Mercury area':
        '%d commerces partenaires (Mercure)',
    'Partner with %d shops in Moon area':
        '%d commerces partenaires (Moon)',
    'Partner with %d shops in Venus area':
        '%d commerces partenaires (Venus)',
    'Partner with %d shops in the Jupiter area':
        '%d commerces partenaires (zone Jupiter)',
    'Partner with %d shops in the Mars area':
        '%d commerces partenaires (zone Mars)',
    'Partner with %d shops in the Mercury area':
        '%d commerces partenaires (zone Mercure)',
    'Partner with %d shops in the Moon area':
        '%d commerces partenaires (zone Moon)',
    'Partner with %d shops in the Venus area':
        '%d commerces partenaires (zone Venus)',
    'Perform %d carom shots':
        '%d carambolages',
    'Perform %d carom shots in pool':
        '%d carambolages au billard',
    'Perform %d combination shots':
        'Réussir %d coups combinés',
    'Perform %d combination shots in pool':
        'Réussir %d coups combinés au billard',
    'Perform %d hat tricks':
        'Réussir %d hat tricks',
    'Perform %d hat tricks in darts':
        '%d hat tricks aux fléchettes',
    'Queen of Passion 1':
        'Queen of Passion 1',
    'Queen of Passion 2':
        'Queen of Passion 2',
    'Queen of Passion 3':
        'Queen of Passion 3',
    'Raise %d shops to Rank S':
        '%d commerces Rang S',
    'Raise all shops to Rank S':
        'Monter tout au Rang S',
    'Recruit %d advisors':
        '%d conseillers',
    'Recruit %d bronze hostesses':
        'Recruter %d hôtesses bronze',
    'Recruit %d bronze hostesses\n*Excluding those recruited with CP':
        'Recruter %d hôtesses bronze\n*Sans les recrutements par PC',
    'Recruit %d gold hostesses':
        'Recruter %d hôtesses or',
    'Recruit %d gold hostesses\n*Excluding those recruited with CP':
        'Recruter %d hôtesses or\n*Sans les recrutements par PC',
    'Recruit %d managers':
        '%d directeurs',
    'Recruit %d platinum hostesses':
        'Recruter %d hôtesses platine',
    'Recruit %d platinum hostesses\n*Excluding those recruited with CP':
        'Recruter %d hôtesses platine\n*Sans les recrutements par PC',
    'Recruit %d security':
        '%d gardes',
    'Recruit %d silver hostesses':
        'Recruter %d hôtesses argent',
    'Recruit %d silver hostesses\n*Excluding those recruited with CP':
        'Recruter %d hôtesses argent\n*Sans les recrutements par PC',
    "Saki's accessory collection 1":
        'Accessoires de Saki 1',
    "Saki's accessory collection 2":
        'Accessoires de Saki 2',
    "Saki's accessory collection 3":
        'Accessoires de Saki 3',
    'Scatter a total of %s':
        'Jeter %s au total',
    'Scattered a total of %s':
        'Avoir jeté %s en tout',
    'Serve a total of %d customers':
        'Servir un total de %d clients',
    'Spend a total of %s':
        'Dépenser %s en tout',
    'Spent a total of %s':
        'Dépensé %s en tout',
    'Take over Jupiter area':
        'Conquérir zone Jupiter',
    'Take over Mars area':
        'Conquérir zone Mars',
    'Take over Mercury area':
        'Conquérir zone Mercure',
    'Take over Moon area':
        'Conquérir zone Moon',
    'Take over Venus area':
        'Conquérir zone Venus',
    'Talk to people %d times':
        'Parler à %d passants',
    'Talk to people around town %d times':
        'Parler à des gens en ville %d fois',
    'Travel %d km by dashing':
        'Courir sur %d km',
    'Travel %d km on foot':
        'Faire %d km à pied',
    'Travel by taxi %d times':
        'Prendre le taxi %d fois',
    'Use %d different Heat Actions':
        'Faire %d actions Heat diff.',
    'Use %d medicine items':
        'Prendre %d remèdes',
    'Use Heat Actions %d times':
        'Faire %d actions Heat',
    'View %d different video clips':
        'Visionner %d vidéos diff.',
    'Win %d coliseum tournaments':
        'Gagner %d tournois Colisée',
    'Win %d shogi game without a take back':
        'Gagner %d jeu shogi sans reprise',
    'Win %d shogi games without a take back':
        'Gagner %d jeux shogi sans reprise',
    'Win coliseum tournaments %d times':
        'Gagner tournois Colisée %d fois',
    "Win the Champions' Cup":
        'Coupe des Champions',
    "Win the Experts' Race":
        'Course des Experts',
    'Win the Introductory Race':
        "Course d'initiation",
    'Win the King of Speed Cup':
        'Coupe Roi Vitesse',
    "Win the Little Racers' Cup":
        'Coupe Petits Pilotes',
    "Win the Pocket Circuit Champions' Cup":
        'Coupe des Champions (Pocket Circuit)',
    "Win the Pocket Circuit Experts' Race":
        'Course des Experts (Pocket Circuit)',
    'Win the Pocket Circuit Introductory Race':
        "Course d'initiation (Pocket Circuit)",
    'Win the Pocket Circuit King of Speed Cup':
        'Coupe Roi de la Vitesse (Pokecir)',
    "Win the Pocket Circuit Little Racers' Cup":
        'Coupe des Petits Pilotes (Pokecir)',
    'Win the Pocket Circuit Pro-Am Race':
        'Gagner la course Pro-Am (Pokecir)',
    "Win the Pocket Circuit Rookies' Race":
        'Course des Débutants (Pokecir)',
    'Win the Pro-Am Race':
        'Gagner le Pro-Am',
    "Win the Rookies' Race":
        'Course Débutants',
    "Yuki's accessory collection 1":
        'Accessoires de Yuki 1',
    "Yuki's accessory collection 2":
        'Accessoires de Yuki 2',
    "Yuki's accessory collection 3":
        'Accessoires de Yuki 3',
}
