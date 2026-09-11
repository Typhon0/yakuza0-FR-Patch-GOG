#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_boot_append.py
----------------------------------
Rebuilds boot.par using the proven 2048-byte sector-aligned append-only model:
1. Starts from pristine clean GOG boot.par (par_original/boot.par, 1,712,128 bytes).
2. Keeps all 225 untouched files at their exact 100% pristine original sector offsets.
3. Appends the 6 French translated tables (scenario, substories, captions, items, string_tbl, battle_deck)
   at the end of the archive, strictly aligned to 2048-byte (0x800) sector boundaries.
"""

import os, sys, struct
sys.path.insert(0, '.')
from scratch.scanner_engine import parse_par

clean_boot_bytes = open('par_original/boot.par', 'rb').read()
rel_boot_bytes = open('release_gog/data/bootpar/boot.par', 'rb').read()

clean_par = parse_par(clean_boot_bytes)
rel_par = parse_par(rel_boot_bytes)

TARGET_FILES = [
    'caption.bin_c',
    'explanation_main_scenario.bin_c',
    'explanation_sub_story.bin_c',
    'item.bin_c',
    'string_tbl.bin_c',
    'battle_deck_list.bin_c',
]

folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_boot_bytes[16:32])
name_offset = 32 + folder_count * 64
rebuilt_boot = bytearray(clean_boot_bytes)

modified_count = 0
for i in range(file_count):
    n_off = name_offset + i * 64
    name = clean_boot_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')
    
    if name in TARGET_FILES:
        r_flags, r_u, r_c, r_data = rel_par[name]
        
        aligned_off = (len(rebuilt_boot) + 2047) & ~2047
        if aligned_off > len(rebuilt_boot):
            rebuilt_boot.extend(b'\x00' * (aligned_off - len(rebuilt_boot)))
        new_offset = len(rebuilt_boot)
        rebuilt_boot.extend(r_data)
        
        e_off = file_table_offset + i * 32
        struct.pack_into('>4I', rebuilt_boot, e_off, r_flags, r_u, r_c, new_offset)
        modified_count += 1
        print(f"  [+] Appended {name:32s} at 2048-aligned offset {hex(new_offset)} (u_sz={r_u}, c_sz={r_c})")

final_aligned = (len(rebuilt_boot) + 2047) & ~2047
if final_aligned > len(rebuilt_boot):
    rebuilt_boot.extend(b'\x00' * (final_aligned - len(rebuilt_boot)))

with open('boot_test.par', 'wb') as f:
    f.write(rebuilt_boot)
with open('release_gog/data/bootpar/boot.par', 'wb') as f:
    f.write(rebuilt_boot)
print(f"[SUCCESS] Wrote boot_test.par ({len(rebuilt_boot)} bytes, {modified_count} modified files) with 100% pristine sector alignment!")
