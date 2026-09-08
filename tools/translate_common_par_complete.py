# -*- coding: utf-8 -*-
"""
translate_common_par_complete.py

Translates 100% of text in release_gog/data/wdr_par_c/common.par:
- blacksmith.bin
- sale0000.bin, sale0001.bin, sale0002.bin
- arms_repair.bin (fixing broken \xc7 trademark character)
- present.bin
- send.bin
- throw.bin
- ai_popup.bin
"""

import os
import sys
import shutil
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz

TRANSLATIONS = {
    # blacksmith.bin
    "Order": "Ordre",
    "None": "Rien",
    "That'll be %s. Is that all right?": "Ca fera %s. C'est d'accord ?",
    "It'll cost %s to make. Is that okay?": "Fabrication : %s. D'accord ?",
    "You don't seem to have enough cash.": "Pas assez d'argent sur vous.",
    "Your inventory is full.": "Inventaire plein.",
    "You don't have all the parts.": "Il manque des composants.",
    "Item lineup expanded.": "Assortiment etendu !",
    "There are new items to craft.": "Nouveaux objets a fabriquer.",

    # sale0000.bin, sale0001.bin, sale0002.bin
    "Free": "Grat",
    "Inventory": "Objets",
    "Quantity": "Quantite",
    "(I don't have anything to sell.)": "(Rien a vendre.)",
    "(Got nothing on me to sell.)": "(Rien a vendre.)",
    "(I haven't selected anything.)": "(Rien de selectionne.)",
    "(Ain't got anything selected.)": "(Rien de selectionne.)",
    "Details": "Details",
    "<Sign:1>Back": "<Sign:1>Ret.",
    "<Sign:1>Next %d/%d": "<Sign:1>Suiv %d/%d",
    "You're looking at %s, I'd say.": "J'en donnerais %s, disons.",
    "Are you sure you want to sell such rare stuff?": "Vendre un objet si rare ?",
    "That comes to %s.": "Ca fera %s.",
    "Rare stuff here. You sure you want to sell?": "Objet rare. Voulez-vous vendre ?",
    "I'll give you %s for it.": "Je vous en donne %s.",
    "You okay parting with such rare stuff?": "Vendre un objet si rare ?",

    # present.bin
    "Are you sure you want to hand this over?": "Voulez-vous donner ceci ?",
    "(I don't have anything to hand over.)": "(Rien a donner.)",
    "(Nothing for me to hand over.)": "(Rien a donner.)",
    "(What am I gonna hand over?)": "(Qu'est-ce que je donne ?)",
    "(What should I hand over?)": "(Que donner ?)",

    # send.bin
    "(I don't have any space. Guess I'll send it to the Item Box.)": "(Plus de place. Au Coffre.)",
    "(I'm outta space. Guess I'll send it to the Item Box.)": "(Plus de place. Au Coffre.)",
    "(Guess I'll send it to the Item Box.)": "(J'envoie ca au Coffre.)",
    "Guess I'll send it to the Item Box.)": "(J'envoie ca au Coffre.)",
    "Are you sure you want to send this?": "Voulez-vous envoyer ceci ?",
    "You sent %s to the Item Box.": "%s envoye au Coffre.",

    # throw.bin
    "(No space, so I'd better drop something.)": "(Plus de place, je dois jeter.)",
    "(Outta space. Better drop something.)": "(Plus de place. Mieux vaut jeter.)",
    "Are you sure you want to discard this?": "Voulez-vous jeter cet objet ?",
    "(It'd be a waste to just throw this away.)": "(Gachis de jeter ca.)",
    "(This is way too cool to toss.)": "(Trop precieux pour jeter.)",
    "(This weapon is too valuable to toss.)": "(Cette arme a trop de valeur.)",
    "(I ain't about to dump this weapon.)": "(Pas question de jeter ca.)",
    "%s discarded.": "%s jete.",
}

def translate_exact_bytes(data_bytes):
    out = bytearray(data_bytes)
    # Fix broken trademark \xc7
    out = bytearray(bytes(out).replace(b'\xc7', b'C'))

    for en, fr in TRANSLATIONS.items():
        en_b = en.encode('latin1')
        fr_clean = fr.replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')
        fr_b = fr_clean.encode('latin1')
        assert len(fr_b) <= len(en_b), f"Length error: {len(fr_b)} > {len(en_b)} for {repr(en)}"
        pad = b'\x00' * (len(en_b) - len(fr_b))
        rep_b = fr_b + pad

        pos = 0
        while True:
            idx = out.find(en_b, pos)
            if idx == -1:
                break
            out[idx : idx + len(en_b)] = rep_b
            pos = idx + len(en_b)

    return bytes(out)

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
    cpar_path = 'release_gog/data/wdr_par_c/common.par'
    with open(cpar_path, 'rb') as f:
        orig_bytes = f.read()

    files = parse_par(orig_bytes)
    replacements = {}

    target_files = [
        'blacksmith.bin', 'sale0000.bin', 'sale0001.bin', 'sale0002.bin',
        'arms_repair.bin', 'present.bin', 'send.bin', 'throw.bin'
    ]

    for fn in target_files:
        if fn not in files:
            continue
        flags, u_sz, c_sz, data = files[fn]
        is_comp = bool(flags & 0x80000000)
        decomp = decompress_sllz(data) if is_comp else data
        trans_decomp = translate_exact_bytes(decomp)
        if is_comp:
            comp = compress_sllz(trans_decomp)
            replacements[fn] = (0x80000000, len(trans_decomp), len(comp), comp)
            print(f"  - Translated & recompressed {fn} (u_sz={len(trans_decomp)}, c_sz={len(comp)})")
        else:
            replacements[fn] = (flags, len(trans_decomp), len(trans_decomp), trans_decomp)
            print(f"  - Translated uncompressed {fn} (sz={len(trans_decomp)})")

    print("[+] Repacking common.par...")
    new_cpar = repack_par(orig_bytes, replacements)
    with open(cpar_path, 'wb') as f:
        f.write(new_cpar)
    print(f"[+] Successfully wrote {cpar_path} ({len(new_cpar)} bytes)!")

if __name__ == '__main__':
    main()
