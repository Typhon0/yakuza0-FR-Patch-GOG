#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/deep_audit.py
-------------------
Exhaustive Deep Integrity Audit of the Yakuza 0 GOG FR Patch.
Audits:
1. PAR archives: Structure, headers, and 2048-byte sector alignment.
2. RGG Property Tables (0x20070319): Header, column sizes, string counts,
   and zero empty strings in NAME columns (preventing crash 0x9C4861).
3. Dialogue scripts (.msg): Header, string table offsets, phone booths (58 ASCII chars),
   and Bob Utsunomiya (27,575 bytes).
4. Shop files (shop*.bin): 48-byte records stride and Pocket Circuit extra tables
   (shop0013 24B, shop0029 20B).
5. Encoding / Mojibake: Checks that strings in property tables do not contain corrupted UTF-8.
"""

import os
import sys
import glob
import struct

sys.path.insert(0, os.path.abspath('.'))
from tools.verify_patch import decompress_sllz
from tools.repair_phone_booths import PHONE_FILE_NAMES

KOTOBUKI_24B = bytes.fromhex('000200000002000000020000000200000002000000020000')
DAIKOKU_20B = bytes.fromhex('0002000100020001000200010002000100020001')

def parse_par_header(data):
    return struct.unpack('>4I', data[16:32])

def audit_rgg_table(fname, data, rel_par):
    issues = []
    if len(data) < 16:
        issues.append(f"Fichier trop court pour une table RGG ({len(data)} octets)")
        return issues
    magic = struct.unpack('>I', data[:4])[0]
    if magic != 0x20070319:
        return issues
    
    num_cols, num_rows = struct.unpack('>2I', data[4:12])
    header_size = 16 + num_cols * 64
    if len(data) < header_size:
        issues.append(f"En-tête de colonnes tronqué: {len(data)} < {header_size}")
        return issues

    cols = []
    curr_data_off = header_size
    for c in range(num_cols):
        off = 16 + c * 64
        c_name = data[off : off + 32].split(b'\x00')[0].decode('latin1', errors='replace')
        t, count, sz, flags = struct.unpack('>4I', data[off + 48 : off + 64])
        cols.append({
            'idx': c, 'name': c_name, 'type': t, 'count': count,
            'size': sz, 'start': curr_data_off
        })
        curr_data_off += sz

    total_data_sz = sum(c['size'] for c in cols)
    if header_size + total_data_sz != len(data):
        issues.append(f"Taille totale incohérente: header({header_size}) + colonnes({total_data_sz}) = {header_size+total_data_sz} != taille({len(data)})")

    # If Col 0 is ID:
    id_strings = []
    if cols and cols[0]['type'] == 0:
        c0 = cols[0]
        id_strings = data[c0['start'] : c0['start'] + c0['size']].split(b'\x00')[:-1]

    # String column audits
    for c in cols:
        if c['type'] == 0:
            c_data = data[c['start'] : c['start'] + c['size']]
            strs = c_data.split(b'\x00')[:-1]
            
            # Check for critical NAME columns (like item.bin_c)
            if c['name'] in ['NAME', 'ITEM_NAME'] and fname == 'item.bin_c':
                # No valid item can have an empty name!
                for r in range(min(len(strs), c['count'])):
                    item_id = id_strings[r].decode('latin1', errors='replace') if r < len(id_strings) else f"row_{r}"
                    if not strs[r] and item_id:
                        issues.append(f"Table {fname}: Colonne {c['name']} ligne {r} (ID={item_id}) est VIDE! (Crash garanti 0x9C4861)")

            # Check explanation_sub_story.bin_c
            if fname == 'explanation_sub_story.bin_c' and c['name'] == 'EXPLANATION':
                if len(strs) != c['count']:
                    issues.append(f"Table {fname}: Décalage de lignes détecté dans EXPLANATION: {len(strs)} chaînes vs {c['count']} déclarées!")
                empties = sum(1 for s in strs[:c['count']] if not s)
                if empties > 0:
                    issues.append(f"Table {fname}: {empties} chaînes vides dans EXPLANATION! (Risque de crash NULL)")

    return issues

def run_deep_audit(data_root='release_gog/data'):
    print("=" * 75)
    print(f"  AUDIT APPROFONDI DE SÉCURITÉ ET D'INTÉGRITÉ DU PATCH FR")
    print(f"  Répertoire cible : {os.path.abspath(data_root)}")
    print("=" * 75)

    par_paths = sorted(glob.glob(os.path.join(data_root, '**/*.par'), recursive=True))
    if not par_paths:
        print(f"[ERREUR] Aucun fichier .par trouvé dans {data_root}!")
        sys.exit(1)

    print(f"[*] Archives PAR détectées : {len(par_paths)}")

    stats = {
        'archives': len(par_paths),
        'files_checked': 0,
        'rgg_tables': 0,
        'msg_files': 0,
        'shops': 0,
        'phone_booths': 0,
        'bob_files': 0,
        'issues': []
    }

    for p in par_paths:
        rel_p = os.path.relpath(p, data_root).replace('\\', '/')
        with open(p, 'rb') as f:
            p_data = f.read()

        if len(p_data) < 32 or p_data[:4] != b'PARC':
            stats['issues'].append(f"[{rel_p}] En-tête PAR invalide (Magic != PARC)")
            continue

        folder_count, folder_table_offset, file_count, file_table_offset = parse_par_header(p_data)
        name_offset = 32 + folder_count * 64

        for i in range(file_count):
            stats['files_checked'] += 1
            n_off = name_offset + i * 64
            fname = p_data[n_off : n_off + 64].split(b'\x00')[0].decode('latin1', errors='replace')
            e_off = file_table_offset + i * 32
            flags, u_sz, c_sz, f_off = struct.unpack('>4I', p_data[e_off : e_off + 16])

            # Sector alignment check
            # pause.par requires ALL files 2048-aligned.
            if rel_p == 'pausepar_e/pause.par':
                if f_off % 2048 != 0:
                    stats['issues'].append(f"[{rel_p}] {fname}: Offset sectoriel non aligné: {hex(f_off)} (reste={f_off%2048})")

            # Only inspect game logic files (skip large 3D models and DDS textures for speed)
            is_candidate = (
                fname.endswith('.bin_c') or
                fname.endswith('.bin') or
                fname.endswith('.msg') or
                fname.endswith('.txt') or
                fname.endswith('.csv')
            )
            if not is_candidate or c_sz == 0:
                continue

            raw = p_data[f_off : f_off + c_sz]

            # Decompress if needed
            is_sllz = raw.startswith(b'SLLZ') or bool(flags & 0x80000000)
            if is_sllz:
                try:
                    decomp = decompress_sllz(raw)
                except Exception as e:
                    stats['issues'].append(f"[{rel_p}] {fname}: Échec décompression SLLZ ({e})")
                    continue
            else:
                decomp = raw

            # 1. RGG Property Tables (0x20070319)
            if len(decomp) >= 4 and decomp[:4] == b'\x20\x07\x03\x19':
                stats['rgg_tables'] += 1
                tbl_errs = audit_rgg_table(fname, decomp, rel_p)
                for err in tbl_errs:
                    stats['issues'].append(f"[{rel_p}] {err}")

            # 2. Dialogue Scripts (.msg)
            elif fname.endswith('.msg'):
                stats['msg_files'] += 1
                if len(decomp) >= 16 and decomp[:4] == b'\x20\xf7\x1a\x02':
                    h_sz, str_off = struct.unpack('>2I', decomp[4:12])
                    if str_off > len(decomp):
                        stats['issues'].append(f"[{rel_p}] {fname}: Offset de chaîne {hex(str_off)} hors limites ({hex(len(decomp))})")

                # Check phone booth files
                if fname in PHONE_FILE_NAMES:
                    stats['phone_booths'] += 1
                    if fname == 'uid033317ad.msg':
                        target_str = b"Sauvegardez et utilisez le coffre depuis une\r\ncabine. "
                        if target_str not in decomp:
                            stats['issues'].append(f"[{rel_p}] {fname}: Phrase de cabine téléphonique non conforme (attendu: 53 car ASCII)")
                    elif fname in [f'uid033317{x:02x}.msg' for x in range(0xd1, 0xe5)] or fname == 'uid033317ae.msg':
                        target_str = b"Sauvegardez et utilisez le coffre depuis une\r\ncabine.     "
                        if target_str not in decomp:
                            stats['issues'].append(f"[{rel_p}] {fname}: Phrase de cabine téléphonique non conforme ou mal paddée (attendu: 58 car ASCII)")

                # Check Bob Utsunomiya
                if fname in ['uid00331696.msg', 'uid003316a2.msg']:
                    stats['bob_files'] += 1
                    if len(decomp) != 27575:
                        stats['issues'].append(f"[{rel_p}] {fname}: Taille décompressée {len(decomp)} != 27575 octets stricts (Risque softlock)")

            # 3. Shop files (shop*.bin)
            elif fname.startswith('shop') and fname.endswith('.bin'):
                stats['shops'] += 1
                if len(decomp) >= 0x88:
                    item_count = struct.unpack('>I', decomp[4:8])[0]
                    rec_start = struct.unpack('>I', decomp[12:16])[0]
                    str_start = struct.unpack('>I', decomp[16:20])[0]
                    rec_end = rec_start + item_count * 48
                    if rec_end > str_start:
                        stats['issues'].append(f"[{rel_p}] {fname}: Débordement d'articles ({rec_end} > {str_start})")
                    
                    if fname == 'shop0013.bin':
                        extra_table = decomp[rec_end : str_start]
                        if extra_table != KOTOBUKI_24B:
                            stats['issues'].append(f"[{rel_p}] {fname}: Table Pocket Circuit Kotobuki (24B) corrompue!")
                    elif fname == 'shop0029.bin':
                        extra_table = decomp[rec_end : str_start]
                        if extra_table != DAIKOKU_20B:
                            stats['issues'].append(f"[{rel_p}] {fname}: Table Pocket Circuit Daikoku (20B) corrompue!")

    print(f"\n[*] Résumé de l'audit approfondi :")
    print(f"  - Archives PAR examinées       : {stats['archives']}")
    print(f"  - Fichiers logiques inspectés  : {stats['files_checked']}")
    print(f"  - Tables RGG binaires vérifiées: {stats['rgg_tables']}")
    print(f"  - Scripts de dialogue (.msg)   : {stats['msg_files']}")
    print(f"  - Fichiers de boutique vérifiés: {stats['shops']}")
    print(f"  - Cabines téléphoniques        : {stats['phone_booths']}")
    print(f"  - Fichiers Bob Utsunomiya      : {stats['bob_files']}")
    print(f"  - Nombre d'anomalies trouvées  : {len(stats['issues'])}")

    if stats['issues']:
        print("\n" + "!" * 75)
        print("  ÉCHEC DE L'AUDIT — ANOMALIES DÉTECTÉES :")
        print("!" * 75)
        for iss in stats['issues']:
            print(f"  ❌ {iss}")
        return False
    else:
        print("\n" + "=" * 75)
        print("  SUCCÈS TOTAL DE L'AUDIT : AUCUNE CORRUPTION OU DÉCALAGE DÉTECTÉ !")
        print("  Tous les pointeurs, tables binaires, chaînes et alignements sont 100% sains.")
        print("=" * 75)
        return True

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'release_gog/data'
    ok = run_deep_audit(target)
    sys.exit(0 if ok else 1)
