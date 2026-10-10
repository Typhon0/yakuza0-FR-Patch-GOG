#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_stay_inplace.py
-----------------------------------
Rebuilds stay.par using pure in-place sector patching:
1. Starts from pristine clean GOG stay.par (exactly 804,864 bytes).
2. Preserves 100% of all original Sega file offsets (zero offset drift, zero PAR table displacement).
3. Injects calibrated French translations strictly within each file's pre-allocated sector gap:
   - activity_list.bin_c (offset 0x3000, max 14336 bytes, new: 14017 bytes)
   - battle_result.bin_c (offset 0x12000, max 4096 bytes, new: 2412 bytes)
   - caba_cast_info.bin_c (offset 0x14000, max 4096 bytes, new: 3575 bytes)
   - cabaret_island_area.bin_c (offset 0x16800, max 4096 bytes, new: 3096 bytes)
   - controller_explain.bin_c (offset 0x22800, max 4096 bytes, new: 3620 bytes)
   - money_island_tarent.bin_c (offset 0x8c800, max 4096 bytes, new: 2848 bytes)
   - response_roulette.bin_c (offset 0x97000, max 4096 bytes, new: 2604 bytes)
   - ultimate.bin_c (offset 0xc0800, max 2048 bytes, new: 1660 bytes)
4. Zero-pads any remaining slack bytes in the gap to keep archive clean.
5. Updates flags, uncompressed size, and compressed size in the file entry table.
6. Guarantees output file length is EXACTLY 804,864 bytes.
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par
from tools.rebuild_clean_stay_append import (
    get_clean_activity_list_bin,
    get_clean_battle_result_bin,
    get_clean_caba_cast_info_bin,
    get_clean_cabaret_island_area_bin,
    get_clean_controller_explain_bin,
    get_clean_money_island_tarent_bin,
    get_clean_response_roulette_bin,
    get_clean_ultimate_bin,
    get_clean_search_arms_agent_bin,
    get_clean_search_arms_location_bin,
    get_clean_search_arms_result_picture_bin,
    get_clean_virtue_shop_bin,
)

def rebuild_clean_stay_inplace(clean_par_path='par_original/stay.par',
                              output_path='release_gog/data/staypar/stay.par'):
    print(f"[+] Reading pristine clean stay.par: {clean_par_path}")
    with open(clean_par_path, 'rb') as f:
        clean_bytes = bytearray(f.read())
    
    orig_len = len(clean_bytes)
    assert orig_len == 804864, f"Unexpected pristine size: {orig_len} != 804864"
    clean_par = parse_par(bytes(clean_bytes))

    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_bytes[16:32])
    name_offset = 32 + folder_count * 64

    # Build entry list to know available gaps
    entries = []
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = clean_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')
        e_off = file_table_offset + i * 32
        flags, u_sz, c_sz, off = struct.unpack('>4I', clean_bytes[e_off : e_off + 16])
        entries.append({
            'idx': i,
            'name': name,
            'flags': flags,
            'u_sz': u_sz,
            'c_sz': c_sz,
            'off': off,
            'e_off': e_off
        })

    entries_by_off = sorted(entries, key=lambda x: x['off'])
    entry_map = {e['name']: e for e in entries}

    generators = {
        'activity_list.bin_c': get_clean_activity_list_bin,
        'battle_result.bin_c': get_clean_battle_result_bin,
        'caba_cast_info.bin_c': get_clean_caba_cast_info_bin,
        'cabaret_island_area.bin_c': get_clean_cabaret_island_area_bin,
        'controller_explain.bin_c': get_clean_controller_explain_bin,
        'money_island_tarent.bin_c': get_clean_money_island_tarent_bin,
        'response_roulette.bin_c': get_clean_response_roulette_bin,
        'search_arms_agent.bin_c': get_clean_search_arms_agent_bin,
        'search_arms_location.bin_c': get_clean_search_arms_location_bin,
        'search_arms_result_picture.bin_c': get_clean_search_arms_result_picture_bin,
        'ultimate.bin_c': get_clean_ultimate_bin,
        'virtue_shop.bin_c': get_clean_virtue_shop_bin,
    }

    modified_count = 0
    for idx, e in enumerate(entries_by_off):
        name = e['name']
        if name in generators:
            next_off = entries_by_off[idx + 1]['off'] if idx + 1 < len(entries_by_off) else orig_len
            available_gap = next_off - e['off']
            
            new_flags, new_u, new_c, new_data = generators[name](clean_par)
            assert len(new_data) == new_c, f"Data len mismatch: {len(new_data)} != {new_c}"
            assert new_c <= available_gap, f"Over-allocation for {name}: {new_c} > {available_gap}"

            # Write in-place into clean_bytes
            off = e['off']
            clean_bytes[off : off + new_c] = new_data
            
            # Zero out any slack bytes between new_c and available_gap if previous file was larger
            if e['c_sz'] > new_c:
                slack = e['c_sz'] - new_c
                clean_bytes[off + new_c : off + e['c_sz']] = b'\x00' * slack

            # Update file entry header (flags, u_sz, c_sz, offset stays unchanged!)
            struct.pack_into('>3I', clean_bytes, e['e_off'], new_flags, new_u, new_c)
            modified_count += 1
            print(f"  [+] In-place patched {name:28s} at sector {hex(off)} (flags={hex(new_flags)}, u={new_u:5d}, c={new_c:5d}, gap={available_gap:5d})")

    assert len(clean_bytes) == orig_len, f"Size changed! {len(clean_bytes)} != {orig_len}"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(clean_bytes)

    print(f"\n[SUCCESS] Wrote {output_path} ({len(clean_bytes)} bytes, {modified_count} files patched in-place)!")
    print(f"Archive length is bit-exact to Sega vanilla (804,864 bytes) with 0 offset drift!")
    return True

if __name__ == '__main__':
    clean_p = sys.argv[1] if len(sys.argv) > 1 else 'par_original/stay.par'
    out_p = sys.argv[2] if len(sys.argv) > 2 else 'release_gog/data/staypar/stay.par'
    rebuild_clean_stay_inplace(clean_p, out_p)
