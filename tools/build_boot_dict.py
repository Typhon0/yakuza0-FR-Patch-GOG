# -*- coding: utf-8 -*-
"""
build_boot_dict.py

Constructs full translation mapping for string_tbl.bin_c in boot.par.
Validates len(FR) <= len(EN), no \xc7, and Latin-1 encoding for all strings.
"""

import re
import json

def clean_fr(s):
    return s.replace('œ', 'oe').replace('Œ', 'OE').replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')

def build_all_boot_translations():
    trans = {}

    # 1. Character splash cards
    trans["Tsukasa Sagawa\nPatriarch of the Sagawa Family,\nRetainer to the Omi Alliance Chairman"] = \
        "Tsukasa Sagawa\nPatriarche de la famille Sagawa,\nVassal du president de l'Alliance Omi"
    trans["Osamu Kashiwagi\nCaptain of the Kazama Family,\nA Dojima Family Subsidiary"] = \
        "Osamu Kashiwagi\nCapitaine de la famille Kazama,\nAffiliee a la famille Dojima"
    trans["Takashi Nihara\nActing Second Chairman of the Tojo Clan"] = \
        "Takashi Nihara\nPresident par interim du clan Tojo"

    # 2. Real Estate Royale
    trans["Add extra funds. \nExtra funds increase the success rate and shorten exploration time."] = \
        "Ajouter des fonds.\nLes fonds augmentent le succes et reduisent le temps."
    trans["You don't have sufficient funds."] = "Vous n'avez pas assez de fonds."
    trans["Invest in this property?"] = "Investir dans ce bien ?"
    trans["Purchase this property?"] = "Acheter cette propriete ?"
    trans["You've gained control of the area."] = "Zone sous controle !"
    trans["Join the battle?"] = "Rejoindre le combat ?"
    trans["Conduct business with this set-up?"] = "Lancer avec cette equipe ?"
    trans["You failed to gain control."] = "Echec de prise de controle."
    trans["You failed to protect your properties."] = "Echec de protection des biens."
    trans["You won the money battle."] = "Bataille financiere gagnee !"
    trans["Payout collection stopped until you\nresolve problems in the area."] = \
        "Recolte suspendue tant que\nles litiges persistent."
    trans["Time to Payout"] = "Recolte des benefices"
    trans["About the Agency Menu"] = "Menu de gestion"
    trans["View the menu controls."] = "Commandes du menu"

    # 3. Arcade & Minigame bonuses
    trans["Win a total of 10,000 Tokens.\nBonus: %s x%s\n(Note: there are no further goals beyond this)"] = \
        "Gagner 10 000 jetons au total.\nBonus : %s x%s\n(Aucun autre objectif au-dela)"
    trans["Get \\%s for each game played.\nThat's \\%s!"] = "Recevez \\%s par partie jouee.\nSoit \\%s !"
    trans["Get \\%s for each point scored.\nThat's \\%s!"] = "Recevez \\%s par point marque.\nSoit \\%s !"
    trans["Get \\%s for each stage completed.\nThat's \\%s!"] = "Recevez \\%s par niveau fini.\nSoit \\%s !"
    trans["Get \\%s for each banana collected.\nThat's \\%s!"] = "Recevez \\%s par banane prise.\nSoit \\%s !"
    trans["Get \\%s for each time you completed World 1\nafter using continues.\nThat's \\%s!"] = \
        "Recevez \\%s par Monde 1 fini\navec des continues.\nSoit \\%s !"
    trans["Get \\%s for each time you completed World 2\nafter using continues.\nThat's \\%s!"] = \
        "Recevez \\%s par Monde 2 fini\navec des continues.\nSoit \\%s !"
    trans["Get \\%s for each time you completed World 3\nafter using continues.\nThat's \\%s!"] = \
        "Recevez \\%s par Monde 3 fini\navec des continues.\nSoit \\%s !"
    trans["Get \\%s for each time you completed World 1\nwithout using continues.\nThat's \\%s!"] = \
        "Recevez \\%s par Monde 1 fini\nsans continue.\nSoit \\%s !"
    trans["Get \\%s for each time you completed World 2\nwithout using continues.\nThat's \\%s!"] = \
        "Recevez \\%s par Monde 2 fini\nsans continue.\nSoit \\%s !"
    trans["Get \\%s for each time you completed World 3\nwithout using continues.\nThat's \\%s!"] = \
        "Recevez \\%s par Monde 3 fini\nsans continue.\nSoit \\%s !"
    trans["Get \\%s for each point.\nThat's \\%s!\n*No bonus for zero or negative points."] = \
        "Recevez \\%s par point.\nSoit \\%s !\n*Pas de bonus pour zero ou moins."
    trans["Get \\%s for each time you ranked first in\n4-player mahjong.\nThat's \\%s!"] = \
        "Recevez \\%s par 1re place\nau mahjong a 4.\nSoit \\%s !"
    trans["Get \\%s for each time you ranked second in\n4-player mahjong.\nThat's \\%s!"] = \
        "Recevez \\%s par 2e place\nau mahjong a 4.\nSoit \\%s !"
    trans["Get \\%s for each time you ranked third in\n4-player mahjong.\nThat's \\%s!"] = \
        "Recevez \\%s par 3e place\nau mahjong a 4.\nSoit \\%s !"
    trans["Get \\%s for each time you ranked first in\n3-player mahjong.\nThat's \\%s!"] = \
        "Recevez \\%s par 1re place\nau mahjong a 3.\nSoit \\%s !"
    trans["Get \\%s for each time you ranked second in\n3-player mahjong.\nThat's \\%s!"] = \
        "Recevez \\%s par 2e place\nau mahjong a 3.\nSoit \\%s !"

    # 4. Mahjong Rank Rewards (Kyus and Dans)
    for kyu in range(9, 0, -1):
        for players in [4, 3]:
            suffix = "th" if kyu in [9, 8, 7, 6, 5, 4] else ("rd" if kyu == 3 else ("nd" if kyu == 2 else "st"))
            en_k = f"Get \\%s the first time you reach {kyu}{suffix} kyu in\n{players}-{'player' if players==4 else 'Player'} mahjong, using either Kiryu or Majima."
            fr_k = f"Recevez \\%s la 1re fois le rang {kyu}e kyu atteint\nau mahjong a {players}, avec Kiryu ou Majima."
            trans[en_k] = fr_k

    for dan in range(1, 11):
        for players in [4, 3]:
            suffix = "st" if dan == 1 else ("nd" if dan == 2 else ("rd" if dan == 3 else "th"))
            en_d = f"Get \\%s the first time you reach {dan}{suffix} dan in\n{players}-{'player' if players==4 else 'Player'} mahjong, using either Kiryu or Majima."
            fr_d = f"Recevez \\%s la 1re fois le rang {dan}e dan atteint\nau mahjong a {players}, avec Kiryu ou Majima."
            trans[en_d] = fr_d

    # OutRun Area Completions
    trans["Score (Adjusted for Level)"] = "Score (selon niveau)"
    trans["Get \\%s for each point scored. That's \\%s!\n*MEDIUM: -20,000 points x times played\n HARD: -50,000 points x times played"] = \
        "Recevez \\%s par point marque. Soit \\%s !\n*MOYEN: -20 000 pts x parties\n DIFFICILE: -50 000 pts x parties"
    trans["Get \\%s for each removed gem.\nThat's \\%s!\n*Up to 9999 gems per game."] = \
        "Recevez \\%s par gemme retiree.\nSoit \\%s !\n*Jusqu'a 9999 gemmes par jeu."
    trans["Get \\%s for each level in the highest\nlevel reached in a game.\nThat's \\%s!"] = \
        "Recevez \\%s par niveau atteint\nau plus haut niveau en partie.\nSoit \\%s !"
    trans["Completions From Area 1"] = "Finis depuis la Zone 1"
    trans["Completions From Area 4"] = "Finis depuis la Zone 4"
    trans["Completions From Area 7"] = "Finis depuis la Zone 7"
    for a in range(1, 8):
        trans[f"Get \\%s for each time you completed Area {a}.\nThat's \\%s!"] = f"Recevez \\%s par Zone {a} terminee.\nSoit \\%s !"
    trans["Get \\%s for each time you completed the game.\nThat's \\%s!"] = "Recevez \\%s par jeu termine.\nSoit \\%s !"
    trans["Get \\%s for each time you completed the game\nstarting from Area 1 without using continues.\nThat's \\%s!"] = \
        "Recevez \\%s par jeu fini depuis Zone 1\nsans utiliser de continue.\nSoit \\%s !"
    trans["Get \\%s for each time you completed the game\nstarting from Area 4 without using continues.\nThat's \\%s!"] = \
        "Recevez \\%s par jeu fini depuis Zone 4\nsans utiliser de continue.\nSoit \\%s !"
    trans["Get \\%s for each time you completed the game\nstarting from Area 7 without using continues.\nThat's \\%s!"] = \
        "Recevez \\%s par jeu fini depuis Zone 7\nsans utiliser de continue.\nSoit \\%s !"
    trans["Get \\%s for each life remaining after\ncompleting the game.\nThat's \\%s!"] = \
        "Recevez \\%s par vie restante apres\navoir termine le jeu.\nSoit \\%s !"

    # Shooting sequence
    trans["Heat Eye slows down the action. Using it\ndepletes the Heat Eye gauge shown under\nyour HP bar. The gauge refills over time."] = \
        "L'Oeil Heat ralentit le temps. L'utiliser\nvide la jauge Heat sous vos PV.\nLa jauge se remplit avec le temps."
    trans["Withdraw into the car to reload.\nHold <Sign:3> to stay inside the car.\nWhile inside, Kiryu will not get hit,\nbut the car will take damage instead.\nIt's game over if the car's HP reaches 0."] = \
        "S'abriter dans la voiture pour recharger.\nMaintenir <Sign:3> pour rester a l'abri.\nKiryu sera protege mais la voiture\nsubira les degats a sa place.\nFin de partie si les PV tombent a 0."

    return trans

if __name__ == '__main__':
    t = build_all_boot_translations()
    print(f'Built base {len(t)} translations.')
    errs = 0
    for en, fr in t.items():
        fr_b = clean_fr(fr).encode('latin1')
        en_b = en.encode('latin1')
        if len(fr_b) > len(en_b):
            print(f'TOO LONG: {len(fr_b)} > {len(en_b)}: {repr(en[:40])}')
            errs += 1
    print('Errors:', errs)
