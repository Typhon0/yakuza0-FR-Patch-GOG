# -*- coding: utf-8 -*-
"""
tools/build_calibrated_substories.py
Calibrates explanation_sub_story.bin_c to strictly fit within the 58,232-byte Sega heap budget.
Produces 100% valid RGG table with 10 columns, 447 rows, French titles and French quest explanations.
"""

import sys
import struct
import os

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from scratch.substory_titles_inplace import SUBSTORY_TITLES_INPLACE
from tools.sllz import compress_sllz

def clean_french_font(text):
    return (text
            .replace('’', "'")
            .replace('‘', "'")
            .replace('“', '"')
            .replace('”', '"')
            .replace('…', '...')
            .replace('œ', 'oe')
            .replace('Œ', 'OE')
            .replace('æ', 'ae')
            .replace('Æ', 'AE')
            .replace('–', '-')
            .replace('—', '-')
            .replace('Ç', 'C')
            .replace('ç', 'c'))

CALIBRATED_EXPLANATIONS = {
    2: "J'ai protégé la voyante. Mais elle semblait savoir\nqu'elle serait attaquée... Je ne veux pas y croire,\nmais se pourrait-il que ce soit vrai ?",
    9: "C'est le gamin qui a pris le jeu d'Akio.\nRien de pire que faire pleurer un enfant.\nTiens bon Akio, je vais récupérer ton jeu.",
    11: "Trouvé le voyou qui a pris l'Ara-Q3 au gamin.\nQuels tristes modèles... Il va recevoir une leçon\nqu'il n'est pas près d'oublier.",
    13: "Trouvé le yakuza qui a pris l'Ara-Q3 au voyou qui l'a volé\nau gosse qui l'a pris à Akio... Trop compliqué !\nQuelqu'un va morfler !",
    14: "Quelle épreuve ! Tout ça pour un jeu. Heureux qu'Akio\nait récupéré son Ara-Q3. J'espère qu'il pourra y jouer\navec son père.",
    18: "Samantha veut une pizza. C'est occidental, donc un fast-food\ndoit en avoir. Direction le Smile Burger.",
    19: "Livrer cette pizza à Samantha tant qu'elle est brûlante.\nLivraison Pizza-La au Champion District, en route !",
    21: "Le quiproquo pizza-visa a créé des remous, mais tout finit\nbien. La pizza, c'est comme un couple : il faut que ce soit chaud.",
    23: "Rencontré le reporter Kasuga au Shellac. J'espère qu'il\névitera les ennuis. Je repasserai au Shellac un de ces quatre.",
    24: "Cet idiot de Kasuga n'a rien écouté et plonge en plein danger.\nJe vais devoir intervenir pour calmer le jeu.",
    25: "Kasuga, le reporter du Shellac, est intrépide. Mais j'ai\nencore beaucoup à apprendre sur les bas-fonds de Kamurocho.",
    27: "Kasuga traque une autre affaire risquée. Le trafic d'humains\nse terrerait vers Pink Alley.",
    28: "Vu Kasuga enquêter sous couverture. J'espère qu'il va bien...\nJe devrais passer au Shellac pour vérifier.",
    29: "Pas revu Kasuga au Shellac depuis sa planque. Mauvais\npressentiment. Direction Pink Alley où je l'ai vu.",
    30: "Ce type vient du réseau de traite d'humains ?\nMieux vaut le neutraliser et sauver Kasuga.",
    31: "Ce Kasuga est ingérable. Mais le boss de ce réseau...\nCette voix et cette carrure... Déjà vu quelque part ?\nMieux vaut ne pas trop y penser.",
    34: "Un groupe yanki populaire joue au Theater Square.\nQui était cet homme qui observait la foule ?",
    36: "Pas facile d'apprendre à un groupe à jouer les durs.\nMais ils ont ce qu'il faut pour percer.\nAccrochez-vous, les Yokomichi Silvers !",
    41: "Apprendre à la Reine Ayu à réprimander était ardu.\nBonne chance, Ayu. Je t'encouragerai de loin.",
    43: "Témoin d'un deal étrange au Kamuro Shopping Area.\nQui était cet homme mystérieux ? Devrais lui parler.",
    44: "Apprendre le mot de passe est tentant, mais ça sent\nles ennuis inutiles. Que faire... ?",
    47: "Hmm ?! Je ne sais pas pourquoi, mais ils veulent se battre.\nImpossible de refuser, on dirait.",
    48: "Après une bagarre, Monmon m'a donné les réponses voulues.\nRetournons voir le type au mot de passe.",
    49: "J'ai gâché la réponse de Monmon. Navré pour le deal,\nmais pas au point d'encaisser des coups.",
    50: "J'ai le mot de passe du mystérieux marchand, mais...\nSu, bo, te... nu, hi... C'est impossible à mémoriser !",
    51: "Je peux enfin acheter à ce marchand. Que d'efforts\npour ce mot de passe... Mais ça en valait la peine.",
    53: "On m'a demandé d'aider une équipe TV. Pas banal.\nJ'irai leur parler quand j'aurai le temps.",
    54: "Je ne connais rien à la télé, mais à moi de briller.\nDébarrassons-nous de ces trouble-fêtes !",
    55: "La télé est un dur métier, mais elle fait rêver.\nContinuez d'inspirer les gens, les gars.",
    57: "Vu un type espionner une hôtesse devant un cabaret.\nMal intentionné ? Je devrais lui parler.",
    58: "Un père veut retrouver sa fille perdue de vue ?\nJ'aimerais bien aider, mais quand j'aurai le temps.",
    61: "Un gamin avait besoin d'un service près du parc.\nJ'aimerais aider, mais pas le temps pour l'instant.",
    62: "Le distributeur cool était un kiosque pour adultes !\nLui acheter ça ? Sinon, il perdra foi envers les adultes.",
    63: "Faufilement discret vers le distributeur dans l'allée\npour acheter ce magazine ! Pas le droit à l'erreur.",
    66: "Une star mondiale viendrait pour un tournage vidéo.\nUne histoire de miracle ? Gare aux ennuis aussi.",
    67: "On me demande de régler un souci sur le clip de Miracle.\nTrop occupé pour l'instant, une autre fois peut-être.",
    68: "Miracle doit être protégé des zombies jusqu'au bout !\nDans quoi me suis-je encore embarqué ?",
    69: "J'ai affronté du monde, mais jamais de morts-vivants !\nPlus jamais je ne combattrai de zombies, c'est sûr.",
    71: "Appel annonçant une femme au carré du fisc régional.\nJe devrai lui parler dès qu'elle arrive.",
    74: "Fouiller le bureau de Maguro Enterprises.\nIl doit y avoir des preuves de leur fraude fiscale.",
    77: "Le téléclub me demande de prendre l'appel d'une femme louche.\nPas le temps pour ça, mais je me demande ce que c'était.",
    79: "La femme du téléclub était une ravisseuse ! Mais priorité\nabsolue : je dois sauver ce gosse.",
    80: "Rencontrer un kidnappeur au téléclub, inédit !\nQuand ta peine sera purgée, on ira ensemble, ravisseur.",
    82: "Recruter du personnel ? Nous en manquons cruellement.\nJe devrais dire à Marina de publier des annonces.",
    83: "Pourquoi dois-je faire l'entretien ? Prévenir Marina\nquand je serai prêt, même si je traîne des pieds.",
    84: "Mener des entretiens est épuisant. Jamais vu un escroc\nau taxi débarquer. Ça m'aidera à cerner les gens.",
    86: "Marina a remis une offre. Les entretiens sont une plaie,\nmais il le faut pour ma secrétaire et la boîte.",
    87: "Cette fois, la candidate est une femme. Les entretiens\nsont pénibles, mais ça fait partie du job.\nPrévenir Marina quand je serai prêt.",
    90: "Dispute houleuse entre lycéens. Les ignorer ne semble\npas juste. Devrais-je parler au petit ami ?",
    93: "Trouvé Mina près de Senryo Avenue, comme dit son copain.\nComment l'aborder et vérifier si elle vend ses dessous ?",
    95: "Mina a été forcée de vendre ses dessous par une Sachiko.\nLa trouver vers le quartier des hôtels : brune, en uniforme.",
    96: "Sachiko est une tête de mule, mes arguments ont fait chou blanc.\nPas le choix, je dois dire la vérité à Mina.",
    97: "Jouer avec le feu brûle, mais laisser ce pervers agir\nserait trop cruel. Je dois intervenir.",
    98: "Sachiko a eu assez peur pour cesser son trafic de lingerie.\nSoulagé pour Mina. Aucun enfant ne devrait vivre ça.",
    104: "Un UFO Catcher ? Délicat, mais je dois prouver au jeune\nmaître que j'en suis capable.",
    106: "Embuscade déjouée sans souci. Qui était ce type ?\nSa voix semblait bien jeune.",
    109: "Le jeune maître avait des gardes du corps après tout.\nHeureux d'avoir pu l'aider. J'espère qu'il a son doudou.",
    110: "L'homme devant le Children's Park s'appelle Bacchus.\nIl sent le saké, mais sait se battre. Il m'a appris\nle style Brawler. M'entraîner avec lui serait utile.",
    116: "Marina a remis une annonce. Pénible de faire passer des\nentretiens, mais c'est pour ma secrétaire et l'entreprise.",
    117: "Ce candidat paraît... particulier. Prévenir Marina\nquand je serai prêt pour l'entretien.",
    118: "La 3e est la bonne : enfin un candidat digne de confiance !\nKoshimizu, j'ai hâte de bosser avec toi.",
    121: "Je ne sais pas ce qui se passe, mais hors de question de voir\nune femme se faire frapper. J'interviens.",
    125: "Marina m'a passé un savon pour l'eau AH-HA. C'est quoi ce système\npyramidal ? Dernière fois que je me fais pigeonner.",
    127: "Miracle au Maharaja ? Rumeur incertaine, mais j'irai voir\nsi je passe dans le coin.",
    128: "Je voulais juste saluer, mais accueil musclé. Ce gorille\nprouve bien que Miracle est à l'intérieur.",
    129: "Miracle, tu es incroyable. Une vraie superstar.\nEn espérant un nouveau défi de danse un jour. Woo !",
    132: "Indices pour la fille de la vidéo : BBQ coréen, bowling\net batting center. Je guetterai ces endroits.",
    136: "La fille ne fait que ressembler à celle de la vidéo.\nNavré pour cette déception. Désolé, mon gars.",
    138: "Une histoire à raconter ? Je devrais écrire à Dolce Kamiya.\nIl y a des cartes postales sur le bureau.",
    139: "Pourvu qu'ils retiennent ma carte ! Mieux vaut écouter\nl'émission de Dolce Kamiya pour vérifier.",
    142: "Une histoire à raconter ? Réécrire à Dolce Kamiya.\nIl reste des cartes postales sur le bureau.",
    143: "J'espère qu'ils retiendront encore ma carte. Écouter\nl'émission de Dolce Kamiya pour voir.",
    146: "Une histoire à raconter ? Écrire encore à Dolce Kamiya.\nLa 3e fois sera la bonne. Cartes sur le bureau.",
    147: "Pourvu qu'ils choisissent encore ma carte. Écouter\nl'émission de Dolce Kamiya pour voir.",
    148: "Jamais pensé rencontrer Dolce Kamiya et lui serrer la main.\nEt j'ai gagné un prix. Vive la radio !",
    150: "Hisaaki me défie en danse au Maharaja.\nJe relèverai le défi si je m'ennuie un de ces quatre.",
    151: "Battu par Hisaaki sur la piste. Revanche dès que j'aurai\nrévisé mes pas. La prochaine fois, je gagne !",
    152: "Battre Hisaaki était plaisant. Selon lui, danser ensemble\nfait de nous des frères. Danser a du bon, finalement.",
    154: "Je croyais me faire draguer, mais c'était un défi de danse.\nCurieux de voir le style de Maiko Ishiodori...",
    155: "Maiko Ishiodori m'a battu sur la piste. Je la redéfierai\nune fois ma technique affûtée. Victoire prochaine !",
    156: "Battu Maiko Ishiodori en danse. D'après elle, un grand\ndanseur arrive d'Osaka. Voyons ce qu'il vaut.",
    158: "Incident au Maharaja qui a dégoûté tout le monde.\nHisaaki et Maiko étaient abattus. Que s'est-il passé ?",
    159: "Un virtuose d'Osaka arrive au Maharaja.\nHâte de voir son niveau sur la piste de danse.",
    160: "Battu par Ogita en danse. J'exigerai ma revanche quand\nma technique sera au point. Victoire prochaine !",
    169: "Elle dit s'appeler Haruki et s'habiller en rouge.\nJe me demande si on parviendra à se croiser.",
    170: "Haruki m'a demandé de la rejoindre dans une chambre d'hôtel.\nElle me plaît, mais j'ignore ses réelles intentions...",
    172: "Haruki m'a posé un lapin, son copain était odieux.\nMais j'ai apprécié nos échanges. Bon vent à elle.",
    173: "Elle dit s'appeler Ayaka. Voix sexy et envoûtante.\nJ'ai vraiment hâte de la rencontrer.",
    175: "Elle dit s'appeler Mirei. J'espère qu'elle est aussi belle\nque sa voix au téléphone le laissait présager.",
    176: "Mirei était bien mignonne, mais le coup de la boîte de mouchoirs\nm'a calmé. Plus d'appels pendant un bon moment !",
    179: "Elle dit s'appeler Riku. Sa voix douce m'a séduit.\nJe veux la rencontrer en personne.",
    180: "Riku m'a posé un lapin et une femme louche m'a dragué.\nJe ne comprends rien aux femmes... Triste soirée.",
    183: "Elle s'appelle Asakura et travaille chez un éditeur.\nElle m'a invité au café. J'irai voir de quoi il retourne.",
    184: "Asakura m'a demandé de tester des positions de combat.\nJe devrais la retrouver pour lui montrer.",
    187: "Les cours de Mika-chan ont affûté sa voiture.\nJe dois améliorer la mienne pour la battre.",
    188: "Victoire contre Mika-chan, mais elle a tenu tête.\nSacrée fille. Mais j'avais l'impression d'être épié...",
    191: "En adulte, Satoru-kun pilote vite. Hors de question\nqu'il colporte des ragots sur moi. Revanche immédiate !",
    192: "Malentendu réglé avec Satoru-kun. Trois pilotes seraient\nencore plus forts à Kamurocho. À voir au circuit.",
    194: "Au Pocket Circuit Stadium, mes potes étaient rétamés.\nUne Sena-chan les a écrasés. Ils veulent que je les venge.",
    195: "Sena-chan n'est pas manchote pour battre tout le monde.\nJe dois peaufiner mes réglages pour l'emporter.",
    198: "Défier Harumi-chan, la prof du Pocket Circuit.\nJe vais lui prouver que les stats ne font pas tout.",
    200: "Harumi-chan était coriace et calculatrice.\nKazuyoshi-kun, le boss du circuit, est en ville. Nouveau défi !",
    203: "Kazuyoshi-kun mérite son titre, il fonce !\nJe dois optimiser ma caisse pour espérer le rattraper.",
    204: "Battu Kazuyoshi-kun et rabiboché le groupe.\nLe Pocket Circuit est génial... Mais qui l'a vaincu aussi ?",
    206: "Qui aurait cru que le Pocket Circuit Fighter était le plus\nrapide de Kamurocho ? Place au défi ultime !",
    208: "Tant appris et d'adversaires valeureux côtoyés.\nDu drame, des rires, de l'amour... Merci, Pocket Circuit !",
    210: "Elle dit s'appeler Maria, voix très sensuelle.\nHâte de la découvrir en vrai.",
    213: "Elle dit s'appeler Sayuri, mignonne et taquine.\nCurieux de voir qui elle est en personne...",
    214: "Sayuri avait l'âge de ma mère ! Ça m'apprendra\nà mieux écouter au club téléphonique.",
    219: "Ce marchand de champignons est-il louche ?\nPeu importe, je dois briser quelques crânes.",
    220: "Kitajima le ramasseur... Un tel nom attire la méfiance.\nIl devrait faire attention à ses fréquentations.",
    223: "Pas pensé qu'on puisse s'exciter sur des télécartes.\nSi j'en trouve d'autres, je lui montrerai.",
    225: "Ce fonds est-il vraiment rentable ?\nJe parlerai à Fukushima pour en savoir plus.",
    226: "Si mes affaires prospèrent, j'investirai dans ce fonds.\nEn espérant que le gars d'Osaka le rentabilise.",
    229: "Le Pocket Circuit Fighter est passionné. L'homme de la situation\npour les courses et de précieux conseils.",
    232: "Fait connaissance avec Miho, nouvelle au Poppo.\nTant à apprendre en supérette... Bon courage à elle !",
    235: "Fait connaissance avec Emiri à l'accueil du Mach Bowl.\nElle adore regarder jouer les clients. Le job de ses rêves.",
    238: "Fait connaissance avec un chef reprenant les sushis de son père.\nIl aurait bien besoin d'un coup de pouce.",
    241: "Rencontré Luka, employée pétillante du Club SEGA rue Nakamichi.\nElle dit assurer sur les jeux de course.",
    245: "Tueur à gages écarté de Bacchus. Le vieux propose\nde m'entraîner. Ça vaut le coup d'accepter.",
    251: "Aidé Kamoji à renvoyer un créancier. Ses leçons\nvalent le détour pour enrichir mon style Brawler.",
    254: "Aidé Mlle Tatsu à récupérer une dette chez un mauvais payeur.\nElle m'enseignera ses secrets du style Beast.",
    257: "Yuki Sato sait se battre, loin du simple voyou.\nMieux vaut être sur mes gardes la prochaine fois.",
    260: "Un type en manteau blanc m'a invité à une fête déjantée.\nPas trop chaud pour l'instant, peut-être plus tard.",
    266: "Aidé un jeune de la famille Dojima contre des yakuzas.\nUn honneur de soutenir mon ancien clan.",
    267: "Appris des techniques d'un jeune de la famille Dojima.\nPrécieux atouts pour mon style Dragon de Dojima.",
    272: "Aidé un employé en galère face à des voyous.\nBienveillance Kamurocho... Toujours un plaisir.",
    273: "L'employé m'a remercié chaleureusement.\nLe quartier est plus sûr grâce à des gens bien.",
    275: "L'escroc du pont a encore frappé. Cette fois,\nje lui réserve une surprise mémorable.",
    276: "Escroc corrigé. Il y réfléchira à deux fois avant\nde duper d'honnêtes gens.",
    278: "Un homme étrange prétend être une divinité.\nJe devrais voir ce qu'il a à raconter.",
    279: "Cette prétendue divinité avait besoin d'un coup de main.\nDrôle de rencontre, mais distrayante.",
    280: "Aidé cette divinité excentrique. Kamurocho recèle\nvraiment de drôles d'oiseaux.",
    283: "Un dragon en devenir. Avec ce chasseur de pantalons,\nnos chemins se recroiseront... Retenir le nom de Ryuji Goda.",
    285: "Éconduit une fille cherchant un faux copain.\nMais elle était aux abois. Aller la voir devant Zuboraya.",
    286: "Faire le faux copain devant son père, pas banal.\nL'amour paternel force le respect. Serai-je un bon père ?",
    288: "Type bizarre croisé à Ashitaba Park. Dépité que je rende\nsa balle à un enfant. Que mijote-t-il ?",
    296: "Mère inquiète pour sa fille, mais m'infiltrer dans une secte\nest risqué. La foi n'est pas un jeu.",
    299: "Ce délire de shooreh pippi est bidon. Forcer ce type\nà me conduire auprès de leur gourou perché !",
    300: "Munan Suzuki montre son vrai visage. Neutraliser\nce faux prophète huileux et libérer Iori-chan !",
    303: "Un téléphone portable ? Le type dit que c'est high-tech,\nmais quel intérêt ? Sauf pour appeler, peut-être.",
    304: "Convaincu d'acheter une batterie pour ce mobile high-tech.\nDon Quijote devrait en avoir en rayon.",
    305: "Le high-tech se mérite. Trouver de quoi soulager l'épaule\nde ce gamin. Une boisson revigorante fera l'affaire.",
    307: "Ce portable apporte bien des soucis. Tester enfin\ncelui d'Idozuka au M Store de Shofukucho.",
    308: "Inutile d'avoir un portable sans personne à appeler.\nBien assez de high-tech pour un bon moment.",
    310: "Que se passe-t-il avec ce costard-cravate ?\nIl prend cher pour un motif bien obscur.",
    311: "Frapper ce cadre n'annulera pas la TVA.\nCes furieux feraient mieux de cesser leur cirque.",
    312: "Conseils fiscaux demandés, mais qu'y connais-je ?\nIl ferait mieux de demander à un spécialiste.",
    313: "Pourvu que mes idées folles n'augmentent pas les impôts !\nSi c'est le cas, désolé pour le Japon...",
    315: "Couple virulent devant le resto de crabes Kani Douraku.\nLeurs cris gênent le commerce, qu'ils s'expliquent ailleurs.",
    316: "Demande en mariage via des mots croisés, élégant !\nJ'aimerais bien donner un coup de main une autre fois.",
    317: "Pour toucher le coeur, il faut parler avec ses mots.\nBelle leçon. Longue vie à ces deux tourtereaux.",
    323: "Peu importe l'avis d'autrui, seule compte ta volonté.\nHeureux que le rêve de Suda-chan prenne vie.",
    325: "L'émission de radio de Dolce offre un prix aux courriers lus.\nUtiliser les cartes postales sur la table du fond.",
    326: "Pourvu que Dolce choisisse ma carte ! Écouter l'émission\nde radio pour connaître le verdict.",
    329: "Une carte lue chez Dolce. Deux de plus pour le million !\nCartes postales disponibles sur la table du fond.",
    330: "Pourvu que Dolce lise encore ma carte ! Brancher\nla radio pour savoir si je gagne.",
    333: "Deux cartes lues chez Dolce ! Plus qu'une pour le million.\nCartes postales dispo sur la table du fond.",
    334: "J'espère que Dolce retiendra ma carte une dernière fois.\nPlus qu'à écouter la radio pour voir le résultat.",
    337: "Vu une annonce de test médical bien rémunéré.\nEn cas de besoin d'argent frais, voir leur agent au parc.",
    338: "Test de drogue conclu. Mon corps a bien réagi,\net la paie était au rendez-vous. Ne pas en abuser.",
    340: "Une voix plaintive sort des toilettes publiques.\nQuelqu'un semble en détresse de papier...",
    341: "Apporter du papier toilette à ce pauvre bougre.\nLe soulagement n'a pas de prix.",
    342: "Cet individu aux toilettes m'a remercié chaleureusement.\nUn geste simple mais salvateur.",
    345: "La rencontre avec cette femme était explosive.\nUne vraie tornade qui ne se laisse pas faire.",
    353: "Aidé un restaurateur en manque d'inspiration.\nLa cuisine d'Osaka ne plaisante pas avec le goût !",
    356: "Recettes perfectionnées avec le chef. Le restaurant\nva faire un carton plein dans Sotenbori.",
    358: "Un homme d'affaires cherche des partenaires solides.\nUne opportunité à saisir pour Club Sunshine.",
    359: "Négociation conclue avec succès. Sunshine étend son réseau\net son prestige dans le quartier.",
    360: "Un client difficile posait des soucis à l'entrée.\nRemis à sa place en douceur.",
    362: "Conseillé une hôtesse débutante sur son comportement.\nLe métier s'apprend pas à pas.",
    363: "L'hôtesse progresse à vue d'oeil. Sunshine forme\nles meilleures de la région.",
    364: "Un concurrent louche rôde autour du cabaret.\nSurveiller ses agissements de près.",
    366: "L'Obatarienne, reine des commères d'Osaka !\nElle gagne la première manche, mais je n'abdique pas.",
    368: "Ce yakuza ignore la furie d'une Obatarienne en rogne.\nMieux vaut intervenir pour sauver ce malheureux.",
    369: "L'être le plus redoutable sous le soleil n'est ni un yakuza\nni un champion... C'est l'Obatarienne d'Osaka.",
    372: "Kengo m'a battu sur la piste. Je dois hausser mon jeu\net lui montrer qui est le maître.",
    373: "Kengo battu en danse, mais insuffisant pour affronter\nMlle Isobe. Ma gloire ne fait que commencer.",
    379: "Folie au Maharaja, la foule scande nos noms.\nMlle Isobe a orchestré notre duel avec classe.",
    380: "Mlle Isobe m'a écrasé en battle de danse.\nJe dois bosser mon jeu pour la revanche. Prochaine fois,\nelle finira deuxième !",
    381: "Mlle Isobe battue en danse ! Futur roi de la piste ou pas,\npour l'heure je savoure mon triomphe.",
    384: "Le faux copain de Yuki-chan était un malentendu, ouf !\nOn compte sur toi pour faire briller Sunshine, Yuki-chan.",
    389: "Hôtesse est un noble métier, pas de honte à avoir.\nCes deux vantards doivent des excuses à Mana-chan.",
    396: "Yuta-kun veille sur sa soeur Hibiki-chan. Bon gamin.\nTenir ma promesse et assurer sa sécurité.",
    398: "Ces brutes harcèlent Saki-chan devant le club ?\nCertains ont vraiment des envies de suicide.",
    402: "Le gars de la cabine veut un pistolet 9 mm automatique.\nLes corvées m'ennuient, mais perdre son jeu m'agace autant...",
    403: "Le gars de la cabine se nomme Simon et m'envoie faire\nses courses pour son petit jeu. Qui est ce type ?",
    406: "Si Sunshine cartonne, je pourrai investir chez Tanioka.\nJ'espère que ce gars de Tokyo fera fructifier la mise.",
    409: "Rencontré un type bizarre mais incollable sur les femmes.\nVisionner des vidéos à Gandhara pour suivre la cadence.",
    412: "La fillette devant l'arcade semblait perdue, mais peut\nrentrer seule. Pourvu que personne ne l'embête.",
    414: "Ces imbéciles ont embêté la mauvaise petite fille.\nMontrons-leur leur monumentale erreur !",
    418: "Rencontré le chef du Komian, un type bien à l'ancienne.\nEt ses plats sont un délice absolu.",
    421: "Le barman du STIJL compare alcools et personnalités,\ntous uniques. Un homme fascinant à écouter.",
    424: "Fait connaissance avec le vendeur du Gandhara.\nPour se détendre, c'est le lieu idéal. Entre mecs, on se comprend.",
    427: "Rencontré Kyoko-chan à l'arcade, un charme exotique.\nJ'irai la revoir au Club SEGA à l'occasion.",
    430: "Les arts de Komeki sont stupéfiants.\nÀ moi d'enseigner deux ou trois leçons au vieux maître !",
    431: "Komeki est un drôle de renard. De nouveaux coups me viennent\nquand j'échange des mandales avec lui.",
    435: "Des battles de breakdance ? Prêt à défier Areshi\net sa bande pour régaler les spectateurs.",
    436: "Areshi est sympa et plein d'idées neuves.\nPrêt à me montrer ses mouvements. Heureux d'avoir fait sa connaissance.",
    444: "Un sale coup menace Sotenbori. Filer aux arènes en taxi\ndès que je serai prêt pour un combat féroce.",
    445: "Un combat capital que je ne peux absolument pas perdre !",
}

def get_calibrated_substories_bin():
    with open('par_original/boot_steam_fr.par', 'rb') as f:
        steam_p = parse_par(f.read())
    d_steam = decompress_sllz(steam_p['explanation_sub_story.bin_c'][3])
    
    num_cols = struct.unpack('>I', d_steam[4:8])[0]
    curr = 16 + num_cols * 64
    
    col_defs = []
    col_payloads = []
    
    for c in range(num_cols):
        off = 16 + c * 64
        name = d_steam[off:off+32].split(b'\x00')[0].decode('latin1')
        meta1 = d_steam[off+32:off+48]
        meta2 = list(struct.unpack('>4I', d_steam[off+48:off+64]))
        col_type, count, size, flag = meta2
        raw = d_steam[curr:curr+size]
        curr += size
        col_defs.append((name, meta1, meta2))
        col_payloads.append(raw)
        
    # Col 0 (TITLE)
    t_raw = col_payloads[0]
    t_count = col_defs[0][2][1]
    pos = 0
    t_entries = []
    for _ in range(t_count):
        r_idx = struct.unpack('>H', t_raw[pos:pos+2])[0]
        end = t_raw.find(b'\x00', pos+2)
        s = t_raw[pos+2:end].decode('latin1')
        t_entries.append((r_idx, s))
        pos = end + 1
        
    new_t_payload = bytearray()
    for r_idx, s in t_entries:
        fr_t = SUBSTORY_TITLES_INPLACE.get(s, s)
        fr_t = clean_french_font(fr_t)
        new_t_payload.extend(struct.pack('>H', r_idx))
        new_t_payload.extend(fr_t.encode('latin1') + b'\x00')
    while len(new_t_payload) % 4 != 0:
        new_t_payload.append(0)
    col_payloads[0] = bytes(new_t_payload)
    col_defs[0][2][2] = len(new_t_payload)
    
    # Col 3 (EXPLANATION)
    e_raw = col_payloads[3]
    e_count = col_defs[3][2][1]
    steam_strs = [s.decode('latin1') for s in e_raw.split(b'\x00')[:e_count]]
    
    new_e_strs = []
    for idx, s in enumerate(steam_strs):
        if idx in CALIBRATED_EXPLANATIONS:
            calibrated = CALIBRATED_EXPLANATIONS[idx]
        else:
            calibrated = s
        calibrated = clean_french_font(calibrated)
        new_e_strs.append(calibrated.encode('latin1'))
        
    new_e_payload = bytearray(b'\x00'.join(new_e_strs) + b'\x00')
    while len(new_e_payload) % 4 != 0:
        new_e_payload.append(0)
    col_payloads[3] = bytes(new_e_payload)
    col_defs[3][2][2] = len(new_e_payload)
    
    # Assemble table
    header = bytearray(d_steam[:16])
    col_headers = bytearray()
    for name, meta1, meta2 in col_defs:
        name_bytes = name.encode('latin1').ljust(32, b'\x00')
        col_headers.extend(name_bytes)
        col_headers.extend(meta1)
        col_headers.extend(struct.pack('>4I', *meta2))
        
    rebuilt = bytes(header + col_headers + b''.join(col_payloads))
    assert len(rebuilt) <= 58232, f"FAIL: Substory table uncompressed size exceeds 58,232 bytes ({len(rebuilt)} > 58232)"
    
    comp = compress_sllz(rebuilt)
    return 0x80000000, len(rebuilt), len(comp), comp

if __name__ == '__main__':
    flags, u_sz, c_sz, comp = get_calibrated_substories_bin()
    print(f"[SUCCESS] Calibrated explanation_sub_story.bin_c: flags=0x{flags:08x}, u_sz={u_sz}, c_sz={c_sz}")
