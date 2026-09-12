#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_wdr_append.py
---------------------------------
Rebuilds release_gog/data/wdr_par_c/wdr.par using the 2048-byte sector-aligned
append-only model (Gold Rule 3 of AGENTS.md):
1. Starts from the pristine clean GOG wdr.par (8,026,112 bytes).
2. Keeps all untouched stage binaries (pac_*.bin), streaming files, and system
   binaries at their exact 100% pristine original sector offsets.
3. Appends all modified/translated files at the end of the archive, each strictly
   aligned to 2048-byte (0x800) sector boundaries.
4. Updates file table entries with correct flags, uncompressed size, compressed size,
   and appended offsets.
5. Guarantees 0 offset-shift crashes in stage loading, wanderer audio streaming,
   or phone booth interactions.
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz
from tools.repair_phone_booths import PHONE_FILE_NAMES, PHONE_TRANSLATIONS, translate_msg_inplace
from tools.rebuild_all_shops_clean import generate_repaired_shops

def rebuild_clean_wdr_append(clean_par_path, curr_par_path, output_path):

    print(f"[+] Reading pristine base: {clean_par_path}")
    with open(clean_par_path, 'rb') as f:
        clean_bytes = f.read()

    print(f"[+] Reading translated reference: {curr_par_path}")
    with open(curr_par_path, 'rb') as f:
        curr_bytes = f.read()

    clean_files = parse_par(clean_bytes)
    curr_files = parse_par(curr_bytes)

    print(f"[+] Pre-generating clean French shops with preserved Pocket Circuit tables...")
    repaired_shops = generate_repaired_shops(clean_par_path, 'release_gog/data/bootpar/boot.par')

    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_bytes[16:32])
    name_offset = 32 + folder_count * 64

    rebuilt = bytearray(clean_bytes)

    PRISTINE_NON_MSG_BINS = {
        'dispose_string.bin', 'snitch.bin', 'ai_popup.bin', 'eg_telephone_card.bin',
        'arms_repair.bin', 'blacksmith.bin', 'present.bin', 'sale0000.bin',
        'sale0001.bin', 'sale0002.bin', 'send.bin', 'throw.bin'
    }

    stats = {'appended': 0, 'kept_orig': 0}

    print(f"[+] Processing {file_count} files in append-only mode...")
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = clean_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')
        e_off = file_table_offset + i * 32
        orig_flags, orig_u, orig_c, orig_off = struct.unpack('>4I', clean_bytes[e_off : e_off + 16])
        orig_data = clean_bytes[orig_off : orig_off + orig_c]

        target_data = None
        target_flags = 0
        target_u_sz = 0
        target_c_sz = 0

        # Keep untouched stage binaries and pristine system bins 100% untouched
        if name.startswith('pac_') or name in PRISTINE_NON_MSG_BINS:
            stats['kept_orig'] += 1
            continue
        elif name in repaired_shops:
            target_flags, target_u_sz, target_c_sz, target_data = repaired_shops[name]
        elif name == 'uid0044018f.msg':
            clean_decomp = decompress_sllz(orig_data) if orig_data.startswith(b'SLLZ') else orig_data
            repaired = clean_decomp.replace(b'Welcome. How can I help you?\x00', b'Bienvenue ! Que voulez-vous?\x00')
            repaired = repaired.replace(b'There you go. Have a nice day!\x00', b'Et voila. Bonne journee !     \x00')
            repaired = repaired.replace(b'Have a nice day!\x00', b'Bonne journee ! \x00')
            assert len(repaired) == len(clean_decomp), f"Mismatch in uid0044018f.msg length: {len(repaired)} != {len(clean_decomp)}"
            comp_data = compress_sllz(repaired)
            target_data = comp_data
            target_flags = 0x80000000
            target_u_sz = len(repaired)
            target_c_sz = len(comp_data)
        elif name in PHONE_FILE_NAMES:
            clean_decomp = decompress_sllz(orig_data) if orig_data.startswith(b'SLLZ') else orig_data
            repaired_decomp, _ = translate_msg_inplace(clean_decomp, PHONE_TRANSLATIONS)
            comp_data = compress_sllz(repaired_decomp)
            target_data = comp_data
            target_flags = 0x80000000
            target_u_sz = len(repaired_decomp)
            target_c_sz = len(comp_data)
        elif name in curr_files:
            curr_item = curr_files[name]
            curr_flags, curr_u, curr_c, curr_data = curr_item
            decomp_curr = decompress_sllz(curr_data) if curr_data.startswith(b'SLLZ') else curr_data
            decomp_orig = decompress_sllz(orig_data) if orig_data.startswith(b'SLLZ') else orig_data
            
            if decomp_curr == decomp_orig:
                stats['kept_orig'] += 1
                continue

            if orig_flags & 0x80000000:
                comp_data = compress_sllz(decomp_curr)
                target_data = comp_data
                target_flags = 0x80000000
                target_u_sz = len(decomp_curr)
                target_c_sz = len(comp_data)
            else:
                target_data = decomp_curr
                target_flags = 0x0
                target_u_sz = len(decomp_curr)
                target_c_sz = len(decomp_curr)
        else:
            stats['kept_orig'] += 1
            continue

        # Append target_data with strict 2048-byte sector alignment
        aligned_off = (len(rebuilt) + 2047) & ~2047
        if aligned_off > len(rebuilt):
            rebuilt.extend(b'\x00' * (aligned_off - len(rebuilt)))
        new_offset = len(rebuilt)
        rebuilt.extend(target_data)

        # Update entry in file table
        struct.pack_into('>4I', rebuilt, e_off, target_flags, target_u_sz, target_c_sz, new_offset)
        stats['appended'] += 1

    # Pad final archive to 2048 bytes
    final_aligned = (len(rebuilt) + 2047) & ~2047
    if final_aligned > len(rebuilt):
        rebuilt.extend(b'\x00' * (final_aligned - len(rebuilt)))

    print(f"[+] Writing rebuilt archive to {output_path} ({len(rebuilt)} bytes, {len(rebuilt)/(1024*1024):.2f} MB)...")
    with open(output_path, 'wb') as f:
        f.write(rebuilt)

    print(f"[+] Complete! Kept pristine: {stats['kept_orig']}, Appended: {stats['appended']}")
    return True

if __name__ == '__main__':
    clean_p = 'par_original/wdr.par'
    curr_p = 'release_gog/data/wdr_par_c/wdr.par'
    out_p = 'release_gog/data/wdr_par_c/wdr.par'
    if len(sys.argv) > 1:
        out_p = sys.argv[1]
    rebuild_clean_wdr_append(clean_p, curr_p, out_p)
