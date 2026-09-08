# -*- coding: utf-8 -*-
"""
translate_stay_par.py

Translates all target tables in release_gog/data/staypar/stay.par:
- money_island_tarent.bin_c
- caba_cast_info.bin_c
- cabaret_island_area.bin_c
- battle_result.bin_c
- ultimate.bin_c
- search_arms_location.bin_c
- search_arms_agent.bin_c
- search_arms_result_picture.bin_c
- activity_list.bin_c
- virtue_shop.bin_c
"""

import os
import sys
import shutil
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from scratch.test_generic_table_translator import translate_rgg_table
from tools.stay_translations_data import STAY_TRANSLATIONS
from tools.sllz import compress_sllz

TARGET_FILES = [
    'money_island_tarent.bin_c',
    'caba_cast_info.bin_c',
    'cabaret_island_area.bin_c',
    'battle_result.bin_c',
    'ultimate.bin_c',
    'search_arms_location.bin_c',
    'search_arms_agent.bin_c',
    'search_arms_result_picture.bin_c',
    'activity_list.bin_c',
    'virtue_shop.bin_c',
]

def repack_par(orig_bytes, file_replacements={}):
    """
    orig_bytes: raw bytes of PAR file
    file_replacements: dict of filename -> (flags, uncomp_size, comp_size, data_bytes)
    """
    magic, unkA, unkB, unkC = struct.unpack('>4I', orig_bytes[:16])
    assert magic == 0x50415243, f"Not a valid PAR archive: {hex(magic)}"
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
        
        # Align to 64 bytes
        aligned_off = (curr_off + 63) & ~63
        if aligned_off > len(rebuilt):
            rebuilt.extend(b'\x00' * (aligned_off - len(rebuilt)))
        
        new_file_offset = len(rebuilt)
        rebuilt.extend(n_data)
        curr_off = len(rebuilt)
        
        # Update entry in rebuilt
        struct.pack_into('>4I', rebuilt, item['entry_offset'], n_flags, n_u_sz, n_c_sz, new_file_offset)
    
    return bytes(rebuilt)

def main():
    stay_path = 'release_gog/data/staypar/stay.par'
    bak_path = stay_path + '.bak'
    if not os.path.exists(bak_path):
        print(f"[+] Creating backup {bak_path}...")
        shutil.copyfile(stay_path, bak_path)

    with open(stay_path, 'rb') as f:
        orig_stay = f.read()

    parsed = parse_par(orig_stay)
    replacements = {}

    print(f"[+] Processing {len(TARGET_FILES)} tables in stay.par...")
    for fn in TARGET_FILES:
        if fn not in parsed:
            print(f"[!] Warning: {fn} not found in stay.par")
            continue
        flags, u_sz, c_sz, data = parsed[fn]
        decomp = decompress_sllz(data) if data[:4] == b'SLLZ' else data
        translated = translate_rgg_table(decomp, STAY_TRANSLATIONS)
        compressed = compress_sllz(translated)
        new_flags = 0x80000000
        replacements[fn] = (new_flags, len(translated), len(compressed), compressed)
        print(f"  - {fn:32s}: raw {u_sz} -> {len(translated)} bytes, comp {c_sz} -> {len(compressed)} bytes")

    print("[+] Repacking stay.par...")
    new_stay = repack_par(orig_stay, replacements)

    with open(stay_path, 'wb') as f:
        f.write(new_stay)
    print(f"[+] Successfully wrote updated {stay_path} ({len(new_stay)} bytes)")

    # Verify repacked stay.par
    print("[+] Verifying repacked stay.par...")
    v_parsed = parse_par(new_stay)
    assert len(v_parsed) == len(parsed), "File count mismatch after repack"
    for fn in TARGET_FILES:
        _, vu_sz, vc_sz, vdata = v_parsed[fn]
        vdecomp = decompress_sllz(vdata)
        assert len(vdecomp) == replacements[fn][1], f"Decompressed size mismatch for {fn}"
        assert vdata[:4] == b'SLLZ', f"Not SLLZ compressed for {fn}"
    print("[+] Verification SUCCESSFUL: all files decompress cleanly!")

if __name__ == '__main__':
    main()
