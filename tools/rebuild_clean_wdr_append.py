#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_clean_wdr_append.py
---------------------------------
Rebuilds release_gog/data/wdr_par_c/wdr.par using the 2048-byte sector-aligned
append-only model (Gold Rule 3 of AGENTS.md):
1. Starts from the pristine clean GOG wdr.par (8,026,112 bytes).
2. Keeps all untouched stage binaries (pac_*.bin), streaming files, and system
   binaries at their exact 100% pristine original sector offsets.
3. Appends all modified/translated files at the end of the archive, each strictly
   aligned to 2048-byte (0x800) sector boundaries.
4. Updates file table entries with correct flags, uncompressed size, compressed size,
   and appended offsets.
5. Guarantees 0 offset-shift crashes in stage loading, wanderer audio streaming,
   or phone booth interactions.
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz
from tools.repair_phone_booths import PHONE_FILE_NAMES, PHONE_TRANSLATIONS, translate_msg_inplace
from tools.rebuild_all_shops_clean import generate_repaired_shops
from scratch.test_merchant_dict import merchant_dict
from scratch.prepare_snitch_translations import SNITCH_FR

def get_clean_french_ai_popup():
    common_path = 'release_gog/data/wdr_par_c/common.par'
    if os.path.exists(common_path):
        with open(common_path, 'rb') as f:
            c_files = parse_par(f.read())
        if 'ai_popup.bin' in c_files:
            raw = c_files['ai_popup.bin'][3]
            decomp = decompress_sllz(raw) if raw.startswith(b'SLLZ') else raw
            if b'Genial !' in decomp:
                comp = compress_sllz(decomp)
                return 0x80000000, len(decomp), len(comp), comp
    if os.path.exists('scratch/ai_popup_curr.bin'):
        with open('scratch/ai_popup_curr.bin', 'rb') as f:
            decomp = f.read()
        comp = compress_sllz(decomp)
        return 0x80000000, len(decomp), len(comp), comp
    raise FileNotFoundError("Could not find translated ai_popup.bin")

def patch_merchant_binary(data_bytes):
    out = bytearray(data_bytes)
    # Fix broken trademark \xc7
    out = bytearray(bytes(out).replace(b'\xc7', b'C'))

    for en, fr in merchant_dict.items():
        en_b = en.encode('latin1')
        fr_clean = fr.replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')
        fr_b = fr_clean.encode('latin1')
        assert len(fr_b) <= len(en_b), f"Length overflow: {len(fr_b)} > {len(en_b)} for {en}"
        rep_b = fr_b + (b'\x00' * (len(en_b) - len(fr_b)))

        pos = 0
        while True:
            idx = out.find(en_b, pos)
            if idx == -1:
                break
            out[idx : idx + len(en_b)] = rep_b
            pos = idx + len(en_b)
    return bytes(out)

def patch_snitch_binary(decomp_snitch):
    out = bytearray(decomp_snitch)
    num_tables = struct.unpack('>I', out[0:4])[0]
    entry_idx = 0
    for t in range(num_tables):
        cnt = struct.unpack('>I', out[8 + t*8 : 12 + t*8])[0]
        off = struct.unpack('>I', out[12 + t*8 : 16 + t*8])[0]
        for i in range(cnt):
            e = out[off + i*16 : off + (i+1)*16]
            id1, id2, start, end = struct.unpack('>4I', e)
            en_text = out[start : end - 1].decode('latin1')
            fr_text = SNITCH_FR[entry_idx]
            fr_clean = fr_text.replace('’', "'").replace('œ', 'oe').replace('Ça', 'Ca')
            fr_b = fr_clean.encode('latin1')
            en_len = (end - 1) - start
            assert len(fr_b) <= en_len, f"Snitch overflow at {entry_idx}: {len(fr_b)} > {en_len}"
            padded_fr = fr_b + (b' ' * (en_len - len(fr_b))) + b'\x00'
            out[start:end] = padded_fr
            entry_idx += 1
    assert len(out) == len(decomp_snitch), "snitch length changed!"
    return bytes(out)

def rebuild_clean_wdr_append(clean_par_path, curr_par_path, output_path):
    print(f"[+] Reading pristine base: {clean_par_path}")
    with open(clean_par_path, 'rb') as f:
        clean_bytes = f.read()

    print(f"[+] Reading translated reference: {curr_par_path}")
    with open(curr_par_path, 'rb') as f:
        curr_bytes = f.read()

    clean_files = parse_par(clean_bytes)
    curr_files = parse_par(curr_bytes)

    print(f"[+] Pre-generating clean French shops with preserved Pocket Circuit tables...")
    repaired_shops = generate_repaired_shops(clean_par_path, 'release_gog/data/bootpar/boot.par')

    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', clean_bytes[16:32])
    name_offset = 32 + folder_count * 64

    rebuilt = bytearray(clean_bytes)

    PRISTINE_NON_MSG_BINS = {
        'dispose_string.bin', 'eg_telephone_card.bin'
    }

    MERCHANT_BINS = {
        'arms_repair.bin', 'blacksmith.bin', 'present.bin', 'sale0000.bin',
        'sale0001.bin', 'sale0002.bin', 'send.bin', 'throw.bin'
    }

    en_bob = (
        b"A Walkman lets you listen to your favorite music as you\r\n"
        b"walk around town. Press and hold <Sign:7> to display the\r\n"
        b"Walkman's controls.\r\n"
        b"Modifiez la cassette depuis le radiocassette de\r\n"
        b"votre planque.           "
    )
    fr_bob_raw = (
        b"Le Walkman permet d'ecouter vos musiques preferees en\r\n"
        b"ville. Maintenez <Sign:7> pour afficher les commandes\r\n"
        b"du Walkman.\r\n"
        b"Modifiez la cassette depuis le radiocassette de\r\n"
        b"votre planque."
    )
    fr_bob = fr_bob_raw + (b' ' * (len(en_bob) - len(fr_bob_raw)))

    stats = {'appended': 0, 'kept_orig': 0}

    print(f"[+] Processing {file_count} files in append-only mode...")
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = clean_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')
        e_off = file_table_offset + i * 32
        orig_flags, orig_u, orig_c, orig_off = struct.unpack('>4I', clean_bytes[e_off : e_off + 16])
        orig_data = clean_bytes[orig_off : orig_off + orig_c]

        target_data = None
        target_flags = 0
        target_u_sz = 0
        target_c_sz = 0

        # Keep untouched stage binaries and pristine system bins 100% untouched
        if name.startswith('pac_') or name in PRISTINE_NON_MSG_BINS:
            stats['kept_orig'] += 1
            continue
        elif name == 'ai_popup.bin':
            target_flags, target_u_sz, target_c_sz, target_data = get_clean_french_ai_popup()
            print(f"  [+] Injected French ai_popup.bin (u_sz={target_u_sz}, c_sz={target_c_sz})")
        elif name in repaired_shops:
            target_flags, target_u_sz, target_c_sz, target_data = repaired_shops[name]
        elif name in MERCHANT_BINS:
            decomp_orig = decompress_sllz(orig_data) if orig_data.startswith(b'SLLZ') or (orig_flags & 0x80000000) else orig_data
            patched = patch_merchant_binary(decomp_orig)
            assert len(patched) == len(decomp_orig)
            if orig_flags & 0x80000000:
                comp_data = compress_sllz(patched)
                target_data = comp_data
                target_flags = 0x80000000
                target_u_sz = len(patched)
                target_c_sz = len(comp_data)
            else:
                target_data = patched
                target_flags = 0x0
                target_u_sz = len(patched)
                target_c_sz = len(patched)
            print(f"  [+] Injected French merchant {name} (u_sz={target_u_sz}, c_sz={target_c_sz})")
        elif name == 'snitch.bin':
            decomp_orig = decompress_sllz(orig_data) if orig_data.startswith(b'SLLZ') or (orig_flags & 0x80000000) else orig_data
            patched = patch_snitch_binary(decomp_orig)
            assert len(patched) == len(decomp_orig)
            comp_data = compress_sllz(patched)
            target_data = comp_data
            target_flags = 0x80000000
            target_u_sz = len(patched)
            target_c_sz = len(comp_data)
            print(f"  [+] Injected French snitch.bin (u_sz={target_u_sz}, c_sz={target_c_sz})")
        elif name == 'uid0044018f.msg':
            clean_decomp = decompress_sllz(orig_data) if orig_data.startswith(b'SLLZ') else orig_data
            repaired = clean_decomp.replace(b'Welcome. How can I help you?\x00', b'Bienvenue ! Que voulez-vous?\x00')
            repaired = repaired.replace(b'There you go. Have a nice day!\x00', b'Et voila. Bonne journee !     \x00')
            repaired = repaired.replace(b'Have a nice day!\x00', b'Bonne journee ! \x00')
            assert len(repaired) == len(clean_decomp), f"Mismatch in uid0044018f.msg length: {len(repaired)} != {len(clean_decomp)}"
            comp_data = compress_sllz(repaired)
            target_data = comp_data
            target_flags = 0x80000000
            target_u_sz = len(repaired)
            target_c_sz = len(comp_data)
        elif name in PHONE_FILE_NAMES:
            clean_decomp = decompress_sllz(orig_data) if orig_data.startswith(b'SLLZ') else orig_data
            repaired_decomp, _ = translate_msg_inplace(clean_decomp, PHONE_TRANSLATIONS)
            comp_data = compress_sllz(repaired_decomp)
            target_data = comp_data
            target_flags = 0x80000000
            target_u_sz = len(repaired_decomp)
            target_c_sz = len(comp_data)
        elif name in ('uid00331696.msg', 'uid003316a2.msg') and name in curr_files:
            curr_data = curr_files[name][3]
            decomp = decompress_sllz(curr_data) if curr_data.startswith(b'SLLZ') else curr_data
            assert len(decomp) == 27575, f"{name} decomp is not 27575 bytes!"
            if en_bob in decomp:
                patched = decomp.replace(en_bob, fr_bob)
            else:
                patched = decomp
            assert len(patched) == 27575
            comp_data = compress_sllz(patched)
            target_data = comp_data
            target_flags = 0x80000000
            target_u_sz = len(patched)
            target_c_sz = len(comp_data)
            print(f"  [+] Injected French {name} (u_sz={target_u_sz}, c_sz={target_c_sz})")
        elif name in curr_files:
            curr_item = curr_files[name]
            curr_flags, curr_u, curr_c, curr_data = curr_item
            decomp_curr = decompress_sllz(curr_data) if curr_data.startswith(b'SLLZ') else curr_data
            decomp_orig = decompress_sllz(orig_data) if orig_data.startswith(b'SLLZ') else orig_data

            if decomp_curr == decomp_orig:
                stats['kept_orig'] += 1
                continue

            if orig_flags & 0x80000000:
                comp_data = compress_sllz(decomp_curr)
                target_data = comp_data
                target_flags = 0x80000000
                target_u_sz = len(decomp_curr)
                target_c_sz = len(comp_data)
            else:
                target_data = decomp_curr
                target_flags = 0x0
                target_u_sz = len(decomp_curr)
                target_c_sz = len(decomp_curr)
        else:
            stats['kept_orig'] += 1
            continue

        # Append target_data with strict 2048-byte sector alignment
        aligned_off = (len(rebuilt) + 2047) & ~2047
        if aligned_off > len(rebuilt):
            rebuilt.extend(b'\x00' * (aligned_off - len(rebuilt)))
        new_offset = len(rebuilt)
        rebuilt.extend(target_data)

        # Update entry in file table
        struct.pack_into('>4I', rebuilt, e_off, target_flags, target_u_sz, target_c_sz, new_offset)
        stats['appended'] += 1

    # Pad final archive to 2048 bytes
    final_aligned = (len(rebuilt) + 2047) & ~2047
    if final_aligned > len(rebuilt):
        rebuilt.extend(b'\x00' * (final_aligned - len(rebuilt)))

    print(f"[+] Writing rebuilt archive to {output_path} ({len(rebuilt)} bytes, {len(rebuilt)/(1024*1024):.2f} MB)...")
    with open(output_path, 'wb') as f:
        f.write(rebuilt)

    print(f"[+] Complete! Kept pristine: {stats['kept_orig']}, Appended: {stats['appended']}")
    return True

if __name__ == '__main__':
    clean_p = sys.argv[1] if len(sys.argv) > 1 else 'par_original/wdr.par'
    curr_p = sys.argv[2] if len(sys.argv) > 2 else 'release_gog/data/wdr_par_c/wdr.par'
    out_p = sys.argv[3] if len(sys.argv) > 3 else 'release_gog/data/wdr_par_c/wdr.par'
    rebuild_clean_wdr_append(clean_p, curr_p, out_p)
