# -*- coding: utf-8 -*-
"""
translate_msg_phase4.py

Translates the remaining 8 English .msg files in release_gog/data/wdr_par_c/wdr.par:
1. uid01070969.msg (Blackjack minigame)
2. uid01070994.msg (Cee-lo minigame)
3. uid01261727.msg (Kamoji Rush style master training)
4. uid01640008.msg (Hostess training: Yuki)
5. uid0164000d.msg (Hostess training: Ai)
6. uid0164000e.msg (Hostess training: Saki)
7. uid0164000f.msg (Hostess training: Hibiki)
8. uid01640010.msg (Hostess training: Chika)

All files maintain bit-exact file lengths with valid internal pointer tables.
"""

import os
import sys
import shutil
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par

BLACKJACK_TRANSLATIONS = {
    '\tiWelcome to the blackjack table.': '\tiBienvenue au blackjack.',
    "Okay, let's begin.": "Commençons.",
    'Welcome to the blackjack table. Would you like\r\nto play against the house, one-on-one?': (
        "Bienvenue au blackjack. Souhaitez-vous jouer\r\nseul contre la banque ?"
    ),
    'Please select "Bet" or "Re-Bet" to place a wager.': 'Choisissez "Miser" ou "Remiser" pour parier.',
    'Here are your cards.': 'Voici vos cartes.',
    "I pulled a green card, so I'll shuffle the deck.": "Carte verte tirée, je mélange le sabot.",
    'You seem to be short on chips. Please come back again soon.': "Vous manquez de jetons. Revenez nous voir.",
    "It's your turn. What would you like to do?": "À vous. Que souhaitez-vous faire ?",
    "It's a bust. What a shame.": "Vous sautez. Quel dommage.",
    "It's the dealer's turn. I'll reveal my cards.": "Au croupier. Je dévoile mes cartes.",
    "The total is less than 17, so I'm drawing a card.": "Moins de 17, je tire une carte.",
    "The dealer's total is 17.": "Le croupier a 17.",
    "The dealer's total is 18.": "Le croupier a 18.",
    "The dealer's total is 19.": "Le croupier a 19.",
    "The dealer's total is 20.": "Le croupier a 20.",
    "The dealer's total is 21.": "Le croupier a 21.",
    'The dealer has a blackjack.': 'Le croupier a un blackjack.',
    'The dealer busted.': 'Le croupier saute.',
    "The dealer's open card is an ace. It could be a blackjack.": "La carte visible est un as. Risque de blackjack.",
    "It wasn't a blackjack. Let's continue with the game.": "Pas de blackjack. Continuons la partie.",
    'You have a blackjack! Congratulations, sir.': 'Blackjack ! Félicitations, monsieur.',
    'However, I do as well. Better luck next time.': 'Moi de même. Partie nulle.',
    'We look forward to seeing you again.': 'Au plaisir de vous revoir.',
    'You seem to be short on chips. Please come again soon.': 'Plus assez de jetons. Revenez vite nous voir.',
    "(The item's effect has worn off.)": "(L'effet de l'objet a disparu.)",
    'You won one game. The maximum bet increased to 300.': '1 victoire. Mise maximale portée à 300.',
    'You won two games in a row. The maximum bet increased\r\nto 500.': '2 victoires de suite. Mise max portée\r\nà 500.',
    'You won three games in a row. The maximum bet increased\r\nto 1,000.': '3 victoires de suite. Mise max portée\r\nà 1 000.',
    'You won one game. The maximum bet increased to 3,000.': '1 victoire. Mise maximale portée à 3 000.',
    'You won two games in a row. The maximum bet increased\r\nto 5,000.': '2 victoires de suite. Mise max portée\r\nà 5 000.',
    'You won three games in a row. The maximum bet increased\r\nto 10,000.': '3 victoires de suite. Mise max portée\r\nà 10 000.',
}

CEELO_TRANSLATIONS = {
    'The banker got a 6, winning the same amount as the stake.': "Le banquier a fait 6 et gagne la mise.",
    'The banker rolled trips, winning three times the stake.': "Le banquier a fait un brelan et gagne 3x.",
    'The banker rolled ace out, winning five times the stake.': "Le banquier a fait 1-1-1 et gagne 5x.",
    'The banker rolled 4-5-6, winning two times the stake.': "Le banquier a fait 4-5-6 et gagne 2x.",
    'The banker got a 1, losing the same amount as the stake.': "Le banquier a fait 1 et perd la mise.",
    'The banker missed the pot, losing the same amount as\r\nthe stake.': "Le banquier a raté le pot et perd sa mise.",
    'The banker did not roll a point, losing the same amount as\r\nthe stake.': "Le banquier n'a pas fait de point et perd.",
    'The banker rolled 1-2-3, losing two times the stake.': "Le banquier a fait 1-2-3 et perd 2x.",
    'The banker rolled 6-3-4, winning two times the stake.': "Le banquier a fait 6-3-4 et gagne 2x.",
    "You got a 6 as the banker, winning the same amount as\r\neveryone's stake.": "Comme banquier, vous faites 6 et gagnez les mises.",
    "You rolled trips as the banker, winning three times\r\neveryone's stake.": "Comme banquier, brelan ! Vous gagnez 3x les mises.",
    "You rolled ace out as the banker, winning five times\r\neveryone's stake.": "Comme banquier, 1-1-1 ! Vous gagnez 5x les mises.",
    "You rolled 4-5-6 as the banker, winning two times\r\neveryone's stake.": "Comme banquier, 4-5-6 ! Vous gagnez 2x les mises.",
    "You got a 1 as the banker, losing the same amount as\r\neveryone's stake.": "Comme banquier, vous faites 1 et perdez les mises.",
    'You missed the pot as the banker, losing the same amount\r\nas the stake.': "Comme banquier, vous ratez le pot et perdez.",
    "You did not roll a point as the banker, losing the same\r\namount as everyone's stake.": "Comme banquier, aucun point marqué : vous perdez.",
    "You rolled 1-2-3 as the banker, losing two times everyone's\r\nstake.": "Comme banquier, 1-2-3 ! Vous perdez 2x les mises.",
    'You rolled 6-3-4 as the banker, winning two times the stake.': "Comme banquier, vous faites 6-3-4 et gagnez 2x.",
    'You rolled trips, winning three times the stake.': "Brelan obtenu ! Vous gagnez 3x votre mise.",
    'You rolled ace out, winning five times the stake.': "1-1-1 obtenu ! Vous gagnez 5x votre mise.",
    'You rolled 4-5-6, winning two times the stake.': "4-5-6 obtenu ! Vous gagnez 2x votre mise.",
    'You missed the pot, losing the same amount as the stake.': "Dés hors du pot. Vous perdez votre mise.",
    'You did not roll a point, losing the same amount as\r\nthe stake.': "Aucun point marqué. Vous perdez votre mise.",
    'You rolled 1-2-3, losing two times the stake.': "1-2-3 obtenu ! Vous perdez 2x votre mise.",
    "You beat the banker's roll, winning the same amount as\r\nthe stake.": "Vous battez le banquier et gagnez la mise.",
    "You lost to the banker's roll, losing the same amount as\r\nthe stake.": "Vous perdez contre le banquier et la mise.",
    "You tied with the banker's roll, so there is no change in\r\nthe stake.": "Égalité avec le banquier : mise conservée.",
    'You rolled 6-3-4, winning two times the stake.': "6-3-4 obtenu ! Vous gagnez 2x votre mise.",
    'You beat all the other players.': 'Vous battez tous les joueurs.',
    'You earned points in this game.': 'Vous remportez des points.',
    'You lost points in this game.': 'Vous perdez des points.',
    'You lost to all the other players.': 'Vous perdez face aux joueurs.',
    'You tied with all the other players.': 'Égalité avec tous les joueurs.',
    'There is no change to your points.': 'Aucun changement de points.',
    'Waiting for other players to finish wagering.': "En attente des mises des autres joueurs.",
    'Everyone has had their turn as the banker. Ending game.': "Tous les tours de banque sont finis. Fin du jeu.",
    'You have no more tags to bet. Ending game.': "Vous n'avez plus de jetons. Fin de partie.",
    'Another player has no more tags to bet. Ending game.': "Un joueur n'a plus de jetons. Fin de partie.",
}

KAMOJI_TRANSLATIONS = {
    "Whoa there, mister. A gun's taking things a bit too far.": (
        "Doucement, mon vieux. Une arme, c'est aller un peu trop loin."
    ),
    "Close, but no cigar. If you want me dead, put together\r\nanother 100 million yen and try again. I'll take you on\r\nanytime.": (
        "Pas loin, mais raté. Si tu me veux mort, réunis encore\r\n100 millions de yens et retente ta chance quand tu veux."
    ),
    "Close, but no cigar. Scrape together another 100 million yen\r\nand try again if you want.": (
        "Pas loin, mais raté. Réunis encore 100 millions de yens\r\net retente ta chance si tu veux."
    ),
    "Kiryu-san!?": "Kiryu-san !?",
    "I know you can hear me! I'm talking to you!": "Je sais que tu m'entends ! C'est à toi que je parle !",
    "...You knew?": "...Tu savais ?",
    "Hey! It's the guy who was fixing to sell that sword.": "Hé ! C'est le gars qui voulait vendre ce katana.",
    "I lost a lot of money thanks to you. How are you going to\r\nmake this right?": (
        "J'ai perdu un paquet d'argent par ta faute.\r\nComment comptes-tu arranger ça ?"
    ),
    "That's why you sent a guy at me with a gun? Too bad it\r\ndidn't work out for you.": (
        "C'est pour ça que tu m'as envoyé un tireur ?\r\nDommage pour toi, ça a raté."
    ),
    "You really get on my nerves... Fine, I'll just have to take\r\ncare of you myself.": (
        "Tu me tapes sur les nerfs... Très bien, je vais devoir\r\nm'occuper de toi moi-même."
    ),
    "What are you waiting for, then? I've spent enough time\r\ndancing around. Punching someone would be great right now.": (
        "Qu'est-ce que tu attends ? J'ai assez esquivé comme ça.\r\nDonner quelques coups de poing me fera le plus grand bien."
    ),
    "Don't try to stop me, Kamoji. This guy's got it coming.": (
        "Ne me retiens pas, Kamoji. Il l'a bien cherché."
    ),
    "Wasn't going to! Hope you gives him his just dessert!\r\nNow you can put all you've learned to the test!": (
        "Pas question ! Corrige-le bien comme il faut !\r\nMontre-lui tout ce que tu as appris !"
    ),
    "To completely pulverize the enemy, you gots to evade all\r\ntheir attacks real smooth-like!": (
        "Pour démolir l'ennemi, tu dois esquiver toutes ses\r\nattaques avec un maximum de fluidité !"
    ),
    "Dance out of their way, then smash their face in to your\r\nheart's content! Anyone not a customer gets no mercy from\r\nme!": (
        "Esquive ses assauts, puis fracasse-lui le portrait\r\ntant que tu veux ! Pas de pitié pour les intrus !"
    ),
    "You learned the Essence of Relentless Barrage.\r\nExploit a gap in the enemy's defenses to unleash a combo\r\nattack. This technical move also incorporates feints. Press\r\n<Sign:1> near a frightened enemy.": (
        "Vous apprenez l'Essence du déluge implacable.\r\nProfitez d'une faille pour déclencher un combo redoutable\r\nintégrant des feintes. Appuyez sur <Sign:1> près d'un\r\nennemi effrayé."
    ),
    "Got it. You just watch.": "Compris. Regarde bien.",
    "You're a good teacher, Kamoji. I'm glad you made me your\r\napprentice. But I'm afraid I have to call it quits on the\r\npunchout game after this.": (
        "Tu es un bon maître, Kamoji. Content d'avoir été ton\r\napprenti. Mais je dois arrêter ce jeu d'esquive\r\naprès tout ça."
    ),
    "Kiryu-san...": "Kiryu-san...",
    "Let's see if you can punch me out before I flatten you!": (
        "Voyons si tu me touches avant que je te mette K.-O. !"
    ),
    "What do you think!? The guy was pretty quick, but you still\r\nsliced him up good!": (
        "Alors, qu'en penses-tu !? Le gars était rapide, mais\r\ntu l'as bien tailladé !"
    ),
    "I was hoping the sword could slice him in two. I'm still\r\nnot really convinced. Mind if I mull it over a bit more?": (
        "J'espérais trancher ce gars en deux. Pas très convaincu.\r\nJe peux y réfléchir encore un peu ?"
    ),
    "Uh, sure! It's a big purchase, so take your time.": (
        "Euh, bien sûr ! C'est un gros achat, prenez le temps."
    ),
    "You think that blade's really enchanted, Kiryu-san?": (
        "Tu crois que ce katana est vraiment magique, Kiryu-san ?"
    ),
    "Who knows? I'm just happy to be in one piece.": (
        "Qui sait ? Je suis déjà bien content d'être entier."
    ),
    "When you go up against a katana, it don't matter if it's\r\nenchanted or not. You dodge, or you get cut in half.": (
        "Face à un katana, enchanté ou non, c'est pareil.\r\nSoit tu esquives, soit tu finis coupé en deux."
    ),
    "I guess so.": "C'est vrai.",
    "You can evade during the motion leading up to a <Sign:6>\r\nguard stance. Press the button at the right time to evade\r\nenemy attacks.": (
        "Vous pouvez esquiver en passant en garde <Sign:6>.\r\nAppuyez au bon moment pour éviter les attaques ennemies."
    ),
    "Don't let that katana get to you, Kiryu-san! Ten million yen\r\nis a big loss to suffer, but get back on your feet and try\r\nagain!": (
        "Te laisse pas abattre, Kiryu-san ! 10 millions perdus,\r\nc'est dur, mais remets-toi en selle et retente !"
    ),
    "I couldn't cut him down. Is this blade really enchanted?": (
        "Je n'ai pas pu le toucher. Ce katana est vraiment magique ?"
    ),
    "Let's talk about this, Kabu-san. I don't think this is\r\ngoing to be a good purchase.": (
        "Parlons-en, Kabu-san. Je ne pense pas que ce soit\r\nun bon investissement."
    ),
    "Let's talk about this, Kabu-san. I don't think this is\r\ngoing to work out.": (
        "Parlons-en, Kabu-san. Je ne pense pas que ce soit\r\nune bonne idée d'acheter ça."
    ),
    "So your name's Kiryu, huh? Well thanks to you, I just lost\r\nout on a big payday.": (
        "Alors tu t'appelles Kiryu ? Grâce à toi, je viens de\r\nperdre un gros paquet de fric."
    ),
    "You're blaming me for your shady business deal going bust?\r\nGet a life.": (
        "Tu me reproches l'échec de tes magouilles ?\r\nTrouve-toi une vie."
    ),
    "Tch. You'll get yours.": "Tch. Tu paieras pour ça.",
    "Was that really an enchanted katana, Kiryu-san?": (
        "C'était vraiment un sabre magique, Kiryu-san ?"
    ),
    "No. In fact, it had mostly lost its edge. He was probably\r\njust hyping it up to make a sale.": (
        "Non, il était même complètement émoussé. Il baratinait\r\njuste pour réussir à le vendre."
    ),
    "No. In fact, it had mostly lost its edge. He was probably\r\njust trying to get a better price for that junk.": (
        "Non. Il était complètement émoussé. Il cherchait\r\njuste à faire monter le prix de cette camelote."
    ),
    "I had a feeling. Who can afford to slap down ten million\r\nlike that anyway?": (
        "Je m'en doutais. Qui peut claquer 10 millions comme ça,\r\nde toute façon ?"
    ),
    "I had a feeling. Who can afford to slap down ten million\r\nlike that, anyway? Must have his priorities all wrong.": (
        "Je m'en doutais. Qui peut claquer 10 millions comme ça,\r\nde toute façon ? Faut vraiment être à côté de ses pompes."
    ),
    "Maybe. Just shows we're not likely to get any takers for the\r\n100 million yen course.": (
        "Peut-être. Preuve qu'on ne trouvera pas de client pour\r\nle stage à 100 millions."
    ),
    "Yeah... Oh, I gots to tell you something.": (
        "Ouais... Oh, j'ai un truc à t'apprendre."
    ),
    "What's that?": "Quoi donc ?",
    "When yer in a pinch and can't get away, shoving the enemy\r\nis another option. Then you move around behind them!": (
        "Quand tu es coincé sans pouvoir fuir, repousser l'ennemi\r\nest une bonne option. Puis passe dans son dos !"
    ),
    "Shove them, huh?": "Les repousser, hein ?",
    "You learned Counter Quickstep. This lets you evade and\r\nswitch places with the enemy. Hold <Sign:4> to enter a\r\nfighting stance, then <Sign:0> in time with an enemy's attack.": (
        "Vous apprenez le Pas vif contre-attaque. Esquivez et\r\npassez dans le dos ennemi. Maintenez <Sign:4> en garde,\r\npuis appuyez sur <Sign:0> au moment de l'attaque."
    ),
    "Thanks, Kamoji. That'll be useful.": "Merci, Kamoji. Ce sera utile.",
    "Heh heh. No rules broken as long as you don't attack.": (
        "Hé hé. Aucune règle enfreinte tant que tu n'attaques pas."
    ),
    "About the winnings, we split the ten million yen entry fee,\r\nand I'll give you back your stake. That makes it 15 million\r\nyen for you.": (
        "Pour les gains, on partage les 10 millions d'inscription,\r\net je te rends ta mise. Ça te fait donc 15 millions\r\nde yens au total."
    ),
    "You're taking five million yen?": "Tu prends 5 millions de yens ?",
    "For overhead and lesson fees! I think I gave you some\r\npretty good advice.": (
        "Frais de gestion et de cours ! Je t'ai donné d'excellents\r\nconseils, non ?"
    ),
    "Fine. I guess it's helped build my skills, so I won't\r\ncomplain.": (
        "Ça va. Ça a bien développé mes réflexes, je ne vais\r\npas me plaindre."
    ),
    "Next up is the 100 million yen prize! I'll be waiting.": (
        "Prochaine étape : les 100 millions ! Je t'attends."
    ),
    "Heh heh. I'll be taking that million yen. That'll cover what\r\nI need to deliver to the family, and leave plenty of change.\r\nTime to paint the town!": (
        "Hé hé. J'empoche ce million de yens. Ça couvrira ma dette\r\nauprès de la famille avec du rab. C'est l'heure de faire\r\nla fête !"
    ),
    "You gots to put in a little more effort, Kiryu-san. Just\r\nkeep your distance and don't stand in front of them, and\r\ndodging'll be easy.": (
        "Un petit effort, Kiryu-san. Garde tes distances et évite\r\nde rester bien en face, esquiver deviendra bien plus\r\nfacile."
    ),
    "Don't get discouraged, Kiryu-san! You can do this!": (
        "Ne te décourage pas, Kiryu-san ! Tu peux le faire !"
    ),
    "Damn, you're hard to pin down! All my earnings, gone...": (
        "Merde, impossible de te toucher ! Tous mes gains, envolés..."
    ),
    "Thanks for trying! I hopes you figure out a way to pay your\r\nboss. If he lets you live, come on back and try again!": (
        "Merci d'avoir essayé ! Trouve vite de quoi payer ton chef.\r\nS'il te laisse en vie, reviens retenter ta chance !"
    ),
    "Good work, Kiryu-san! That guy sure packed a punch, didn't\r\nhe!?": (
        "Beau boulot, Kiryu-san ! Ce gars cognait dur, pas vrai !?"
    ),
    "Good work, Kiryu-san! That guy sure packed a punch, didn't\r\nhe?": (
        "Beau boulot, Kiryu-san ! Ce gars cognait dur, pas vrai ?"
    ),
    "Yeah, I wasn't so sure about that one.": "Oui, j'ai failli me faire surprendre.",
    "When you can't evade and your guard is broken, you gots to\r\nstay calm and put up your guard again. Then you'll be\r\nprotected.": (
        "Si tu ne peux pas esquiver et que ta garde est brisée,\r\ngarde ton calme et replace ta garde aussitôt pour te\r\nprotéger."
    ),
    "Putting up my guard again, huh?": "Replacer ma garde, hein ?",
    "You learned Floating Re-Guard 1. Press <Sign:6> after your\r\nguard is broken to move away and put up your guard again.": (
        "Vous apprenez Reprise de garde 1. Appuyez sur <Sign:6>\r\naprès un bris de garde pour reculer et vous protéger\r\nde nouveau."
    ),
    "Great idea, Kamoji. That'll come in handy.": "Bonne idée, Kamoji. Ce sera bien utile.",
    "About the winnings, we split the million yen entry fee,\r\nand I'll give you back your stake. So that's one and a half\r\nmillion yen for you.": (
        "Pour les gains, on partage le million d'inscription et je\r\nte rends ta mise. Ça te fait donc 1,5 million de yens\r\nau total."
    ),
    "Heh, even half the winnings is a nice prize.": "Hé, même la moitié reste une belle prime.",
    "Be seeing you.": "À la prochaine.",
    "Heh heh. I'll be taking that prize money.": "Hé hé. C'est moi qui rafle la mise.",
    "You gots to put in a little more effort, Kiryu-san. You\r\nought to keep your distance.": (
        "Fais un petit effort, Kiryu-san. Tu devrais plutôt garder\r\ntes distances."
    ),
    "You gots to put in a little more effort, Kiryu-san. You\r\noughta be dodging guys like that no sweat!": (
        "Un petit effort, Kiryu-san. Tu devrais esquiver ce genre\r\nde gars les doigts dans le nez !"
    ),
    "You gots to put in a little more effort, Kiryu-san.\r\nYou ought to keep your distance.": (
        "Un petit effort, Kiryu-san. Tu devrais plutôt garder\r\ntes distances."
    ),
    "You gots to put in a little more effort, Kiryu-san.\r\nYou oughta be dodging guys like that no sweat!": (
        "Un petit effort, Kiryu-san. Tu devrais esquiver ce genre\r\nde gars les doigts dans le nez !"
    ),
    "Hold <Sign:4> to enter a fighting stance, then <Sign:3> to\r\nQuickstep while still facing the enemy. Watch for their\r\nattacks closely, and press <Sign:3> at the right time.": (
        "Maintenez <Sign:4> pour vous mettre en garde, puis\r\n<Sign:3> pour esquiver face à l'ennemi. Observez ses\r\ncoups et appuyez au bon moment sur <Sign:3>."
    ),
    "Grr... How do you move so fast? I don't get it.": (
        "Grr... Comment tu bouges si vite ? J'y pige rien."
    ),
    "Nice effort there! Thanks for trying! Always happy to do\r\na rematch!": (
        "Bien essayé ! Merci d'avoir tenté ! Reviens quand tu\r\nveux pour une revanche !"
    ),
    "Good work, Kiryu-san! You was quick as the wind there!": (
        "Beau boulot, Kiryu-san ! Tu as été vif comme l'éclair !"
    ),
    "Well, it was a better challenge than a drunk at least.": (
        "C'était toujours plus stimulant qu'un ivrogne de rue."
    ),
    "When you take a hit, swing your head around so's you don't\r\neat another big punch.": (
        "Quand tu encaisses, esquive de la tête pour ne pas\r\nte prendre un second coup."
    ),
    "Swing my head? Like bobbing and weaving? Okay, I'll remember\r\nthat.": (
        "Esquiver de la tête ? Comme une feinte ? D'accord,\r\nje retiendrai."
    ),
    "You learned Damage Weaving. Press <Sign:6> or <Sign:3> when hit\r\nby an enemy attack to perform a weaving move and dodge\r\nout of the way.": (
        "Vous apprenez Esquive sous impact. Appuyez sur <Sign:6>\r\nou <Sign:3> en étant touché pour esquiver aussitôt et vous\r\ndégager."
    ),
    "That's some good advice, Kamoji. I'll put it to use.": (
        "C'est un excellent conseil, Kamoji. J'en ferai bon usage."
    ),
    "About the winnings, we split the \\100,000 entry fee,\r\nand I'll give you back your stake. That means 150,000 yen\r\nfor you.": (
        "Pour les gains, on partage les 100 000 ¥ d'inscription\r\net je te rends ta mise. Ça te fait 150 000 yens\r\nau total."
    ),
    "Until next time, then.": "À la prochaine, alors.",
    "Heh heh. Got my money's worth. See ya.": "Hé hé. J'en ai eu pour mon argent. Salut.",
    "Gah, I can't land a blow! You're pretty good at dodging!\r\nStill, the exercise did me good. Thanks.": (
        "Argh, impossible de te toucher ! Tu esquives bien !\r\nÇa m'a fait faire de l'exercice. Merci."
    ),
    "Good fight! Too bad luck wasn't on your side. Come on back\r\nand try again!": (
        "Beau combat ! Dommage, la chance n'était pas là.\r\nReviens quand tu veux !"
    ),
    "Fine work, Kiryu-san! You was slippery as an eel. The\r\nchallenger seemed satisfied, too.": (
        "Beau travail, Kiryu-san ! Tu as été insaisissable.\r\nLe challenger a l'air ravi aussi."
    ),
    "Yeah, it turned out all right. Bet winning is a pretty\r\nthankless job in this case, though.": (
        "Ouais, ça s'est bien passé. Mais gagner est un rôle\r\nassez ingrat dans ce genre de pari."
    ),
    "One thing you can try is evading at the last possible\r\nmoment. Pulling that off's a great feeling!": (
        "Tu devrais essayer d'esquiver au tout dernier moment.\r\nRéussir ça procure une sensation géniale !"
    ),
    "Dodging at the last minute, huh?": "Esquiver au dernier moment, hein ?",
    "You learned Swallow Spirit. Press <Sign:3> in time with\r\nenemy attacks to build up the Heat Gauge.": (
        "Vous apprenez Esprit de l'hirondelle. Esquivez avec\r\n<Sign:3> au moment d'une attaque pour remplir la jauge\r\nde Furia."
    ),
    "That's good advice, Kamoji. Much appreciated.": "C'est un bon conseil, Kamoji. Merci bien.",
    "Heh!? Heh heh. Let's do this again sometime.": "Hein !? Hé hé. On remettra ça à l'occasion.",
    "About the winnings, we split the \\10,000 entry fee,\r\nand I'll give you back your stake. So that's 15,000 yen\r\nfor you.": (
        "Pour les gains, on partage les 10 000 ¥ d'inscription\r\net je te rends ta mise. Ça te fait donc 15 000 yens\r\nau total."
    ),
    "We split the winnings?": "On partage les gains ?",
    "Consider it overhead and lesson fees! Pretty fair if you\r\nask me.": (
        "Considère ça comme des frais de cours ! Très honnête\r\nsi tu veux mon avis."
    ),
    "Next up is \\100,000. I'll be waiting!": "Prochaine étape : 100 000 ¥. Je t'attends !",
}

def translate_msg_inplace(data_bytes, translations):
    out = bytearray(data_bytes)
    translated_count = 0
    for en_str, fr_str in translations.items():
        fr_clean = fr_str.replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')
        en_bytes = en_str.encode('latin1') + b'\x00'
        fr_bytes = fr_clean.encode('latin1') + b'\x00'
        assert len(fr_bytes) <= len(en_bytes), f"French string too long: {len(fr_bytes)} > {len(en_bytes)} for {repr(en_str)}"
        pos = 0
        while True:
            idx = out.find(en_bytes, pos)
            if idx == -1:
                break
            padded = fr_bytes + b'\x00' * (len(en_bytes) - len(fr_bytes))
            out[idx : idx + len(en_bytes)] = padded
            translated_count += 1
            pos = idx + len(en_bytes)
    return bytes(out), translated_count

def translate_msg_pool(data_bytes, pool_start, pool_end, translations):
    out = bytearray(data_bytes)
    pool_max = pool_end - pool_start
    ptrs = [i for i in range(0, pool_start, 4) if pool_start <= struct.unpack('>I', out[i:i+4])[0] < pool_end]
    
    new_pool = bytearray()
    new_offsets = {}
    
    for p in ptrs:
        old_off = struct.unpack('>I', out[p:p+4])[0]
        old_s = out[old_off:out.find(b'\x00', old_off)].decode('latin1')
        fr_s = translations.get(old_s, old_s)
        fr_s = fr_s.replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')
        s_bytes = fr_s.encode('latin1') + b'\x00'
        if s_bytes not in new_offsets:
            curr_off = pool_start + len(new_pool)
            new_offsets[s_bytes] = curr_off
            new_pool.extend(s_bytes)
        struct.pack_into('>I', out, p, new_offsets[s_bytes])
        
    assert len(new_pool) <= pool_max, f"Pool overflow: {len(new_pool)} > {pool_max}"
    new_pool.extend(b'\x00' * (pool_max - len(new_pool)))
    out[pool_start:pool_end] = new_pool
    assert len(out) == len(data_bytes)
    return bytes(out)

def build_hostess_msg(d_target, d_template, hostess_name):
    out = bytearray(d_target)
    POOL_START = 0x7f30
    POOL_END = 0x98c0
    POOL_MAX = POOL_END - POOL_START
    
    ptrs = [i for i in range(0, 31104, 4) if 31104 <= struct.unpack('>I', d_template[i:i+4])[0] < 37700]
    
    new_pool = bytearray()
    new_offsets = {}
    
    for p in ptrs:
        t_off = struct.unpack('>I', d_template[p:p+4])[0]
        s = d_template[t_off:d_template.find(b'\x00', t_off)].decode('latin1')
        s = s.replace('Mana', hostess_name)
        s = s.replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')
        
        # Minor natural shortenings
        if "Je suis super contente que vous m'ayez\r\ndemandée !" in s:
            s = s.replace("Je suis super contente que vous m'ayez\r\ndemandée !", "Ravie que vous m'ayez demandée !")
        if "Vous êtes venu me voir ! Vous êtes peut-être tombé amoureux\r\nde moi !" in s:
            s = s.replace("Vous êtes venu me voir ! Vous êtes peut-être tombé amoureux\r\nde moi !", "Vous venez me voir ! Peut-être amoureux de moi !")
        if "Je vous ai attendu, Majima-san ! Amusons-nous aujourd'hui !" in s:
            s = s.replace("Je vous ai attendu, Majima-san ! Amusons-nous aujourd'hui !", "Je vous attendais, Majima-san ! Amusons-nous !")
        if "C'est un plaisir de vous revoir, Majima-san !" in s:
            s = s.replace("C'est un plaisir de vous revoir, Majima-san !", "Plaisir de vous revoir, Majima-san !")
        if "Merci infiniment d'être venu me voir !" in s:
            s = s.replace("Merci infiniment d'être venu me voir !", "Merci beaucoup d'être venu me voir !")
            
        s_bytes = s.encode('latin1') + b'\x00'
        if s_bytes not in new_offsets:
            curr_off = POOL_START + len(new_pool)
            new_offsets[s_bytes] = curr_off
            new_pool.extend(s_bytes)
        struct.pack_into('>I', out, p, new_offsets[s_bytes])
        
    assert len(new_pool) <= POOL_MAX, f"Hostess pool overflow: {len(new_pool)} > {POOL_MAX}"
    new_pool.extend(b'\x00' * (POOL_MAX - len(new_pool)))
    out[POOL_START:POOL_END] = new_pool
    assert len(out) == len(d_target)
    return bytes(out)

def main():
    wdr_path = 'release_gog/data/wdr_par_c/wdr.par'
    bak_path = wdr_path + '.phase4.bak'
    if not os.path.exists(bak_path):
        print(f"[+] Creating backup {bak_path}...")
        shutil.copyfile(wdr_path, bak_path)

    with open(wdr_path, 'rb') as f:
        wdr_data = bytearray(f.read())

    files = parse_par(wdr_data)
    
    # Locate file offsets in wdr.par
    magic, unkA, unkB, unkC = struct.unpack('>4I', wdr_data[:16])
    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', wdr_data[16:32])
    name_offset = 32 + folder_count * 64
    
    file_info = {}
    for i in range(file_count):
        fn = wdr_data[name_offset + i*64 : name_offset + (i+1)*64].split(b'\x00')[0].decode('latin1')
        e_off = file_table_offset + i * 32
        flags, u_sz, c_sz, f_off = struct.unpack('>4I', wdr_data[e_off : e_off + 16])
        file_info[fn] = (e_off, flags, u_sz, c_sz, f_off)

    d_mana = files['uid01640011.msg'][3]

    print("[+] Translating 1. uid01070969.msg (Blackjack)...")
    bj_raw = files['uid01070969.msg'][3]
    bj_fr, _ = translate_msg_inplace(bj_raw, BLACKJACK_TRANSLATIONS)
    e_off, flags, u_sz, c_sz, f_off = file_info['uid01070969.msg']
    assert len(bj_fr) == c_sz
    wdr_data[f_off : f_off + c_sz] = bj_fr

    print("[+] Translating 2. uid01070994.msg (Cee-lo)...")
    cl_raw = files['uid01070994.msg'][3]
    cl_fr, _ = translate_msg_inplace(cl_raw, CEELO_TRANSLATIONS)
    e_off, flags, u_sz, c_sz, f_off = file_info['uid01070994.msg']
    assert len(cl_fr) == c_sz
    wdr_data[f_off : f_off + c_sz] = cl_fr

    print("[+] Translating 3. uid01261727.msg (Kamoji Rush Style Training)...")
    km_raw = files['uid01261727.msg'][3]
    km_fr = translate_msg_pool(km_raw, 0x5de8, 0x7bb8, KAMOJI_TRANSLATIONS)
    e_off, flags, u_sz, c_sz, f_off = file_info['uid01261727.msg']
    assert len(km_fr) == c_sz
    wdr_data[f_off : f_off + c_sz] = km_fr

    hostesses = [
        ('uid01640008.msg', 'Yuki'),
        ('uid0164000d.msg', 'Ai'),
        ('uid0164000e.msg', 'Saki'),
        ('uid0164000f.msg', 'Hibiki'),
        ('uid01640010.msg', 'Chika'),
    ]

    for idx, (fn, hname) in enumerate(hostesses, start=4):
        print(f"[+] Translating {idx}. {fn} (Hostess: {hname})...")
        h_raw = files[fn][3]
        h_fr = build_hostess_msg(h_raw, d_mana, hname)
        e_off, flags, u_sz, c_sz, f_off = file_info[fn]
        assert len(h_fr) == c_sz
        wdr_data[f_off : f_off + c_sz] = h_fr

    print("[+] Writing updated wdr.par...")
    with open(wdr_path, 'wb') as f:
        f.write(wdr_data)

    print("[+] Successfully translated all 8 target .msg files and updated wdr.par!")

if __name__ == '__main__':
    main()
