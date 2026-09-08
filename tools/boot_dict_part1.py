# -*- coding: utf-8 -*-
"""
build_boot_part1.py
Strings 0 to 250 of string_tbl_848.json
"""

import json

P1 = {
    # 0..4: Characters & Funds
    "Tsukasa Sagawa\nPatriarch of the Sagawa Family,\nRetainer to the Omi Alliance Chairman":
        "Tsukasa Sagawa\nPatriarche famille Sagawa,\nVassal du chef Alliance Omi",
    "Osamu Kashiwagi\nCaptain of the Kazama Family,\nA Dojima Family Subsidiary":
        "Osamu Kashiwagi\nCapitaine famille Kazama,\nBranche clan Dojima",
    "Takashi Nihara\nActing Second Chairman of the Tojo Clan":
        "Takashi Nihara\nPresident par interim du clan Tojo",
    "Add extra funds. \nExtra funds increase the success rate and shorten exploration time.":
        "Ajouter des fonds.\nLes fonds augmentent le succes et reduisent le temps.",
    "You don't have sufficient funds.":
        "Vous n'avez pas assez de fonds.",

    # 5..9: Thoughts
    "Gonna win this one!": "Je vais gagner !",
    "Got this in the bag.": "C'est dans la poche.",
    "Hurry up, will you?": "Plus vite !",
    "Time to bluff!": "Je bluffe !",
    "Got to think a bit...": "Voyons voir...",

    # 10..24: Real estate Royale
    "Return to Game": "Retour au jeu",
    "Kiss on the Cheek": "Bise sur la joue",
    "About the Agency Menu": "Menu de gestion",
    "View the menu controls.": "Commandes du menu",
    "Time to Payout": "Paiement",
    "Invest in this property?": "Investir dans ce bien ?",
    "Purchase this property?": "Acheter ce bien ?",
    "You've gained control of the area.": "Zone sous controle !",
    "Join the battle?": "Participer ?",
    "Conduct business with this set-up?": "Lancer avec cette equipe ?",
    "You failed to gain control.": "Echec de prise de controle.",
    "You failed to protect your properties.": "Echec de protection des biens.",
    "You won the money battle.": "Victoire financiere !",
    "Payout collection stopped until you\nresolve problems in the area.":
        "Recolte suspendue tant que\nles litiges persistent.",
    "Win a total of 10,000 Tokens.\nBonus: %s x%s\n(Note: there are no further goals beyond this)":
        "Gagner 10 000 jetons au total.\nBonus : %s x%s\n(Aucun autre objectif au-dela)",

    # 25..40: Arcade & Mahjong wins
    "Get \\%s for each game played.\nThat's \\%s!": "Recevez \\%s par partie jouee.\nSoit \\%s !",
    "Get \\%s for each point scored.\nThat's \\%s!": "Recevez \\%s par point marque.\nSoit \\%s !",
    "Get \\%s for each stage completed.\nThat's \\%s!": "Recevez \\%s par niveau fini.\nSoit \\%s !",
    "Get \\%s for each banana collected.\nThat's \\%s!": "Recevez \\%s par banane prise.\nSoit \\%s !",
    "Get \\%s for each time you completed World 1\nafter using continues.\nThat's \\%s!":
        "Recevez \\%s par Monde 1 fini\navec des continues.\nSoit \\%s !",
    "Get \\%s for each time you completed World 2\nafter using continues.\nThat's \\%s!":
        "Recevez \\%s par Monde 2 fini\navec des continues.\nSoit \\%s !",
    "Get \\%s for each time you completed World 3\nafter using continues.\nThat's \\%s!":
        "Recevez \\%s par Monde 3 fini\navec des continues.\nSoit \\%s !",
    "Get \\%s for each time you completed World 1\nwithout using continues.\nThat's \\%s!":
        "Recevez \\%s par Monde 1 fini\nsans continue.\nSoit \\%s !",
    "Get \\%s for each time you completed World 2\nwithout using continues.\nThat's \\%s!":
        "Recevez \\%s par Monde 2 fini\nsans continue.\nSoit \\%s !",
    "Get \\%s for each time you completed World 3\nwithout using continues.\nThat's \\%s!":
        "Recevez \\%s par Monde 3 fini\nsans continue.\nSoit \\%s !",
    "Get \\%s for each point.\nThat's \\%s!\n*No bonus for zero or negative points.":
        "Recevez \\%s par point.\nSoit \\%s !\n*Pas de bonus pour zero ou moins.",
    "Get \\%s for each time you ranked first in\n4-player mahjong.\nThat's \\%s!":
        "Recevez \\%s par 1re place\nau mahjong a 4.\nSoit \\%s !",
    "Get \\%s for each time you ranked second in\n4-player mahjong.\nThat's \\%s!":
        "Recevez \\%s par 2e place\nau mahjong a 4.\nSoit \\%s !",
    "Get \\%s for each time you ranked third in\n4-player mahjong.\nThat's \\%s!":
        "Recevez \\%s par 3e place\nau mahjong a 4.\nSoit \\%s !",
    "Get \\%s for each time you ranked first in\n3-player mahjong.\nThat's \\%s!":
        "Recevez \\%s par 1re place\nau mahjong a 3.\nSoit \\%s !",
    "Get \\%s for each time you ranked second in\n3-player mahjong.\nThat's \\%s!":
        "Recevez \\%s par 2e place\nau mahjong a 3.\nSoit \\%s !",

    # 79..97: OutRun & Arcade completions
    "Score (Adjusted for Level)": "Score (selon niveau)",
    "Get \\%s for each point scored. That's \\%s!\n*MEDIUM: -20,000 points x times played\n HARD: -50,000 points x times played":
        "Recevez \\%s par point marque. Soit \\%s !\n*MOYEN: -20 000 pts x parties\n DIFFICILE: -50 000 pts x parties",
    "Get \\%s for each removed gem.\nThat's \\%s!\n*Up to 9999 gems per game.":
        "Recevez \\%s par gemme.\nSoit \\%s !\n*Jusqu'a 9999 gemmes.",
    "Get \\%s for each level in the highest\nlevel reached in a game.\nThat's \\%s!":
        "Recevez \\%s par niveau atteint\nau plus haut niveau en partie.\nSoit \\%s !",
    "Completions From Area 1": "Finis depuis la Zone 1",
    "Completions From Area 4": "Finis depuis la Zone 4",
    "Completions From Area 7": "Finis depuis la Zone 7",
    "Get \\%s for each time you completed Area 1.\nThat's \\%s!": "Recevez \\%s par Zone 1 terminee.\nSoit \\%s !",
    "Get \\%s for each time you completed Area 2.\nThat's \\%s!": "Recevez \\%s par Zone 2 terminee.\nSoit \\%s !",
    "Get \\%s for each time you completed Area 3.\nThat's \\%s!": "Recevez \\%s par Zone 3 terminee.\nSoit \\%s !",
    "Get \\%s for each time you completed Area 4.\nThat's \\%s!": "Recevez \\%s par Zone 4 terminee.\nSoit \\%s !",
    "Get \\%s for each time you completed Area 5.\nThat's \\%s!": "Recevez \\%s par Zone 5 terminee.\nSoit \\%s !",
    "Get \\%s for each time you completed Area 6.\nThat's \\%s!": "Recevez \\%s par Zone 6 terminee.\nSoit \\%s !",
    "Get \\%s for each time you completed Area 7.\nThat's \\%s!": "Recevez \\%s par Zone 7 terminee.\nSoit \\%s !",
    "Get \\%s for each time you completed the game.\nThat's \\%s!": "Recevez \\%s par jeu termine.\nSoit \\%s !",
    "Get \\%s for each time you completed the game\nstarting from Area 1 without using continues.\nThat's \\%s!":
        "Recevez \\%s par jeu fini depuis Zone 1\nsans utiliser de continue.\nSoit \\%s !",
    "Get \\%s for each time you completed the game\nstarting from Area 4 without using continues.\nThat's \\%s!":
        "Recevez \\%s par jeu fini depuis Zone 4\nsans utiliser de continue.\nSoit \\%s !",
    "Get \\%s for each time you completed the game\nstarting from Area 7 without using continues.\nThat's \\%s!":
        "Recevez \\%s par jeu fini depuis Zone 7\nsans utiliser de continue.\nSoit \\%s !",
    "Get \\%s for each life remaining after\ncompleting the game.\nThat's \\%s!":
        "Recevez \\%s par vie restante apres\navoir termine le jeu.\nSoit \\%s !",

    # 98..99: Highway shoot-em-up
    "Heat Eye slows down the action. Using it\ndepletes the Heat Eye gauge shown under\nyour HP bar. The gauge refills over time.":
        "L'Oeil Heat ralentit le temps. L'utiliser\nvide la jauge Heat sous vos PV.\nLa jauge se remplit avec le temps.",
    "Withdraw into the car to reload.\nHold <Sign:3> to stay inside the car.\nWhile inside, Kiryu will not get hit,\nbut the car will take damage instead.\nIt's game over if the car's HP reaches 0.":
        "S'abriter dans la voiture pour recharger.\nMaintenir <Sign:3> pour rester a l'abri.\nKiryu sera protege mais la voiture\nsubira les degats a sa place.\nFin de partie si les PV tombent a 0.",

    # 100..119: Cabaret Club operational
    "Wants to talk": "Veut discuter",
    "Wants to party": "Veut s'amuser",
    "Club sales have reached %d0000 yen.": "Ventes du club : %d0000 yens.",
    "%s's sales have reached %d0000 yen.": "Ventes de %s : %d0000 yens.",
    "Check requested for table No. %d.": "Addition table n %d.",
    "<Color:255,0,0,255>Could not seat guest due to lack of girls.<Color:Default>":
        "<Color:255,0,0,255>Hotesse manquante : client non place.<Color:Default>",
    "<Color:255,0,0,255>Rival's sales are up!<Color:Default>":
        "<Color:255,0,0,255>Les rivaux montent !<Color:Default>",
    "<Color:255,0,0,255>%d guest(s) have left due to rival's interference.<Color:Default>":
        "<Color:255,0,0,255>%d client(s) partis a cause des rivaux.<Color:Default>",
    "Time for the check.": "L'addition !",
    "Wants to be pampered": "Veut etre chouchoute",
    "Target Club Mars Area customers.\nIncrease fan base in this area.":
        "Cibler la clientele Club Mars.\nAugmenter vos fans dans la zone.",
    "Target Club Moon Area customers.\nThey are critical and difficult.":
        "Cibler la clientele Club Moon.\nClients tres exigeants.",
    "More fans from word-of-mouth bonus!": "Bonus de fans : bouche-a-oreille !",
    "Slightly more fans from word-of-mouth.": "Quelques fans par le bouche-a-oreille.",
    "Challenge received from Club Mars.": "Defi recu du Club Mars.",
    "Challenge received from Club Jupiter.": "Defi recu du Club Jupiter.",
    "Challenge received from Club Mercury.": "Defi recu du Club Mercure.",
    "Challenge received from Club Venus.": "Defi recu du Club Venus.",
    "Challenge received from Club Moon.": "Defi recu du Club Moon.",
    "Challenge received from multiple rivals.": "Defis recus de multiples rivaux.",

    # 120..149: System & inventories
    "Use the left stick to select a destination.": "Utilisez stick gauche pour destination.",
    "Sent items to hideout's storage.": "Objets envoyes au Coffre.",
    "Could not send some items due to item's storage limit.": "Coffre plein : envoi impossible.",
    "Use <Sign:6> and <Sign:4> to switch between abilities tabs.": "Utilisez <Sign:6> et <Sign:4> pour changer d'onglets.",
    "Use <Sign:6> and <Sign:4> to switch between items/weapons.": "Utilisez <Sign:6> et <Sign:4> pour armes/objets.",
    "Temporarily switch to Easy difficulty?": "Passer en difficulte Facile ?",
    "Are you sure you want to switch to Easy?": "Voulez-vous passer en Facile ?",
    "Your carried weapons list is full.\nSelect a weapon to move to the Item Box.":
        "Liste d'armes transportees pleine.\nChoisir une arme vers le Coffre.",
    "Your item list is full.\nSelect an item to move to the Item Box.":
        "Inventaire plein.\nChoisir un objet vers le Coffre.",
    "No items selected. Okay to proceed?": "Rien de choisi. Continuer ?",
    "Are you sure you want to suspend?": "Voulez-vous suspendre ?",
    "Use this title?": "Ce titre ?",
    "Cancel the order request?\n(Items given will be returned.)":
        "Annuler la commande ?\n(Objets fournis rendus.)",
    "Shogi is 5 points a game.\nWill you pay?": "Shogi : 5 points la partie.\nPayer ?",
    "Upload PlayStation\x7fVita save data\nto the server and overwrite?":
        "Envoyer donnees PS Vita\nsur serveur et ecraser ?",
    "Overwrite PlayStation\x7fVita save data\nwith data on the server?":
        "Ecraser donnees PS Vita\navec celles du serveur ?",
    "Upload PlayStation\x7f3 save data\nto the server and overwrite?":
        "Envoyer donnees PS3\nsur serveur et ecraser ?",
    "Upload PlayStation\x7f4 save data\nto the server and overwrite?":
        "Envoyer donnees PS4\nsur serveur et ecraser ?",
    "The save data on the server has a higher\ncharacter level (experience points). Are you sure\nyou want to upload and overwrite that data?":
        "Donnees serveur de niveau superieur.\nVoulez-vous vraiment ecraser\nces donnees ?",
    "The save data on the server has a longer\nplay time. Are you sure you want to upload\nand overwrite that data?":
        "Donnees serveur avec plus de jeu.\nVoulez-vous vraiment ecraser\nces donnees ?",
    "The save data on the server has a lower\ncharacter level (experience points). Are you sure\nyou want to download and overwrite this data?":
        "Donnees serveur de niveau inferieur.\nVoulez-vous vraiment ecraser\nces donnees ?",
    "The save data on the server has a shorter\nplay time. Are you sure you want to download\nand overwrite this data?":
        "Donnees serveur avec moins de jeu.\nVoulez-vous vraiment ecraser\nces donnees ?",
    "Repair weapon with a repair kit?": "Reparer arme avec ce kit ?",
    "Your health and heat are full. Use anyway?": "Vie et Heat au max. Utiliser quand meme ?",
    "Return to barracks?": "Caserne ?",
    "Return to Climax Battles menu?": "Retour au menu Climax ?",
    "Use this nickname?": "Ce pseudo ?",
    "Once purchased this cannot be changed. Okay to proceed?": "Achat definitif. Continuer ?",
    "Okay to proceed?": "Continuer ?",
    "Do you want to withdraw?": "Voulez-vous quitter ?",

    # 150..179: PSN, tags, pool & gambling
    "Purchase the Yakuza 0 PlayStation?Vita Game Pack to play. Do you want to access the PlayStation\x7fStore?":
        "Achetez le Pack PS Vita Yakuza 0 pour jouer. Ouvrir le PlayStation\x7fStore ?",
    "Cancel wooden tag exchange?\nTags already exchanged will be paid back in cash.":
        "Annuler echange de plaques ?\nPlaques echangees remboursees en cash.",
    "Cancel chip exchange?\nChips already exchanged will be paid back in cash.":
        "Annuler echange de jetons ?\nJetons echanges remourses en cash.",
    "You don't need to use that now.": "Inutile d'utiliser ca.",
    "You can't use that here.": "Inutilisable ici.",
    "You can't equip that on this character.": "Equipement impossible sur ce perso.",
    "No skills to equip.": "Rien a equiper.",
    "You aren't entitled to equip that.": "Vous ne pouvez pas equiper ceci.",
    "Download failed. Save data not\nuploaded to the server.":
        "Echec telechargement.\nDonnees non envoyees au serveur.",
    "Uploading. Do not turn off the power.\nIt may cause data to become corrupted.":
        "Envoi en cours. N'eteignez pas.\nRisque de corrompre les donnees.",
    "Downloading. Do not turn off the power.\nIt may cause data to become corrupted.":
        "Reception en cours. N'eteignez pas.\nRisque de corrompre les donnees.",
    "Because you were disconnected from your previous match,\nyour %s ranking points dropped by %s.\nKeep the following in mind when playing:\n-Play using a reliable connection.\n-Avoid power loss due to low battery charge or error.\n-Do not intentionally turn off the power or disconnect.":
        "Deconnexion au match precedent :\npoints de rang %s reduits de %s.\nRappels pour jouer :\n-Connexion stable requise.\n-Eviter coupures de courant.\n-Ne pas deconnecter volontairement.",
    "Cannot upload because you\nsigned out from PSN.": "Envoi impossible :\ndeconnecte du PSN.",
    "Cannot download because you\nsigned out from PSN.": "Reception impossible :\ndeconnecte du PSN.",
    "Checking server data.\nDo not turn off the power.\nIt may cause data to become corrupted.":
        "Verification serveur. N'eteignez pas.\nRisque de corrompre les donnees.",
    "Not enough points.\nReturning to mode selection screen.": "Points insuffisants.\nRetour au choix du mode.",
    "2 wireless controllers are\nrequired for this mode.": "2 manettes sans fil\nrequises pour ce mode.",
    "Upload/download not available because\nanother user's save data has been loaded.\n\nIf you want to reset the save data,\ndelete the Basic Free Yakuza 0 App for\nPlayStation\x7fVita from the home screen.":
        "Transfert indisponible : donnees\nd'un autre utilisateur chargees.\n\nPour reinitialiser, supprimez\nl'application Yakuza 0 de l'ecran d'accueil.",
    "You cannot change the difficulty during a battle.": "Changement de difficulte impossible en combat.",
    "Because you were disconnected from your previous\nmatch, you can only make changes up to\n%s = %d - %d =%d yen. Keep the following in mind.":
        "Deconnexion du match precedent :\nlimite fixee a %s = %d - %d =%d yens.\nGardez cela a l'esprit.",
    "Because you were disconnected from your previous\nmatch, you can unfortunately only make changes\nup to %s = %d yen. Keep the following in mind.":
        "Deconnexion du match precedent :\nlimite fixee a %s = %d yens.\nGardez cela a l'esprit.",
    "Thank you for playing %s.\nYou can now make changes up to\n%s = %d + %d = %d yen.":
        "Merci d'avoir joue a %s.\nVous pouvez miser jusqu'a\n%s = %d + %d = %d yens.",
    "Select the Mahjong King stakes.\nYou can make changes up to %s %s = %d yen.\nYou cannot set stakes exceeding your current money.":
        "Mises du Roi du Mahjong.\nLimite : %s %s = %d yens.\nMises superieures a votre cash interdites.",
    "Congratulations!\nYou've played %s enough times that you can now\nchange up to the maximum limit of %s = %d yen.":
        "Felicitations !\nAssez de parties a %s pour debloquer\nla limite max de %s = %d yens.",
    "-Play using a reliable connection.\n-Avoid power loss due to low battery charge or error.\n-Do not intentionally turn off the power or disconnect.":
        "-Connexion stable requise.\n-Eviter coupures de courant ou batterie faible.\n-Ne pas deconnecter expres.",
    "-Play using a reliable connection.\n-Avoid power loss or disconnect due to input error.\n-Do not intentionally turn off the power or disconnect.":
        "-Connexion stable requise.\n-Eviter erreurs de saisie ou coupures.\n-Ne pas deconnecter expres.",
    "What you could buy with the money lost": "Achats possibles avec l'argent perdu",
    "What you could buy with the money earned": "Ce qu'on peut acheter avec les gains",
    "Place the cue ball.": "Placer la blanche.",
    "Select a pocket in which to sink the ball.": "Choisir la poche pour la bille.",

    # 180..199: Billiards shots & chatter
    "Select amount to bet.": "Montant a miser.",
    "Time for some fun.": "Amusons-nous.",
    "You okay?/You need to relax.": "Ca va ? / Detends-toi.",
    "Eight ball in the side pocket.": "La 8 dans la poche du milieu.",
    "Eight ball in the corner pocket.": "Bille 8 dans la poche de coin.",
    "Okay, you ready?": "Alors, pret ?",
    "Ain't you the shit?/Whoa.": "Pas mal du tout !",
    "Oh, I lost that one.": "J'ai rate ca.",
    "Give me a break, will you?": "Laisse-moi un peu !",
    "What a shot!/Now that was something!/Amazing!": "Quel tir ! / Superbe coup ! / Incroyable !",
    "This ends here./I'm going to win.": "Ca s'arrete la. / Je vais gagner.",
    "Wait, what?/How'd that happen?": "Attends, quoi ? / Comment ca ?",
    "That's the best you can do?/Hee hee.": "C'est tout ce que tu sais faire ?",
    "Are you kidding me?/Huh.": "Tu rigoles ? / Hein.",
    "Ah.../You the man.": "Bien joue.",
    "That's all you got?/Lame.": "C'est tout ? / Nul.",
    "Eight in the side.": "La 8 au milieu.",
    "Eight in the corner.": "La 8 dans le coin.",
    "What the hell?/Shit...": "Fait chier...",
    "In the Dark": "A l'aveugle",

    # 200..209: Hostess Makeover
    "Change the shape and color of eyebrows.": "Changer forme et teinte des sourcils.",
    "Change the shape and color of eyelashes.": "Changer forme et teinte des cils.",
    "Change the shape and color of eyeliner.": "Changer le trace d'eye-liner.",
    "Change the shape and color of eye shadow.": "Changer le fard a paupieres.",
    "Change the color of color contacts.": "Changer la teinte des lentilles.",
    "Revert back to the first outfit?\nPurchased items will remain.":
        "Revenir a la tenue de depart ?\nAchats effectues conserves.",
    "You can save a dress to your favorites.": "Enregistrer robe en favori.",
    "Open for business with this lineup?": "Ouvrir avec ces hotesses ?",
    "Partnered with %s.": "Partenaire : %s.",
    "Partner With Business?": "Devenir partenaire ?",

    # 210..227: Casino Poker & Roulette bets
    "Place your bet.\nYou can bet up to %s chips.": "Placez votre mise.\nJusqu'a %s jetons.",
    "Are you done betting?": "Fin des mises ?",
    "The payout is %d to 1.\nYou can bet %s more chips.": "Paiement : %d/1.\nEncore %s jetons.",
    "The payout is %d to 1.\n%s chips have been bet.": "Paiement : %d/1.\n%s jetons mises.",
    "The payout is %d to 1.\nYou can't place any more bets.": "Paiement : %d contre 1.\nPlus aucune mise possible.",
    "You don't have enough chips.": "Pas assez de jetons.",
    "Play for High Stakes": "Jouer grosses mises",
    "End this round.": "Fin du tour.",
    "How to Play": "Commandes",
    "Select the betting limit.": "Choisir limite de mise.",
    "You will be dealt 2 cards. Use these and\n5 community cards to create a 5-card\npoker hand.":
        "2 cartes en main. Combinez-les aux\n5 cartes communes pour faire\nla meilleure main.",
    "You will be dealt 3 cards, 2 to keep and 1\nto discard. Use these and 5 community cards\nto create a 5-card poker hand.":
        "3 cartes recues : 2 gardees, 1 jetee.\nCombinez-les aux 5 communes pour faire\nla meilleure main.",
    "You will be dealt 4 cards. Use 2 of your\nprivate cards and 3 out of 5 community cards\nto create a 5-card poker hand.":
        "4 cartes recues. Utilisez 2 d'entre elles\net 3 des 5 cartes communes pour former\nune main de poker.",
    "Learn how to play Texas Hold'em\nby playing a practice game.":
        "Apprenez le Texas Hold'em\nvia une partie d'entrainement.",
    "Learn how to play Pineapple Hold'em\nby playing a practice game.":
        "Apprenez le Pineapple Hold'em\nvia une partie d'entrainement.",
    "Learn how to play Omaha Hold'em\nby playing a practice game.":
        "Apprenez l'Omaha Hold'em\nvia une partie d'entrainement.",
    "Can't win with this.": "Impossible de gagner.",
    "Time to raise!": "Je relance !",

    # 228..250: Karaoke, Fishing rods & tournament
    "I Wanna Take You Home": "I Wanna Take You Home",
    "A crowd favorite that everyone enjoys!": "Un classique adore de tous !",
    "A hit single from the Popstar Prince, Miracle Johnson!": "Un tube planetaire de Miracle Johnson !",
    "More songs are available in the retail version.": "Plus de morceaux dans la version complete.",
    "A fishing rod for beginners. Used for river or\nsea fishing. Not very good.":
        "Canne debutant. Pour riviere ou mer.\nAssez mediocre.",
    "A rod suited for river fishing. Raises chances\nof river fish biting and sensitivity.":
        "Canne de riviere. Bonne sensibilite et\ntouches accrues en eau douce.",
    "A rod ideal for river fishing. Very sensitive,\nwith good reach. Makes it easier to hook fish.":
        "Canne riviere ideale. Tres sensible et\nbonne portee. Ferrage aise.",
    "A rod suited for sea fishing. Raises chances\nof sea fish biting and sensitivity.":
        "Canne marine. Bonne sensibilite et\ntouches accrues en mer.",
    "A rod ideal for sea fishing. Very sensitive,\nwith good reach. Makes it easier to hook fish.":
        "Canne mer ideale. Tres sensible et\ngrande portee. Ferrage aise.",
    "An extremely high-performance rod for river\nand sea fishing. Raises chances of fish\nbiting and has a very long reach.":
        "Canne d'elite riviere et mer. Sensibilite\nextreme et immense portee de tir.",
    "Declare nine terminals/honors for draw?": "Declarer 9 tuiles terminales (nulle) ?",
    "Return to Mode Selection": "Retour au choix du mode",
    "Test your mahjong skills against various\nopponents and aim to win the Dragon Series.\nIt costs 500 points to enter the first time,\nbut is free afterwards.":
        "Affrontez divers adversaires au mahjong\net tentez de remporter la Dragon Series.\n500 pts la premiere entree, gratuit ensuite.",
    "Test your mahjong skills against various\nopponents and aim to win the Dragon Series\nYou need 500 points to enter.":
        "Affrontez divers adversaires au mahjong\net tentez de remporter la Dragon Series.\n500 points requis pour entrer.",
    "Test your mahjong skills against various\nopponents and aim to win the Dragon Series.":
        "Affrontez divers adversaires au mahjong\net gagnez la serie du Dragon.",
    "Test your mahjong skills against various\nopponents and aim to win the Dragon Series.\nIt costs 500 points to enter the first time, but\nis free afterwards.":
        "Affrontez divers adversaires au mahjong\net gagnez la Dragon Series.\n500 pts a la 1re entree, puis gratuit.",
    "Four Concealed Pungs with Single Wait": "Quatre brelans caches (attente 1)",
    "Robbing the Kong": "Vol de Kong",
}

# Add Mahjong Rank Rewards (kyus and dans)
for kyu in range(9, 0, -1):
    for players in [4, 3]:
        suffix = "th" if kyu in [9, 8, 7, 6, 5, 4] else ("rd" if kyu == 3 else ("nd" if kyu == 2 else "st"))
        en_k = f"Get \\%s the first time you reach {kyu}{suffix} kyu in\n{players}-{'player' if players==4 else 'Player'} mahjong, using either Kiryu or Majima."
        fr_k = f"Recevez \\%s au rang {kyu}e kyu atteint\nau mahjong a {players}, avec Kiryu ou Majima."
        P1[en_k] = fr_k

for dan in range(1, 11):
    for players in [4, 3]:
        suffix = "st" if dan == 1 else ("nd" if dan == 2 else ("rd" if dan == 3 else "th"))
        en_d = f"Get \\%s the first time you reach {dan}{suffix} dan in\n{players}-{'player' if players==4 else 'Player'} mahjong, using either Kiryu or Majima."
        fr_d = f"Recevez \\%s au rang {dan}e dan atteint\nau mahjong a {players}, avec Kiryu ou Majima."
        P1[en_d] = fr_d
