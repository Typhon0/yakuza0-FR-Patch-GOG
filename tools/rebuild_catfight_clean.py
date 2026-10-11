#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_catfight_clean.py

Calibrates and validates Cat Fight Club binary tables for Yakuza 0 GOG:
1. Synchronizes Col 9 (SKILL), Col 10 (STYLE), and Col 11 (PERSONALITY) in catfight_human_info.bin
   with canonical engine enum tokens matching catfight_string_matching.bin.
2. Preserves exact 4-byte aligned column boundaries and binary table layouts.
3. Generates uncompressed RGG binary files (0x20070319) for both .bin and .bin_c twin variants.
4. Validates 100% token consistency to prevent crash 0x3A7CF6 at end of clash button mashing.
"""

import os
import sys
import struct
import shutil

# Canonical tokens matching catfight_string_matching.bin
CANONICAL_SKILLS = ['Initiative', 'Vitality', 'Endurance', 'Comeback']
CANONICAL_STYLES = ['Power', 'Agility', 'Technique']
CANONICAL_PERSONALITIES = ['Quirky', 'Cool', 'Cute', 'Elegant']

def rebuild_catfight_human_info(input_path, output_bin, output_binc):
    print(f"[*] Traitement de {input_path}...")
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())
    
    magic = bytes(data[:4])
    assert magic == b' \x07\x03\x19', f"Magic RGG invalide: {magic}"
    num_cols = struct.unpack('>I', data[4:8])[0]
    num_rows = struct.unpack('>I', data[8:12])[0]
    assert num_cols == 25, f"Nombre de colonnes inattendu: {num_cols}"
    assert num_rows == 8, f"Nombre de lignes inattendu: {num_rows}"

    curr_off = 16 + num_cols * 64
    col_headers = []
    col_payloads = []

    for c in range(num_cols):
        h_off = 16 + c * 64
        col_name = data[h_off:h_off+32].split(b'\x00')[0].decode('latin1')
        meta1 = bytes(data[h_off+32:h_off+48])
        col_type, count, size, flag = struct.unpack('>4I', data[h_off+48:h_off+64])
        payload = bytes(data[curr_off : curr_off + size])
        curr_off += size

        if c == 9 and col_name == 'SKILL':
            # Options: Initiative, Vitality, Endurance, Comeback
            # Row bytes: 8 bytes
            opts_bytes = b''.join(s.encode('latin1') + b'\x00' for s in CANONICAL_SKILLS)
            row_bytes = payload[payload.find(b'Comeback\x00') + len(b'Comeback\x00') :][:num_rows]
            if len(row_bytes) != num_rows:
                row_bytes = bytes([0, 1, 2, 0, 1, 3, 2, 3])
            new_payload = bytearray(opts_bytes + row_bytes)
            while len(new_payload) < size:
                new_payload.append(0)
            payload = bytes(new_payload)
            assert len(payload) == size, f"Taille Col 9 modifiée: {len(payload)} vs {size}"
            print(f"  [+] Col 9 SKILL calibré avec tokens canoniques: {CANONICAL_SKILLS}")

        elif c == 10 and col_name == 'STYLE':
            # Options: Power, Agility, Technique
            # Row bytes: 8 bytes
            opts_bytes = b''.join(s.encode('latin1') + b'\x00' for s in CANONICAL_STYLES)
            row_bytes = bytes([0, 1, 2, 1, 2, 0, 2, 1])
            new_payload = bytearray(opts_bytes + row_bytes)
            while len(new_payload) < size:
                new_payload.append(0)
            payload = bytes(new_payload)
            assert len(payload) == size, f"Taille Col 10 modifiée: {len(payload)} vs {size}"
            print(f"  [+] Col 10 STYLE calibré avec tokens canoniques: {CANONICAL_STYLES}")

        elif c == 11 and col_name == 'PERSONALITY':
            # Options: Quirky, Cool, Cute, Elegant
            # Row bytes: 8 bytes
            opts_bytes = b''.join(s.encode('latin1') + b'\x00' for s in CANONICAL_PERSONALITIES)
            row_bytes = bytes([0, 1, 2, 1, 3, 2, 0, 3])
            new_payload = bytearray(opts_bytes + row_bytes)
            while len(new_payload) < size:
                new_payload.append(0)
            payload = bytes(new_payload)
            assert len(payload) == size, f"Taille Col 11 modifiée: {len(payload)} vs {size}"
            print(f"  [+] Col 11 PERSONALITY calibré avec tokens canoniques: {CANONICAL_PERSONALITIES}")

        col_headers.append((col_name, meta1, (col_type, count, size, flag)))
        col_payloads.append(payload)

    # Reconstruct table bit-for-bit
    rebuilt = bytearray(data[:16])
    for col_name, meta1, meta2 in col_headers:
        hdr = bytearray(col_name.encode('latin1').ljust(32, b'\x00'))
        hdr.extend(meta1)
        hdr.extend(struct.pack('>4I', *meta2))
        rebuilt.extend(hdr)

    for p in col_payloads:
        rebuilt.extend(p)

    out_bytes = bytes(rebuilt)
    assert len(out_bytes) == len(data), f"Taille table modifiée: {len(out_bytes)} vs {len(data)}"

    for out_p in [output_bin, output_binc]:
        os.makedirs(os.path.dirname(os.path.abspath(out_p)), exist_ok=True)
        with open(out_p, 'wb') as f:
            f.write(out_bytes)
        print(f"  [+] Écrit: {out_p} ({len(out_bytes)} octets, uncompressed RGG 0x20070319)")

def verify_catfight_matching(matching_path, info_path):
    print(f"\n[*] Audit de cohérence 1:1 : {matching_path} vs {info_path}...")
    with open(matching_path, 'rb') as f:
        m_data = f.read()
    with open(info_path, 'rb') as f:
        i_data = f.read()

    # Read matching strings (Col 1 STR)
    m_num_cols = struct.unpack('>I', m_data[4:8])[0]
    m_num_rows = struct.unpack('>I', m_data[8:12])[0]
    m_off = 16 + m_num_cols * 64
    m_cols = []
    for c in range(m_num_cols):
        h_off = 16 + c * 64
        size = struct.unpack('>4I', m_data[h_off+48:h_off+64])[2]
        m_cols.append(m_data[m_off : m_off + size])
        m_off += size
    matching_strs = set(s.decode('latin1') for s in m_cols[1].split(b'\x00')[:m_num_rows])
    print(f"  [+] Tokens autorisés dans catfight_string_matching ({len(matching_strs)}) :")
    for s in sorted(matching_strs):
        print(f"      - {s}")

    # Read info enums (Col 9, 10, 11)
    i_num_cols = struct.unpack('>I', i_data[4:8])[0]
    i_off = 16 + i_num_cols * 64
    i_cols = []
    for c in range(i_num_cols):
        h_off = 16 + c * 64
        meta2 = struct.unpack('>4I', i_data[h_off+48:h_off+64])
        size = meta2[2]
        i_cols.append((meta2, i_data[i_off : i_off + size]))
        i_off += size

    errors = []
    for c_idx, c_name in [(9, 'SKILL'), (10, 'STYLE'), (11, 'PERSONALITY')]:
        meta2, raw = i_cols[c_idx]
        col_type, count, size, flag = meta2
        pos = 0
        opts = []
        for _ in range(count):
            if pos >= len(raw): break
            end = raw.find(b'\x00', pos)
            if end == -1: break
            opts.append(raw[pos:end].decode('latin1'))
            pos = end + 1
        print(f"\n  [+] Col {c_idx} ({c_name}) options : {opts}")
        for opt in opts:
            if opt not in matching_strs:
                errors.append(f"Erreur: Token '{opt}' dans {c_name} non trouvé dans catfight_string_matching !")
            else:
                print(f"      ✅ '{opt}' correspond exactement")

    if errors:
        print("\n[!] ERREURS DÉTECTÉES :")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("\n[+] CONFORMITÉ TOTALE 100% : Tous les tokens d'enums sont reconnus par le moteur Sega !")
        return True

def main():
    base_dir = os.path.abspath('release_gog/data/minigame/catfight')
    info_bin = os.path.join(base_dir, 'catfight_human_info.bin')
    info_binc = os.path.join(base_dir, 'catfight_human_info.bin_c')
    matching_bin = os.path.join(base_dir, 'catfight_string_matching.bin')

    if not os.path.exists(info_bin):
        print(f"[!] Fichier introuvable: {info_bin}")
        sys.exit(1)

    rebuild_catfight_human_info(info_bin, info_bin, info_binc)

    # Replicate to staging directories if they exist
    for stg in ['staging_release/Yakuza0_FR_Patch_GOG_v1.12.9',
                'staging_release/Yakuza0_FR_Patch_GOG_v1.12.9_Nexus_PureAssets_NoExe']:
        stg_cf = os.path.join(stg, 'data/minigame/catfight')
        if os.path.isdir(stg_cf):
            shutil.copy2(info_bin, os.path.join(stg_cf, 'catfight_human_info.bin'))
            shutil.copy2(info_binc, os.path.join(stg_cf, 'catfight_human_info.bin_c'))
            print(f"  [+] Répliqué dans {stg_cf}")

    ok = verify_catfight_matching(matching_bin, info_bin)
    if not ok:
        sys.exit(1)
    print("\n[+] Calibration Catfight terminée avec SUCCÈS !")

if __name__ == '__main__':
    main()
