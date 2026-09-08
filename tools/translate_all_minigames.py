# -*- coding: utf-8 -*-
"""
translate_all_minigames.py

Applies 100% French localization to all standalone minigame files in release_gog/data/minigame:
1. pokecir.par (pokecir_parts.bin_c)
2. cabaret/caba_item_list.bin_c
3. catfight/catfight_information.bin_c, catfight_string.bin_c, catfight_human_info.bin_c, catfight_human_condition.bin_c
4. bakara/baccarat_cpu.bin_c, bakara/baccarat_gallery_msg.bin_c
5. chohan/minigame_chohan_bakuto.bin_c
6. fishing/fishing_fish_info.bin_c, fishing/fishing_bag_info.bin_c, fishing/fishing_sao_info.bin_c
7. poker/poker_com_*.bin_c (18 files)
"""

import os
import sys
import shutil
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from scratch.test_generic_table_translator import translate_rgg_table
from tools.sllz import compress_sllz
from tools.minigame_translations_data import MINIGAME_TRANSLATIONS
from tools.pause_translations_data import PAUSE_TRANSLATIONS
from scratch.test_pokecir_translation import POKECIR_DESCS

# Combine with pause translations and pocket circuit descs
ALL_MINIGAME = {}
ALL_MINIGAME.update(PAUSE_TRANSLATIONS)
ALL_MINIGAME.update(POKECIR_DESCS)
ALL_MINIGAME.update(MINIGAME_TRANSLATIONS)

# Sanitize all translations: no raw Ç (0xC7)
CLEAN_MINIGAME = {}
for k, v in ALL_MINIGAME.items():
    v_clean = v.replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')
    CLEAN_MINIGAME[k] = v_clean

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

def process_table_file(file_path):
    bak_path = file_path + '.bak'
    if not os.path.exists(bak_path):
        shutil.copyfile(file_path, bak_path)
    
    with open(bak_path, 'rb') as f:
        raw = f.read()
    
    decomp = decompress_sllz(raw)
    translated_table = translate_rgg_table(decomp, CLEAN_MINIGAME)
    comp = compress_sllz(translated_table)
    
    with open(file_path, 'wb') as f:
        f.write(comp)
    print(f"  [+] {os.path.basename(file_path)}: translated table (decomp {len(decomp)} -> {len(translated_table)}, comp {len(raw)} -> {len(comp)})")

def process_pokecir_par():
    par_path = 'release_gog/data/minigame/pokecir.par'
    bak_path = par_path + '.bak'
    if not os.path.exists(bak_path):
        shutil.copyfile(par_path, bak_path)
    
    with open(bak_path, 'rb') as f:
        orig_bytes = f.read()
    
    pfiles = parse_par(orig_bytes)
    flags, u_sz, c_sz, raw_data = pfiles['pokecir_parts.bin_c']
    decomp = bytearray(decompress_sllz(raw_data))
    
    matched = 0
    for en, fr in CLEAN_MINIGAME.items():
        if len(en) < 4: continue
        en_b = en.encode('latin1') + b'\x00'
        fr_b = fr.encode('latin1') + b'\x00'
        if len(fr_b) <= len(en_b):
            pos = 0
            while True:
                idx = decomp.find(en_b, pos)
                if idx == -1: break
                decomp[idx : idx + len(en_b)] = fr_b + b'\x00' * (len(en_b) - len(fr_b))
                matched += 1
                pos = idx + len(en_b)
    
    print(f"  [+] pokecir_parts.bin_c: replaced {matched} strings in-place")
    comp_parts = compress_sllz(bytes(decomp))
    new_par = repack_par(orig_bytes, {
        'pokecir_parts.bin_c': (flags, len(decomp), len(comp_parts), comp_parts)
    })
    with open(par_path, 'wb') as f:
        f.write(new_par)
    print(f"  [+] Repacked {par_path} ({len(new_par)} bytes)")

def main():
    print("[+] Starting minigame translations...")
    
    # 1. Pocket Circuit
    print("\n[1/7] Pocket Circuit:")
    process_pokecir_par()
    
    # 2. Cabaret Makeover
    print("\n[2/7] Cabaret Makeover:")
    process_table_file('release_gog/data/minigame/cabaret/caba_item_list.bin_c')
    
    # 3. Catfight
    print("\n[3/7] Catfight Club:")
    for fn in ['catfight_information.bin_c', 'catfight_string.bin_c', 'catfight_human_info.bin_c', 'catfight_human_condition.bin_c']:
        process_table_file(os.path.join('release_gog/data/minigame/catfight', fn))
    
    # 4. Baccarat
    print("\n[4/7] Baccarat Casino:")
    for fn in ['baccarat_cpu.bin_c', 'baccarat_gallery_msg.bin_c']:
        process_table_file(os.path.join('release_gog/data/minigame/bakara', fn))
    
    # 5. Cho-han
    print("\n[5/7] Cho-han Gambling Hall:")
    process_table_file('release_gog/data/minigame/chohan/minigame_chohan_bakuto.bin_c')
    
    # 6. Fishing
    print("\n[6/7] Fishing:")
    for fn in ['fishing_fish_info.bin_c', 'fishing_bag_info.bin_c', 'fishing_sao_info.bin_c']:
        process_table_file(os.path.join('release_gog/data/minigame/fishing', fn))
    
    # 7. Poker
    print("\n[7/7] Poker Opponents:")
    poker_dir = 'release_gog/data/minigame/poker'
    for fn in sorted(os.listdir(poker_dir)):
        if fn.endswith('.bin_c'):
            process_table_file(os.path.join(poker_dir, fn))
    
    print("\n[+] All minigames translated successfully!")

if __name__ == '__main__':
    main()
