# -*- coding: utf-8 -*-
"""
translate_stay_par_complete.py

Translates 100% of remaining English text in release_gog/data/staypar/stay.par:
- search_arms_location.bin_c (42 strings)
- search_arms_result_picture.bin_c (5 strings)
- response_roulette.bin_c (4 strings)
- tougijyo_realtime_quest.bin_c (1 string)
- controller_explain.bin_c (2 strings)
- activity_list.bin_c (2 Mahjong strings)
"""

import os
import sys
import shutil
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz

STAY_TRANSLATIONS = {
    # search_arms_location.bin_c
    "\x1aA continent with lush natural\nenvironments. Some areas suffer\nfrom instability and crime.":
        "\x1aContinent a la nature sauvage.\nCertaines zones souffrent de\nl'instabilite et du crime.",

    ")Areas known for oil, extreme\nwealth, and abject poverty.\nTravel can be dangerous.":
        ")Zones de petrole, richesse et\nextreme pauvrete.\nVoyage perilleux.",

    "1Many nations have been gaining\neconomic momentum but some areas\nare still unstable.":
        "1Nations en plein essor economique\nmais certaines regions restent\ninstables.",

    "6A continent with a rich natural\nenvironment. Some areas suffer\nfrom internal conflicts.":
        "6Continent riche en ressources.\nCertaines zones souffrent de\nconflits internes.",

    "Tracked down the location of a dangerous\ninsurgent cabal...":
        "Repere le repaire d'un dangereux\ngroupe d'insurges...",

    "Arrived in a small town with barely\na soul in sight...":
        "Arrive dans un bourg sans\name qui vive...",

    "Searching for the destination, struggling\nagainst a fierce blizzard...":
        "Recherche de l'objectif au beau milieu\nd'un blizzard glacial...",

    "After wandering through a maze of narrow streets\nlined with old houses...":
        "Apres avoir erre dans un lacis de ruelles\nbordees de vieilles batisses...",

    "Deep in the mountains, where no roads go...":
        "Au fond des monts, loin de toute route...",

    "On a deserted street corner in the middle of\nthe city...":
        "Au coin d'une rue deserte en plein coeur\nde la ville...",

    "Walking along a deserted road that seemed\nto go on forever...":
        "Sur une route isolee qui semblait\nsans fin...",

    "Traveled toward the destination, trying not to get\ndistracted by the breathtaking natural beauty...":
        "En route vers l'objectif, subjuge par la splendeur\nsauvage des paysages...",

    "Some rumors says they're researching alien\ntechnologies at this cleverly hidden base...":
        "Des rumeurs parlent de recherches extraterrestres\ndans cette base secrete...",

    "Walking down a hidden set of stairs in a slum\nknown for its violence and lawlessness...":
        "Descente d'escaliers dans un bidonville\nconnu pour son non-droit...",

    "Arrived at the bar, a favorite of the capital's\npower brokers...":
        "Arrive au bar prise par les puissants\nde la capitale...",

    "Walking among crowded stalls, the buyers\nloudly haggling with sellers...":
        "Parmi les etals, les acheteurs\nnegocient avec les marchands...",

    "Persuaded a local fisherman to provide transportation\nto an island...":
        "Un pecheur local a accepte de m'emmener\nsur l'ile voisine...",

    "Roaming the slums of Hong Kong, with jumbled dwellings\nand varied smells...":
        "Dans les taudis de Hong Kong, entre bicoques\net odeurs epicees...",

    "Crossing the desert was an arduous journey...":
        "Traverser le desert fut un voyage epuisant...",

    "The office sign was so dirty it was illegible.\nInside, the shady group was waiting for me!":
        "L'enseigne etait illisible. A l'interieur,\nle groupe louche m'attendait !",

    "Made it to the settlement! But the locals\nseem less than welcoming...":
        "Arrive au village ! Mais les locaux\nsont loin d'etre accueillants...",

    "There it was, the renowned dojo!":
        "Le celebre dojo etait bien la !",

    "No one noticed as I entered the posh building\nand made my way to the elevator in the lobby!":
        "Entre dans l'immeuble huppe sans alerter personne,\nvers l'ascenseur du hall !",

    "An older man appeared before us. How will the\nnegotiations go!?":
        "Un vieil homme est apparu.\nQue donneront les pourparlers !?",

    "Arrived at a large residence, took a deep breath,\nand rang the doorbell!":
        "Arrive a la grande demeure, un grand souffle,\net coup de sonnette !",

    "Made contact with some locals! They seemed reluctant,\nbut eventually agreed to talk!":
        "Contact etabli avec les locaux ! Reticents,\nils ont fini par parler !",

    "Encountered a shady individual!\nHe beckoned me to follow him...":
        "Croise un individu louche !\nIl m'a fait signe de le suivre...",

    "Found a secret facility, and managed to sneak past\nthe guards and get inside unseen!":
        "Base secrete trouvee ! Infiltration reussie\nsans alerter la garde !",

    "Based on prior research, made contact with someone\nwilling to offer access for a fee!":
        "Grace aux infos, contact noue avec quelqu'un\npret a m'aider contre cash !",

    "Far from towns, beyond steep peaks and deadly\nprecipices, was the hidden village!":
        "Loin des villes, par-dela les pics rocheux,\nvoici le village cache !",

    "Stumbled into the bar! It was pretty empty,\nso I wasted no time approaching the barman.":
        "Entre dans le bar ! Quasi vide, j'ai vite\naborde le barman sur place.",

    "Far from towns, beyond steep peaks and deadly\nprecipices, was a hidden village!":
        "Loin des villes, par-dela les monts escarpes,\nvoici un village secret !",

    "We were immediately surrounded by a group of thugs!\nTime to start worrying!":
        "Encercle aussitot par une bande de loubards !\nCa commence a chauffer !",

    "Reached an eerie place, when through the swirling\nsnow, someone appeared to come toward me!":
        "Arrive en ce lieu sinistre, une silhouette avance\nvers moi dans le blizzard !",

    "Made it to a settlement! But the locals\nseem less than welcoming...":
        "Arrive au village ! Mais les locaux\nsont peu accueillants...",

    "I encountered a shady individual!\nHe beckoned me to follow him...":
        "Croise un individu louche !\nIl m'a fait signe de le suivre...",

    "Managed to infiltrate a hideout! Not much time\nto explore...":
        "Infiltration dans un repaire ! Peu de temps\npour fouiller...",

    "Found the ancient ruins! The atmosphere is eerie,\nbut we must press on...":
        "Ruines antiques trouvees ! L'ambiance est glauque,\nmais on avance...",

    "Found some ancient ruins! The atmosphere is eerie,\nbut we must press on...":
        "D'antiques ruines trouvees ! Atmospere glauque,\nmais il faut avancer...",

    "A group of men suddenly appeared! After putting a canvas\nsack over my head, they took me to the negotiations!":
        "Des hommes ont surgi ! Un sac sur la tete,\net m'ont amene negocier !",

    "We found the auction house! How many bids can we win\nwithout going over budget!?":
        "Salle des ventes trouvee ! Combien de lots remporter\nsans exploser le budget !?",

    "The teahouse hides a secret back room for customers\nwho want more than gunpowder tea.":
        "Le salon de the cache une arriere-salle secrete\npour clients aux gouts speciaux.",

    # search_arms_result_picture.bin_c
    "Language barrier!\nNo choice but to rely on signs and gestures.":
        "Barriere de langue !\nOblige de communiquer par signes.",

    "In luck we trust!\nNegotiations come down to a coin toss.":
        "Coup de chance !\nNegociation a pile ou face.",

    "Dangerous temptations!\nApproached by a third party with a side deal.":
        "Tentations risquees !\nUn tiers propose un deal parallele.",

    "It's too spicy!\nTreated to a hellishly hot meal.":
        "C'est trop epice !\nRepas diaboliquement pimente.",

    "Can't read maps!\nMission successful, but got lost on the way home.":
        "Perdus en route !\nMission reussie, mais perdus au retour.",

    # response_roulette.bin_c
    "Good to go.": "Pret.",
    "A big bet for <!--Name-->-san.": "Grosse mise: <!--Name-->-san.",
    "Ugh, this sucks.": "Pff, la poisse.",
    "Time to pray.": "Faut prier.",

    # tougijyo_realtime_quest.bin_c
    "Guard to block an attack!": "Bloquer une attaque !",

    # controller_explain.bin_c
    "How to Play": "Commandes",
    "Back to Title": "Ecran titre",

    # activity_list.bin_c
    "Go out with Riichi Ippatsu": "Gagner avec Riichi Ippatsu",
    "Go out with Full Straight": "Gagner avec Grande Suite",
}

def translate_exact_bytes(data_bytes):
    out = bytearray(data_bytes)
    # Fix broken trademark \xc7
    out = bytearray(bytes(out).replace(b'\xc7', b'C'))

    for en, fr in STAY_TRANSLATIONS.items():
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
    if len(sys.argv) > 1:
        target = sys.argv[1]
        data_dir = os.path.join(target, 'data') if os.path.isdir(os.path.join(target, 'data')) else target
        stay_path = os.path.join(data_dir, 'staypar', 'stay.par') if os.path.isdir(data_dir) else target
    else:
        stay_path = 'release_gog/data/staypar/stay.par'
    bak_path = stay_path + '.pre_stay_complete.bak'
    if not os.path.exists(bak_path) and os.path.exists(stay_path):
        print(f"[+] Backing up {stay_path}...")
        shutil.copyfile(stay_path, bak_path)

    with open(stay_path, 'rb') as f:
        orig_bytes = f.read()

    files = parse_par(orig_bytes)
    replacements = {}

    target_files = [
        'search_arms_location.bin_c',
        'search_arms_result_picture.bin_c',
        'response_roulette.bin_c',
        'tougijyo_realtime_quest.bin_c',
        'controller_explain.bin_c',
        'activity_list.bin_c'
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

    print("[+] Repacking stay.par...")
    new_stay = repack_par(orig_bytes, replacements)
    with open(stay_path, 'wb') as f:
        f.write(new_stay)
    print(f"[+] Successfully wrote {stay_path} ({len(new_stay)} bytes)!")

if __name__ == '__main__':
    main()
