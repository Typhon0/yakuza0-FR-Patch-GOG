#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_pause_2048.py
---------------------------------
Rebuilds release_gog/data/pausepar_e/pause.par with strict 2048-byte sector
alignment for ALL 3,820 files.

Fixes the 0x234B0 / 0x234B7 crash when entering Kotobuki Drugs and Daikoku Drugstore,
which sell Staminan Light (2d_yk_staminan_lite.dds).
"""

import os
import sys
import struct
import shutil

def rebuild_pause_2048(input_path, output_path):
    print(f"[+] Reading {input_path}...")
    with open(input_path, 'rb') as f:
        data = f.read()

    magic, unkA, unkB, unkC = struct.unpack('>4I', data[:16])
    assert magic == 0x50415243, f"Not a PAR archive: {hex(magic)}"
    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', data[16:32])
    name_offset = 32 + folder_count * 64

    entries = []
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = data[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')
        e_off = file_table_offset + i * 32
        flags, u_sz, c_sz, f_off = struct.unpack('>4I', data[e_off : e_off + 16])
        raw_file = data[f_off : f_off + c_sz]
        entries.append({
            'idx': i,
            'name': name,
            'e_off': e_off,
            'flags': flags,
            'u_sz': u_sz,
            'c_sz': c_sz,
            'f_off': f_off,
            'data': raw_file
        })

    # Sort entries by original file offset to preserve sequential order
    sorted_entries = sorted(entries, key=lambda e: e['f_off'])
    first_file_offset = (sorted_entries[0]['f_off'] + 2047) & ~2047
    
    rebuilt = bytearray(data[:sorted_entries[0]['f_off']])
    # Pad header up to first_file_offset
    if len(rebuilt) < first_file_offset:
        rebuilt.extend(b'\x00' * (first_file_offset - len(rebuilt)))
    
    curr_off = len(rebuilt)
    
    for item in sorted_entries:
        aligned_off = (curr_off + 2047) & ~2047
        if aligned_off > len(rebuilt):
            rebuilt.extend(b'\x00' * (aligned_off - len(rebuilt)))
        
        new_file_offset = len(rebuilt)
        assert new_file_offset % 2048 == 0, f"Offset {new_file_offset} not 2048-aligned!"
        rebuilt.extend(item['data'])
        curr_off = len(rebuilt)
        
        # Update entry table
        struct.pack_into('>4I', rebuilt, item['e_off'], item['flags'], item['u_sz'], item['c_sz'], new_file_offset)

    final_aligned = (len(rebuilt) + 2047) & ~2047
    if final_aligned > len(rebuilt):
        rebuilt.extend(b'\x00' * (final_aligned - len(rebuilt)))

    print(f"[+] Rebuilt {len(sorted_entries)} files with 100% 2048-byte sector alignment.")
    print(f"[+] Output size: {len(rebuilt)} bytes ({len(rebuilt) / (1024*1024):.2f} MB)")
    
    # Validation
    for item in sorted_entries:
        flags, u_sz, c_sz, f_off = struct.unpack('>4I', rebuilt[item['e_off']:item['e_off']+16])
        assert f_off % 2048 == 0, f"Validation failure: {item['name']} not 2048-aligned ({hex(f_off)})"
        if flags & 0x80000000:
            assert rebuilt[f_off:f_off+4] == b'SLLZ', f"SLLZ header corrupted for {item['name']} at {hex(f_off)}"

    print("[+] ALL 3,820 files verified 2048-byte sector-aligned and headers valid!")

    with open(output_path, 'wb') as f:
        f.write(rebuilt)
    print(f"[+] Saved successfully to {output_path}")

if __name__ == '__main__':
    inp = 'release_gog/data/pausepar_e/pause.par'
    out = 'release_gog/data/pausepar_e/pause.par'
    if len(sys.argv) > 2:
        inp = sys.argv[1]
        out = sys.argv[2]
    elif len(sys.argv) > 1:
        out = sys.argv[1]
    rebuild_pause_2048(inp, out)
