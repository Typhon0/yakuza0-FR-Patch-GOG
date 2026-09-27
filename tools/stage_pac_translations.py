# -*- coding: utf-8 -*-
"""
tools/stage_pac_translations.py
--------------------------------
Calibrated French translations for all stage PAC files (pac_STID_*.bin) in wdr.par:
- pac_STID_ST_OSAKA.bin (Osaka street NPCs, Iwao Bridge living statue scene, Majima barks)
- pac_STID_ST_KAMURO.bin (Kamurocho street NPCs, punks, tissue vendors, Kiryu barks)
- pac_STID_ST_K_WESTPARK.bin (West Park gambling den)
- pac_STID_ST_O_CASINO.bin (Sotenbori casino)
- pac_STID_ST_K_MAHARAJA.bin & pac_STID_ST_O_MAHARAJA.bin (Disco Maharaja)
- All other stage combat / story PAC files.

Every single French string is calibrated so that:
len(fr.encode('latin1')) <= len(en.encode('latin1'))
Space-padding is used to maintain bit-exact file length.
"""

PAC_TRANSLATIONS = {
    # --- OSAKA / SOTENBORI (pac_STID_ST_OSAKA.bin) ---
    "Can't block bullets!":
        "Balles imparables !",
    "Someone, anyone... Help!":
        "À l'aide ! Pitié !",
    "Hey! You there!":
        "Hé ! Vous là !",
    "Please! Let me explain!":
        "Laissez-moi parler !",
    "You're not getting away with this!":
        "Vous ne fuirez pas comme ça !",
    "What the hell's going on!?":
        "Mais que se passe-t-il !?",
    "I'm so cold...":
        "J'ai froid...",
    "To the Bed of Styx":
        "Au Lit du Styx",
    "(Not like I had business across the bridge anyway.  Gotta hurry to Hogushi Kaikan now.)":
        "(J'ai rien à faire de l'autre côté du pont. Vite, filons au Hogushi Kaikan.)",
    "(Gotta keep my distance.)":
        "(Gardons nos distances)",
    "(Wonder what's up...  I got no time for detours.)":
        "(Que se passe-t-il... Pas le temps de traîner)",
    "(Wonder what's up...  Well, I got places to be.)":
        "(Bizarre... Enfin, j'ai des choses à faire.)",
    "(This's the long way around...)":
        "(C'est un long détour...)",
    "(Gotta hurry to Hogushi Kaikan!)":
        "(Vite au Hogushi Kaikan !)",
    "(Gotta head north to Sotenbori Street!)":
        "(Filons au nord, rue Sotenbori !)",
    "(Stairs are a bad idea...)":
        "(Évitons les escaliers...)",
    "(Better avoid the stairs...)":
        "(Mieux vaut fuir l'escalier)",
    "Please, let my daughter go!":
        "Laissez partir ma fille !",
    "Who are you guys?":
        "Qui êtes-vous !?",
    "I want to play some more!":
        "Je veux encore jouer !",
    "(The target's \\2,000,000, and we're  showin' off the  Essence of Blade Bitin' .)":
        "(L'objectif est 2 000 000 ¥, en sortant  l'Essence du croc de lame .)",
    "(The target's \\2,000,000, and  we're showin' off  Rollin' Snake .)":
        "(L'objectif est 2 000 000 ¥, en sortant  le Serpent roulant .)",
    "(The target's \\2,000,000, and  we're showin' off  Dash Pirouette .)":
        "(L'objectif est 2 000 000 ¥, en sortant  la Pirouette éclair .)",
    "(The target's \\2,000,000, and we're  showin' off  Pose Soul (Finisher) .)":
        "(L'objectif est 2 000 000 ¥, en sortant  l'Âme de pose (Finisher) .)",
    "(The target's \\2,000,000, and we're  showin' off the  Essence of Friendly Fire .)":
        "(L'objectif est 2 000 000 ¥, en sortant  l'Essence du tir allié .)",
    "(The target's \\2,000,000.)":
        "(Objectif: 2 000 000 ¥.)",

    # --- KAMUROCHO (pac_STID_ST_KAMURO.bin) ---
    "Oh, Mina-chan...  What should I do?":
        "Oh Mina-chan... Que dois-je faire?",
    "Be honest with me!":
        "Parle franchement!",
    "How about some pocket tissues?":
        "Un petit paquet de mouchoirs ?",
    "Get your tissues here!":
        "Mouchoirs gratuits ici",
    "Win three rounds!":
        "Gagnez 3 rounds !",
    "The third battle begins!":
        "3e round, c'est parti !",
    "At last, this is it!":
        "Nous y voilà enfin !",
    "Almost there!":
        "Presque là !",
    "Don't get shot!":
        "Gare aux tirs !",
    "Don't get careless!":
        "Reste vigilant !",
    "Wanna go start a fight?":
        "On cherche la bagarre ?",
    "Isn't there anyone strong here?":
        "Y a personne de fort par ici ?",
    "I wanna beat someone to a pulp.":
        "J'veux éclater quelqu'un !",
    "It's massacre time.":
        "L'heure du massacre",
    "Isn't there anyone better?":
        "Y a personne de meilleur ?",
    "I'm bored outta my skull!":
        "Je m'ennuie à mourir !",
    "Dammit, how lame is this?":
        "Fait chier, la honte !",
    "Let's go kick some ass.":
        "Cassons de la gueule !",
    "Did you see those lameoids?":
        "T'as vu ces gros minables ?",
    "(Main roads are too risky.  Better stick to back alleys.)":
        "(Les grands axes sont trop risqués. Prenons les ruelles.)",
    "(Main roads are too risky. I should  take back alleys to Pink Street.)":
        "(Les grands axes sont risqués. Je prends les ruelles vers Pink St.)",
    "(Can't go back the way I came.  My best bet's going to Pink Street.)":
        "(Impossible de reculer. Mieux vaut filer vers Pink Street.)",
    "(Can't go back the way I came.  I've gotta get through Pink Street.)":
        "(Impossible de rebrousser chemin. Je dois passer par Pink Street.)",
    "(This way's dangerous.  Gotta get away from here.)":
        "(Trop dangereux par là. Je dois vite m'éloigner.)",
    "The Popstar Prince?":
        "Le Prince Pop ?",
    "Please, don't hit me...":
        "Pitié, pas de coups !",
    "Ahh! Please don't hit me!":
        "Aah ! Pas de coups !",
    "Shut up!":
        "La ferme",
    "I can't wait.":
        "J'ai hâte !",
    "I hope she's all right...":
        "Pourvu qu'elle aille bien",
    "Was she okay?":
        "Elle va bien?",
    "Where'd she go?":
        "Où est-elle ?",
    "What a cutie...":
        "Quel canon...",
    "(Hmm, this isn't where  Nishiki's meeting me.)":
        "(Hmm, c'est pas ici le rencard de Nishiki.)",
    "You're begging for an ass-kicking!":
        "Tu cherches une bonne raclée toi !",
    "This is bullshit!":
        "C'est bidon !",
    "Don't gimme that shit.":
        "Pas d'histoires !",
    "You're dead.":
        "T'es mort.",
    "Hand it over.":
        "Donne-moi ça.",
    "Yeah! Let's do it!":
        "Ouais, en avant !",
    "I just wanna knock someone out.":
        "J'veux assommer un type !",
    "Dammit, I'm bored!":
        "Fait chier, marre",
    "Let's kill that dude.":
        "Butons ce mec-là.",
    "There's someone pissing me off.":
        "Y en a un qui me les brise.",
    "Heh, sure, I'll help.":
        "Ouais, je t'aide !",
    "This is all we got?":
        "C'est tout ?",
    "We need victims with more dough.":
        "Faut des pigeons plus blindés.",
    "Gotta find someone like that...":
        "Faut dégoter un pigeon...",
    "Yeah, time to go nuts!":
        "Place au carnage !",
    "Sounds like fun.":
        "Ça a l'air cool.",
    "This domain is ours!":
        "Ce coin est à nous !",
    "Defy us, and it's game over!":
        "Défie-nous, et t'es mort !",
    "Dude, I'm in a heinous mood.":
        "Mec, j'suis d'humeur noire !",
    "Haha, for sure.":
        "Haha, clair !",
    "I'm losing my edge...":
        "Je perds la main...",
    "I wanna fight someone buff.":
        "J'veux taper un balèze !",
    "Damn, I want a woman!":
        "J'veux une femme !",
    "Like, way too weak.":
        "Genre, trop naze !",
    "I can't wait for a real fight.":
        "Trop hâte d'un vrai combat.",
    "Dude, I feel like shit!":
        "Mec, j'me sens naze !",
    "This is ticking me off.":
        "Ça commence à me soûler",
    "Let's just do this.":
        "Allez, on y va.",
    "Dude, I need money.":
        "M'faut du fric !",
    "Let's go rob someone around here.":
        "Allons braquer quelqu'un par ici.",
    "Dude, I'm bored.":
        "Mec, je m'ennuie",
    "I need some competition.":
        "Il me faut des rivaux !",
    "Everyone's too weak around here.":
        "Tous des mauviettes par ici.",
    "So glad you're joining us.":
        "Ravi que tu sois là !",
    "Not that caller again...":
        "Encore ce type au tel...",

    # --- MINIGAMES & CASINOS (WEST PARK, CASINO, MAHARAJA) ---
    "Cho-han's the game to play!":
        "Le Chô-han, c'est le top !",
    "Come play oicho-kabu!":
        "Venez à l'Oicho !",
    "How about koi-koi?":
        "Et un Koi-koi ?",
    "Cee-lo is really fun!":
        "Le Cee-lo, ça gère !",
    "Would you like to play poker?":
        "Voulez-vous jouer au poker ?",
    "How about roulette?":
        "Et une roulette ?",
    "Play high rate blackjack here!":
        "Blackjack grosses mises ici !",
    "Welcome!":
        "Entrez !",
    "Welcome":
        "Salut !",
    "I'm the greatest dancer!":
        "Le roi de la danse !",
    "What is with that guy?":
        "Il a quoi ce type ?",
    "What's with the mask?":
        "C'est quoi ce masque?",
    "Miss Isobe! I love you!":
        "Isobe ! Je vous aime !",
    "Majima! You can do it!":
        "Majima ! Assure !",

    # --- STAGES COMBAT & SCÉNARIO ---
    "(It's shut tight. That door's not budging.)":
        "(Verrouillée. Cette porte ne bouge pas.)",
    "Still more are on the way!":
        "D'autres gars arrivent !",
    "This is it!":
        "C'est parti",
    "(It's too dangerous to go back up. Gotta find those two...)":
        "(Trop dangereux de remonter. Retrouvons ces deux-là...)",
    "(I need to buy time for them to get out.)":
        "(Je dois faire diversion pour leur fuite)",
    "(I'll take the elevator.)":
        "(Je prends l'ascenseur.)",
    "Gotta get that 500  grand somehow...":
        "Faut trouver ces 500 000 ¥...",
    "Watch out for the time!":
        "Attention au chrono !",
    "It's not over yet!":
        "C'est pas fini !",
    "Guns can't stop you!":
        "Rien ne vous stoppe!",
    "Win five fights!":
        "Gagnez 5 combats",
    "Beat three enemies!":
        "Battez 3 ennemis !",
    "It's the final countdown!":
        "C'est le compte à rebours",
    "Here's the third!":
        "Voici le 3e !",
    "Use your Heat actions!":
        "Vos actions Heat !",
    "Even more foes are coming!":
        "D'autres ennemis arrivent!",
    "More enemies are on the way!":
        "D'autres ennemis arrivent !",
    "Reinforcements are on the way!":
        "Des renforts sont en route !",
    "Table at the Back":
        "Table du fond",
    "Table near the Back":
        "Table vers le fond",
    "Hello!":
        "Salut!",
    "Enjoy your time at our bar.":
        "Amusez-vous dans notre bar",

    # --- CLERK & SHOP PROMPTS ---
    "Thank you. That comes to %s.":
        "Merci bien. Ça fera %s.",
    "Would you like to order this?":
        "Voulez-vous commander ceci ?",
    "Is this what you want?":
        "Est-ce bien cela ?",
    "(I don't have any space.)":
        "(Je n'ai plus de place.)",
    "(I don't need this.)":
        "(Pas besoin de ça.)",

    # --- CABARET PARTNERSHIP BUSINESSES ---
    "(Rakuen-en, eh? That's a Club Mars area business.)":
        "(Rakuen-en, hein ? Zone du Club Mars.)",
    "(M Zoku Sotenbori, eh? That's a Club Mercury area business.)":
        "(M Zoku Sotenbori, hein ? Zone Club Mercury.)",
    "(Izakaya Ryoshimaru, eh? That's a Club Mercury area  business.)":
        "(Izakaya Ryoshimaru, hein ? Zone Club Mercury.)",
    "(Izakaya Ryoshimaru, eh? That's a Club Mercury area\r\nbusiness.)":
        "(Izakaya Ryoshimaru, hein ?\r\nZone Club Mercury.)",
    "(Hammurabi Records, eh? That's a Club Mercury area  business.)":
        "(Hammurabi Records, hein ? Zone Club Mercury.)",
    "(Hammurabi Records, eh? That's a Club Mercury area\r\nbusiness.)":
        "(Hammurabi Records, hein ?\r\nZone Club Mercury.)",
    "(Death Curry, eh? That's a Club Venus area business.)":
        "(Death Curry, hein ? Zone Club Venus.)",
    "(Sokyu Cinema, eh? That's a Club Venus area business.)":
        "(Sokyu Cinema, hein ? Zone Club Venus.)",
    "(Pachinko Winde West, eh? That's a Club Venus area  business.)":
        "(Pachinko Winde West, hein ? Zone Club Venus.)",
    "(Pachinko Winde West, eh? That's a Club Venus area\r\nbusiness.)":
        "(Pachinko Winde West, hein ?\r\nZone Club Venus.)",
    "(Fuguta, eh? That's a Club Venus area business.)":
        "(Fuguta, hein ? Zone Club Venus.)",
    "(Sotenbori Kabuki Theater, eh? That's a Club Venus area  business.)":
        "(Théâtre Kabuki Sotenbori, hein ? Zone Venus.)",
    "(Sotenbori Kabuki Theater, eh? That's a Club Venus area\r\nbusiness.)":
        "(Théâtre Kabuki Sotenbori, hein ?\r\nZone Club Venus.)",
    "(Crepe Cats, eh? That's a Club Venus area business.)":
        "(Crepe Cats, hein ? Zone Club Venus.)",
    "(Yakitori Torikko, eh? That's a Club Venus area business.)":
        "(Yakitori Torikko, hein ? Zone Club Venus.)",
    "(Gyu-masu, eh? That's a Club Venus area business.)":
        "(Gyu-masu, hein ? Zone Club Venus.)",
    "Sh-Shut up!":
        "T-Tais-toi!",

    # --- MINOR DIALOGUE BARKS & PROMPTS ---
    "Heh, thanks.": "Hé, merci.",
    "Sorry I messed up.": "Désolé, j'ai raté.",
    "Oh... I see...": "Oh... je vois.",
    "Really... Thanks.": "Vraiment, merci.",
    "to  enter shot mode.": "pour viser.",
    "Select an opponent.": "Choisis un rival.",
    "Excuse me!": "Pardon !",
    "Excuse me.": "Pardon.",
    "Thanks.": "Merci.",
    "Yeah.": "Ouais",
    "Use Quickstep Combos!": "Combos d'esquive !",
    "Oh yeah, 6-3-4! That's Musashi!": "Ouais, 6-3-4 ! C'est Musashi !",
    "Hell yeah, 6-3-4! Musashi!": "Et ouais, 6-3-4 ! Musashi!",

    # --- CRLF STREET BARKS & DANCE/STATUE VARIANTS ---
    "(Not like I had business across the bridge anyway.\r\nGotta hurry to Hogushi Kaikan now.)":
        "(J'ai rien à faire de l'autre côté du pont.\r\nVite, filons au Hogushi Kaikan.)",
    "(No time for detours.\r\nI gotta get to the Grand.)":
        "(Pas de détour.\r\nJe dois filer au Grand.)",
    "(Wonder what's up...\r\nI got no time for detours.)":
        "(Que se passe-t-il...\r\nPas le temps de traîner.)",
    "(Wonder what's up...\r\nWell, I got places to be.)":
        "(Bizarre...\r\nEnfin, j'ai des choses à faire.)",
    "(Closed for construction...)":
        "(Fermé pour travaux...)",
    "(The target's \\2,000,000, and we're\r\nshowin' off the <Color:7>Essence of Blade Bitin'<Color:Default>.)":
        "(La cible : 2 000 000 ¥, place à l'\r\n<Color:7>Essence du brise-lame<Color:Default> !)",
    "(The target's \\2,000,000, and\r\nwe're showin' off <Color:7>Rollin' Snake<Color:Default>.)":
        "(La cible : 2 000 000 ¥, place\r\nau <Color:7>Serpent roulant<Color:Default> !)",
    "(The target's \\2,000,000, and\r\nwe're showin' off <Color:7>Dash Pirouette<Color:Default>.)":
        "(La cible : 2 000 000 ¥, place à la\r\n<Color:7>Pirouette sprint<Color:Default> !)",
    "(The target's \\2,000,000, and we're\r\nshowin' off <Color:7>Pose Soul (Finisher)<Color:Default>.)":
        "(La cible : 2 000 000 ¥, place à la\r\n<Color:7>Pose de l'âme (Finisher)<Color:Default> !)",
    "(The target's \\2,000,000, and we're\r\nshowin' off the <Color:7>Essence of Friendly Fire<Color:Default>.)":
        "(La cible : 2 000 000 ¥, place à l'\r\n<Color:7>Essence de tir allié<Color:Default> !)",
    "Nearly finished!":
        "Bientôt fini !",
    "Ready to go home?":
        "Prêt à rentrer ?",
    "(Main roads are too risky.\r\nBetter stick to back alleys.)":
        "(Grands axes trop risqués.\r\nPrenons les ruelles.)",
    "(Main roads are too risky. I should\r\ntake back alleys to Pink Street.)":
        "(Grands axes risqués. Prenons les\r\nruelles vers Pink Street.)",
    "(Can't go back the way I came.\r\nMy best bet's going to Pink Street.)":
        "(Impossible de rebrousser chemin.\r\nCap sur Pink Street.)",
    "(Can't go back the way I came.\r\nI've gotta get through Pink Street.)":
        "(Impossible de faire demi-tour.\r\nPassons par Pink Street.)",
    "(This way's dangerous.\r\nGotta get away from here.)":
        "(Endroit dangereux.\r\nFaut partir d'ici.)",
    "(Better set them straight before\r\nthey try anything really stupid.)":
        "(Mieux vaut les calmer avant\r\nqu'ils ne fassent une bêtise.)",
    "(Hmm, this isn't where\r\nNishiki's meeting me.)":
        "(Hmm, pas ici que Nishiki\r\ndoit me retrouver.)",
    "This'll be awesome!":
        "Ça va être génial !",
    "Let's rob 'em, too.":
        "Dépouillons-les !",
    "No one can hold their own against us.":
        "Nul ne fait le poids contre nous !",
    "So not worth my time.":
        "Pas d'temps à perdre.",
    "Time for an ass-kicking!":
        "L'heure de la raclée !",
}

if __name__ == '__main__':
    import sys
    too_long = []
    for en, fr in PAC_TRANSLATIONS.items():
        en_b = en.encode('latin1')
        fr_b = fr.encode('latin1')
        if len(fr_b) > len(en_b):
            too_long.append((en, fr, len(fr_b), len(en_b)))

    if too_long:
        print(f"FAILED: {len(too_long)} strings are too long:")
        for en, fr, lfr, len_ in too_long:
            print(f"  {lfr} > {len_} : {repr(en)} -> {repr(fr)}")
        sys.exit(1)
    else:
        print(f"SUCCESS! All {len(PAC_TRANSLATIONS)} strings strictly satisfy len(fr) <= len(en)!")

