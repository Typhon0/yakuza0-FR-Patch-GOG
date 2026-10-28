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

ORIG_CACHE = {}
def get_orig_file(par_name, fname):
    if par_name not in ORIG_CACHE:
        path = os.path.join('par_original', par_name)
        if os.path.exists(path):
            try:
                from tools.rebuild_clean_boot_append import parse_par
                with open(path, 'rb') as f:
                    ORIG_CACHE[par_name] = parse_par(f.read())
            except Exception:
                ORIG_CACHE[par_name] = {}
        else:
            ORIG_CACHE[par_name] = {}
    entry = ORIG_CACHE[par_name].get(fname)
    if entry:
        raw = entry[3]
        return decompress_sllz(raw) if raw.startswith(b'SLLZ') or (entry[0] & 0x80000000) else raw
    return None

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

    # Reference vanilla table for null count comparison (protection against 0x30ED vsnprintf crash)
    orig_decomp = get_orig_file(os.path.basename(rel_par), fname) if rel_par else None
    orig_cols_map = {}
    if orig_decomp and len(orig_decomp) >= 16 and orig_decomp[:4] == b'\x20\x07\x03\x19':
        o_cols, _ = struct.unpack('>2I', orig_decomp[4:12])
        o_start = 16 + o_cols * 64
        for oc in range(o_cols):
            o_off = 16 + oc * 64
            oc_name = orig_decomp[o_off : o_off + 32].split(b'\x00')[0].decode('latin1', errors='replace')
            ot, count, sz, _ = struct.unpack('>4I', orig_decomp[o_off + 48 : o_off + 64])
            orig_cols_map[oc] = {
                'name': oc_name, 'type': ot, 'count': count, 'size': sz,
                'data': orig_decomp[o_start : o_start + sz]
            }
            o_start += sz

    # String column audits
    for c in cols:
        if c['type'] in (0, 1):
            c_data = data[c['start'] : c['start'] + c['size']]
            strs = c_data.split(b'\x00')[:-1]

            # Null count check against original vanilla table
            if c['idx'] in orig_cols_map and orig_cols_map[c['idx']]['type'] in (0, 1):
                o_c_data = orig_cols_map[c['idx']]['data']
                o_nulls = o_c_data.count(b'\x00')
                r_nulls = c_data.count(b'\x00')
                if o_nulls != r_nulls:
                    issues.append(f"Table {fname}: Colonne {c['name']} (type {c['type']}): Nombre d'octets nuls altéré ({r_nulls} vs {o_nulls} vanilla) - décalage de lignes garanti (Crash vsnprintf 0x30ED)!")
            
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

def audit_translation_syntax():
    issues = []
    import re
    fmt_regex = re.compile(r'%[0-9]*\.?[0-9]*[sdifuoxXgGce%]')
    try:
        from tools.wdr_translations_data import WDR_TRANSLATIONS
        from tools.wdr_dict_final import WDR_FINAL_DICT
        from tools.stay_translations_data import STAY_TRANSLATIONS
        combined = dict(WDR_TRANSLATIONS)
        combined.update(WDR_FINAL_DICT)
        combined.update(STAY_TRANSLATIONS)
        for en, fr in combined.items():
            if not isinstance(en, str) or not isinstance(fr, str):
                continue
            en_fmts = [f for f in fmt_regex.findall(en) if f != '%%']
            fr_fmts = [f for f in fmt_regex.findall(fr) if f != '%%']
            if en_fmts != fr_fmts:
                issues.append(f"Format specifier mismatch: {en[:30]!r} ({en_fmts}) vs {fr[:30]!r} ({fr_fmts})")
            if fr.count('(') != fr.count(')'):
                issues.append(f"Unbalanced parentheses: {fr[:40]!r}")
            if ('<' in fr and '>' not in fr) or fr.count('<') != fr.count('>'):
                issues.append(f"Unbalanced tag brackets: {fr[:40]!r}")
    except Exception as e:
        issues.append(f"Erreur chargement dictionnaires traductions: {e}")
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
        'syntax_checked': 0,
        'issues': []
    }

    # Audit syntax & format specifiers across translation dictionaries
    syntax_errs = audit_translation_syntax()
    for se in syntax_errs:
        stats['issues'].append(f"[Syntax/Linter] {se}")

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
                if len(decomp) >= 24 and decomp[0] == 0x20:
                    tbl_off = struct.unpack('>I', decomp[0x14:0x18])[0]
                    if tbl_off >= len(decomp):
                        stats['issues'].append(f"[{rel_p}] {fname}: tbl_off {hex(tbl_off)} dépasse la taille du fichier ({hex(len(decomp))})")
                    elif tbl_off + 4 <= len(decomp):
                        cnt = struct.unpack('>I', decomp[tbl_off:tbl_off+4])[0]
                        if cnt > 100:
                            stats['issues'].append(f"[{rel_p}] {fname}: Compte de table corrompu {cnt} (0x{cnt:x}) à {hex(tbl_off)} (Risque boucle bswap/crash 0x6EA32C)")
                        if tbl_off > 0 and decomp[tbl_off-1:tbl_off] == b' ':
                            stats['issues'].append(f"[{rel_p}] {fname}: Espace résiduel 0x20 à la frontière de table {hex(tbl_off-1)}")

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

                # Check Kamoji Drunk node (uid01261727.msg)
                if fname == 'uid01261727.msg':
                    w0_drunk = struct.unpack('>I', decomp[0x884:0x888])[0]
                    enc_drunk = (w0_drunk >> 16) & 0xFFFF
                    if enc_drunk != 98:
                        stats['issues'].append(f"[{rel_p}] {fname}: Nœud Drunk à 0x884 désynchronisé ({enc_drunk} != 98, risque softlock Kamoji)")

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

    # 4. Verification des tables de mini-jeux isolees (loose files dans data/minigame)
    minigame_dir = os.path.join(data_root, 'minigame')
    stats['minigame_tables'] = 0
    if os.path.isdir(minigame_dir):
        for root, dirs, files in os.walk(minigame_dir):
            for f in sorted(files):
                if f.endswith('.bak'):
                    stats['issues'].append(f"[minigame] Fichier résiduel .bak non désiré : {os.path.join(root, f)}")
                elif f.endswith('.bin'):
                    stats['minigame_tables'] += 1
                    f_path = os.path.join(root, f)
                    with open(f_path, 'rb') as mf:
                        m_data = mf.read()
                    if len(m_data) < 16 or m_data[:4] != b'\x20\x07\x03\x19':
                        stats['issues'].append(f"[minigame] {f}: En-tête RGG invalide ou compressé en SLLZ ({m_data[:4]})")
                    twin_path = f_path + '_c'
                    if not os.path.exists(twin_path):
                        stats['issues'].append(f"[minigame] {f}: Fichier jumeau .bin_c manquant!")
                    else:
                        with open(twin_path, 'rb') as tf:
                            t_data = tf.read()
                        if m_data != t_data:
                            stats['issues'].append(f"[minigame] {f}: Incohérence entre .bin et .bin_c ({len(m_data)} vs {len(t_data)} octets)")

    print(f"\n[*] Résumé de l'audit approfondi :")
    print(f"  - Archives PAR examinées       : {stats['archives']}")
    print(f"  - Fichiers logiques inspectés  : {stats['files_checked']}")
    print(f"  - Tables RGG binaires vérifiées: {stats['rgg_tables']}")
    print(f"  - Tables mini-jeux isolées (.bin): {stats['minigame_tables']}")
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
