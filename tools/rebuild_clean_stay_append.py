#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_stay_append.py
----------------------------------
Rebuilds stay.par using the proven 2048-byte sector-aligned append-only model:
1. Starts from pristine clean GOG stay.par (804,864 bytes).
2. Keeps all untouched files (including response_wanderer, gamma_setting, etc.)
   at their exact 100% pristine original sector offsets.
3. Appends modified French tables at the end of the archive, strictly aligned
   to 2048-byte (0x800) boundaries.
"""

import os, sys, struct
sys.path.insert(0, '.')
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz
from tools.translate_stay_par_complete import STAY_TRANSLATIONS, translate_exact_bytes

clean_stay_bytes = open('scratch/diag/current_active_par/data/staypar/stay.par', 'rb').read()
clean_par = parse_par(clean_stay_bytes)

# Target tables to localize in stay.par
TARGET_TABLES = [
    'activity_list.bin_c',
    'controller_explain.bin_c',
    'correlation_person.bin_c',
    'response_roulette.bin_c',
    'search_arms_location.bin_c',
    'search_arms_result_picture.bin_c',
    'tougijyo_realtime_quest.bin_c',
    'tutorial.bin_c',
    'virtue_shop.bin_c',
]

# We can also get French versions of correlation_person, tutorial, virtue_shop from release_gog
rel_stay_bytes = open('release_gog/data/staypar/stay.par', 'rb').read()
rel_par = parse_par(rel_stay_bytes)

folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_stay_bytes[16:32])
name_offset = 32 + folder_count * 64
rebuilt_stay = bytearray(clean_stay_bytes)

modified_count = 0
for i in range(file_count):
    n_off = name_offset + i * 64
    name = clean_stay_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')
    
    payload = None
    target_flags = 0x0
    target_u_sz = 0
    target_c_sz = 0
    
    if name in TARGET_TABLES:
        c_flags, c_u, c_c, c_data = clean_par[name]
        is_comp = bool(c_flags & 0x80000000)
        c_decomp = decompress_sllz(c_data) if is_comp else c_data
        
        # Check if we translate in-place with STAY_TRANSLATIONS
        translated = translate_exact_bytes(c_decomp)
        
        # If rel_par has a richer translation (e.g. tutorial or correlation_person)
        if name in ['correlation_person.bin_c', 'tutorial.bin_c', 'virtue_shop.bin_c']:
            r_flags, r_u, r_c, r_data = rel_par[name]
            r_decomp = decompress_sllz(r_data) if (r_flags & 0x80000000) else r_data
            translated = r_decomp
            
        if is_comp:
            comp = compress_sllz(translated)
            payload = comp
            target_flags = 0x80000000
            target_u_sz = len(translated)
            target_c_sz = len(comp)
        else:
            payload = translated
            target_flags = 0x0
            target_u_sz = len(translated)
            target_c_sz = len(translated)
            
    if payload is not None:
        aligned_off = (len(rebuilt_stay) + 2047) & ~2047
        if aligned_off > len(rebuilt_stay):
            rebuilt_stay.extend(b'\x00' * (aligned_off - len(rebuilt_stay)))
        new_offset = len(rebuilt_stay)
        rebuilt_stay.extend(payload)
        
        e_off = file_table_offset + i * 32
        struct.pack_into('>4I', rebuilt_stay, e_off, target_flags, target_u_sz, target_c_sz, new_offset)
        modified_count += 1
        print(f"  [+] Appended {name} at 2048-aligned offset {hex(new_offset)} (u_sz={target_u_sz}, c_sz={target_c_sz})")

final_aligned = (len(rebuilt_stay) + 2047) & ~2047
if final_aligned > len(rebuilt_stay):
    rebuilt_stay.extend(b'\x00' * (final_aligned - len(rebuilt_stay)))

with open('stay_test.par', 'wb') as f:
    f.write(rebuilt_stay)
print(f"[SUCCESS] Wrote stay_test.par ({len(rebuilt_stay)} bytes, {modified_count} modified files) with 100% pristine sector alignment!")
