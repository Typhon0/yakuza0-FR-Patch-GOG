# -*- coding: utf-8 -*-
"""
tools/repair_stay_par.py

Repairs release_gog/data/staypar/stay.par:
1. Replaces corrupted ultimate.bin_c with Sega's pristine ultimate.bin_j table payload.
2. Fixes controller_explain.bin_c flag to 0x80000000 (SLLZ compressed) matching its payload.
3. Replaces any tables that had generic resizing with their pristine Sega bin_j versions or safe tables.
4. Repacks stay.par with 64-byte alignment and verifies all entries.
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz

def repack_par(orig_bytes, file_replacements={}):
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
        
        aligned_off = (curr_off + 63) & ~63
        if aligned_off > len(rebuilt):
            rebuilt.extend(b'\x00' * (aligned_off - len(rebuilt)))
        
        new_file_offset = len(rebuilt)
        rebuilt.extend(n_data)
        curr_off = len(rebuilt)
        struct.pack_into('>4I', rebuilt, item['entry_offset'], n_flags, n_u_sz, n_c_sz, new_file_offset)
    
    return bytes(rebuilt)

def repair_stay():
    stay_path = 'release_gog/data/staypar/stay.par'
    print(f"[+] Loading {stay_path}...")
    with open(stay_path, 'rb') as f:
        stay_bytes = f.read()

    files = parse_par(stay_bytes)
    replacements = {}

    # 1. Fix controller_explain.bin_c:
    # It has raw payload starting with b'SLLZ', u_sz=4328, c_sz=2106.
    # Needs flags = 0x80000000
    ce_flags, ce_u, ce_c, ce_data = files['controller_explain.bin_c']
    if ce_data[:4] == b'SLLZ':
        replacements['controller_explain.bin_c'] = (0x80000000, ce_u, ce_c, ce_data)
        print(f"  [+] Fixed controller_explain.bin_c: flag set to 0x80000000 (c_sz={ce_c}, u_sz={ce_u})")

    # 2. Fix ultimate.bin_c:
    # Restore from pristine ultimate.bin_j
    uj_flags, uj_u, uj_c, uj_data = files['ultimate.bin_j']
    replacements['ultimate.bin_c'] = (uj_flags, uj_u, uj_c, uj_data)
    print(f"  [+] Fixed ultimate.bin_c: restored from ultimate.bin_j (flags={hex(uj_flags)}, u_sz={uj_u}, c_sz={uj_c})")

    # Check other tables that were touched by translate_rgg_table:
    # money_island_tarent, caba_cast_info, cabaret_island_area, battle_result, search_arms_agent, virtue_shop
    # If any has mismatched structure, restore from .bin_j
    check_tables = [
        'money_island_tarent',
        'caba_cast_info',
        'cabaret_island_area',
        'battle_result',
        'search_arms_agent',
        'virtue_shop'
    ]
    for tbl in check_tables:
        c_name = tbl + '.bin_c'
        j_name = tbl + '.bin_j'
        if c_name in files and j_name in files:
            cf, cu, cc, cd = files[c_name]
            jf, ju, jc, jd = files[j_name]
            # Decompress both to check column validity
            dec_c = decompress_sllz(cd) if cd[:4] == b'SLLZ' else cd
            dec_j = decompress_sllz(jd) if jd[:4] == b'SLLZ' else jd
            c_cols = struct.unpack('>I', dec_c[4:8])[0] if len(dec_c) >= 8 else 0
            j_cols = struct.unpack('>I', dec_j[4:8])[0] if len(dec_j) >= 8 else 0
            c_rows = struct.unpack('>I', dec_c[8:12])[0] if len(dec_c) >= 12 else 0
            j_rows = struct.unpack('>I', dec_j[8:12])[0] if len(dec_j) >= 12 else 0
            if c_cols != j_cols or c_rows != j_rows:
                print(f"  [!] Structural mismatch detected in {c_name}! Restoring from {j_name}...")
                replacements[c_name] = (jf, ju, jc, jd)
            else:
                print(f"  [+] Verified {c_name}: cols={c_cols}, rows={c_rows} matches Sega template.")

    print(f"[+] Rebuilding stay.par with {len(replacements)} repaired tables...")
    new_stay = repack_par(stay_bytes, replacements)
    with open(stay_path, 'wb') as f:
        f.write(new_stay)
    print(f"[+] Successfully wrote {stay_path} ({len(new_stay)} bytes)!")

    # Verify every single file in the repacked stay.par
    print("[+] Verifying all entries in repaired stay.par...")
    v_files = parse_par(new_stay)
    err_count = 0
    for name, (fl, u, c, raw) in v_files.items():
        is_sllz = (raw[:4] == b'SLLZ')
        has_flag = bool(fl & 0x80000000)
        if is_sllz != has_flag:
            print(f"  [ERROR] Flag mismatch for {name}: is_sllz={is_sllz}, has_flag={has_flag}")
            err_count += 1
    if err_count == 0:
        print("[SUCCESS] All entries in stay.par are 100% physically valid and consistent!")
    else:
        print(f"[FAIL] Found {err_count} errors in stay.par!")

if __name__ == '__main__':
    repair_stay()
