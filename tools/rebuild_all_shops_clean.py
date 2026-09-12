#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_all_shops_clean.py
--------------------------------
Translates all shop files (shop0000.bin - shop0034.bin, ex_shop0000.bin) in wdr.par:
1. Preserves 100% of binary prefixes (0x0 to str_start), including:
   - All item records
   - All trailing category tables:
     * shop0013.bin (Kotobuki Drugs): 24 bytes Pocket Circuit category table
     * shop0029.bin (Daikoku Drugstore): 20 bytes Pocket Circuit category table
     * shop0014.bin: 8 bytes
     * shop0019.bin (Ebisuya Pawn): 296 bytes
     * shop0031.bin: 8 bytes
2. Translates all 30 shop UI strings (0x10 to 0x88) to French with valid updated pointers.
   Never iterates beyond 30 pointers (prevents corrupting item records in shop0019.bin).
3. Translates all Item descriptions to French with valid updated pointers, mapped directly
   by item_id from the master French table in boot.par -> item.bin_c.
4. Preserves exact Sega GOG compression architecture:
   - Files originally compressed are SLLZ-compressed (flags=0x80000000)
   - Files originally uncompressed remain uncompressed (flags=0x0)
"""

import os, sys, struct
sys.path.insert(0, '.')
from tools.verify_patch import decompress_sllz
from tools.sllz import compress_sllz
from tools.shop_translations_data import SHOP_ITEM_TRANSLATIONS, ITEM_ID_TRANSLATIONS
from tools.translate_shops import UI_TRANSLATIONS

def parse_par_entries(data):
    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', data[16:32])
    name_offset = 32 + folder_count * 64
    files = {}
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = data[n_off:n_off+64].split(b'\x00')[0].decode('latin1')
        e_off = file_table_offset + i * 32
        flags, u_sz, c_sz, f_off = struct.unpack('>4I', data[e_off:e_off+16])
        files[name] = (flags, u_sz, c_sz, data[f_off:f_off+c_sz])
    return files

def translate_single_shop(clean_decomp, sname):
    item_count = struct.unpack('>I', clean_decomp[4:8])[0]
    rec_start = struct.unpack('>I', clean_decomp[12:16])[0]
    str_start = struct.unpack('>I', clean_decomp[0x10:0x14])[0]
    
    # 1. 100% exact copy of header + records + extra tables
    new_bin = bytearray(clean_decomp[:str_start])
    
    # 2. Translate UI strings (exactly 30 pointers from 0x10 to 0x88)
    for i in range(30):
        p = struct.unpack('>I', clean_decomp[0x10 + i*4 : 0x14 + i*4])[0]
        if p == 0:
            continue
        end = clean_decomp.find(b'\x00', p)
        en_s = clean_decomp[p:end].decode('latin1')
        fr_s = UI_TRANSLATIONS.get(en_s, en_s)
        new_p = len(new_bin)
        struct.pack_into('>I', new_bin, 0x10 + i*4, new_p)
        new_bin.extend(fr_s.encode('latin1') + b'\x00')
        
    # 3. Translate Item descriptions mapped by (sname, i) or item_id
    for i in range(item_count):
        rec_off = rec_start + i * 48
        item_id = struct.unpack('>H', clean_decomp[rec_off : rec_off + 2])[0]
        clean_desc_ptr = struct.unpack('>I', clean_decomp[rec_off + 0x20 : rec_off + 0x24])[0]
        if clean_desc_ptr == 0:
            continue
            
        c_end = clean_decomp.find(b'\x00', clean_desc_ptr)
        en_desc = clean_decomp[clean_desc_ptr:c_end].decode('latin1')
        
        fr_desc = None
        if (sname, i) in SHOP_ITEM_TRANSLATIONS:
            fr_desc = SHOP_ITEM_TRANSLATIONS[(sname, i)][1]
        elif item_id in ITEM_ID_TRANSLATIONS:
            fr_desc = ITEM_ID_TRANSLATIONS[item_id]
        else:
            fr_desc = en_desc
            
        new_p = len(new_bin)
        struct.pack_into('>I', new_bin, rec_off + 0x20, new_p)
        new_bin.extend(fr_desc.encode('latin1') + b'\x00')
        
    while len(new_bin) % 4 != 0:
        new_bin.append(0)
        
    return bytes(new_bin)

def generate_repaired_shops(clean_par_path='par_original/wdr.par', *args, **kwargs):
    print(f"[+] Using master shop translations ({len(SHOP_ITEM_TRANSLATIONS)} verified French shop item descriptions)")
    
    with open(clean_par_path, 'rb') as f:
        clean_files = parse_par_entries(f.read())
        
    repaired_shops = {}
    shop_names = [f for f in sorted(clean_files.keys()) if (f.startswith('shop') or f.startswith('ex_shop')) and f.endswith('.bin')]
    print(f"[+] Processing {len(shop_names)} shop binaries with pristine base from {clean_par_path}...")
    
    for sname in shop_names:
        c_flags, c_u, c_c, c_raw = clean_files[sname]
        c_decomp = decompress_sllz(c_raw) if (c_flags & 0x80000000) else c_raw
        
        new_decomp = translate_single_shop(c_decomp, sname)
        
        if c_flags & 0x80000000:
            comp_data = compress_sllz(new_decomp)
            repaired_shops[sname] = (0x80000000, len(new_decomp), len(comp_data), comp_data)
            print(f"  [+] {sname:14s}: COMPRESSED SLLZ {len(new_decomp)} -> {len(comp_data)} bytes")
        else:
            repaired_shops[sname] = (0x0, len(new_decomp), len(new_decomp), new_decomp)
            print(f"  [+] {sname:14s}: UNCOMPRESSED {len(new_decomp)} bytes")
            
    return repaired_shops

if __name__ == '__main__':
    repaired = generate_repaired_shops()
    print(f"\n[+] Successfully repaired all {len(repaired)} shop files!")
