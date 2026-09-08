# -*- coding: utf-8 -*-
"""
translate_pause_par_complete.py

Translates all remaining English in release_gog/data/pausepar_e/pause.par:
- tougijyo_participant.bin_c (30 Bed of Styx fighter profiles)
- extra.bin_c (4 strings)
"""

import os
import sys
import shutil
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz

PAUSE_TRANSLATIONS = {
    # 1. Karate brawler (277)
    "An infamous brawler skilled in karate. He worked\nin the criminal underworld as a mercenary and\nexecutioner, terminating the lives of countless\nyakuza. Although he was said to have died in a\none-on-one fight with a certain individual, here\nhe is now, ready to reclaim his crown.":
        "Bagareur redoute, maitre en karate. Il a servi\nde mercenaire et bourreau dans la pègre, tuant\nde nombreux yakuza. On le croyait mort lors d'un\nduel singulier, mais le voici pret a reprendre\nsa couronne dans l'arene.",

    # 2. Fabio South America (352)
    "Hailing from a South American nation infamous\nfor its political instability, Fabio was feared\neven among the crime bosses there. It was said\nthat one whisper was all he needed to get anyone\nput to death. He left the country when the\ngovernment mobilized the army in a fierce battle\nagainst organized crime. This place is just\nanother safe house to him.":
        "Venu d'Amerique du Sud, Fabio terrifiait les\nparrains locaux. Un simple murmure de sa part\nsuffisait a faire executer quiconque. Il a fui son\npays quand l'armee s'est levee contre les cartels.\nPour lui, cet endroit n'est qu'une planque de plus.",

    # 3. Chinese assassin (284)
    "A Chinese assassin known to select the cruelest\npossible methods in eliminating his targets.\nRather than just do his job, he went the extra\nlength to torture victims until they begged to be\nkilled. Ended up in the Bed of Styx when even his\nboss started feeling unsafe with him around.":
        "Tueur a gages chinois employant les methodes\nles plus atroces. Il torturait ses victimes\njusqu'a ce qu'elles supplient d'etre achevees.\nIl a atterri au Lit du Styx apres que son propre\npatron ait commence a craindre pour sa vie.",

    # 4. Lover killer (384)
    "A professional who would have no qualms about\nkilling even his lover, should someone pay him to\ndo it. His tactic was to bring a girlfriend with\nhim and approach the target, pretending to focus\nsolely on his companion. Then he'd swiftly make\nthe kill, and silence the girl forever, too. But\none day, the girl he used as distraction proved to\nbe an influential mafia boss's mistress...":
        "Tueur froid capable d'assassiner sa compagne pour\nune prime. Sa tactique : approcher sa cible avec\nune conquete pour détourner l'attention, frapper\net liquider la fille aussi. Mais un jour, son leurre\ns'est averee etre la maitresse d'un chef mafieux...",

    # 5. Otake vigilante (342)
    "Otake used to offer his services to the victims of\nheinous crimes and their families to exact revenge\nfor the wrongs committed against them. He thought\nhe was doing the right thing, until he killed a\ntarget and was then hired by their family to take\nrevenge for his death. After that eye-opener,\nhe came willingly to the Bed of Styx to atone.":
        "Otake vengeait les familles de victimes de crimes\nodieux. Persuade d'agir pour le bien, jusqu'au\njour ou les proches d'une cible l'ont engage pour\nvenger la mort qu'il venait de causer. Ecrasé par\ncette prise de conscience, il est venu au Lit du\nStyx pour expier ses fautes.",

    # 6. Arctic bear (389)
    "A huge bear captured near the arctic about ten\nyears ago. Multiple tests have shown that this\nbear possesses extraordinary strength, speed, and\nintelligence rivaling that of humans. As research\nteam members kept getting eaten and the costs of\nkeeping this ever-hungry animal fed were simply\ntoo high, it was eventually donated to the Bed of\nStyx where it could feed to its heart's content.":
        "Ours colossal capture dans l'Arctique il y a 10 ans.\nDes tests ont revele une force et une vitesse hors\nnormes, rivalisant avec l'intellect humain. Apres\navoir devore plusieurs chercheurs et vu le cout de\nson alimentation, il fut donne au Lit du Styx ou\nil peut se repaitre a volonte.",

    # 7. Egyptian arms dealer (284)
    "A young Egyptian who built a fortune selling\nsmuggled weapons to nations at war. He supplied\nboth sides of any conflict, betraying his clients'\nsecrets for money. His clients caught on to his\ndouble dealings and shipped him off to a place he\ncould not be expected to ever return from.":
        "Jeune Egyptien enrichi par la contrebande d'armes.\nFournissant les deux camps de chaque guerre et\nvendant leurs secrets. Ses clients ont fini par\ndecouvrir son double jeu et l'ont expédie dans\nun enfer d'ou l'on ne revient jamais.",

    # 8. American ninja (286)
    "An American assassin relying on ninja skills. Many\nconsidered him a joke at first, but he gradually\nbuilt his reputation in the criminal underworld as\na capable, precise killer. He came to the Bed of\nStyx driven by curiosity about Japan--the country\nwhere his fighting style originated.":
        "Tueur americain adepte du ninjutsu. D'abord pris\npour un clown, il s'est batit une solide reputation\nd'assassin chirurgical dans la pegre. Venu au Lit\ndu Styx par curiosite pour le Japon, berceau de\nson art du combat.",

    # 9. Conspiring terrorist (381)
    "A terrorist conspiring with a certain foreign\ncountry against Japan. He was captured when \nseeking asylum in return for top-secret intelligence. \nThe Public Security Intelligence Agency had to first\nascertain what information he had stolen, so they\nsent him to the Bed of Styx with a promise of\nreturn to normal custody when he reveals his \nsources. He's still not willing to talk.":
        "Terroriste complotant contre le Japon avec une\npuissance etrangere. Arrete alors qu'il demandait\nl'asile contre des secrets d'Etat. Les services\nde securite l'ont jete au Lit du Styx jusqu'a ce\nqu'il revele ses sources. Il garde le silence.",

    # 10. Legionnaire mercenary (398)
    "While his real name is unknown, he is said to be\nJapanese. He always detested humans and figured\nthat soldiering was the job for him; not only did\nhe get to kill people with impunity, but he got a\nsalary for it. He fought with armies all over the\nworld as a mercenary, joining in any conflict. But\nwhen he came to Japan, his father, deeply ashamed\nof his doings, handed him over to the Bed of Styx.":
        "Nom reel inconnu, sans doute japonais. Haisant les\nhommes, il a trouve sa voie comme mercenaire :\ntuer en toute impunite tout en etant paye. Apres\navoir fait le coup de feu aux quatre coins du globe,\nson propre pere, ecoeure, l'a livre au Lit du Styx\na son retour au Japon.",

    # 11. Asagiri license to kill (315)
    "Asagiri claims to have been issued a license to\nkill from the head of a certain superpower. He had\nseveral wealthy supporters in Japan, but ended up\nkilling all of them because they weren't showing\nhim enough respect. He fled to the Bed of Styx\nto avoid capture by the police.":
        "Asagiri pretend posseder un permis de tuer d'une\ngrande puissance. Soutenu par de riches mecenes au\nJapon, il les a tous massacres car ils manquaient\nde respect envers lui. Il s'est refugie au Lit du\nStyx pour echapper aux policiers.",

    # 12. Small village murderer (356)
    "Murdered all twenty inhabitants of a small village\nfor pure fun. Said to have made full use of his\ninnocent appearance to fool and trap his victims.\nThe authorities covered up the incident, worried\nthat the news of the mass slaughter would disrupt\npublic peace. Meanwhile, they shipped the murderer\noff to the Bed of Styx.":
        "A massacre les vingt villageois d'un hameau pour\nle plaisir. Utilisant son air innocent pour pieger\nses victimes. L'affaire a ete etouffee pour eviter\nla panique generale, et le boucher a ete expédie\nau Lit du Styx en grand secret.",

    # 13. Hospital director son (299)
    "Son of the director of a large hospital, he made a\nlot of money from illegal surgeries. With his knife\nskills, he is easily capable of slicing a man to\nribbons. He killed his father in a fit of rage and\ntook refuge in the Bed of Styx where money\ntranscends morals.":
        "Fils de directeur d'hopital, enrichi par des\noperations clandestines. Au scalpel, il decoupe\nun homme en lambeaux. Apres avoir egorge son pere\ndans un acces de rage, il a gagne le Lit du Styx\nou l'or supplante la morale.",

    # 14. Organ dealer cook (400)
    "Officially a cook, but also an organ dealer behind\nthe scenes. He is an imposing brute of a man who\nwas forced to join the Bed of Styx by the yakuza\nafter botching an organ extraction on a living\nyakuza member. At the Bed of Styx, he enjoys meals\nof questionable meats--making other competitors\nwonder about their source.":
        "Cuisinier de facade, trafiquant d'organes dans\nl'ombre. Ce colosse a ete jete au Lit du Styx par\nles yakuza apres avoir rate un prelevement sur un\ndes leurs encore en vie. Il s'y regale de viandes\ndouteuses... dont nul n'ose demander l'origine.",

    # 15. Berserk yakuza (354)
    "A normally quite harmless yakuza who turns into a\nrampaging beast when someone insults his dead\nmother. He made a vow to his mother that he would\nnever retreat, not even in death. Having killed\nsome of his colleagues who were making fun of his\nmother, he came to the Bed of Styx, expecting not\nto leave the cage alive.":
        "Yakuza d'ordinaire inoffensif devenant un fauve\nsi l'on insulte sa defunte mere. Ayant jure a sa\nmere de ne jamais reculer, il a massacre ses pairs\nqui se moquaient d'elle avant d'atterrir au Lit du\nStyx, pret a y mourir dans la cage.",

    # 16. Rich buffoon (303)
    "A buffoon with plenty of inherited money and\nmurderous urges. He is said to have spent quite an\namount on developing a special drug that makes his\nbody immune to any and all pain. In order to test\nhis newly attained invulnerability, he bought\nhis way into the Bed of Styx.":
        "Heritier fortuné aux pulsions meurtrieres. Il a\nenglouti une fortune pour creer une drogue qui le\nrend insensible a la douleur. Pour tester sa toute\nnouvelle invulnerabilite, il a paye pour entrer\nau Lit du Styx.",

    # 17. Crime writer (330)
    "This crime writer came close to winning a major\nliterary prize with his first work. Driven by his\ndesire to write realistic crime novels, he sought\nto experience the gruesome acts in person. Having\nkilled three people in real life, he is now writing\na novel while waiting for his matches at the Bed\nof Styx.":
        "Auteur de polars frole par un grand prix. Guide\npar la quete d'un realisme absolu, il a voulu vivre\nle meurtre en chair et en os. Apres 3 homicides,\nil redige son prochain roman entre deux combats\nsanglants au Lit du Styx.",

    # 18. Sumo rogue (333)
    "His career path started in the world of sumo but\nthen took a sudden turn. His raw power in the ring\nwas too much for opponents, and he ended up\nkilling three of them in matches. Banned for life\nfrom the sport, he ended up in the Bed of Styx\nwhere killing isn't considered a foul.":
        "Ancien lutteur de sumo banni a vie. Sa puissance\ndevastatrice a coute la vie a trois rivaux sur le\ndohyo. Sans avenir sportif, il s'est tourne vers\nle Lit du Styx, ou tuer ses adversaires n'a rien\nd'une faute.",

    # 19. Bosozoku leader (353)
    "A talented street fighter who used to lead a\nmotorcycle gang with several thousand members. He\nis so full of pride he cannot accept even a single\nloss. He abandoned the gang when he was defeated\nby an ordinary high-school kid. Now at the Bed of\nStyx, he seeks to become a completely defeated man\nor a truly invincible fighter.":
        "Ancien chef d'un gang de motards de milliers de\nmembres. Rongé par l'orgueil, il n'accepte aucun\nechec. Humilie par un simple lyceen, il a dissous\nson gang pour rejoindre le Lit du Styx, en quete\nde destruction ou d'invincibilite.",

    # 20. Sadistic SM (335)
    "Well-known in the world of S&M, his sadistic\ntendencies know no bounds. He is considered\na terrifying fiend who will not stop until his\nopponents are covered in blood and groaning in\npain. Entering the Bed of Styx was just another\nway for him to satisfy his desire to see others\nsuffer.":
        "Figure sadique dont la cruaute ne connait nulle\nlimite. Un monstre sans pitie qui ne s'arrete que\nlorsque son rival baigne dans son sang et hurle\nd'agonie. Le Lit du Styx est son terrain de jeu\nideal pour voir souffrir autrui.",

    # 21. Serial killer (361)
    "Suspected of committing serial murders in Japan\nbut never proven guilty, this assassin fled to\nHong Kong where he continued killing for money. A\ntrained professional, he is determined to protect\nhimself by all means, using dirty tricks whenever\nhe sees fit. Ended up at the Bed of Styx after an\nincident in Hong Kong.":
        "Soupconne de meurtres en serie au Japon, ce tueur\ns'est enfui a Hong Kong pour continuer a gage.\nProfessionnel pret a tout pour survivre, usant des\npires coups bas. Il a fini au Lit du Styx suite a\nun incident a Hong Kong.",

    # 22. Marriage fraudster (392)
    "An ex-martial artist and an infamous marriage\nfraudster, this charmer deceived over 100 women\nwith his sweet talk, eventually killing any\nvictims who tried to press charges against him. In\na way, his sweet talk served him well; a rich\nsponsor pays for his living expenses at the Bed of\nStyx, in exchange for regular updates on his fights.":
        "Ex-champion d'arts martiaux et escroc au mariage.\nIl a berne plus de 100 femmes par ses flatteries,\nassassinant celles qui voulaient porter plainte.\nSes talents de charmeur payent encore : une riche\nadmiratrice finance son sejour au Lit du Styx.",

    # 23. Collector (386)
    "Some people collect stamps or antiques, but\nTsuchikura's passion is skulls. Not animal skulls,\nthough; he is only interested in human ones. He\nreportedly has dozens in his private collection.\nSince no one was willing to sell him any, he began\nmaking his own. He joined the Bed of Styx because\nhe can acquire rare skulls from all over the world.":
        "Tsuchikura collectionne les cranes humains. Nul\nne voulant lui en vendre, il a decide de fabriquer\nles siens en tuant. Il est entre au Lit du Styx\ncar il espere y recolter des cranes rares venus\ndes quatre coins du monde.",

    # 24. Human hunter (380)
    "Gondo was a law-abiding hunter until one day he\nwas attacked by a man who had lost his way in\nthe mountains. He killed the man in self-defense,\nbut the experience awoke a new desire in him: to\nhunt the ultimate game, other humans. When his\nvillage caught on to what he was doing, they exiled\nhim to the Bed of Styx.":
        "Chasseur autrefois sans histoire, attaque un jour\npar un rodeur en montagne. L'ayant abattu en etat\nde legitime defense, l'acte a reveille en lui une\npassion pour la traque d'humains. Chasse de son\nvillage, il a ete banni au Lit du Styx.",

    # 25. Escaped convict (375)
    "An escaped convict who long evaded capture by\nassuming the identities of the people he killed.\nIn one year alone, he assumed seven different\nidentities. When cornered by police, he went on\na rampage, killing the officers. Realizing that he\ncould no longer show his face in society, he came\nto the Bed of Styx.":
        "Evade de prison ayant usurpe les identites de ses\nvictimes pour fuir. En un an, il a pris 7 noms.\nCerne par les forces de l'ordre, il a massacre\nles agents. Ne pouvant plus vivre en societe, il\na gagne le Lit du Styx.",

    # 26. Corrupt official (329)
    "Once a high-ranking government official, he\nruthlessly took bribes and amassed immense wealth.\nWhen some of his subordinates planned to blow the\nwhistle on his corruption, he had them killed.\nAfter the crimes came to light, he took his\nbillions and fled to the Bed of Styx.":
        "Haut fonctionnaire corrompu amasseur de fortunes.\nQuand ses subordonnes ont menace de le balancer,\nil les a fait assassiner. Sa traitrise revelee au\ngrand jour, il a fui au Lit du Styx avec son pactole.",

    # 27. Voyeur assassin (320)
    "Shibata was a very curious man. This incorrigible\nvoyeur developed a taste for murder after he was\ndiscovered in an act of voyeurism and killed the\nwoman to keep her quiet. He came to the Bed of\nStyx to watch other competitors fight, drawn by\nhis curiosity.":
        "Shibata, voyeur invetere, a developpe un gout pour\nle sang apres avoir poignarde une femme pour la\nfaire taire. Il est venu au Lit du Styx afin de\nvoir s'entretuer les gladiateurs, toujours guide\npar sa curiosite malsaine.",

    # 28. Bicycle thief (378)
    "Stealing 3,000 bicycles is not a good thing, but\nit's by no means a violent crime. But it was just\npart of Inagaki's training. The constant biking\ngave him strong legs, which he then used in fights\nagainst rival gangs. He was forced to enter the\nBed of Styx by a loan shark from whom he had\nborrowed a huge amount of money.":
        "Voler 3 000 velos faisait partie de l'entrainement\nd'Inagaki. Pedaler jour et nuit lui a donne des\njambes d'acier pour le combat de rue. Endette\njusqu'au cou, un usurier l'a force a combattre au\nLit du Styx pour rembourser.",

    # 29. Fallen hero (330)
    "A young man who was known as a local hero,\ndefending his community from thugs and criminals.\nHowever, after accidentally killing someone during\na fight, he was overwhelmed by guilt and entered\nthe Bed of Styx as self-imposed punishment,\nseeking death in the ring.":
        "Ancien heros local qui defendait son quartier des\nvauriens. Rongé par les remords apres avoir tue\nun jeune par accident lors d'une rixe, il est\nentre au Lit du Styx pour y trouver la mort en\nguise d'expiation.",

    # 30. Forger (343)
    "A former martial artist who made a career as a\nforger. He used his skills to forge valuable\nantiques and artwork, amassing a small fortune.\nWhen his clients began to catch on to his deceit,\nhe killed them to protect his secrets. He came to\nthe Bed of Styx after running out of people to\nkill.":
        "Ancien combattant devenu faussaire de genie. Il a\namasse une fortune en copiant des antiquites rares.\nQuand ses commanditaires ont flaire la supercherie,\nil les a assassines pour garder son secret, avant\nd'atterrir au Lit du Styx.",

    # 31. Asagiri v2 (315)
    "Asagiri claims to have been issued a license to\nkill. He freely admits to being involved in\nseveral high profile murders, but does not\nconsider it a crime. As for the secret government\nagencies, they deny that any such license has been\ngranted to him, or that they even exist. It's easy\nto see why he ended up here.":
        "Asagiri pretend posseder un permis de tuer.\nIl avoue sans gene plusieurs meurtres retentissants\nsans les juger criminels. Les agences secretes\nnient toutefois lui avoir delivre un tel permis,\nou meme exister. On comprend aisement comment il a\natterri ici.",

    # 32. Tsuji v2 (356)
    "Murdered all twenty inhabitants of a small village\n15 years ago. There were no witnesses or even\ncircumstantial evidence, so it was not possible\nfor the prosecutor to bring charges against him\nbefore the statute of limitations. Certain he was\noff the hook, Tsuji confessed it all to the police\ndetective in charge, who made sure he'd never walk\nfree again.":
        "A massacre les 20 habitants d'un village il y a\n15 ans. Faute de temoins et de preuves, aucune\npoursuite n'avait pu aboutir avant prescription.\nPensant etre tire d'affaire, Tsuji a tout avoue a\nl'inspecteur en charge, qui a veille a ce qu'il ne\nsoit plus jamais libre.",

    # 33. Doctor v2 (299)
    "Son of the director of a large hospital, he made a\npastime of slipping deadly drugs into the IV drips\nof random patients. He was confident no one could\never prove his guilt, but among the families of\nhis victims was a Bed of Styx patron who knew of\nanother way to bring the killer doctor to justice.":
        "Fils d'un patron d'hopital, il injectait des poisons\ndans les perfusions de patients au hasard. Sur de\nsa parfaite impunite, il ignorait que parmi les\nproches des defunts se trouvait un parrain du Lit du\nStyx bien decide a lui faire payer.",

    # 34. Cook v2 (400)
    "Officially a cook, but also an organ dealer behind\nthe scenes. To conceal evidence, he'd cook all the\nparts he couldn't sell and serve them to restaurant\ncustomers, until he discovered a hunger for human\nflesh and this lust became his primary motivation\ninstead. He didn't kill anyone, but the yakuza\nhad enough of him gobbling up all the merchandise\nand gave him a one-way ticket to the Bed of Styx.":
        "Cuisinier de facade et trafiquant d'organes.\nPour detruire les preuves, il cuisinait les restes\npour ses clients, jusqu'a developper un appetit pour\nla chair humaine. Sans avoir tue lui-meme, les yakuza\nont fini par se lasser de le voir devorer le stock\net l'ont expedie tout droit au Lit du Styx.",

    # 35. Chidori v2 (354)
    "A normally quite harmless yakuza who turns into a\nsly and bloodthirsty murderer after a few drinks.\nHis split personality was exploited by his family,\nwho'd get him drunk and send him off to do dirty\nwork. The police were confused when they brought\nin the sober Chidori for questioning, but when\nlegal issues are a problem, the Bed of Styx is\nthe answer.":
        "Yakuza doux devenant un fauve sanguinaire apres\nquelques verres. Sa double personnalite etait\nexploitee par son clan, qui le saoulait pour les\nsales besognes. La police ne comprenait rien face\na un Chidori sobre, mais la justice du Lit du Styx\na vite regle la question.",

    # 36. Buffoon v2 (303)
    "A buffoon with plenty of inherited money and\nmurderous tendencies. Every now and then he'd\nkidnap someone and bring them back to his mansion\nwhere he'd kill them at his leisure, paying off\nthe police so they'd ask no questions. Finally,\npleas for justice reached one of the patrons of\nthe Bed of Styx...":
        "Heritier fortuné aux pulsions sanguinaires.\nIl enlevait des gens dans son manoir pour les\ntuer a loisir, achetant le silence des flics.\nLes appels a l'aide des familles ont fini par\ntoucher l'un des parrains du Lit du Styx...",

    # 37. Writer v2 (330)
    "This crime writer came close to winning a major\nliterary award for his mystery novels and made\nseveral appearances on TV. Then one day, someone\nwrote anonymously to local newspapers that he'd\nbeen testing out his fictional ideas for the\nperfect crime in reality. The day after the story\nwas published, Doyle mysteriously vanished.":
        "Auteur de polars frole par un grand prix,\nstar de la television. Un jour, une lettre anonyme\na revele aux journaux qu'il testait ses crimes\nparfaits dans la vraie vie. Des le lendemain de\nla parution, Doyle a mysterieusement disparu.",

    # 38. Sumo v2 (333)
    "His career path started in the world of sumo but\ntook him to national politics. Certain politicians\nmade quite a lot of money through his match-fixing,\nbut his luck ran out when the media found out\nabout his shady dealings. He faked his own death\nand disappeared, but now here he is, making a new\nname for himself in the Bed of Styx.":
        "Passe du sumo aux coulisses du pouvoir politique.\nDes elus se sont enrichis grace a ses matches truques,\nmais la presse a decouvert le pot aux roses. Apres\navoir simule sa mort, il a disparu pour refaire\nsa vie dans l'arene du Lit du Styx.",

    # 39. Yanai v2 (353)
    "A talented street fighter who used to lead a\nmotorcycle gang, but his underlings soon had\nenough of his explosive character and left. Yanai\nhoped to be scouted by the yakuza, and he grew\nincreasingly angry when they continued to ignore\nhim. When his one-man raids crushed several local\nyakuza families, they arranged to have him sent to\nthe Bed of Styx.":
        "Bagarreur d'elite jadis a la tete d'un gang,\nabandonne par ses hommes a cause de sa rage.\nRejete par les yakuza qu'il revait d'integrer,\nYanai s'est venge en ecrasant plusieurs clans a\nlui tout seul. Ces derniers ont vite complote\npour l'expedier au Lit du Styx.",

    # 40. SM v2 (335)
    "Well-known in the world of S&M, his sadistic\ntendencies only grew stronger as he aged. His need\nfor ever-stronger stimulation eventually led to\npresumably accidental deaths of his masochistic\npartners. He got off with a suspended sentence,\nbut the aggrieved families of his victims pulled\nsome strings to banish him to the Bed of Styx.":
        "Celebre dans le milieu S&M, son sadisme s'est\nexacerbe avec l'age. Sa quete d'emotions fortes a\nprovoque la mort de plusieurs partenaires.\nCondamne a du sursis, les familles des victimes\nont use de leurs relations pour le bannir ici.",

    # 41. Cannibal v2 (361)
    "Suspected of committing serial murders in Japan\nbut never officially charged, as the crimes could\nnot be proved with the bodies eaten. Not even a\nspeck of blood could be found--he made sure to\nquickly do the dishes after each meal. The\nvictims' families had no doubt as to his guilt,\nhowever, and saw to it that this criminal was\ntaken off the streets for good.":
        "Soupconne de meurtres en serie sans condamnation,\nles corps etant devores. Pas la moindre trace de\nsang : il nettoyait tout apres chaque repas.\nPersuadees de sa culpabilite, les familles ont\nfait en sorte que ce monstre quitte la societe\npour toujours.",

    # 42. Seducer v2 (392)
    "An ex-martial artist and an infamous marriage\nfraudster that targeted women who had boyfriends.\nHe'd seduce them by feeding them lies about their\nmen being cheaters. Outraged boyfriends would meet\nface-first with his fists. Then he'd use wile and\nguile to get money and favors from the women who\nbelieved he was going to marry them. All was going\nwell until he picked a yakuza's sweetheart...":
        "Escroc ciblant les femmes en couple. Il inventait\ndes tromperies pour briser les menages et rossait\nles compagnons revoltes. Il extorquait ensuite argent\net faveurs a ses proies promises au mariage. Tout\nallait bien jusqu'au jour ou il a seduit la femme\nd'un haut gradé des yakuza...",

    # 43. Tsuchibori v2 (386)
    "Some people collect stamps or antiques, but\nTsuchibori has a passion for cross-sections of\nhuman bodies. He's got ways to keep his mutilated\nvictims alive. Even though he was caught red-\nhanded, Tsuchibori did not actually commit murder,\nso he couldn't be sent to death row. This further\ninfuriated the families of the victims his cruelty\ndrove to insanity, so they had him \"collected.\"":
        "Tsuchibori collectionne des coupes anatomiques\nhumaines. Il maintenait ses victimes en vie.\nPris en flagrant delit mais sans homicide formel,\nil a echappe a la peine de mort. Les familles\ndes victimes, devenues folles de douleur, ont fini\npar le faire 'enlever' pour de bon.",

    # 44. Hunter v2 (380)
    "Gondo was a law-abiding hunter until one day he\nwas accidentally wounded by a poacher. From then\non he single-mindedly tracked down poachers, which\nwould have been commendable, were it not for the fact\nthat they would often end up getting shot--\"mistaken \nfor a deer\" or \"hit by a stray bullet,\" as Gondo put it.\nBefore a case could be brought against him, he\nsuddenly vanished...":
        "Chasseur autrefois sans histoire, blesse par\nun braconnier. Des lors, il s'est mis a traquer\nles braconniers qui finissaient souvent abattus,\n'pris pour un cerf' selon ses dires.\nAvant qu'un proces ne s'ouvre contre lui, il a\nmysterieusement disparu...",

    # 45. Mask v2 (375)
    "An escaped convict who long evaded capture by\nassuming the identity of his victims. Whenever it\nseemed like the police were on his track, he'd\nkill again, mutilate the body beyond recognition,\nand assume a new identity. But even he realized\nhe could not go on like this forever, so he fled\nto the Bed of Styx. Used to concealing his\nidentity, he hides his face behind a mask.":
        "Evade ayant longtemps fui en usurpant l'identite\nde ses victimes. Senteur de police proche, il tuait\na nouveau et mutilait le cadavre pour reprendre un\nautre nom. Conscient de l'impasse, il a fui au Lit\ndu Styx ou il dissimule son visage sous un masque.",

    # 46. Coup v2 (329)
    "Once a high-ranking government official, he\nruthlessly eliminated political opponents by any\nmeans available. When his wrongdoings were\nexposed, he attempted to seize power through a\nmilitary coup d'etat, which fortunately failed.\nHe fled to Japan, but was captured by the local\nChinese community and interned in the Bed of Styx.":
        "Haut fonctionnaire ayant liquide ses opposants par\ntous les moyens. Ses crimes devoiles, il a tente un\ncoup d'Etat militaire qui a echoue. Réfugie au\nJapon, il a ete capture par la diaspora chinoise\net enferme au Lit du Styx.",

    # 47. Shibata v2 (320)
    "Shibata was a very curious man. This incorrigible\npeeping tom would still have led a more or less\nnormal life if his curiosity hadn't led him to\ninadvertently witness certain activities of the\ncriminal underworld. Given a choice between death\nand the Bed of Styx, he chose the latter,\na decision he probably now regrets.":
        "Shibata etait un voyeur invetere. Il aurait mene\nune vie ordinaire si sa curiosite ne l'avait pas\npousse a espionner les activites de la pegre.\nPlace devant le choix entre la mort et le Lit du\nStyx, il a choisi l'arene, ce qu'il regrette.",

    # 48. Bike v2 (378)
    "Stealing 3,000 bicycles is not a good thing, but\nit's not the kind of crime that lands you in the\nBed of Styx. Except this particular bicycle thief\nalso happened to murder the boss of an opposing\ncriminal organization, and then to add insult to\ninjury, he stole his bike too. The police dropped\nthe case due to insufficient evidence, but the\nvictim's underlings had other plans.":
        "Voler 3 000 velos ne mene pas d'ordinaire au Lit\ndu Styx. Mais ce voleur a aussi assassine le chef\nd'un clan rival, lui derobant son velo au passage.\nL'enquete close faute de preuves, les hommes du\ndefunt ont arrange sa disparition vers l'arene.",

    # 49. Hero v2 (330)
    "A young man who was known as a local hero,\ndefending the weak from thugs and perverts. What\nthe public never found out was that when there\nwere no villains to fight, their hero would\nbrutally assault innocent passers-by, run away,\nthen beat up a different person and frame them as\nthe assailant. Now, justice has caught up to him.":
        "Jeune homme salue comme un heros local face aux\nmalfrats. Quand les voyous manquaient, il agressait\ndes innocents, s'enfuyait puis tabassait un tiers\npour l'accuser du crime. La justice a fini par le\nrattraper pour le plonger dans l'arene.",

    # 50. Fortune v2 (343)
    "A former martial artist who made a career as a\nfortune-teller renowned for accuracy. He did more\nthan just fortune-telling though, effectively\nbrainwashing his customers, ordering them to kill\nthe people they held a grudge against. He used to\nrevel in the power he had over others' lives, till\nsomeone saw through his tricks and sent him here.":
        "Ancien lutteur devenu voyant repute. Il lavait le\ncerveau de ses clients en leur ordonnant de tuer\nleurs rivaux. Grise par ce pouvoir de vie et de\nmort, un client clairvoyant a perce son manege et\nl'a fait expedier ici.",

    # extra.bin_c (4 strings)
    "*For online play, you need to be signed in to\nyour PlayStation~Network account.\n\nFor more information about PlayStation~Network,\nsee the PlayStation\x7f3 user's manual or\nthe following website:\n\nhttps://www.playstationnetwork.com/home":
        "*Pour jouer en ligne, connectez-vous a votre\ncompte PlayStation~Network.\n\nPour en savoir plus sur PlayStation~Network,\nconsultez le manuel PlayStation\x7f3 ou le site :\n\nhttps://www.playstationnetwork.com/home",

    "\x01*For online play, you need to be signed in to\nyour account for PlayStation~Network.\n\nFor more information about PlayStation~Network,\nsee the PlayStation\x7f4 user's guide or\nthe following website:\n\nhttps://www.playstationnetwork.com/home":
        "\x01*Pour le jeu en ligne, connectez-vous a\nvotre compte PlayStation~Network.\n\nPour en savoir plus sur PlayStation~Network,\nconsultez le guide PlayStation\x7f4 ou le site :\n\nhttps://www.playstationnetwork.com/home",

    "Special Item Packs (2/2)\n\nIf your PlayStation\x7f3 is connected to\nthe network, you will be prompted about installing\nspecial item pack updates if one is available\nwhen you boot Yakuza 0.\nIf an update fails for any reason, you can\nmanually download it by going to Online Mode and\nselecting Manual Update.":
        "Packs d'objets speciaux (2/2)\n\nSi votre PlayStation\x7f3 est connectee au reseau,\nla mise a jour de packs d'objets vous sera\nproposee au demarrage de Yakuza 0.\nEn cas d'echec, telechargez-la manuellement via\nMode en ligne puis Mise a jour manuelle.",

    "\x01Special Item Packs (2/2)\n\nIf your PlayStation\x7f4 is connected to\nPlayStation~Network, you will be prompted about\ninstalling special item pack updates if one is\navailable when you boot Yakuza 0.":
        "\x01Packs d'objets speciaux (2/2)\n\nSi votre PlayStation\x7f4 est connectee au\nPlayStation~Network, les packs d'objets vous\nseront proposes au demarrage de Yakuza 0.",
}

def translate_exact_bytes(data_bytes):
    out = bytearray(data_bytes)
    out = bytearray(bytes(out).replace(b'\xc7', b'C'))

    for en, fr in PAUSE_TRANSLATIONS.items():
        en_b = en.encode('latin1')
        fr_clean = fr.replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')
        fr_b = fr_clean.encode('latin1')
        assert len(fr_b) <= len(en_b), f"Length error: {len(fr_b)} > {len(en_b)} for {repr(en)}"
        pad = b'\x00' * (len(en_b) - len(fr_b))
        rep_b = fr_b + pad

        pos = 0
        while True:
            idx = out.find(en_b, pos)
            if idx == -1:
                break
            out[idx : idx + len(en_b)] = rep_b
            pos = idx + len(en_b)

    return bytes(out)

def repack_par(orig_bytes, file_replacements={}):
    magic, unkA, unkB, unkC = struct.unpack('>4I', orig_bytes[:16])
    assert magic == 0x50415243
    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', orig_bytes[16:32])
    name_offset = 32 + folder_count * 64
    
    entries = []
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = orig_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')
        e_off = file_table_offset + i * 32
        entry_meta = list(struct.unpack('>8I', orig_bytes[e_off : e_off + 32]))
        flags, u_sz, c_sz, f_off = entry_meta[:4]
        raw_file = orig_bytes[f_off : f_off + c_sz]
        entries.append({
            'idx': i,
            'name': name,
            'entry_offset': e_off,
            'entry_meta': entry_meta,
            'flags': flags,
            'u_sz': u_sz,
            'c_sz': c_sz,
            'f_off': f_off,
            'data': raw_file
        })
    
    sorted_entries = sorted(entries, key=lambda e: e['f_off'])
    first_file_offset = sorted_entries[0]['f_off']
    rebuilt = bytearray(orig_bytes[:first_file_offset])
    curr_off = first_file_offset
    
    for item in sorted_entries:
        name = item['name']
        if name in file_replacements:
            n_flags, n_u_sz, n_c_sz, n_data = file_replacements[name]
        else:
            n_flags, n_u_sz, n_c_sz, n_data = item['flags'], item['u_sz'], item['c_sz'], item['data']
        
        aligned_off = (curr_off + 63) & ~63
        if aligned_off > len(rebuilt):
            rebuilt.extend(b'\x00' * (aligned_off - len(rebuilt)))
        
        new_file_offset = len(rebuilt)
        rebuilt.extend(n_data)
        curr_off = len(rebuilt)
        struct.pack_into('>4I', rebuilt, item['entry_offset'], n_flags, n_u_sz, n_c_sz, new_file_offset)
    
    return bytes(rebuilt)

def main():
    pause_path = 'release_gog/data/pausepar_e/pause.par'
    bak_path = pause_path + '.pre_pause_complete.bak'
    if not os.path.exists(bak_path):
        print(f"[+] Backing up {pause_path}...")
        shutil.copyfile(pause_path, bak_path)

    with open(pause_path, 'rb') as f:
        orig_bytes = f.read()

    files = parse_par(orig_bytes)
    replacements = {}

    target_files = [
        'tougijyo_participant.bin_c',
        'extra.bin_c'
    ]

    for fn in target_files:
        if fn not in files:
            continue
        flags, u_sz, c_sz, data = files[fn]
        is_comp = bool(flags & 0x80000000)
        decomp = decompress_sllz(data) if is_comp else data
        trans_decomp = translate_exact_bytes(decomp)
        if is_comp:
            comp = compress_sllz(trans_decomp)
            replacements[fn] = (0x80000000, len(trans_decomp), len(comp), comp)
            print(f"  - Translated & recompressed {fn} (u_sz={len(trans_decomp)}, c_sz={len(comp)})")
        else:
            replacements[fn] = (flags, len(trans_decomp), len(trans_decomp), trans_decomp)
            print(f"  - Translated uncompressed {fn} (sz={len(trans_decomp)})")

    print("[+] Repacking pause.par...")
    new_pause = repack_par(orig_bytes, replacements)
    with open(pause_path, 'wb') as f:
        f.write(new_pause)
    print(f"[+] Successfully wrote {pause_path} ({len(new_pause)} bytes)!")

if __name__ == '__main__':
    main()
