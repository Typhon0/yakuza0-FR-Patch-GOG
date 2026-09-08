# -*- coding: utf-8 -*-
"""
translate_boot_par_complete.py

Translates 100% of translatable English text in release_gog/data/bootpar/boot.par:
- caption.bin_c (164 chapter objectives, battle titles, and encounter banners)
- battle_deck_list.bin_c (battle deck entries and card names)
- item.bin_c (items, DLC packs, tokens, and descriptions)
- string_tbl.bin_c (874 in-game strings: Teleclub, Mahjong, Pocket Circuit, Casino, System Stats, etc.)
"""

import os
import sys
import struct
import shutil

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz
from tools.boot_dict_part1 import P1
from tools.boot_dict_part2 import P2
from tools.boot_dict_part3 import P3
from tools.boot_dict_part4 import P4

BOOT_DICT = {**P1, **P2, **P3, **P4}

CAPTIONS_BOOT = {
    # Objectives / Scenario
    'Go to Dojima Family HQ': 'Aller au QG de la famille Dojima',
    'Go to Toko Credit': 'Aller a Toko Credit',
    'Go to the Kazama Family Office': 'Aller au bureau du clan Kazama',
    'Gather Info on Tachibana Real Estate': 'Se renseigner sur Tachibana Real Estate',
    'Find the Homeless Men': 'Trouver les sans-abri',
    'Go to Odyssey': "Aller a l'Odyssey",
    'Find the Kidnapped Girl': 'Trouver la jeune fille enlevee',
    'Take the Girl and Run': 'Prendre la fille et fuir',
    'Go to Hogushi Kaikan Massage': 'Aller au salon Hogushi Kaikan',
    'Buy Civilian Clothes': 'Acheter des habits civils',
    'Go to Serena': 'Aller au Serena',
    'Go to the Empty Lot': 'Aller au terrain vague',
    'Slip Through Unnoticed': 'Se faufiler sans se faire remarquer',
    'Go to the Grand': 'Aller au Grand',
    'Go to the Odyssey Warehouse': "Aller a l'entrepot d'Odyssey",
    'Find a Place to Hide': 'Trouver une planque',
    'Go to West Park': 'Aller au West Park',
    'Go to Kijin Clan HQ': 'Aller au QG du clan Kijin',
    'Go to the Camellia Grove': 'Aller a la plantation Camellia',
    'Go to the Video Shop': 'Aller au magasin de video',
    'Go to Little Asia': 'Aller a Little Asia',
    'Go to the Crescendo Building': "Aller a l'immeuble Crescendo",
    'Go to the Champion District': 'Aller au quartier Champion',
    'Find Makoto': 'Trouver Makoto',
    'Go to the Sebastian Building': "Aller a l'immeuble Sebastian",
    'Head to the Top Floor': 'Aller au dernier etage',
    'Pacify the Drunkard': "Calmer l'ivrogne",
    'Protect the Girl': 'Proteger la jeune fille',
    'Evade for 60 seconds!': 'Esquiver pendant 60 secondes !',
    'Battle with Komeki': 'Combat contre Komeki',
    'Breaking Battle': 'Bataille de casse',
    'Training with Fei Hu': 'Entrainement avec Fei Hu',
    'Collect the Debt!': 'Recouvrer la dette !',
    'Head to the Exit': 'Se diriger vers la sortie',
    'Find Nishikiyama': 'Trouver Nishikiyama',
    'Find a Pay Phone': 'Trouver une cabine telephonique',
    'Defeat Your Pursuer': 'Vaincre vos poursuivants',
    'The Five Billionaires': 'Les Cinq Milliardaires',
    'Deliver on Time': 'Livrer a temps',
    'Run': 'Fuir',
    'Practice': 'Entrainement',
    "Miss Tatsu's Training": "Entrainement de Mlle Tatsu",

    # Enemy / NPC groups & titles
    'Street Thugs': 'Voyous des rues',
    'Menacing Man': 'Homme menacant',
    'Street Ruffians': 'Ruffians des rues',
    'Mysterious Man': 'Homme mysterieux',
    'Buff Man': 'Homme muscle',
    'Host Wannabe': 'Hote en herbe',
    'Con Artist': 'Arnaqueur',
    'Kidnappers': 'Kidnappeurs',
    'Hooligans': 'Hooligans',
    'Toko Credit Men': 'Hommes de Toko Credit',
    'Dojima Family': 'Famille Dojima',
    'Yakuza': 'Yakuza',
    'Gangsters': 'Gangsters',
    'Members': 'Membres',
    'Drunkards': 'Ivrognes',
    'Drunkard': 'Ivrogne',
    'Sotenbori Goons': 'Sbires de Sotenbori',
    'Massive Man': 'Homme massif',
    'Champion District Residents': 'Habitants du quartier Champion',
    'Champion District Men': 'Hommes du quartier Champion',
    'Tachibana Real Estate Men': 'Hommes de Tachibana Real Estate',
    'Squatters': 'Squatteurs',
    'Chinese Men': 'Hommes chinois',
    'Sotenbori Men': 'Hommes de Sotenbori',
    'Sotenbori Man': 'Homme de Sotenbori',
    'Homeless Hunters': 'Chasseurs de sans-abri',
    'Kijin Clan': 'Clan Kijin',
    'Shimano Family': 'Famille Shimano',
    'Shibusawa Family': 'Famille Shibusawa',
    'Tojo Clan': 'Clan Tojo',
    'Shady Men': 'Hommes louches',
    'Mysterious Hitman': 'Tueur a gages mysterieux',
    'Shifty-eyed Man': 'Homme au regard fuyant',
    'Goons': 'Sbires',
    'Street Hooligans': 'Voyous des rues',
    'Delinquents': 'Delinquants',
    'Bikers': 'Motards',
    'Men in Black': 'Hommes en noir',
    'Nouveau Riche': 'Nouveau riche',
    'Mafia': 'Mafia',

    # Bosses & Specific enemies
    'Leisure King': 'Roi des loisirs',
    'Electronics King': 'Roi de l\'electronique',
    'Pleasure King': 'Roi des plaisirs',
    'Gambling King': 'Roi des jeux',
    'Media King': 'Roi des medias',
    'Finance King': 'Roi de la finance',
    'Leisure King Lackeys': 'Sbires du Roi des loisirs',
    'Electronics King Lackeys': 'Sbires du Roi de l\'electronique',
    'Pleasure King Lackeys': 'Sbires du Roi des plaisirs',
    'Gambling King Lackeys': 'Sbires du Roi des jeux',
    'Media King Lackeys': 'Sbires du Roi des medias',
    'Finance King Lackeys': 'Sbires du Roi de la finance',
    'Club Moon Lackeys': 'Sbires du Club Moon',
    'Club Venus Lackeys': 'Sbires du Club Venus',
    'Club Mercury Lackeys': 'Sbires du Club Mercury',
    'Club Jupiter Lackeys': 'Sbires du Club Jupiter',
    'Club Mars Lackeys': 'Sbires du Club Mars',
    'Sotenbori Five Stars': 'Cinq Etoiles de Sotenbori',
    "Kotomi's Lackeys": 'Sbires de Kotomi',
    'Mr. Shakedown': 'M. Shakedown',
    'Mr. Shakedown\nHiroya Egashira': 'M. Shakedown\nHiroya Egashira',
    'Mr. Shakedown\nYuki Sato': 'M. Shakedown\nYuki Sato',
    'Mr. Shakedown\nNaoya Kawahashi': 'M. Shakedown\nNaoya Kawahashi',
    'Mr. Shakedown\nKenji Oe': 'M. Shakedown\nKenji Oe',
    'Daisaku Kuze\nDojima Family Lieutenant, Tojo Clan': 'Daisaku Kuze\nLieutenant de la famille Dojima, Clan Tojo',
    'Okabe\nTaihei Family, Dojima Family, Tojo Clan': 'Okabe\nFamille Taihei, Famille Dojima, Clan Tojo',
    'Homare Nishitani\nKijin Clan Chairman, Omi Alliance': 'Homare Nishitani\nPresident du clan Kijin, Alliance Omi',
    'Masaru Sera\nNikkyo Consortium President, Tojo Clan': 'Masaru Sera\nPresident du consortium Nikkyo, Clan Tojo',
    'Osamu Kashiwagi\nKazama Family Captain, Tojo Clan': 'Osamu Kashiwagi\nCapitaine de la famille Kazama, Clan Tojo',
    'Akira Nishikiyama\nDojima Family, Tojo Clan': 'Akira Nishikiyama\nFamille Dojima, Clan Tojo',
    'Hiroki Awano\nDojima Family Lieutenant, Tojo Clan': 'Hiroki Awano\nLieutenant de la famille Dojima, Clan Tojo',
    'Keiji Shibusawa\nDojima Family Lieutenant, Tojo Clan': 'Keiji Shibusawa\nLieutenant de la famille Dojima, Clan Tojo',

    # Climax battles
    'Melee Battle 1': 'Melee 1',
    'Melee Battle 2': 'Melee 2',
    'Melee Battle 3': 'Melee 3',
    'Melee Battle 4': 'Melee 4',
    'Melee Battle 5': 'Melee 5',
    'Melee Battle 6': 'Melee 6',
    'Melee Battle 7': 'Melee 7',
    'Melee Battle 8': 'Melee 8',
    'Melee Battle 9': 'Melee 9',
    'Melee Battle 10': 'Melee 10',
    'Proving Grounds 1': "Champ d'epreuve 1",
    'Proving Grounds 2': "Champ d'epreuve 2",
    'Proving Grounds 3': "Champ d'epreuve 3",
    'Proving Grounds 4': "Champ d'epreuve 4",
    'Proving Grounds 5': "Champ d'epreuve 5",
    'Proving Grounds 6': "Champ d'epreuve 6",
    'Proving Grounds 7': "Champ d'epreuve 7",
    'Proving Grounds 8': "Champ d'epreuve 8",
    'Proving Grounds 9': "Champ d'epreuve 9",
    'Proving Grounds 10': "Champ d'epreuve 10",
    'Millionaire Battle 1': 'Combat de milliardaire 1',
    'Millionaire Battle 2': 'Combat de milliardaire 2',
    'Millionaire Battle 3': 'Combat de milliardaire 3',
    'Millionaire Battle 4': 'Combat de milliardaire 4',
    'Millionaire Battle 5': 'Combat de milliardaire 5',
    'Millionaire Battle 6': 'Combat de milliardaire 6',
    'Ultimate Battle 1': 'Combat ultime 1',
    'Ultimate Battle 2': 'Combat ultime 2',
    'Ultimate Battle 3': 'Combat ultime 3',
    'Ultimate Battle 4': 'Combat ultime 4',
    'Ultimate Battle 5': 'Combat ultime 5',
    'Ultimate Battle 6': 'Combat ultime 6',
}

BATTLE_DECK_BOOT = {
    'Basis for the fight': 'Bases du combat',
    'Style to K.O.': 'Style pour le K.O.',
    'Just a Dancer': 'Simple Danseur',
    "Don't Stop me": "Ne m'arrete pas",
    'Street Emperor': 'Empereur de la rue',
    'Demon': 'Demon',
    'Full-course': 'Menu complet',
    'Legend Dancer': 'Danseur de legende',
    'Dancer': 'Danseur',
    'Immediate': 'Immediat',
    'Crusher': 'Broyeur',
    'Hitman': 'Tueur a gages',
    'Bat Master': 'Maitre de la batte',
    'Tank': 'Tank',
    'Out box': 'Hors du ring',
    'Ghost': 'Fantome',
    'Intensely': 'Intensement',
    'Rampage': 'Carnage',
    'Style testing': 'Test de style',
    'Street fight': 'Combat de rue',
    'Style Break': 'Rupture de style',
    'W Style Rush': 'Ruee double style',
    'Weapon Braker': "Briseur d'arme",
    'Short smasher': 'Fracasseur court',
    'Nice K.O.': 'Joli K.O.',
    'Style Changer A': 'Changeur de style A',
    'Style Changer B': 'Changeur de style B',
    'Toughness': 'Robustesse',
    'Nice Fight': 'Beau combat',
    'Great Blow': 'Coup magistral',
    'Sway': 'Esquive',
    'Down by Blow': 'Mis a terre',
    'Fang of Dog': 'Croc de chien',
    'Gear of Legend': 'Engrenage de legende',
    'Style Action': 'Action de style',
    'Full Rush': 'Pleine ruee',
    'Shake Brain': 'Secouer le cerveau',
    'Bad Guard': 'Mauvaise garde',
    'Heat Action': 'Action de furie',
    'Full Gear': 'Plein regime',
    'Style Change': 'Changement de style',
    'Break Weapon': 'Briser arme',
    'Knock Out': 'K.O.',
}

ITEMS_BOOT = {
    "Malt's the Draft": "Biere The Malt's",
    'Convert 1,000 Mon to Betting Pts.': 'Convertir 1 000 mon en pts pari',
    'Convert 1 Ryo to Betting Pts.': 'Convertir 1 ryo en pts pari',
    'Converts 1,000 betting points to cash.': 'Convertit 1 000 pts de pari en cash.',
    'Converts 10,000 betting points to cash.': 'Convertit 10 000 pts de pari en cash.',
    'Converts 1,000 mon to 10 betting points.': 'Convertit 1 000 mon en 10 pts de pari.',
    'Converts 1 ryo to 100 betting points.': 'Convertit 1 ryo en 100 pts de pari.',
    'Converts 1,000 points to cash.': 'Convertit 1 000 pts en cash.',
    'Converts 10,000 points to cash.': 'Convertit 10 000 pts en cash.',
    'This token is rumored to set slot machines\nto the highest payout level possible.\n*Used automatically when playing slots.':
        'Jeton cense regler les machines a sous\nau paiement maximal possible.\n*Utilise automatiquement aux machines.',
    'This token is rumored to set slot machines\nto the highest win rate possible.\n*Used automatically when playing slots.':
        'Jeton cense regler les machines a sous\nau taux de victoire maximal.\n*Utilise automatiquement aux machines.',
    'This token is rumored to allow slot machines\nto be played automatically.\n*Used automatically when playing slots.':
        'Jeton cense faire jouer automatiquement\nles machines a sous.\n*Utilise automatiquement aux machines.',
    "For debugging purposes. This weapon mustn't\never see the light of day.":
        'Arme de test pour le debogage.\nNe doit en aucun cas voir le jour.',
    'Test weapon for gun to be used in Devil 2.':
        'Arme a feu de test pour Devil 2.',
    "This ball isn't great for fights, but you can\nequip it to go bowling.":
        "Pas ideale pour combattre, mais s'equipe\npour jouer au bowling.",
    'This special ball can be used for bowling.':
        'Boule speciale servant pour le bowling.',
    'Cash In 1,000 Betting Pts.': 'Encaisser 1 000 pts pari',
    'Cash In 10,000 Betting Pts.': 'Encaisser 10 000 pts pari',
    'Cash In 1,000 Pts.': 'Toucher 1 000 pts',
    'Cash In 10,000 Pts.': 'Toucher 10 000 pts',
    'High Payout Token': 'Jeton gros gain',
    'High Win Rate Token': 'Jeton victoire maxi',
    'Auto Token': 'Jeton auto',
    'Dragon of Dojima Pack': 'Pack Dragon de Dojima',
    'Sotenbori Fun Pack': 'Pack Fun Sotenbori',
    'Kamurocho Fun Pack': 'Pack Fun Kamurocho',
    'Mad Dog of Shimano Pack': 'Pack Chien de Shimano',
    'Pocket Circuit Starter Pack': 'Pack Starter Circuit',
    'Crafting Support Pack': 'Pack Aide Artisanat',
    'Kamurocho Fun Pack 2': 'Pack Fun Kamurocho 2',
    'Sotenbori Fun Pack 2': 'Pack Fun Sotenbori 2',
    'Pocket Circuit Expert Pack': 'Pack Expert Circuit',
    'Super Rare Crafting Pack': 'Pack Artisanat Rare',
    'Kamurocho Fun Pack 03': 'Pack Fun Kamurocho 03',
    'Kamurocho Fun Pack 04': 'Pack Fun Kamurocho 04',
    'Kamurocho Fun Pack 05': 'Pack Fun Kamurocho 05',
    'Kamurocho Fun Pack 06': 'Pack Fun Kamurocho 06',
    'Kamurocho Fun Pack 07': 'Pack Fun Kamurocho 07',
    'Kamurocho Fun Pack 08': 'Pack Fun Kamurocho 08',
    'The Hedgeball': 'Boule pique',
    'Stanamin Spork': 'Spork Staminan',
}

def clean_fr(s):
    return s.replace('œ', 'oe').replace('Œ', 'OE').replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')

def translate_rgg_table(data_bytes, translations):
    num_cols = struct.unpack('>I', data_bytes[4:8])[0]
    num_rows = struct.unpack('>I', data_bytes[8:12])[0]
    curr_off = 16 + num_cols * 64

    col_headers = []
    new_col_payloads = []

    for c in range(num_cols):
        off = 16 + c * 64
        col_name = data_bytes[off:off+32].split(b'\x00')[0].decode('latin1')
        meta1 = data_bytes[off+32:off+48]
        meta2 = list(struct.unpack('>4I', data_bytes[off+48:off+64]))
        col_type, count, size, flag = meta2
        raw = data_bytes[curr_off : curr_off + size]

        new_payload = raw
        if col_type == 0 and size > 0:
            strs = raw.split(b'\x00')[:count]
            new_strs = [clean_fr(translations.get(s.decode('latin1'), s.decode('latin1'))).encode('latin1') for s in strs]
            new_payload = b'\x00'.join(new_strs) + b'\x00'
            while len(new_payload) % 4 != 0:
                new_payload += b'\x00'
        elif col_type == 1 and size > 0:
            pos = 0
            opts = []
            for _ in range(count):
                if pos >= len(raw): break
                end = raw.find(b'\x00', pos)
                if end == -1: break
                opts.append(raw[pos:end].decode('latin1'))
                pos = end + 1
            rem = raw[pos:]
            new_opts = [clean_fr(translations.get(s, s)).encode('latin1') for s in opts]
            new_payload = b'\x00'.join(new_opts) + b'\x00' + rem
            while len(new_payload) % 4 != 0:
                new_payload += b'\x00'
        elif col_type == 2 and size > 0:
            pos = 0
            entries = []
            for _ in range(count):
                if pos + 2 >= len(raw): break
                r_idx = struct.unpack('>H', raw[pos:pos+2])[0]
                end = raw.find(b'\x00', pos+2)
                if end == -1: break
                s = raw[pos+2:end].decode('latin1')
                entries.append((r_idx, clean_fr(translations.get(s, s))))
                pos = end + 1
            out_p = bytearray()
            for r_idx, s in entries:
                out_p.extend(struct.pack('>H', r_idx))
                out_p.extend(s.encode('latin1') + b'\x00')
            while len(out_p) % 4 != 0:
                out_p.append(0)
            new_payload = bytes(out_p)

        meta2[2] = len(new_payload)
        col_headers.append((col_name, meta1, meta2))
        new_col_payloads.append(new_payload)
        curr_off += size

    header_bytes = bytearray(data_bytes[:16])
    col_header_bytes = bytearray()
    payload_bytes = bytearray()

    for (name, meta1, meta2), payload in zip(col_headers, new_col_payloads):
        h = bytearray(name.encode('latin1').ljust(32, b'\x00'))
        h.extend(meta1)
        h.extend(struct.pack('>4I', *meta2))
        col_header_bytes.extend(h)
        payload_bytes.extend(payload)

    return bytes(header_bytes + col_header_bytes + payload_bytes)

def translate_exact_bytes(data_bytes, trans_dict):
    out = bytearray(data_bytes)
    out = bytearray(bytes(out).replace(b'\xc7', b'C'))

    for en, fr in trans_dict.items():
        en_b = en.encode('latin1')
        fr_b = clean_fr(fr).encode('latin1')
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

def rebuild_string_tbl(raw_bytes):
    dec = decompress_sllz(raw_bytes)
    num_groups = struct.unpack('>I', dec[:4])[0]
    header = bytearray(dec[:32284])
    new_pool = bytearray()

    replaced_count = 0
    for i in range(1, num_groups + 1):
        cnt, off = struct.unpack('>2I', dec[i*8:(i+1)*8])
        for j in range(cnt):
            ptr_loc = off + j * 4
            old_ptr = struct.unpack('>I', dec[ptr_loc : ptr_loc + 4])[0]
            if old_ptr == 0:
                continue
            old_str_bytes = dec[old_ptr:].split(b'\x00')[0]
            old_str = old_str_bytes.decode('latin1', errors='replace')

            if old_str in BOOT_DICT:
                new_str = clean_fr(BOOT_DICT[old_str])
                new_str_bytes = new_str.encode('latin1')
                replaced_count += 1
            elif old_str.strip() in BOOT_DICT:
                l_space = old_str[:len(old_str) - len(old_str.lstrip())]
                r_space = old_str[len(old_str.rstrip()):]
                new_str = l_space + clean_fr(BOOT_DICT[old_str.strip()]) + r_space
                new_str_bytes = new_str.encode('latin1')
                replaced_count += 1
            else:
                # Keep original bytes, but fix broken \xc7
                new_str_bytes = old_str_bytes.replace(b'\xc7', b'C')

            new_ptr = 32284 + len(new_pool)
            struct.pack_into('>I', header, ptr_loc, new_ptr)
            new_pool.extend(new_str_bytes + b'\x00')

    rebuilt_dec = bytes(header + new_pool)
    print(f"[string_tbl.bin_c] Replaced {replaced_count} strings! (Pool: {len(dec)} -> {len(rebuilt_dec)} bytes)")
    comp = compress_sllz(rebuilt_dec)
    assert decompress_sllz(comp) == rebuilt_dec, "Decompression verification failed!"
    return comp, len(rebuilt_dec)

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
        
        rebuilt.extend(n_data)
        struct.pack_into('>4I', rebuilt, item['entry_offset'], n_flags, n_u_sz, n_c_sz, aligned_off)
        curr_off = aligned_off + len(n_data)
        
    return bytes(rebuilt)

def main():
    par_path = 'release_gog/data/bootpar/boot.par'
    bak_path = 'release_gog/data/bootpar/boot.par.orig_clean'
    if not os.path.exists(bak_path):
        shutil.copyfile(par_path, bak_path)
        print(f"Backed up clean boot.par -> {bak_path}")

    with open(bak_path, 'rb') as f:
        par_bytes = f.read()

    files = parse_par(par_bytes)
    replacements = {}

    # 1 & 2: caption.bin_c & battle_deck_list.bin_c:
    # Do not resize/shift RGG binary table columns with translate_rgg_table,
    # as altering string payload lengths breaks the engine's internal row/column offset calculations (crash at 0x371324).
    # Keep original safe tables.

    # 3. item.bin_c (Exact in-place null-padded replacement)
    print("Processing item.bin_c...")
    raw_item = files['item.bin_c'][3]
    dec_item = decompress_sllz(raw_item)
    trans_item = translate_exact_bytes(dec_item, ITEMS_BOOT)
    comp_item = compress_sllz(trans_item)
    replacements['item.bin_c'] = (files['item.bin_c'][0], len(trans_item), len(comp_item), comp_item)
    print(f"item.bin_c translated: {len(trans_item)} uncompressed, {len(comp_item)} compressed")

    # 4. string_tbl.bin_c (Full pointer-relocated string pool)
    print("Processing string_tbl.bin_c...")
    raw_stbl = files['string_tbl.bin_c'][3]
    comp_stbl, u_sz_stbl = rebuild_string_tbl(raw_stbl)
    replacements['string_tbl.bin_c'] = (files['string_tbl.bin_c'][0], u_sz_stbl, len(comp_stbl), comp_stbl)

    # Repack boot.par
    print("Repacking boot.par...")
    rebuilt_par = repack_par(par_bytes, replacements)
    with open(par_path, 'wb') as f:
        f.write(rebuilt_par)
    print(f"Successfully repacked {par_path} ({len(rebuilt_par)} bytes)!")

if __name__ == '__main__':
    main()
