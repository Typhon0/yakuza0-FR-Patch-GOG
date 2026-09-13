#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_boot_append.py
----------------------------------
Rebuilds boot.par using the proven 2048-byte sector-aligned append-only model:
1. Starts from pristine clean GOG boot.par (par_original/boot.par, 1,712,128 bytes).
2. Keeps all untouched files at their exact 100% pristine original sector offsets.
3. Appends the verified French translated tables:
   - caption.bin_c (15,376 bytes uncompressed)
   - explanation_main_scenario.bin_c (23,772 bytes uncompressed)
   - explanation_sub_story.bin_c (strict 58,232 bytes uncompressed, space-padded, prevents crash 0x371324)
   - item.bin_c (192,308 bytes uncompressed, proven French stable baseline)
   - string_tbl.bin_c (158,893 bytes uncompressed)
   - battle_deck_list.bin_c (2,972 bytes uncompressed)
   - encounter_pupup_message.bin_c (strict 24,908 bytes uncompressed, 6,189 bytes SLLZ compressed)
4. Strictly omits oversized tables that exceed the Sega GOG boot heap buffer (ability, tips_tutorial, etc.).
5. Strictly aligns every appended file to 2048-byte (0x800) sector boundaries.
6. Pads the total archive size to a multiple of 2048 bytes.
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz

def get_clean_french_encounter_popup_bin():
    fr_boot_path = 'par_original/boot_steam_fr.par'
    with open(fr_boot_path, 'rb') as f:
        fr_files = parse_par(f.read())
    raw = fr_files['encounter_pupup_message.bin_c'][3]
    decomp = decompress_sllz(raw) if raw.startswith(b'SLLZ') else raw
    assert len(decomp) == 24908, f"Unexpected encounter_pupup_message.bin_c length: {len(decomp)}"
    comp = compress_sllz(decomp)
    return 0x80000000, len(decomp), len(comp), comp

def rebuild_boot_par(clean_par_path='par_original/boot.par',
                     ref_par_path='scratch/data/bootpar/boot.par',
                     output_path='release_gog/data/bootpar/boot.par'):
    print(f"[+] Reading pristine clean boot.par: {clean_par_path}")
    with open(clean_par_path, 'rb') as f:
        clean_boot_bytes = f.read()
    clean_par = parse_par(clean_boot_bytes)

    print(f"[+] Reading reference verified boot.par: {ref_par_path}")
    with open(ref_par_path, 'rb') as f:
        ref_boot_bytes = f.read()
    ref_par = parse_par(ref_boot_bytes)

    epm_entry = get_clean_french_encounter_popup_bin()

    TARGET_FILES = {
        'caption.bin_c': ref_par['caption.bin_c'],
        'explanation_main_scenario.bin_c': ref_par['explanation_main_scenario.bin_c'],
        'explanation_sub_story.bin_c': ref_par['explanation_sub_story.bin_c'],
        'item.bin_c': ref_par['item.bin_c'],
        'string_tbl.bin_c': ref_par['string_tbl.bin_c'],
        'battle_deck_list.bin_c': ref_par['battle_deck_list.bin_c'],
        'encounter_pupup_message.bin_c': epm_entry,
    }

    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_boot_bytes[16:32])
    name_offset = 32 + folder_count * 64
    rebuilt_boot = bytearray(clean_boot_bytes)

    print(f"[+] Rebuilding boot.par with {len(TARGET_FILES)} target files...")
    modified_count = 0
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = clean_boot_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')

        if name in TARGET_FILES:
            r_flags, r_u, r_c, r_data = TARGET_FILES[name]

            # Align strictly to 2048-byte sector boundary
            aligned_off = (len(rebuilt_boot) + 2047) & ~2047
            if aligned_off > len(rebuilt_boot):
                rebuilt_boot.extend(b'\x00' * (aligned_off - len(rebuilt_boot)))
            new_offset = len(rebuilt_boot)
            rebuilt_boot.extend(r_data)

            e_off = file_table_offset + i * 32
            struct.pack_into('>4I', rebuilt_boot, e_off, r_flags, r_u, r_c, new_offset)
            modified_count += 1
            print(f"  [+] Appended {name:32s} at sector {hex(new_offset)} (flags={hex(r_flags)}, u_sz={r_u:6d}, c_sz={r_c:6d})")

    # Pad archive total size to 2048-byte multiple
    final_aligned = (len(rebuilt_boot) + 2047) & ~2047
    if final_aligned > len(rebuilt_boot):
        rebuilt_boot.extend(b'\x00' * (final_aligned - len(rebuilt_boot)))

    with open(output_path, 'wb') as f:
        f.write(rebuilt_boot)
    print(f"\n[SUCCESS] Wrote {output_path} ({len(rebuilt_boot)} bytes, {modified_count} modified files) with strict 2048-byte sector alignment!")
    return True

if __name__ == '__main__':
    clean_p = sys.argv[1] if len(sys.argv) > 1 else 'par_original/boot.par'
    ref_p = sys.argv[2] if len(sys.argv) > 2 else 'scratch/data/bootpar/boot.par'
    out_p = sys.argv[3] if len(sys.argv) > 3 else 'release_gog/data/bootpar/boot.par'
    rebuild_boot_par(clean_p, ref_p, out_p)
