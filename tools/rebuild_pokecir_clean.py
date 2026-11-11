#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_pokecir_clean.py
------------------------------
Rebuilds release_gog/data/minigame/pokecir.par enforcing Golden Rule 1 & 3:
- Strict 2,048-byte sector alignment on EVERY file ((curr_off + 2047) & ~2047).
- Preserves all 63 files and their French translations (pokecir_parts.bin_c, pokecir_course.bin_c, pokecir_competition.bin_c).
- Preserves SLLZ compression flags (0x80000000).
- Pads final archive to 2,048-byte sector boundary.
- Eradicates the Pocket Circuit loading freeze caused by asynchronous sector streaming misalignment.
"""

import os
import sys
import struct

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verify_patch import ParValidator

def rebuild_pokecir_par(input_par: str, output_par: str) -> bool:
    print(f"[*] Lecture de l'archive source : {input_par}...")
    with open(input_par, 'rb') as f:
        data = f.read()

    magic, unkA, unkB, unkC = struct.unpack('>4I', data[:16])
    assert magic == 0x50415243, f"Format PARC invalide : {hex(magic)}"
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

    sorted_entries = sorted(entries, key=lambda e: e['f_off'])
    first_file_offset = (sorted_entries[0]['f_off'] + 2047) & ~2047
    rebuilt = bytearray(data[:sorted_entries[0]['f_off']])
    if len(rebuilt) < first_file_offset:
        rebuilt.extend(b'\x00' * (first_file_offset - len(rebuilt)))

    curr_off = len(rebuilt)
    for item in sorted_entries:
        aligned_off = (curr_off + 2047) & ~2047
        if aligned_off > len(rebuilt):
            rebuilt.extend(b'\x00' * (aligned_off - len(rebuilt)))
        
        item['new_f_off'] = len(rebuilt)
        rebuilt.extend(item['data'])
        curr_off = len(rebuilt)

    final_aligned = (len(rebuilt) + 2047) & ~2047
    if final_aligned > len(rebuilt):
        rebuilt.extend(b'\x00' * (final_aligned - len(rebuilt)))

    # Update file table entries in header
    for item in entries:
        struct.pack_into(
            '>4I',
            rebuilt,
            item['e_off'],
            item['flags'],
            item['u_sz'],
            item['c_sz'],
            item['new_f_off']
        )

    print(f"[*] Recompilation terminée : {len(data)} o -> {len(rebuilt)} o ({file_count} fichiers)")
    os.makedirs(os.path.dirname(os.path.abspath(output_par)), exist_ok=True)
    with open(output_par, 'wb') as f:
        f.write(rebuilt)

    print(f"[*] Validation d'intégrité de {output_par}...")
    v = ParValidator(output_par)
    v.validate()
    if v.issues:
        print(f"[ERREUR] Échec de validation : {v.issues}")
        return False
    print("[SUCCÈS] pokecir.par est 100% conforme et rigoureusement aligné sur 2 048 octets !")
    return True

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_par = os.path.join(repo_root, "release_gog", "data", "minigame", "pokecir.par")
    rebuild_pokecir_par(target_par, target_par)

if __name__ == '__main__':
    main()
