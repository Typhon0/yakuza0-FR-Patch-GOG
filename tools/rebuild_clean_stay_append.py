#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_stay_append.py
----------------------------------
Rebuilds release_gog/data/staypar/stay.par using the 2048-byte sector-aligned
append-only model (Gold Rule 3 of AGENTS.md):
1. Starts from pristine clean GOG stay.par (804,864 bytes).
2. Keeps all untouched files (including response_wanderer at 0x9a000) at their exact
   100% pristine original sector offsets.
3. Translates all completion & management tables with translate_rgg_table
   (rebuilding string column headers meta2[2] dynamically to prevent crash 0x371324).
4. Appends all modified French tables at the end of the archive, each strictly aligned
   to 2048-byte (0x800) boundaries.
5. Pads archive to 2048-byte sector boundary.
"""

import os
import sys
import struct
import json

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from scratch.test_generic_table_translator import translate_rgg_table
from tools.stay_translations_data import STAY_TRANSLATIONS
from tools.sllz import compress_sllz

EXTRA_TRANSLATIONS = {
    # search_arms_location RESULT1
    "Visited an old, run-down shopping district\nnear Sotenbori...": "Visite d'un vieux quartier commercant delabre\npres de Sotenbori...",
    "Tracked down the location of a dangerous\ninsurgent cabal...": "Localisation d'une dangereuse cabale\nd'insurges...",
    "Arrived in a small town with barely\na soul in sight...": "Arrivee dans une petite ville sans presque\nune ame qui vive...",
    "Searching for the destination, struggling\nagainst a fierce blizzard...": "En quete du lieu, luttant contre un blizzard\nglacial...",
    "After wandering through a maze of narrow streets\nlined with old houses...": "Apres avoir erre dans un lacis de ruelles\nbordees de vieilles maisons...",
    "Deep in the mountains, where no roads go...": "Au fin fond des montagnes, la ou nulle route ne mene...",
    "On a deserted street corner in the middle of\nthe city...": "Au coin d'une rue deserte en plein coeur\nde la ville...",
    "Looks like a quiet residential area...": "On dirait un quartier residentiel paisible...",
    "Walking along a deserted road that seemed\nto go on forever...": "Marchant sur une route deserte qui semblait\nsans fin...",
    "Approached a grand building in a prime downtown\narea...": "Approche d'un imposant edifice au coeur du quartier\nd'affaires...",
    "Traveled toward the destination, trying not to get\ndistracted by the breathtaking natural beauty...": "En route vers l'objectif, en evitant d'etre distrait\npar la beaute des paysages...",
    "Some rumors says they're researching alien\ntechnologies at this cleverly hidden base...": "Des rumeurs disent qu'on y etudie des technologies\naliennes dans cette base secrete...",
    "Walking down a hidden set of stairs in a slum\nknown for its violence and lawlessness...": "Descente d'un escalier derobe dans un bidonville\nrepute pour sa violence...",
    "Arrived at the bar, a favorite of the capital's\npower brokers...": "Arrivee au bar couru des figures d'influence\nde la capitale...",
    "Walking among crowded stalls, the buyers\nloudly haggling with sellers...": "Arpentant les etals combles ou acheteurs\net vendeurs marchandent ferme...",
    "A huge stadium rises above rows of brick houses,\nbut under its shadow...": "Un stade colossal domine des rangees de briques,\nmais dans son ombre...",
    "Persuaded a local fisherman to provide transportation\nto an island...": "Convaincu un pecheur local de naviguer\njusqu'a une ile...",
    "After countless hours wandering through\nthis spooky forest...": "Apres d'interminables heures d'errance\ndans cette foret sinistre...",
    "One expansive mansion after another lines this\nexclusive residential district...": "D'immenses manoirs se succedent dans ce quartier\nresidentiel tres chic...",
    "Roaming the slums of Hong Kong, with jumbled dwellings\nand varied smells...": "Errant dans les bas-fonds de Hong Kong, entre bicoques\net odeurs epicees...",
    "Crossing the desert was an arduous journey...": "La traversee du desert fut un voyage epuisant...",

    # search_arms_location RESULT2
    "Managed to sneak into the store despite\nsuspicious looks from the shoppers!": "Reussi a se glisser dans la boutique malgre les regards\nsoupconneux des chalands !",
    "The office sign was so dirty it was illegible.\nInside, the shady group was waiting for me!": "L'enseigne etait illisible de crasse.\nA l'interieur, le groupe louche attendait !",
    "Stepped inside an inconspicuous old family house!": "Penetre dans une modeste maison familiale sans histoire !",
    "Made it to the settlement! But the locals\nseem less than welcoming...": "Arrive au village ! Mais les autochtones semblent\nplutot hostiles...",
    "There it was, the renowned dojo!": "Il etait la : le celebre dojo !",
    "No one noticed as I entered the posh building\nand made my way to the elevator in the lobby!": "Personne n'a rien vu quand je suis entre dans l'immeuble\nchic vers l'ascenseur du hall !",
    "An older man appeared before us. How will the\nnegotiations go!?": "Un homme d'age mur est apparu. Comment vont tourner\nles pourparlers !?",
    "There they were--in an office building with\nthe name plate so worn out it was illegible.": "Les voila : dans un bureau dont la plaque etait\ntrop usee pour etre dechiffree.",
    "Arrived at a large residence, took a deep breath,\nand rang the doorbell!": "Arrive devant une vaste demeure, profonde inspiration,\net sonnette actionnee !",
    "Made contact with some locals! They seemed reluctant,\nbut eventually agreed to talk!": "Contact pris avec les gens du coin ! Reticents d'abord,\nils ont fini par parler !",
    "Encountered a shady individual!\nHe beckoned me to follow him...": "Rencontre d'un type louche !\nIl m'a fait signe de le suivre...",
    "Found a secret facility, and managed to sneak past\nthe guards and get inside unseen!": "Installation secrete trouvee, gardes esquives\net entree reussie sans bruit !",
    "Based on prior research, made contact with someone\nwilling to offer access for a fee!": "Grace a mes recherches, contact noue avec un passeur\nmoyennant finances !",
    "Far from towns, beyond steep peaks and deadly\nprecipices, was the hidden village!": "Loin des villes, au-dela des cimes et des gouffres,\nle village secret se dressait !",
    "Stumbled into the bar! It was pretty empty,\nso I wasted no time approaching the barman.": "Entre dans le bar ! Presque deserte, j'ai vite\naborde le barman sans attendre.",
    "Far from towns, beyond steep peaks and deadly\nprecipices, was a hidden village!": "Loin des villes, par-dela les pics et les precipices,\nvoila le village cache !",
    "Entered the premises, gave the password, and was ushered\ninto a back room! How will the negotiations go!?": "Entre sur place, mot de passe donne, conduit dans l'arriere-salle !\nComment se passeront les tractations !?",
    "The contact was already waiting! He nodded in greeting,\nbut seems untalkative.": "Le contact m'attendait deja ! Un hochement de tete,\nmais l'homme est peu bavard.",
    "We were immediately surrounded by a group of thugs!\nTime to start worrying!": "Aussitot encercles par une bande de malfrats !\nIl y a de quoi s'inquieter !",
    "We were suddenly surrounded by threatening shadows!\nWill the negotiations go smoothly!?": "Soudainement cerne par des ombres menacantes !\nLes tractations iront-elles sans accroc !?",
    "Found a tightly-guarded building, and hesitated only\nslightly before heading inside!": "Trouve un batiment ultra-garde, courte hesitation\navant d'y penetrer !",
    "Reached an eerie place, when through the swirling\nsnow, someone appeared to come toward me!": "Arrive dans un lieu lugubre, a travers la tourmente de neige,\nquelqu'un s'avance vers moi !",
    "I encountered a shady individual!\nHe beckoned me to follow him...": "J'ai rencontre un individu louche !\nIl m'a fait signe de le suivre...",
    "Managed to infiltrate a hideout! Not much time\nto explore...": "Infiltration d'une planque reussie ! Peu de temps\npour fouiller...",
    "Found the ancient ruins! The atmosphere is eerie,\nbut we must press on...": "Ruines antiques trouvees ! L'ambiance est sinistre,\nmais il faut continuer...",
    "Found some ancient ruins! The atmosphere is eerie,\nbut we must press on...": "Quelques ruines antiques trouvees ! Ambiance lugubre,\nmais il faut avancer...",
    "A group of men suddenly appeared! After putting a canvas\nsack over my head, they took me to the negotiations!": "Un groupe a surgi ! Sac en toile sur la tete,\nils m'ont conduit aux tractations !",
    "We found the auction house! How many bids can we win\nwithout going over budget!?": "Salle des ventes trouvee ! Combien de lots gagner\nsans exploser le budget !?",
    "The teahouse hides a secret back room for customers\nwho want more than gunpowder tea.": "La maison de the cache une arriere-salle pour les clients\nen quete d'autre chose que du the gunpowder.",

    # search_arms_location HINTS
    "Dispatch agents to locations in\nJapan. Expenses are lower when\ncompared to dispatching overseas.": "Envoyez des agents au Japon.\nLes frais sont moins eleves que pour\nun depart a l'etranger.",
    "Offers a wide range of locations,\nranging from the cold north to\nthe jungles of Central America.": "Offre un large choix de lieux,\ndes glaces du grand nord jusqu'aux\njungles d'Amerique centrale.",
    "Difficult to get to, with\nsupposedly nothing to see apart\nfrom miles of snow and ice... ": "Difficile d'acces, avec a priori\nrien d'autre a voir que des lieues\nde neige et de glace...",
    "A continent with lush natural\nenvironments. Some areas suffer\nfrom instability and crime.": "Un continent a la nature luxuriante.\nCertaines regions souffrent de criminalite\net d'instabilite.",
    "Cold climates can make travel\nchallenging. Local crime groups\nare good suppliers of weapons.": "Le climat glacial complique les trajets.\nLes cartels locaux sont d'excellents\nfournisseurs d'armes.",
    "Famous big cities and tourist\ndestinations with mafia families\npulling strings from the shadows.": "Grandes metropoles celebres ou des familles\nmafieuses tirent les ficelles\ndans l'ombre.",
    "Areas known for oil, extreme\nwealth, and abject poverty.\nTravel can be dangerous.": "Regions celebres pour leur petrole et richesses.\nLes deplacements peuvent y etre\nperilleux.",
    "Many nations have been gaining\neconomic momentum but some areas\nare still unstable.": "Pays en plein essor economique,\nmais plusieurs zones restent encore\ninstables.",
    "A continent with a rich natural\nenvironment. Some areas suffer\nfrom internal conflicts.": "Un continent riche en ressources naturelles.\nCertaines contrees subissent des conflits\ninternes.",

    # tougijyo_realtime_quest
    "Crowd Pleaser": "Favori du public",
    "Knock down an opponent!": "Renversez un adversaire !",
    "Perform a Heat Action!": "Effectuez une action Heat !",
    "Land a counterattack!": "Placez une contre-attaque !",
    "Guard to block an attack!": "Bloquez une attaque en garde !",
    "Land a Finishing Blow!": "Placez un coup de grace !",
    "Evade incoming attacks!": "Esquivez les attaques ennemies !",
    "Throw your opponent!": "Projetez votre adversaire !",
    "Perform a Style Action!": "Effectuez une action de style !",

    # Mahjong in activity_list
    "Go out with Riichi Ippatsu": "Gagner avec un Riichi Ippatsu",
    "Go out with Full Straight": "Gagner avec un Full Straight",

    # search_arms_result_picture (multiline cells)
    "Sudden setback!\nInterference from the locals.": "Coup dur soudain !\nInterference des locaux.",
    "Hair-raising encounter!\nAttacked by a wild beast.": "Rencontre terrifiante !\nAttaque par une bete sauvage.",
    "Unforeseen difficulties!\nNegotiation partners get too inquisitive.": "Difficultes imprevues !\nPartenaires de negociation trop curieux.",
    "Caught in the crossfire!\nSupplier's foes launch a surprise attack.": "Pris entre deux feux !\nAttaque surprise des ennemis du fournisseur.",
    "Things get awkward!\nNegotiation partner's mom steps in.": "La situation devient embarrassante !\nLa mere du negociateur s'interpose.",
    "Language barrier!\nNo choice but to rely on signs and gestures.": "Barriere de la langue !\nPas d'autre choix que les signes et gestes.",
    "Tight spot!\nSurrounded by men who look like bad news.": "Mauvaise passe !\nEntoure d'individus peu recommandables.",
    "In luck we trust!\nNegotiations come down to a coin toss.": "En s'en remettant a la chance !\nNegociations decidees a pile ou face.",
    "Twins or clones!?\nNegotiation partner's doppelganger appears.": "Jumeaux ou clones !?\nLe sosie du negociateur apparait.",
    "Dangerous temptations!\nApproached by a third party with a side deal.": "Dangereuses tentations !\nApproche par un tiers avec un deal louche.",
    "Good reception!\nGreeted in a very promising way.": "Tres bon accueil !\nAccueilli de facon tres prometteuse.",
    "It's too spicy!\nTreated to a hellishly hot meal.": "C'est trop epice !\nInvite a un repas diaboliquement pimente.",
    "Can't read maps!\nMission successful, but got lost on the way home.": "Incapable de lire une carte !\nMission reussie, mais egare sur le retour.",
    "Crazy unbelievable success!\nMission went swimmingly and treasure was found!": "Succes incroyable et fou !\nMission royale et tresor trouve !",
    "Resounding success!\nMission went even better than hoped.": "Succes retentissant !\nLa mission s'est deroulee au-dela des esperances.",
    "Yarr, thar be treasure!\nMiraculously stumbled upon treasure.": "Mille sabords, voila un tresor !\nTresor deniche par pur miracle.",
    "Success!\nMission went reasonably well.": "Succes !\nLa mission s'est plutot bien passee.",

    # ultimate
    "Overcome all these attackers!": "Triomphez de tous ces assaillants !",
    "Beat all enemies while fighting in an altered state.": "Battez tous les ennemis dans un etat modifie.",
    "Defeat all foes using Dragon of Dojima style without taking damage.": "Terrassez tous les ennemis en style Dragon de Dojima sans degats.",
    "Beat all enemies using Mad Dog of Shimano style without taking damage.": "Battez tous les ennemis en style Chien enrage de Shimano sans degats.",
}

def load_master_stay_dict():
    master = dict(STAY_TRANSLATIONS)
    for fn in ['scratch/activity_translations.json', 'scratch/agent_translations.json', 'scratch/location_translations.json']:
        if os.path.exists(fn):
            with open(fn, 'r', encoding='utf-8') as f:
                master.update(json.load(f))
    master.update(EXTRA_TRANSLATIONS)

    clean = {}
    for k, v in master.items():
        s = v.replace('œ', 'oe').replace('Œ', 'OE')
        s = s.replace('’', "'").replace('‘', "'")
        s = s.replace('«', '"').replace('»', '"')
        s = s.replace('“', '"').replace('”', '"')
        s = s.replace('…', '...')
        s = s.replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')
        clean[k] = s
    return clean

def rebuild_clean_stay_append(clean_par_path, rel_par_path, output_path):
    print(f"[+] Reading pristine clean stay.par: {clean_par_path}")
    with open(clean_par_path, 'rb') as f:
        clean_bytes = f.read()
    clean_par = parse_par(clean_bytes)

    print(f"[+] Reading reference release stay.par: {rel_par_path}")
    with open(rel_par_path, 'rb') as f:
        rel_bytes = f.read()
    rel_par = parse_par(rel_bytes)

    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_bytes[16:32])
    name_offset = 32 + folder_count * 64
    rebuilt_stay = bytearray(clean_bytes)

    clean_dict = load_master_stay_dict()
    print(f"[+] Loaded master stay dictionary with {len(clean_dict)} entries")

    TRANSLATED_TABLES = {
        'activity_list.bin_c',
        'money_island_tarent.bin_c',
        'caba_cast_info.bin_c',
        'cabaret_island_area.bin_c',
        'search_arms_agent.bin_c',
        'search_arms_location.bin_c',
        'search_arms_result_picture.bin_c',
        'battle_result.bin_c',
        'ultimate.bin_c',
        'tougijyo_realtime_quest.bin_c',
        'response_roulette.bin_c',
    }

    PRESERVE_FRENCH_REL = {
        'correlation_person.bin_c',
        'tutorial.bin_c',
        'virtue_shop.bin_c',
    }

    modified_count = 0
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = clean_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')

        payload = None
        target_flags = 0
        target_u_sz = 0
        target_c_sz = 0

        if name in PRESERVE_FRENCH_REL and name in rel_par:
            r_flags, r_u, r_c, r_data = rel_par[name]
            payload = r_data
            target_flags = r_flags
            target_u_sz = r_u
            target_c_sz = r_c
        elif name in TRANSLATED_TABLES and name in clean_par:
            c_flags, c_u, c_c, c_data = clean_par[name]
            is_comp = bool(c_flags & 0x80000000) or c_data.startswith(b'SLLZ')
            decomp = decompress_sllz(c_data) if is_comp else c_data

            translated = translate_rgg_table(decomp, clean_dict)
            comp = compress_sllz(translated)
            payload = comp
            target_flags = 0x80000000
            target_u_sz = len(translated)
            target_c_sz = len(comp)

        if payload is not None:
            aligned_off = (len(rebuilt_stay) + 2047) & ~2047
            if aligned_off > len(rebuilt_stay):
                rebuilt_stay.extend(b'\x00' * (aligned_off - len(rebuilt_stay)))
            new_offset = len(rebuilt_stay)
            rebuilt_stay.extend(payload)

            e_off = file_table_offset + i * 32
            struct.pack_into('>4I', rebuilt_stay, e_off, target_flags, target_u_sz, target_c_sz, new_offset)
            modified_count += 1
            print(f"  [+] Appended {name:32s} at sector {hex(new_offset)} (u_sz={target_u_sz:6d}, c_sz={target_c_sz:6d})")

    final_aligned = (len(rebuilt_stay) + 2047) & ~2047
    if final_aligned > len(rebuilt_stay):
        rebuilt_stay.extend(b'\x00' * (final_aligned - len(rebuilt_stay)))

    with open(output_path, 'wb') as f:
        f.write(rebuilt_stay)
    print(f"\n[SUCCESS] Wrote {output_path} ({len(rebuilt_stay)} bytes, {modified_count} modified files) with strict 2048-byte sector alignment!")
    return True

if __name__ == '__main__':
    clean_p = sys.argv[1] if len(sys.argv) > 1 else 'par_original/stay.par'
    if not os.path.exists(clean_p):
        clean_p = 'scratch/diag/current_active_par/data/staypar/stay.par'
    rel_p = sys.argv[2] if len(sys.argv) > 2 else 'release_gog/data/staypar/stay.par'
    out_p = sys.argv[3] if len(sys.argv) > 3 else 'release_gog/data/staypar/stay.par'
    rebuild_clean_stay_append(clean_p, rel_p, out_p)
