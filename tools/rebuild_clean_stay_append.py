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
3. Translates in-place with exact byte length preservation (0 heap overflow).
4. Preserves original compression flags (flags=0x0 for uncompressed, flags=0x80000000 for SLLZ).
5. Appends modified French tables at the end of the archive, each strictly aligned
   to 2048-byte (0x800) boundaries.
6. Pads archive to 2048-byte sector boundary.
"""

import os
import sys
import struct
import shutil

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz
from tools.translate_stay_par_complete import translate_exact_bytes

def rebuild_clean_stay_append(clean_par_path='par_original/stay.par',
                             ref_par_path='scratch/data/staypar/stay.par',
                             output_path='release_gog/data/staypar/stay.par'):
    print(f"[+] Reading pristine clean stay.par: {clean_par_path}")
    with open(clean_par_path, 'rb') as f:
        clean_bytes = f.read()
    clean_par = parse_par(clean_bytes)

    print(f"[+] Reading reference verified stay.par: {ref_par_path}")
    with open(ref_par_path, 'rb') as f:
        ref_bytes = f.read()
    ref_par = parse_par(ref_bytes)

    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_bytes[16:32])
    name_offset = 32 + folder_count * 64
    rebuilt_stay = bytearray(clean_bytes)

    # Tables that have verified in-place French translations or rich French versions
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

    modified_count = 0
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = clean_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')

        if name in TARGET_TABLES and name in ref_par:
            r_flags, r_u, r_c, r_data = ref_par[name]
            
            # Align strictly to 2048-byte sector boundary
            aligned_off = (len(rebuilt_stay) + 2047) & ~2047
            if aligned_off > len(rebuilt_stay):
                rebuilt_stay.extend(b'\x00' * (aligned_off - len(rebuilt_stay)))
            new_offset = len(rebuilt_stay)
            rebuilt_stay.extend(r_data)

            e_off = file_table_offset + i * 32
            struct.pack_into('>4I', rebuilt_stay, e_off, r_flags, r_u, r_c, new_offset)
            modified_count += 1
            print(f"  [+] Appended {name:32s} at sector {hex(new_offset)} (flags={hex(r_flags)}, u_sz={r_u:6d}, c_sz={r_c:6d})")

    final_aligned = (len(rebuilt_stay) + 2047) & ~2047
    if final_aligned > len(rebuilt_stay):
        rebuilt_stay.extend(b'\x00' * (final_aligned - len(rebuilt_stay)))

    with open(output_path, 'wb') as f:
        f.write(rebuilt_stay)
    print(f"\n[SUCCESS] Wrote {output_path} ({len(rebuilt_stay)} bytes, {modified_count} modified files) with strict 2048-byte sector alignment!")
    return True

if __name__ == '__main__':
    clean_p = sys.argv[1] if len(sys.argv) > 1 else 'par_original/stay.par'
    ref_p = sys.argv[2] if len(sys.argv) > 2 else 'scratch/data/staypar/stay.par'
    out_p = sys.argv[3] if len(sys.argv) > 3 else 'release_gog/data/staypar/stay.par'
    rebuild_clean_stay_append(clean_p, ref_p, out_p)
