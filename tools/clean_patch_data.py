#!/usr/bin/env python3
"""
clean_patch_data.py
Automated text and mojibake cleaning tool for Yakuza 0 VOSTFR patch.
Eliminates:
 - UTF-8 typographic apostrophes (\\xe2\\x80\\x99 / â€™) that render as 'TM'
 - UTF-8 accent residues (Ã©, Ã¨, Ã , Ãª, Ã‰...)
 - UTF-8 ligatures (\\xc5\\x93 -> oe)
 - UTF-8 ellipsis (\\xe2\\x80\\xa6 -> ...)
Directly in data archives (boot.par, wdr.par) without modifying font textures.
"""

import os
import sys
import struct
import io
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sllz import compress_sllz, decompress_sllz

# Exact replacements (bad_sequence, clean_sequence)
# Every replacement has len(clean_sequence) <= len(bad_sequence) so it can be padded with null bytes
TEXT_REPLACEMENTS = [
    # 1. boot.par -> item.bin_c
    (
        b"Poulet au yuzu et soba d\xe2\x80\x99\xc3\xa9pinards\x00",
        b"Poulet au yuzu et soba d'\xe9pinards\x00"
    ),
    (
        b"Pi\xc3\xa8ce d\xe2\x80\x99OVNI\x00",
        b"Pi\xe8ce d'OVNI\x00"
    ),
    (
        b"Ses balles ont des effets diff\xc3\xa9rents. L'inconv\xc3\xa9nient,\nc'est qu'on ne sait pas ce que c'est avant\nd\xe2\x80\x99avoir tirer.\x00",
        b"Ses balles ont des effets diff\xe9rents. L'inconv\xe9nient,\nc'est qu'on ne sait pas ce que c'est avant\nd'avoir tir\xe9.\x00"
    ),
    (
        b"Porter cet encens intrigant vous rend plus susceptible\nde rencontrer des ennemis ayant beaucoup d\xe2\x80\x99argent.\x00",
        b"Porter cet encens intrigant vous rend plus susceptible\nde rencontrer des ennemis ayant beaucoup d'argent.\x00"
    ),
    (
        b"Ce fragment de m\xc3\xa9t\xc3\xa9orite est un objet extr\xc3\xaamement\nrare. \xc3\x89tant donn\xc3\xa9 ses origines d\xe2\x80\x99un autre monde,\nil se vendrait sans doute pour une petite fortune.\x00",
        b"Ce fragment de m\xe9t\xe9orite est un objet extr\xeamement\nrare. \xc9tant donn\xe9 ses origines d'un autre monde,\nil se vendrait sans doute pour une petite fortune.\x00"
    ),

    # 2. boot.par -> explanation_sub_story.bin_c
    (
        b"J'ai trouv\xc3\xa9 le yakuza qui a pris Ara-Q3 au voyou qui\nl'a pris au gamin qui l'a arrach\xc3\xa9 \xc3\xa0 Akio \xc3\xa0 l'origine.\n\xe2\x80\xa6 Trop compliqu\xc3\xa9 ! Quelqu'un va se faire frapper !\x00",
        b"J'ai trouv\xe9 le yakuza qui a pris Ara-Q3 au voyou qui\nl'a pris au gamin qui l'a arrach\xe9 \xe0 Akio \xe0 l'origine.\n... Trop compliqu\xe9 ! Quelqu'un va se faire frapper !\x00"
    ),

    # 3. boot.par -> tips_tutorial.bin_c
    (
        b"La s\xc3\xa9curit\xc3\xa9 a r\xc3\xa9solu le conflit\nSant\xc3\xa9 r\xc3\xa9duite de \xe2\x98\x85\x00",
        b"La s\xe9curit\xe9 a r\xe9solu le conflit\nSant\xe9 r\xe9duite de \xe2\x98\x85\x00"
    ),
    (
        b"La s\xc3\xa9curit\xc3\xa9 a r\xc3\xa9solu le conflit\nSant\xc3\xa9 r\xc3\xa9duite de \xe2\x98\x85\xe2\x98\x85\x00",
        b"La s\xe9curit\xe9 a r\xe9solu le conflit\nSant\xe9 r\xe9duite de \xe2\x98\x85\xe2\x98\x85\x00"
    ),
    (
        b"La s\xc3\xa9curit\xc3\xa9 a r\xc3\xa9solu le conflit\nSant\xc3\xa9 r\xc3\xa9duite de \xe2\x98\x85\xe2\x98\x85\xe2\x98\x85\x00",
        b"La s\xe9curit\xe9 a r\xe9solu le conflit\nSant\xe9 r\xe9duite de \xe2\x98\x85\xe2\x98\x85\xe2\x98\x85\x00"
    ),

    # 4. wdr.par -> restaurant0006.bin
    (
        b"Cet ensemble propose un sandwich au bacon, aux \xc5\x93ufs\net \xc3\xa0 la laitue sur du pain blanc.\x00",
        b"Cet ensemble propose un sandwich au bacon, aux oeufs\net \xe0 la laitue sur du pain blanc.\x00"
    ),

    # 5. wdr.par -> uid010c1655.msg
    (
        b"Hein ? Rester silencieux pendant l\xe2\x80\x99\xc3\xa9v\xc3\xa9nement ? Une session\r\nsans parler ne serait-elle pas un drame ?\x00",
        b"Hein ? Rester silencieux pendant l'\xe9v\xe9nement ? Une session\r\nsans parler ne serait-elle pas un drame ?\x00"
    ),

    # 6. wdr.par -> uid010c1780.msg
    (
        b"C\xe2\x80\x99est l\xe2\x80\x99hopital qui se moque de la charit\xc3\xa9. Nous sommes faits du\r\nm\xc3\xaame bois, toi et moi.\x00",
        b"C'est l'hopital qui se moque de la charit\xe9. Nous sommes faits du\r\nm\xeame bois, toi et moi.\x00"
    ),

    # 7. wdr.par -> uid010c16b0.msg
    (
        b"La cote de s\xc3\xa9curit\xc3\xa9 de la zone Leisure King a baiss\xc3\xa9 d'un niveau.\r\nLa cote de r\xc3\xa9solution de probl\xc3\xa8mes du personnel de s\xc3\xa9curit\xc3\xa9 en\r\nservice a \xc3\xa9t\xc3\xa9 r\xc3\xa9duite d'un niveau \xe2\x98\x85.\x00",
        b"La cote de s\xe9curit\xe9 de la zone Leisure King a baiss\xe9 d'un niveau.\r\nLa cote de r\xe9solution de probl\xe8mes du personnel de s\xe9curit\xe9 en\r\nservice a \xe9t\xe9 r\xe9duite d'un niveau \xe2\x98\x85.\x00"
    ),

    # 8. wdr.par -> uid010c16be.msg
    (
        b"La cote de s\xc3\xa9curit\xc3\xa9 de la zone Electronics King a baiss\xc3\xa9 d'un niveau.\r\nLa note de r\xc3\xa9solution de probl\xc3\xa8mes pour le personnel de s\xc3\xa9curit\xc3\xa9 en\r\nservice a \xc3\xa9t\xc3\xa9 r\xc3\xa9duite d'un niveau \xe2\x98\x85.\x00",
        b"La cote de s\xe9curit\xe9 de la zone Electronics King a baiss\xe9 d'un niveau.\r\nLa note de r\xe9solution de probl\xe8mes pour le personnel de s\xe9curit\xe9 en\r\nservice a \xe9t\xe9 r\xe9duite d'un niveau \xe2\x98\x85.\x00"
    ),

    # 9. wdr.par -> uid010c16ce.msg
    (
        b"La note de s\xc3\xa9curit\xc3\xa9 de la zone Gambling King a baiss\xc3\xa9 d'un niveau.\r\nLa cote de r\xc3\xa9solution de probl\xc3\xa8mes du personnel de s\xc3\xa9curit\xc3\xa9 en\r\nservice a \xc3\xa9t\xc3\xa9 r\xc3\xa9duite d'un niveau \xe2\x98\x85.\x00",
        b"La note de s\xe9curit\xe9 de la zone Gambling King a baiss\xe9 d'un niveau.\r\nLa cote de r\xe9solution de probl\xe8mes du personnel de s\xe9curit\xe9 en\r\nservice a \xe9t\xe9 r\xe9duite d'un niveau \xe2\x98\x85.\x00"
    ),
]

def parse_par_table(par_data):
    magic, unkA, unkB, unkC = struct.unpack('>4I', par_data[:16])
    assert magic == 0x50415243, "Not a valid PARC archive"
    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', par_data[16:32])
    
    file_names_offset = 32 + folder_count * 64
    entries = {}
    for i in range(file_count):
        name_offset = file_names_offset + i * 64
        name = par_data[name_offset:name_offset+64].split(b'\x00')[0].decode('latin1')
        entry_offset = file_table_offset + i * 32
        flags, uncomp_sz, comp_sz, offset = struct.unpack('>4I', par_data[entry_offset:entry_offset+16])
        entries[name] = {
            'index': i,
            'entry_offset': entry_offset,
            'flags': flags,
            'uncomp_size': uncomp_sz,
            'comp_size': comp_sz,
            'offset': offset,
            'raw_data': par_data[offset:offset+comp_sz]
        }
    return entries

def is_text_candidate(name):
    """Determines whether a file in PAR archive contains French human text."""
    if name.endswith('.msg'):
        return True
    if name.startswith('restaurant') and name.endswith('.bin'):
        return True
    if name.startswith('explanation_') and name.endswith('.bin_c'):
        return True
    if name.startswith('encounter_') and name.endswith('.bin_c'):
        return True
    if name.startswith('tips_') and name.endswith('.bin_c'):
        return True
    if name in ['item.bin_c', 'cmn.bin']:
        return True
    return False

def clean_data_buffer(data_bytes, filename=None):
    """Replaces known corrupted text sequences in-place with null-padding."""
    data = bytearray(data_bytes)
    modified = False
    mod_count = 0
    for bad, good in TEXT_REPLACEMENTS:
        idx = 0
        while True:
            pos = data.find(bad, idx)
            if pos == -1:
                break
            diff = len(bad) - len(good)
            assert diff >= 0, f"Error: replacement {good} is longer than {bad}"
            padded = good + (b'\x00' * diff)
            data[pos:pos+len(bad)] = padded
            modified = True
            mod_count += 1
            idx = pos + len(bad)

    # Normalize Ç majuscule (\xc7) to C (\x43) to prevent the Trade Mark (™) font glitch
    if filename and is_text_candidate(filename):
        # 1. \xc7a -> Ca
        ca_count = data.count(b'\xc7a')
        if ca_count > 0:
            data = bytearray(bytes(data).replace(b'\xc7a', b'Ca'))
            modified = True
            mod_count += ca_count
        # 2. \xc7A in French words (followed by punctuation, space, newline or null)
        for term in [b'\xc7A ', b'\xc7A.', b'\xc7A ?', b'\xc7A !', b'\xc7A\r', b'\xc7A\n', b'\xc7A\x00']:
            term_rep = term.replace(b'\xc7A', b'CA')
            cnt = data.count(term)
            if cnt > 0:
                data = bytearray(bytes(data).replace(term, term_rep))
                modified = True
                mod_count += cnt

    return bytes(data) if modified else None, mod_count

def patch_par_archive(par_path):
    print(f"\nProcessing archive: {par_path}")
    with open(par_path, 'rb') as f:
        par_data = bytearray(f.read())
        
    entries = parse_par_table(par_data)
    total_modified_files = 0
    total_modifications = 0
    
    for name, info in entries.items():
        if not (name.endswith('.bin') or name.endswith('.bin_c') or name.endswith('.msg') or name == 'cmn.bin'):
            continue
            
        raw = info['raw_data']
        is_sllz = bool(info['flags'] & 0x80000000) or raw[:4] == b'SLLZ'
        
        uncompressed = decompress_sllz(raw) if is_sllz else raw
        cleaned, count = clean_data_buffer(uncompressed, filename=name)
        
        if cleaned:
            total_modified_files += 1
            total_modifications += count
            print(f"  [+] Cleaned {name}: {count} sentence correction(s) applied")
            
            if is_sllz:
                new_comp = compress_sllz(cleaned)
                old_comp_sz = info['comp_size']
                print(f"      SLLZ recompressed: {len(new_comp)} bytes (original slot: {old_comp_sz})")
                assert len(new_comp) <= old_comp_sz, f"Recompressed size {len(new_comp)} exceeded original slot {old_comp_sz}"
                # Pad to exact slot size to preserve all subsequent file offsets
                padded_comp = new_comp + b'\x00' * (old_comp_sz - len(new_comp))
                par_data[info['offset'] : info['offset'] + old_comp_sz] = padded_comp
                # Update compressed size in the PAR entry table
                struct.pack_into('>I', par_data, info['entry_offset'] + 8, len(new_comp))
            else:
                old_sz = info['comp_size']
                assert len(cleaned) == old_sz, f"Uncompressed size mismatch for {name}: {len(cleaned)} vs {old_sz}"
                par_data[info['offset'] : info['offset'] + old_sz] = cleaned

    if total_modified_files > 0:
        # Create backup if not already present
        bak_path = par_path + ".bak"
        if not os.path.exists(bak_path):
            shutil.copyfile(par_path, bak_path)
            print(f"  Backup created: {bak_path}")
        # Save updated par
        with open(par_path, 'wb') as f:
            f.write(par_data)
        print(f"  Saved {par_path} successfully ({total_modified_files} files updated, {total_modifications} corrections).")
    else:
        print(f"  No modifications required for {par_path}.")

def main():
    target_archives = [
        'release_gog/data/bootpar/boot.par',
        'release_gog/data/wdr_par_c/wdr.par',
    ]
    
    for arch in target_archives:
        if os.path.isfile(arch):
            patch_par_archive(arch)
        else:
            print(f"Warning: {arch} not found.")

if __name__ == '__main__':
    main()
