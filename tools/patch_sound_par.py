#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/patch_sound_par.py
------------------------
Fast, self-contained, in-place append-only patcher for sound.par:
Updates English street-encounter subtitles (.mfp files):
- Harassment & rescue events (thugs, victims, bouncers, hostesses, citizens)
- Ambient NPC street barks in Kamurocho & Sotenbori (CWandererSoundStreamer / CMfp::Initialize)
- Respects Sega CMfp::Initialize bit-exact requirement (anti-crash 0x19CAC0).
- Strict 2048-byte sector alignment (Golden Rule 3).

Zero external dependencies (pure Python standard library).
"""

import os
import sys
import struct
import time

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.sllz import compress_sllz, decompress_sllz
from tools.sound_subtitles_data import SOUND_SUBTITLES


def build_replacement_table():
    """Build list of (bytes_en, bytes_fr_padded) with bit-exact length assertion."""
    replacements = []
    for en_str, fr_str in SOUND_SUBTITLES.items():
        if en_str == fr_str:
            continue
        b_en = en_str.encode('latin1')
        b_fr = fr_str.encode('latin1')
        pad = len(b_en) - len(b_fr)
        assert pad >= 0, f"FATAL: French string longer than English for '{en_str}'"
        b_fr_pad = b_fr + b' ' * pad
        assert len(b_fr_pad) == len(b_en)
        replacements.append((b_en, b_fr_pad))
    # CRITICAL: Sort by descending length so composite sentences match before shorter substrings
    replacements.sort(key=lambda x: len(x[0]), reverse=True)
    return replacements


def patch_sound_par_inplace(sound_par_path, check_only=False):
    """
    Patch all English street encounter subtitles in sound.par in-place via append-only.
    Maintains 100% bit-exact decompressed sizes and 2048-byte sector alignment.
    """
    if not os.path.exists(sound_par_path):
        print(f"[-] {sound_par_path} not found.")
        return False

    replacements = build_replacement_table()
    action_label = "Checking sound subtitles" if check_only else "Patching sound subtitles (bit-exact)"
    print(f"[+] {action_label} in {sound_par_path} ({len(replacements)} translation pairs)...")
    t0 = time.time()

    with open(sound_par_path, 'r+b' if not check_only else 'rb') as f:
        # Read PARC header
        header = f.read(32)
        if header[:4] != b'PARC':
            print("[-] Invalid PAR header!")
            return False

        folder_count, folder_tbl_off, file_count, file_tbl_off = struct.unpack('>4I', header[16:32])
        name_tbl_off = 32 + folder_count * 64

        # Read name table and file entries table
        f.seek(name_tbl_off)
        names_raw = f.read(file_count * 64)

        f.seek(file_tbl_off)
        entries_raw = bytearray(f.read(file_count * 32))

        # Find end of archive for append
        f.seek(0, 2)
        end_off = f.tell()

        patched_count = 0
        already_patched_count = 0
        total_subtitles_patched = 0

        # Scan all .mfp files
        for idx in range(file_count):
            name = names_raw[idx*64 : (idx+1)*64].split(b'\x00')[0].decode('latin1')
            if not name.endswith('.mfp'):
                continue

            entry_bytes = entries_raw[idx*32 : (idx+1)*32]
            flags, u_sz, c_sz, data_off = struct.unpack('>4I', entry_bytes[:16])

            f.seek(data_off)
            payload = f.read(c_sz)
            if flags == 0x80000000:
                try:
                    dec = decompress_sllz(payload)
                except Exception:
                    continue
            else:
                dec = payload

            # Check if any replacement applies
            modified = bytearray(dec)
            rep_count = 0
            for b_en, b_fr_pad in replacements:
                if b_en in modified:
                    modified = bytearray(bytes(modified).replace(b_en, b_fr_pad))
                    rep_count += 1

            if rep_count == 0:
                # Check if already contains French translation
                if any(b_fr_pad in dec for b_en, b_fr_pad in replacements):
                    already_patched_count += 1
                continue

            # Strict bit-exact assertion: decompressed size MUST NEVER CHANGE
            assert len(modified) == len(dec), (
                f"FATAL: length mismatch on {name}: {len(dec)} -> {len(modified)}"
            )

            if check_only:
                patched_count += 1
                total_subtitles_patched += rep_count
                continue

            comp = compress_sllz(bytes(modified))

            # Sector align to 2048 bytes (Golden Rule 3)
            aligned_off = (end_off + 2047) & ~2047
            pad_len = aligned_off - end_off
            f.seek(end_off)
            if pad_len > 0:
                f.write(b'\x00' * pad_len)
            f.write(comp)
            end_off = f.tell()

            # Update file table entry in archive
            new_entry = struct.pack('>4I', 0x80000000, len(modified), len(comp), aligned_off)
            f.seek(file_tbl_off + idx * 32)
            f.write(new_entry)

            # Update entries_raw in memory to stay coherent
            entries_raw[idx*32 : idx*32+16] = new_entry

            patched_count += 1
            total_subtitles_patched += rep_count

        if not check_only and patched_count > 0:
            # Final sector padding of archive
            final_aligned = (end_off + 2047) & ~2047
            if final_aligned > end_off:
                f.seek(end_off)
                f.write(b'\x00' * (final_aligned - end_off))

    elapsed = time.time() - t0
    if check_only:
        print(f"[CHECK] Found {patched_count} unpatched .mfp files ({already_patched_count} already patched) in {elapsed:.2f}s.")
        return patched_count == 0
    else:
        print(f"[SUCCESS] Patched {patched_count} .mfp files ({total_subtitles_patched} subtitle occurrences, {already_patched_count} already up-to-date) in {elapsed:.2f}s!")
        return True


if __name__ == '__main__':
    check = '--check' in sys.argv
    target = 'release_gog/data/soundpar/sound.par'
    for arg in sys.argv[1:]:
        if not arg.startswith('-'):
            target = arg
            break
    success = patch_sound_par_inplace(target, check_only=check)
    sys.exit(0 if success else 1)
