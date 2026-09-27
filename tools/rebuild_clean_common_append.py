#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_common_append.py
------------------------------------
Rebuilds release_gog/data/wdr_par_c/common.par using the proven 2048-byte
sector-aligned Append-Only model (Golden Rules 1, 3, 5 & 10 of AGENTS.md):
1. Starts from pristine clean GOG common.par (par_original/common.par, 32,768 bytes).
2. Translates all merchant/service menu files:
   - blacksmith.bin (Dragon & Tiger craft menu)
   - arms_repair.bin (Dragon & Tiger repair menu)
   - sale0000.bin, sale0001.bin, sale0002.bin (Ebisu Pawn selling menus)
   - send.bin (Item box send menu)
   - throw.bin (Discard item menu)
   - present.bin (Gifting menu)
3. Preserves exact byte lengths in-place with zero offset shifting.
4. Preserves exact compression flags:
   - flags = 0x80000000 for SLLZ files (blacksmith, arms_repair, sale0000-0002)
   - flags = 0x0 for uncompressed files (send, throw, present)
5. Appends modified French files at the end, each aligned to strict 2048-byte sector boundaries.
6. Pads the total archive to a 2048-byte multiple.
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz

COMMON_TRANSLATIONS = {
    # blacksmith.bin
    "Order": "Créer",
    "None": "Rien",
    "That'll be %s. Is that all right?": "Ça fera %s. Cela vous convient ?",
    "It'll cost %s to make. Is that okay?": "La fabrication coûtera %s. OK ?",
    "You don't seem to have enough cash.": "Vous n'avez pas assez d'argent.",
    "Your inventory is full.": "L'inventaire est plein.",
    "You don't have all the parts.": "Il vous manque des pièces.",
    "Item lineup expanded.": "Nouveaux plans dispos",
    "There are new items to craft.": "Nouveaux objets à fabriquer.",

    # arms_repair.bin
    "Kamiyama Works Lv.%d": "Kamiyama Works Nv.%d",
    "(I don't have anything that needs repair.)": "(Je n'ai rien à faire réparer ici.)",
    "(Ain't got anything that needs repair.)": "(J'ai rien à faire réparer sur moi.)",
    "That'll come to %s.": "Ça fera %s.",
    "(Looks like I'm a little short.)": "(On dirait que je suis à court.)",
    "(I'm short on cash.)": "(Je suis à court.)",

    # sale0000.bin, sale0001.bin, sale0002.bin
    "Free": "Grat",
    "Inventory": "Objets",
    "Quantity": "Quantité",
    "(I don't have anything to sell.)": "(Je n'ai rien à vendre ici.)",
    "(Got nothing on me to sell.)": "(Rien à vendre sur moi.)",
    "(I haven't selected anything.)": "(Je n'ai rien sélectionné.)",
    "(Ain't got anything selected.)": "(J'ai rien sélectionné ici.)",
    "Details": "Détails",
    "<Sign:1>Back": "<Sign:1>Exit",
    "<Sign:1>Next %d/%d": "<Sign:1>Page %d/%d",
    "You're looking at %s, I'd say.": "Je dirais que ça vaut %s.",
    "Are you sure you want to sell such rare stuff?": "Sûr de vouloir vendre un objet si rare ?",
    "That comes to %s.": "Ça fera %s.",
    "Rare stuff here. You sure you want to sell?": "Objet rare. Sûr de vouloir le vendre ?",
    "I'll give you %s for it.": "Je vous en donne %s.",
    "You okay parting with such rare stuff?": "D'accord pour céder un objet si rare ?",

    # send.bin
    "(I don't have any space. Guess I'll send it to the Item Box.)": "(Plus de place. Je vais l'envoyer au Coffre.)",
    "(I'm outta space. Guess I'll send it to the Item Box.)": "(Plus de place. Je vais l'envoyer au Coffre.)",
    "Are you sure you want to send this?": "Voulez-vous envoyer cet objet ?",
    "You sent %s to the Item Box.": "Vous envoyez %s au Coffre.",

    # throw.bin
    "(No space, so I'd better drop something.)": "(Plus de place, je devrais jeter ça.)",
    "(Outta space. Better drop something.)": "(Plus de place, mieux vaut jeter ça.)",
    "Are you sure you want to discard this?": "Voulez-vous vraiment jeter ceci ?",
    "(It'd be a waste to just throw this away.)": "(Ce serait du gâchis de jeter ça.)",
    "(This is way too cool to toss.)": "(Trop précieux pour jeter ça.)",
    "(This weapon is too valuable to toss.)": "(Cette arme est bien trop précieuse.)",
    "(I ain't about to dump this weapon.)": "(Hors de question de jeter ça.)",
    "%s discarded.": "%s jeté.",

    # present.bin
    "(I don't have anything to hand over.)": "(Je n'ai rien à donner sur moi.)",
    "(Nothing for me to hand over.)": "(Rien à donner sur moi.)",
    "(What should I hand over?)": "(Que devrais-je donner ?)",
    "(What am I gonna hand over?)": "(Qu'est-ce que je donne ?)",
    "Are you sure you want to hand this over?": "Voulez-vous donner cet objet ?"
}

def translate_buffer(data_bytes):
    out = bytearray(data_bytes)
    for en, fr in COMMON_TRANSLATIONS.items():
        en_b = en.encode('latin1')
        fr_b = fr.encode('latin1')
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

def rebuild_clean_common_append(clean_par_path='par_original/common.par',
                                output_path='release_gog/data/wdr_par_c/common.par'):
    print(f"[+] Reading pristine clean common.par: {clean_par_path}")
    with open(clean_par_path, 'rb') as f:
        clean_bytes = f.read()
    clean_par = parse_par(clean_bytes)

    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_bytes[16:32])
    name_offset = 32 + folder_count * 64
    rebuilt_common = bytearray(clean_bytes)

    TARGET_FILES = [
        'ai_popup.bin',
        'blacksmith.bin',
        'arms_repair.bin',
        'sale0000.bin',
        'sale0001.bin',
        'sale0002.bin',
        'send.bin',
        'throw.bin',
        'present.bin'
    ]

    # Load clean French ai_popup.bin from wdr.par
    with open('release_gog/data/wdr_par_c/wdr.par', 'rb') as wf:
        wdr_files = parse_par(wf.read())
    fr_aipop_flags, fr_aipop_u, fr_aipop_c, fr_aipop_data = wdr_files['ai_popup.bin']

    modified_count = 0
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = clean_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')

        if name in TARGET_FILES:
            if name == 'ai_popup.bin':
                new_flags = 0x80000000
                new_u_sz = fr_aipop_u
                new_c_sz = fr_aipop_c
                payload = fr_aipop_data
            else:
                flags, u_sz, c_sz, raw_data = clean_par[name]
                is_sllz = bool(flags & 0x80000000) or raw_data.startswith(b'SLLZ')
                decomp = decompress_sllz(raw_data) if is_sllz else raw_data

                translated_decomp = translate_buffer(decomp)
                assert len(translated_decomp) == len(decomp), f"Size mismatch for {name}: {len(translated_decomp)} != {len(decomp)}"

                if is_sllz:
                    comp = compress_sllz(translated_decomp)
                    new_flags = 0x80000000
                    new_u_sz = len(translated_decomp)
                    new_c_sz = len(comp)
                    payload = comp
                else:
                    new_flags = 0x0
                    new_u_sz = len(translated_decomp)
                    new_c_sz = len(translated_decomp)
                    payload = translated_decomp

            # Strict 2048-byte sector alignment
            aligned_off = (len(rebuilt_common) + 2047) & ~2047
            if aligned_off > len(rebuilt_common):
                rebuilt_common.extend(b'\x00' * (aligned_off - len(rebuilt_common)))

            new_file_offset = len(rebuilt_common)
            rebuilt_common.extend(payload)

            # Update entry in file table
            e_off = file_table_offset + i * 32
            struct.pack_into('>4I', rebuilt_common, e_off, new_flags, new_u_sz, new_c_sz, new_file_offset)
            modified_count += 1
            print(f"  [+] Appended {name:20s} at sector {hex(new_file_offset)} (flags={hex(new_flags)}, u_sz={new_u_sz:5d}, c_sz={new_c_sz:5d})")

    # Pad total archive to 2048-byte multiple
    final_aligned = (len(rebuilt_common) + 2047) & ~2047
    if final_aligned > len(rebuilt_common):
        rebuilt_common.extend(b'\x00' * (final_aligned - len(rebuilt_common)))

    with open(output_path, 'wb') as f:
        f.write(rebuilt_common)

    print(f"\n[SUCCESS] Wrote {output_path} ({len(rebuilt_common)} bytes, {modified_count} files translated) with strict 2048-byte sector alignment!")
    return True

if __name__ == '__main__':
    clean_p = sys.argv[1] if len(sys.argv) > 1 else 'par_original/common.par'
    out_p = sys.argv[2] if len(sys.argv) > 2 else 'release_gog/data/wdr_par_c/common.par'
    rebuild_clean_common_append(clean_p, out_p)
