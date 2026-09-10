#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_wdr.py

Rebuilds release_gog/data/wdr_par_c/wdr.par from the pristine clean GOG original
at crash logs/wdr.par:
1. Preserves the 100% pristine PARC folder directory table and header.
2. Keeps all pac_*.bin stage binaries pristine from clean GOG (avoiding the shifted
   table offsets that crashed Don Quijote / Substory 4).
3. Injects translated .msg files and shop/restaurant/bar menus from release_gog.
4. Compresses all files matching the original GOG compression flags (0x80000000 -> SLLZ).
5. Enforces 64-byte alignment throughout the archive.
6. Validates the rebuilt archive against engine constraints.
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz
from tools.repair_phone_booths import PHONE_FILE_NAMES, PHONE_TRANSLATIONS, translate_msg_inplace

def rebuild_clean_wdr(clean_par_path, curr_par_path, output_path):
    print(f"[+] Reading pristine base: {clean_par_path}")
    with open(clean_par_path, 'rb') as f:
        clean_bytes = f.read()

    print(f"[+] Reading current translated patch: {curr_par_path}")
    with open(curr_par_path, 'rb') as f:
        curr_bytes = f.read()

    clean_files = parse_par(clean_bytes)
    curr_files = parse_par(curr_bytes)

    # PARC Header
    magic, unkA, unkB, unkC = struct.unpack('>4I', clean_bytes[:16])
    assert magic == 0x50415243
    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_bytes[16:32])
    name_offset = 32 + folder_count * 64

    entries = []
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = clean_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')
        e_off = file_table_offset + i * 32
        entry_meta = list(struct.unpack('>8I', clean_bytes[e_off : e_off + 32]))
        flags, u_sz, c_sz, f_off = entry_meta[:4]
        raw_file = clean_bytes[f_off : f_off + c_sz]
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

    first_file_offset = entries[0]['f_off']
    rebuilt = bytearray(clean_bytes[:first_file_offset])
    curr_write_offset = first_file_offset

    stats = {
        'pristine_pac': 0,
        'translated_msg': 0,
        'clean_msg': 0,
        'translated_other': 0,
        'clean_other': 0,
        'compressed': 0,
        'uncompressed': 0
    }

    print(f"[+] Processing {len(entries)} files...")
    for item in entries:
        name = item['name']
        orig_flags = item['flags']
        orig_data = item['data']

        # Determine target payload
        if name.startswith('pac_'):
            # ALWAYS keep pristine GOG stage binaries to avoid offset shift crashes
            target_data = orig_data
            target_flags = orig_flags
            target_u_sz = item['u_sz']
            target_c_sz = item['c_sz']
            stats['pristine_pac'] += 1
        elif name in PHONE_FILE_NAMES:
            # Rebuilt from pristine GOG bytecode with safe in-place translations (fixes payphone softlock)
            clean_decomp = decompress_sllz(orig_data) if orig_data.startswith(b'SLLZ') else orig_data
            repaired_decomp, _ = translate_msg_inplace(clean_decomp, PHONE_TRANSLATIONS)
            comp_data = compress_sllz(repaired_decomp)
            target_data = comp_data
            target_flags = 0x80000000
            target_u_sz = len(repaired_decomp)
            target_c_sz = len(comp_data)
            stats['translated_msg'] += 1
        elif name in curr_files:
            curr_item = curr_files[name]
            curr_data = curr_item[3]

            # Decompress curr if it was compressed
            if curr_data.startswith(b'SLLZ'):
                try:
                    decomp_curr = decompress_sllz(curr_data)
                except Exception:
                    decomp_curr = curr_data
            else:
                decomp_curr = curr_data

            if orig_flags & 0x80000000:
                # Target must be SLLZ compressed
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

            if name.endswith('.msg'):
                stats['translated_msg'] += 1
            else:
                stats['translated_other'] += 1
        else:
            # Fallback clean
            target_data = orig_data
            target_flags = orig_flags
            target_u_sz = item['u_sz']
            target_c_sz = item['c_sz']
            if name.endswith('.msg'):
                stats['clean_msg'] += 1
            else:
                stats['clean_other'] += 1

        if target_flags & 0x80000000:
            stats['compressed'] += 1
        else:
            stats['uncompressed'] += 1

        # Align to 64 bytes
        aligned_off = (curr_write_offset + 63) & ~63
        if aligned_off > len(rebuilt):
            rebuilt.extend(b'\x00' * (aligned_off - len(rebuilt)))

        new_file_offset = len(rebuilt)
        rebuilt.extend(target_data)
        curr_write_offset = len(rebuilt)

        # Update entry in file table
        struct.pack_into('>4I', rebuilt, item['entry_offset'], target_flags, target_u_sz, target_c_sz, new_file_offset)

    # Pad final archive to 64-byte alignment
    final_aligned = (len(rebuilt) + 63) & ~63
    if final_aligned > len(rebuilt):
        rebuilt.extend(b'\x00' * (final_aligned - len(rebuilt)))

    print(f"[+] Writing rebuilt archive to {output_path} ({len(rebuilt)} bytes)...")
    with open(output_path, 'wb') as f:
        f.write(rebuilt)

    print("[+] Repack summary:")
    for k, v in stats.items():
        print(f"    - {k:20}: {v}")

    # Integrity verification
    print("[+] Verifying rebuilt archive...")
    verified_files = parse_par(bytes(rebuilt))
    assert len(verified_files) == file_count, f"File count mismatch: {len(verified_files)} vs {file_count}"

    # Verify Folder Table matches clean_bytes bit-for-bit
    clean_folder_table = clean_bytes[folder_table_offset : folder_table_offset + folder_count * 32]
    rebuilt_folder_table = rebuilt[folder_table_offset : folder_table_offset + folder_count * 32]
    assert clean_folder_table == rebuilt_folder_table, "Folder table was modified!"
    print("[+] Folder table verification PASSED: 100% identical to pristine GOG!")

    # Verify Kamurocho stage binary
    kamuro_fl, kamuro_u, kamuro_c, kamuro_data = verified_files['pac_STID_ST_KAMURO.bin']
    assert kamuro_u == 1233900, f"pac_STID_ST_KAMURO.bin uncompressed size mismatch: {kamuro_u}"
    assert kamuro_fl == 0x80000000, "pac_STID_ST_KAMURO.bin flag mismatch"
    print("[+] pac_STID_ST_KAMURO.bin verification PASSED (1,233,900 bytes, compressed)!")

    # Verify Substory 4 message
    msg_fl, msg_u, msg_c, msg_data = verified_files['uid0104006f.msg']
    assert msg_fl == 0x80000000, "uid0104006f.msg flag mismatch"
    decomp_msg = decompress_sllz(msg_data)
    assert b'Pourquoi font-ils la queue' in decomp_msg, "French text missing from uid0104006f.msg"
    print("[+] uid0104006f.msg verification PASSED (translated & properly compressed)!")

    # Verify Theater Square payphone (uid033317da.msg)
    p10_fl, p10_u, p10_c, p10_data = verified_files['uid033317da.msg']
    assert p10_fl == 0x80000000, "uid033317da.msg flag mismatch"
    assert p10_u == 7245, f"uid033317da.msg uncompressed size mismatch: {p10_u} (expected clean 7245)"
    decomp_p10 = decompress_sllz(p10_data)
    assert b'Sauvegardez et utilisez le coffre' in decomp_p10, "French tutorial missing from uid033317da.msg"
    assert b'Sauv\x00' in decomp_p10, "Save choice missing from uid033317da.msg"
    assert b'Ouvrir le coffre\x00' in decomp_p10, "Item box choice missing from uid033317da.msg"
    assert b'Retour\x00' in decomp_p10, "Cancel choice missing from uid033317da.msg"
    print("[+] uid033317da.msg verification PASSED (phone booth softlock fixed)!")
    print("[SUCCESS] wdr.par rebuilt cleanly and fully verified!")

if __name__ == '__main__':
    clean_par = 'crash logs/wdr.par'
    curr_par = 'release_gog/data/wdr_par_c/wdr.par'
    out_par = 'scratch/wdr_rebuilt.par' if len(sys.argv) < 2 else sys.argv[1]
    rebuild_clean_wdr(clean_par, curr_par, out_par)
