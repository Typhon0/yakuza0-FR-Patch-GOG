#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/repair_radio_dolce.py
===========================
Repairs the permanent softlock in Substory 47 (Dolce Kamiya's radio broadcast)
across all related .msg files in wdr.par:
- uid000c169e.msg
- uid010c16e4.msg
- uid010c16e8.msg
- uid010c16ec.msg
- uid010c16fc.msg
- uid010c16fe.msg
- uid010c1703.msg
- uid010c1705.msg

Root Cause (AGENTS.md Rule 2 & DEBUG_KNOWLEDGE_BASE.md Section 3):
Dialogue string "Alors, restez a l'ecoute ! Au revoir et a la\\nprochaine !" was
padded with 20 null bytes (\\x00*20) instead of space-padding (b' '*20).
The Sega typewriter routine (0x140396783) prematurely terminates on \\x00 before
reaching the 75 expected characters encoded in the node, waiting forever and
never triggering the dialogue advance event.

This script replaces the 20 null bytes with 20 spaces (b' ' * 20), restoring the
full printable length so the typewriter finishes typing and unlocks progression.
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz

TARGET_FILES = {
    'uid000c169e.msg',
    'uid010c16e4.msg',
    'uid010c16e8.msg',
    'uid010c16ec.msg',
    'uid010c16fc.msg',
    'uid010c16fe.msg',
    'uid010c1703.msg',
    'uid010c1705.msg',
}

def repack_par_aligned(orig_bytes, file_replacements={}):
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

        aligned_off = (curr_off + 2047) & ~2047
        if aligned_off > len(rebuilt):
            rebuilt.extend(b'\x00' * (aligned_off - len(rebuilt)))

        new_file_offset = len(rebuilt)
        rebuilt.extend(n_data)
        curr_off = len(rebuilt)
        struct.pack_into('>4I', rebuilt, item['entry_offset'], n_flags, n_u_sz, n_c_sz, new_file_offset)

    final_aligned = (len(rebuilt) + 2047) & ~2047
    if final_aligned > len(rebuilt):
        rebuilt.extend(b'\x00' * (final_aligned - len(rebuilt)))

    return bytes(rebuilt)

def repair_radio_files(wdr_path='release_gog/data/wdr_par_c/wdr.par'):
    print(f"[+] Loading {wdr_path}...")
    with open(wdr_path, 'rb') as f:
        wdr_bytes = f.read()

    files = parse_par(wdr_bytes)
    replacements = {}
    total_repaired = 0

    target_pattern = b"prochaine !\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    replacement_pattern = b"prochaine !" + (b" " * 20)

    for fn in sorted(TARGET_FILES):
        if fn not in files:
            print(f"[-] Warning: {fn} not found in wdr.par")
            continue

        flags, u_sz, c_sz, raw_data = files[fn]
        decomp = bytearray(decompress_sllz(raw_data) if (flags & 0x80000000 or raw_data.startswith(b'SLLZ')) else raw_data)

        # 1. Replace 20 null bytes with 20 spaces after "prochaine !"
        matches = 0
        pos = 0
        while True:
            idx = decomp.find(target_pattern, pos)
            if idx == -1:
                break
            decomp[idx : idx + len(target_pattern)] = replacement_pattern
            matches += 1
            pos = idx + len(replacement_pattern)

        # 2. Also check variant with 19 null bytes (in case of \r\n vs \n)
        variant_19 = b"prochaine !\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        variant_19_rep = b"prochaine !" + (b" " * 19)
        pos = 0
        while True:
            idx = decomp.find(variant_19, pos)
            if idx == -1:
                break
            decomp[idx : idx + len(variant_19)] = variant_19_rep
            matches += 1
            pos = idx + len(variant_19_rep)

        if matches > 0:
            comp_data = compress_sllz(bytes(decomp))
            replacements[fn] = (0x80000000, len(decomp), len(comp_data), comp_data)
            total_repaired += 1
            print(f"  [+] {fn}: Repaired {matches} softlock occurrences (space-padded, decomp len={len(decomp)})")

    if total_repaired > 0:
        print(f"\n[+] Repacking {wdr_path} with 2048-byte sector alignment...")
        new_wdr = repack_par_aligned(wdr_bytes, replacements)
        with open(wdr_path, 'wb') as f:
            f.write(new_wdr)
        print(f"[SUCCESS] Repaired {total_repaired} Dolce Kamiya files in {wdr_path} ({len(new_wdr)} bytes)!")
        return True
    else:
        print("[!] No occurrences found to repair.")
        return False

if __name__ == '__main__':
    repair_radio_files()
