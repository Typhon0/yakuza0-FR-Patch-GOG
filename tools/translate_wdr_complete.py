# -*- coding: utf-8 -*-
"""
translate_wdr_complete.py
Applies all translations (WDR_TRANSLATIONS + WDR_FINAL_DICT) to release_gog/data/wdr_par_c/wdr.par.
Verifies pure Latin1, no 0xC7, len(FR) <= len(EN), and repacks the PAR.
"""

import os
import sys
import shutil
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz
from tools.wdr_translations_data import WDR_TRANSLATIONS
from tools.wdr_dict_final import WDR_FINAL_DICT

def clean_fr(s):
    return s.replace('œ', 'oe').replace('Œ', 'OE').replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')

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

def main():
    wdr_path = 'release_gog/data/wdr_par_c/wdr.par'
    bak_path = wdr_path + '.pre_final.bak'
    if not os.path.exists(bak_path):
        print(f"[+] Creating backup {bak_path}...")
        shutil.copyfile(wdr_path, bak_path)

    # Combine translations
    combined = dict(WDR_TRANSLATIONS)
    combined.update(WDR_FINAL_DICT)
    print(f"[+] Total translations loaded: {len(combined)}")

    # Sort descending by key length to avoid prefix/substring collisions
    sorted_translations = sorted(combined.items(), key=lambda x: len(x[0]), reverse=True)

    with open(wdr_path, 'rb') as f:
        orig_bytes = f.read()

    files = parse_par(orig_bytes)
    replacements = {}
    total_matches = 0
    modified_files = 0

    for fn, (flags, u_sz, c_sz, data) in sorted(files.items()):
        is_compressed = data.startswith(b'SLLZ')
        try:
            decomp = bytearray(decompress_sllz(data))
        except Exception:
            decomp = bytearray(data)

        file_matched = 0
        for en, fr in sorted_translations:
            en_b = en.encode('latin1')
            fr_clean = clean_fr(fr)
            fr_b = fr_clean.encode('latin1')
            if len(fr_b) <= len(en_b):
                pos = 0
                while True:
                    idx = decomp.find(en_b, pos)
                    if idx == -1:
                        break
                    decomp[idx : idx + len(en_b)] = fr_b + b'\x00' * (len(en_b) - len(fr_b))
                    file_matched += 1
                    pos = idx + len(en_b)

        if file_matched > 0:
            modified_files += 1
            total_matches += file_matched
            if is_compressed:
                comp = compress_sllz(bytes(decomp))
                replacements[fn] = (flags, len(decomp), len(comp), comp)
            else:
                replacements[fn] = (flags, len(decomp), len(decomp), bytes(decomp))
            print(f"  [+] {fn:25}: replaced {file_matched:3} occurrences")

    print(f"\n[+] Total strings replaced: {total_matches} across {modified_files} files!")
    print("[+] Repacking wdr.par...")
    new_wdr = repack_par(orig_bytes, replacements)
    with open(wdr_path, 'wb') as f:
        f.write(new_wdr)
    print(f"[+] Successfully wrote {wdr_path} ({len(new_wdr)} bytes)!")

    # Verify repack by parsing
    print("[+] Verifying repacked wdr.par...")
    parsed = parse_par(new_wdr)
    print(f"[+] Successfully verified! {len(parsed)} files present in repacked wdr.par.")

if __name__ == '__main__':
    main()
