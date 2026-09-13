#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_boot_append.py
----------------------------------
Rebuilds boot.par using the proven 2048-byte sector-aligned append-only model:
1. Starts from pristine clean GOG boot.par (par_original/boot.par, 1,712,128 bytes).
2. Keeps all untouched files at their exact 100% pristine original sector offsets.
3. Appends all French translated tables at the end of the archive,
   strictly aligned to 2048-byte (0x800) sector boundaries.
4. Complies with the 58,232-byte static heap allocation limit for substories (0x371324).
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz
from tools.clean_patch_data import TEXT_REPLACEMENTS
from tools.build_calibrated_substories import get_calibrated_substories_bin

def get_clean_french_item_bin():
    fr_boot_path = 'par_original/boot_steam_fr.par'
    with open(fr_boot_path, 'rb') as f:
        fr_files = parse_par(f.read())
    raw = fr_files['item.bin_c'][3]
    decomp = decompress_sllz(raw) if raw[:4] == b'SLLZ' else raw
    
    buf = bytearray(decomp)
    for bad, good in TEXT_REPLACEMENTS[:5]:
        diff = len(bad) - len(good)
        padded = good + b'\x00' * diff
        buf = bytearray(bytes(buf).replace(bad, padded))
        
    comp = compress_sllz(bytes(buf))
    return 0x80000000, len(buf), len(comp), comp

def get_clean_french_encounter_popup_bin():
    fr_boot_path = 'par_original/boot_steam_fr.par'
    with open(fr_boot_path, 'rb') as f:
        fr_files = parse_par(f.read())
    raw = fr_files['encounter_pupup_message.bin_c'][3]
    decomp = decompress_sllz(raw) if raw.startswith(b'SLLZ') else raw
    assert len(decomp) == 24908, f"Unexpected encounter_pupup_message.bin_c length: {len(decomp)}"
    comp = compress_sllz(decomp)
    return 0x80000000, len(decomp), len(comp), comp

def get_french_ability_bin(fr_par):
    raw = fr_par['ability.bin_c'][3]
    dec = decompress_sllz(raw) if raw[:4] == b'SLLZ' else raw
    comp = compress_sllz(dec)
    return 0x80000000, len(dec), len(comp), comp

def get_french_complete_heat_bin(fr_par):
    raw = fr_par['complete_heat.bin_c'][3]
    dec = decompress_sllz(raw) if raw[:4] == b'SLLZ' else raw
    comp = compress_sllz(dec)
    return 0x80000000, len(dec), len(comp), comp

def get_french_complete_shisho_bin(fr_par):
    raw = fr_par['complete_shisho.bin_c'][3]
    dec = decompress_sllz(raw) if raw[:4] == b'SLLZ' else raw
    # uncompressed in vanilla GOG
    return 0x00000000, len(dec), len(dec), dec

def get_french_tips_tutorial_bin(fr_par):
    raw = fr_par['tips_tutorial.bin_c'][3]
    dec = decompress_sllz(raw) if raw[:4] == b'SLLZ' else raw
    # clean mojibakes
    dec = dec.replace(b'\xc3\xa9', b'\xe9')
    dec = dec.replace(b'\xe2\x80\x99', b"'")
    comp = compress_sllz(dec)
    return 0x80000000, len(dec), len(comp), comp

def get_french_mail_bin(fr_par):
    raw = fr_par['mail.bin_c'][3]
    dec = decompress_sllz(raw) if raw[:4] == b'SLLZ' else raw
    # uncompressed in vanilla GOG
    return 0x00000000, len(dec), len(dec), dec

def get_french_money_result_bin(fr_par):
    raw = fr_par['money_result.bin_c'][3]
    dec = decompress_sllz(raw) if raw[:4] == b'SLLZ' else raw
    # uncompressed in vanilla GOG
    return 0x00000000, len(dec), len(dec), dec

def get_french_restaurant_menu_bin(fr_par):
    raw = fr_par['restaurant_menu.bin_c'][3]
    dec = decompress_sllz(raw) if raw[:4] == b'SLLZ' else raw
    comp = compress_sllz(dec)
    return 0x80000000, len(dec), len(comp), comp

def get_merged_string_tbl_bin(clean_par, rel_par, fr_par):
    def get_stbl_dict(raw):
        dec = decompress_sllz(raw) if raw[:4] == b'SLLZ' else raw
        num_groups = struct.unpack('>I', dec[:4])[0]
        strs = {}
        for i in range(1, num_groups + 1):
            cnt, off = struct.unpack('>2I', dec[i*8:(i+1)*8])
            for j in range(cnt):
                ptr_loc = off + j * 4
                old_ptr = struct.unpack('>I', dec[ptr_loc : ptr_loc + 4])[0]
                if old_ptr == 0:
                    continue
                s = dec[old_ptr:].split(b'\x00')[0]
                strs[(i, j)] = s
        return strs

    clean_raw = clean_par['string_tbl.bin_c'][3]
    clean_dec = decompress_sllz(clean_raw) if clean_raw[:4] == b'SLLZ' else clean_raw
    clean_strs = get_stbl_dict(clean_raw)
    rel_strs = get_stbl_dict(rel_par['string_tbl.bin_c'][3])
    fr_strs = get_stbl_dict(fr_par['string_tbl.bin_c'][3])

    merged_strs = dict(rel_strs)
    for k, c_s in clean_strs.items():
        r_s = rel_strs.get(k, c_s)
        f_s = fr_strs.get(k, c_s)
        if r_s == c_s and f_s != c_s:
            merged_strs[k] = f_s

    num_groups = struct.unpack('>I', clean_dec[:4])[0]
    header = bytearray(clean_dec[:32284])
    new_pool = bytearray()

    for i in range(1, num_groups + 1):
        cnt, off = struct.unpack('>2I', clean_dec[i*8:(i+1)*8])
        for j in range(cnt):
            ptr_loc = off + j * 4
            old_ptr = struct.unpack('>I', clean_dec[ptr_loc : ptr_loc + 4])[0]
            if old_ptr == 0:
                continue
            s_bytes = merged_strs[(i, j)]
            new_ptr = 32284 + len(new_pool)
            struct.pack_into('>I', header, ptr_loc, new_ptr)
            new_pool.extend(s_bytes + b'\x00')

    rebuilt_dec = bytes(header + new_pool)
    comp = compress_sllz(rebuilt_dec)
    return 0x80000000, len(rebuilt_dec), len(comp), comp

def rebuild_boot_par():
    clean_boot_bytes = open('par_original/boot.par', 'rb').read()
    rel_boot_bytes = open('release_gog/data/bootpar/boot.par', 'rb').read()
    fr_boot_bytes = open('par_original/boot_steam_fr.par', 'rb').read()

    clean_par = parse_par(clean_boot_bytes)
    rel_par = parse_par(rel_boot_bytes)
    fr_par = parse_par(fr_boot_bytes)

    TARGET_FILES = [
        'caption.bin_c',
        'explanation_main_scenario.bin_c',
        'explanation_sub_story.bin_c',
        'item.bin_c',
        'string_tbl.bin_c',
        'battle_deck_list.bin_c',
        'encounter_pupup_message.bin_c',
        'ability.bin_c',
        'complete_heat.bin_c',
        'complete_shisho.bin_c',
        'tips_tutorial.bin_c',
        'mail.bin_c',
        'money_result.bin_c',
        'restaurant_menu.bin_c',
    ]

    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_boot_bytes[16:32])
    name_offset = 32 + folder_count * 64
    rebuilt_boot = bytearray(clean_boot_bytes)

    print(f"Rebuilding boot.par with {len(TARGET_FILES)} target files...")
    modified_count = 0
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = clean_boot_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')
        
        if name in TARGET_FILES:
            if name == 'item.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_french_item_bin()
            elif name == 'encounter_pupup_message.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_french_encounter_popup_bin()
            elif name == 'explanation_sub_story.bin_c':
                r_flags, r_u, r_c, r_data = get_calibrated_substories_bin()
            elif name == 'string_tbl.bin_c':
                r_flags, r_u, r_c, r_data = get_merged_string_tbl_bin(clean_par, rel_par, fr_par)
            elif name == 'ability.bin_c':
                r_flags, r_u, r_c, r_data = get_french_ability_bin(fr_par)
            elif name == 'complete_heat.bin_c':
                r_flags, r_u, r_c, r_data = get_french_complete_heat_bin(fr_par)
            elif name == 'complete_shisho.bin_c':
                r_flags, r_u, r_c, r_data = get_french_complete_shisho_bin(fr_par)
            elif name == 'tips_tutorial.bin_c':
                r_flags, r_u, r_c, r_data = get_french_tips_tutorial_bin(fr_par)
            elif name == 'mail.bin_c':
                r_flags, r_u, r_c, r_data = get_french_mail_bin(fr_par)
            elif name == 'money_result.bin_c':
                r_flags, r_u, r_c, r_data = get_french_money_result_bin(fr_par)
            elif name == 'restaurant_menu.bin_c':
                r_flags, r_u, r_c, r_data = get_french_restaurant_menu_bin(fr_par)
            else:
                # caption.bin_c, explanation_main_scenario.bin_c, battle_deck_list.bin_c
                r_flags, r_u, r_c, r_data = rel_par[name]
            
            # Align strictly to 2048-byte sector boundary
            aligned_off = (len(rebuilt_boot) + 2047) & ~2047
            if aligned_off > len(rebuilt_boot):
                rebuilt_boot.extend(b'\x00' * (aligned_off - len(rebuilt_boot)))
            new_offset = len(rebuilt_boot)
            rebuilt_boot.extend(r_data)
            
            e_off = file_table_offset + i * 32
            struct.pack_into('>4I', rebuilt_boot, e_off, r_flags, r_u, r_c, new_offset)
            modified_count += 1
            print(f"  [+] Appended {name:32s} at 2048-aligned offset {hex(new_offset)} (u_sz={r_u}, c_sz={r_c})")

    # Pad archive total size to 2048-byte multiple
    final_aligned = (len(rebuilt_boot) + 2047) & ~2047
    if final_aligned > len(rebuilt_boot):
        rebuilt_boot.extend(b'\x00' * (final_aligned - len(rebuilt_boot)))

    with open('boot_test.par', 'wb') as f:
        f.write(rebuilt_boot)
    with open('release_gog/data/bootpar/boot.par', 'wb') as f:
        f.write(rebuilt_boot)
    print(f"[SUCCESS] Wrote release_gog/data/bootpar/boot.par ({len(rebuilt_boot)} bytes, {modified_count} modified files) with 100% pristine sector alignment!")

if __name__ == '__main__':
    rebuild_boot_par()
