#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_stay_append.py
----------------------------------
Rebuilds release_gog/data/staypar/stay.par using the 2048-byte sector-aligned
append-only model (Gold Rule 3 of AGENTS.md):
1. Starts from pristine clean GOG stay.par (804,864 bytes).
2. Keeps all untouched files (including response_wanderer at 0x9a000) at their exact
   100% pristine original sector offsets.
3. Translates in-place with exact byte length preservation (0 heap overflow).
4. Cleans all residual UTF-8 / mojibake characters in correlation_person.bin_c bit-for-bit.
5. Preserves original compression flags (flags=0x0 for uncompressed, flags=0x80000000 for SLLZ).
6. Appends modified French tables at the end of the archive, each strictly aligned
   to 2048-byte (0x800) boundaries.
7. Pads archive to 2048-byte sector boundary.
"""

import os
import sys
import struct
import shutil

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz
from tools.translate_stay_par_complete import translate_exact_bytes
from tools.calibrate_stay_tables import (
    CABARET_AREA_CALIBRATED,
    BATTLE_RESULT_CALIBRATED,
    CABA_CAST_CALIBRATED,
    MONEY_ISLAND_TARENT_CALIBRATED,
    ULTIMATE_CALIBRATED,
    SEARCH_ARMS_PICTURE_CALIBRATED,
    SEARCH_ARMS_AGENT_CALIBRATED,
    SEARCH_ARMS_LOCATION_CALIBRATED,
    ACTIVITY_LIST_CALIBRATED,
)

def apply_in_place_clean(raw_data, trans_dict, table_name=''):
    out = bytearray(raw_data)
    for en, fr in trans_dict.items():
        en_b = en.encode('latin1')
        fr_clean = fr.replace('’', "'").replace('‘', "'").replace('«', '"').replace('»', '"').replace('œ', 'oe').replace('Œ', 'OE')
        fr_b = fr_clean.encode('latin1')
        diff = len(en_b) - len(fr_b)
        assert diff >= 0, f"Translation too long for {table_name}: {repr(en)}"
        rep_b = fr_b + (b' ' * diff)
        assert len(rep_b) == len(en_b)
        
        pos = 0
        while True:
            idx = out.find(en_b, pos)
            if idx == -1:
                break
            out[idx : idx + len(en_b)] = rep_b
            pos = idx + len(en_b)
    
    clean_bytes = bytes(out)
    assert len(clean_bytes) == len(raw_data), f"Length altered for {table_name}: {len(clean_bytes)} != {len(raw_data)}"
    assert clean_bytes.count(b'\x00') == raw_data.count(b'\x00'), f"Null count altered for {table_name}!"
    return clean_bytes

def get_clean_correlation_person_bin(ref_par):
    raw = ref_par['correlation_person.bin_c'][3]
    dec = decompress_sllz(raw) if raw[:4] == b'SLLZ' else raw

    col5_start = 16 + 6 * 64 + 148 + 377 + 512 + 696 + 1213
    col5_data = dec[col5_start : col5_start + 45948]

    strs = col5_data.split(b'\x00')[:86]
    new_strs = []
    for s in strs:
        try:
            text = s.decode('utf-8')
            text = text.replace('’', "'").replace('‘', "'").replace('œ', 'oe').replace('Œ', 'OE')
            encoded = text.encode('latin1')
            diff = len(s) - len(encoded)
            assert diff >= 0
            new_strs.append(encoded + b' ' * diff)
        except Exception:
            new_strs.append(s)

    new_col5_data = b'\x00'.join(new_strs) + b'\x00'
    if len(new_col5_data) < len(col5_data):
        new_col5_data += col5_data[len(new_col5_data):]

    assert len(new_col5_data) == len(col5_data)
    new_dec = dec[:col5_start] + new_col5_data + dec[col5_start + len(col5_data):]
    assert len(new_dec) == len(dec)

    comp = compress_sllz(new_dec)
    return 0x80000000, len(new_dec), len(comp), comp

def get_clean_activity_list_bin(clean_par):
    raw = decompress_sllz(clean_par['activity_list.bin_c'][3])
    clean = apply_in_place_clean(raw, ACTIVITY_LIST_CALIBRATED, 'activity_list.bin_c')
    comp = compress_sllz(clean)
    return 0x80000000, len(clean), len(comp), comp

def get_clean_search_arms_agent_bin(clean_par):
    raw = decompress_sllz(clean_par['search_arms_agent.bin_c'][3])
    clean = apply_in_place_clean(raw, SEARCH_ARMS_AGENT_CALIBRATED, 'search_arms_agent.bin_c')
    comp = compress_sllz(clean)
    return 0x80000000, len(clean), len(comp), comp

def get_clean_search_arms_location_bin(clean_par):
    raw = decompress_sllz(clean_par['search_arms_location.bin_c'][3])
    clean = apply_in_place_clean(raw, SEARCH_ARMS_LOCATION_CALIBRATED, 'search_arms_location.bin_c')
    comp = compress_sllz(clean)
    return 0x80000000, len(clean), len(comp), comp

def get_clean_controller_explain_bin(clean_par):
    raw = clean_par['controller_explain.bin_c'][3]
    clean = raw.replace(b'How to Play', b'Commandes  ')
    clean = clean.replace(b'Back to Title', b'Ecran titre  ')
    assert len(clean) == len(raw), f"Length mismatch in controller_explain: {len(clean)} != {len(raw)}"
    assert clean.count(b'\x00') == raw.count(b'\x00'), "Null count diff in controller_explain!"
    return 0x0, len(clean), len(clean), clean

def get_clean_response_roulette_bin(clean_par):
    raw = clean_par['response_roulette.bin_c'][3]
    clean = raw.replace(b'Good to go.', b'Pret !     ')
    clean = clean.replace(b'A big bet for <!--Name-->-san.', b'Grosse mise: <!--Name-->-san. ')
    clean = clean.replace(b'Ugh, this sucks.', b'Pff, la poisse. ')
    clean = clean.replace(b'Time to pray.', b'Faut prier.  ')
    assert len(clean) == len(raw), f"Length mismatch in response_roulette: {len(clean)} != {len(raw)}"
    assert clean.count(b'\x00') == raw.count(b'\x00'), "Null count diff in response_roulette!"
    return 0x0, len(clean), len(clean), clean

def get_clean_tougijyo_realtime_quest_bin(clean_par):
    raw = decompress_sllz(clean_par['tougijyo_realtime_quest.bin_c'][3])
    clean = raw.replace(b'Guard to block an attack!', b'Bloquez l\'attaque adverse')
    assert len(clean) == len(raw), f"Length mismatch in tougijyo_realtime_quest: {len(clean)} != {len(raw)}"
    assert clean.count(b'\x00') == raw.count(b'\x00'), "Null count diff in tougijyo_realtime_quest!"
    comp = compress_sllz(clean)
    return 0x80000000, len(clean), len(comp), comp

def get_clean_cabaret_island_area_bin(clean_par):
    raw = clean_par['cabaret_island_area.bin_c'][3]
    clean = apply_in_place_clean(raw, CABARET_AREA_CALIBRATED, 'cabaret_island_area.bin_c')
    return 0x0, len(clean), len(clean), clean

def get_clean_battle_result_bin(clean_par):
    raw = clean_par['battle_result.bin_c'][3]
    clean = apply_in_place_clean(raw, BATTLE_RESULT_CALIBRATED, 'battle_result.bin_c')
    return 0x0, len(clean), len(clean), clean

def get_clean_caba_cast_info_bin(clean_par):
    raw = decompress_sllz(clean_par['caba_cast_info.bin_c'][3])
    clean = apply_in_place_clean(raw, CABA_CAST_CALIBRATED, 'caba_cast_info.bin_c')
    comp = compress_sllz(clean)
    return 0x80000000, len(clean), len(comp), comp

def get_clean_money_island_tarent_bin(clean_par):
    raw = decompress_sllz(clean_par['money_island_tarent.bin_c'][3])
    clean = apply_in_place_clean(raw, MONEY_ISLAND_TARENT_CALIBRATED, 'money_island_tarent.bin_c')
    comp = compress_sllz(clean)
    return 0x80000000, len(clean), len(comp), comp

def get_clean_ultimate_bin(clean_par):
    raw = decompress_sllz(clean_par['ultimate.bin_c'][3])
    clean = apply_in_place_clean(raw, ULTIMATE_CALIBRATED, 'ultimate.bin_c')
    comp = compress_sllz(clean)
    return 0x80000000, len(clean), len(comp), comp

def get_clean_search_arms_result_picture_bin(clean_par):
    raw = decompress_sllz(clean_par['search_arms_result_picture.bin_c'][3])
    clean = apply_in_place_clean(raw, SEARCH_ARMS_PICTURE_CALIBRATED, 'search_arms_result_picture.bin_c')
    comp = compress_sllz(clean)
    return 0x80000000, len(clean), len(comp), comp

def rebuild_clean_stay_append(clean_par_path='par_original/stay.par',
                             ref_par_path='scratch/data/staypar/stay.par',
                             output_path='release_gog/data/staypar/stay.par'):
    print(f"[+] Reading pristine clean stay.par: {clean_par_path}")
    with open(clean_par_path, 'rb') as f:
        clean_bytes = f.read()
    clean_par = parse_par(clean_bytes)

    print(f"[+] Reading reference verified stay.par: {ref_par_path}")
    with open(ref_par_path, 'rb') as f:
        ref_bytes = f.read()
    ref_par = parse_par(ref_bytes)

    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_bytes[16:32])
    name_offset = 32 + folder_count * 64
    rebuilt_stay = bytearray(clean_bytes)

    # Tables that have verified in-place French translations or rich French versions
    # All in-place string replacements MUST preserve exact byte length and null counts (b' ' padding, not b'\x00')
    TARGET_TABLES = [
        'activity_list.bin_c',
        'battle_result.bin_c',
        'caba_cast_info.bin_c',
        'cabaret_island_area.bin_c',
        'controller_explain.bin_c',
        'correlation_person.bin_c',
        'money_island_tarent.bin_c',
        'response_roulette.bin_c',
        'search_arms_agent.bin_c',
        'search_arms_location.bin_c',
        'search_arms_result_picture.bin_c',
        'tougijyo_realtime_quest.bin_c',
        'tutorial.bin_c',
        'ultimate.bin_c',
        'virtue_shop.bin_c',
    ]

    modified_count = 0
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = clean_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')

        if name in TARGET_TABLES:
            if name == 'correlation_person.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_correlation_person_bin(ref_par)
            elif name == 'activity_list.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_activity_list_bin(clean_par)
            elif name == 'battle_result.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_battle_result_bin(clean_par)
            elif name == 'caba_cast_info.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_caba_cast_info_bin(clean_par)
            elif name == 'cabaret_island_area.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_cabaret_island_area_bin(clean_par)
            elif name == 'controller_explain.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_controller_explain_bin(clean_par)
            elif name == 'money_island_tarent.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_money_island_tarent_bin(clean_par)
            elif name == 'response_roulette.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_response_roulette_bin(clean_par)
            elif name == 'search_arms_agent.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_search_arms_agent_bin(clean_par)
            elif name == 'search_arms_location.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_search_arms_location_bin(clean_par)
            elif name == 'search_arms_result_picture.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_search_arms_result_picture_bin(clean_par)
            elif name == 'tougijyo_realtime_quest.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_tougijyo_realtime_quest_bin(clean_par)
            elif name == 'ultimate.bin_c':
                r_flags, r_u, r_c, r_data = get_clean_ultimate_bin(clean_par)
            elif name in ref_par:
                r_flags, r_u, r_c, r_data = ref_par[name]
            else:
                continue
            
            # Align strictly to 2048-byte sector boundary
            aligned_off = (len(rebuilt_stay) + 2047) & ~2047
            if aligned_off > len(rebuilt_stay):
                rebuilt_stay.extend(b'\x00' * (aligned_off - len(rebuilt_stay)))
            new_offset = len(rebuilt_stay)
            rebuilt_stay.extend(r_data)

            e_off = file_table_offset + i * 32
            struct.pack_into('>4I', rebuilt_stay, e_off, r_flags, r_u, r_c, new_offset)
            modified_count += 1
            print(f"  [+] Appended {name:32s} at sector {hex(new_offset)} (flags={hex(r_flags)}, u_sz={r_u:6d}, c_sz={r_c:6d})")

    final_aligned = (len(rebuilt_stay) + 2047) & ~2047
    if final_aligned > len(rebuilt_stay):
        rebuilt_stay.extend(b'\x00' * (final_aligned - len(rebuilt_stay)))

    with open(output_path, 'wb') as f:
        f.write(rebuilt_stay)
    print(f"\n[SUCCESS] Wrote {output_path} ({len(rebuilt_stay)} bytes, {modified_count} modified files) with strict 2048-byte sector alignment!")
    return True

if __name__ == '__main__':
    clean_p = sys.argv[1] if len(sys.argv) > 1 else 'par_original/stay.par'
    ref_p = sys.argv[2] if len(sys.argv) > 2 else 'scratch/data/staypar/stay.par'
    out_p = sys.argv[3] if len(sys.argv) > 3 else 'release_gog/data/staypar/stay.par'
    rebuild_clean_stay_append(clean_p, ref_p, out_p)
