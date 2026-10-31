#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/rebuild_minigame_par.py
-----------------------------
Rebuilds release_gog/data/pausepar_e/minigame.par with translated high-definition
textures for minigame rules (starting with Catfight rule_catfight00..04).

Enforces Golden Rule 3:
- Strict 2,048-byte sector alignment on EVERY file ((curr_off + 2047) & ~2047).
- SLLZ compression with flags = 0x80000000.
"""

import os
import sys
import struct
import subprocess
import time
import numpy as np

# Ensure tools directory is in sys.path
_tools_dir = os.path.dirname(os.path.abspath(__file__))
if _tools_dir not in sys.path:
    sys.path.insert(0, _tools_dir)

from sllz import compress_sllz
from verify_patch import ParValidator


def encode_png_to_dxt1(png_path: str, dds_header: bytes) -> bytes:
    """Encodes a 1024x512 RGB PNG into a 262,272-byte DXT1 DDS file."""
    cmd = ['ffmpeg', '-y', '-i', png_path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    raw = res.stdout
    assert len(raw) == 1024 * 512 * 3, f"Unexpected raw size for {png_path}: {len(raw)}"
    arr = np.frombuffer(raw, dtype=np.uint8).reshape((512, 1024, 3))
    
    # Reshape to 4x4 blocks: (128, 256, 16, 3) -> 32,768 blocks of 16 RGB pixels
    blocks = arr.reshape(128, 4, 256, 4, 3).transpose(0, 2, 1, 3, 4).reshape(32768, 16, 3)
    
    min_c = blocks.min(axis=1)
    max_c = blocks.max(axis=1)
    
    c0 = ((max_c[:, 0].astype(np.uint32) >> 3) << 11) | ((max_c[:, 1].astype(np.uint32) >> 2) << 5) | (max_c[:, 2].astype(np.uint32) >> 3)
    c1 = ((min_c[:, 0].astype(np.uint32) >> 3) << 11) | ((min_c[:, 1].astype(np.uint32) >> 2) << 5) | (min_c[:, 2].astype(np.uint32) >> 3)
    
    swap_mask = c0 < c1
    c0[swap_mask], c1[swap_mask] = c1[swap_mask], c0[swap_mask].copy()
    max_c[swap_mask], min_c[swap_mask] = min_c[swap_mask], max_c[swap_mask].copy()
    
    eq_mask = c0 == c1
    c0[eq_mask & (c0 < 65535)] += 1
    
    p0 = max_c.astype(np.float32)
    p1 = min_c.astype(np.float32)
    p2 = (2.0 * p0 + p1) / 3.0
    p3 = (p0 + 2.0 * p1) / 3.0
    pal = np.stack([p0, p1, p2, p3], axis=1) # (32768, 4, 3)
    
    blocks_f = blocks.astype(np.float32) # (32768, 16, 3)
    diff = blocks_f[:, :, None, :] - pal[:, None, :, :]
    dist_sq = np.sum(diff ** 2, axis=3)
    indices = np.argmin(dist_sq, axis=2).astype(np.uint32)
    
    shifts = (np.arange(16, dtype=np.uint32) * 2)
    packed_indices = np.sum(indices << shifts, axis=1, dtype=np.uint32)
    
    dt = np.dtype([('c0', '<u2'), ('c1', '<u2'), ('idx', '<u4')])
    block_arr = np.empty(32768, dtype=dt)
    block_arr['c0'] = c0.astype(np.uint16)
    block_arr['c1'] = c1.astype(np.uint16)
    block_arr['idx'] = packed_indices
    
    dds_bytes = dds_header + block_arr.tobytes()
    assert len(dds_bytes) == 262272, f"Invalid DDS size: {len(dds_bytes)}"
    return dds_bytes


def rebuild_minigame_par(input_par: str, output_par: str, replacements: dict):
    """
    Rebuilds minigame.par with strict 2048-byte sector alignment.
    replacements: dict mapping filename (str) -> (raw_decompressed_bytes, flags)
    """
    print(f"[*] Lecture de l'archive source : {input_par}...")
    with open(input_par, 'rb') as f:
        data = f.read()

    magic, unkA, unkB, unkC = struct.unpack('>4I', data[:16])
    assert magic == 0x50415243, f"Format PARC invalide : {hex(magic)}"
    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', data[16:32])
    name_offset = 32 + folder_count * 64

    entries = []
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = data[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')
        e_off = file_table_offset + i * 32
        flags, u_sz, c_sz, f_off = struct.unpack('>4I', data[e_off : e_off + 16])
        raw_file = data[f_off : f_off + c_sz]
        entries.append({
            'idx': i,
            'name': name,
            'e_off': e_off,
            'flags': flags,
            'u_sz': u_sz,
            'c_sz': c_sz,
            'f_off': f_off,
            'data': raw_file
        })

    # Preserve sequential order by original offset
    sorted_entries = sorted(entries, key=lambda e: e['f_off'])
    
    # Process replacements
    replaced_count = 0
    for item in sorted_entries:
        fn = item['name']
        if fn in replacements:
            uncomp_data, new_flags = replacements[fn]
            if new_flags & 0x80000000:
                print(f"    [+] Compression SLLZ de {fn} ({len(uncomp_data)} o)...")
                comp_data = compress_sllz(uncomp_data)
            else:
                comp_data = uncomp_data
            item['data'] = comp_data
            item['u_sz'] = len(uncomp_data)
            item['c_sz'] = len(comp_data)
            item['flags'] = new_flags
            replaced_count += 1
            print(f"    [✓] {fn}: {item['u_sz']} o -> {item['c_sz']} o (compressé SLLZ, flags={hex(new_flags)})")

    print(f"[*] {replaced_count} fichier(s) remplacé(s). Recompilation avec alignement sectoriel 2048 o...")

    first_file_offset = (sorted_entries[0]['f_off'] + 2047) & ~2047
    rebuilt = bytearray(data[:sorted_entries[0]['f_off']])
    if len(rebuilt) < first_file_offset:
        rebuilt.extend(b'\x00' * (first_file_offset - len(rebuilt)))

    curr_off = len(rebuilt)
    for item in sorted_entries:
        aligned_off = (curr_off + 2047) & ~2047
        if aligned_off > len(rebuilt):
            rebuilt.extend(b'\x00' * (aligned_off - len(rebuilt)))
        
        item['new_f_off'] = len(rebuilt)
        rebuilt.extend(item['data'])
        curr_off = len(rebuilt)

    # Pad archive to multiple of 2048
    final_aligned = (len(rebuilt) + 2047) & ~2047
    if final_aligned > len(rebuilt):
        rebuilt.extend(b'\x00' * (final_aligned - len(rebuilt)))

    # Update file table entries in header
    for item in entries:
        e_off = item['e_off']
        new_off = item['new_f_off']
        flags = item['flags']
        u_sz = item['u_sz']
        c_sz = item['c_sz']
        struct.pack_into('>4I', rebuilt, e_off, flags, u_sz, c_sz, new_off)

    with open(output_par, 'wb') as f:
        f.write(rebuilt)

    print(f"[✓] Archive sauvegardée : {output_par} ({len(rebuilt) / (1024*1024):.2f} Mo, 100% alignée 2048 o)")


def main():
    repo_root = os.path.dirname(_tools_dir)
    target_par = os.path.join(repo_root, "release_gog", "data", "pausepar_e", "minigame.par")
    
    if not os.path.isfile(target_par):
        print(f"[ERREUR] Archive introuvable : {target_par}")
        sys.exit(1)

    # Read DDS header (128 bytes)
    hdr_path = "/tmp/orig_catfight00.dds"
    if not os.path.isfile(hdr_path):
        # Extract from archive
        with open(target_par, 'rb') as f:
            data = f.read()
        fl_off = struct.unpack('>I', data[28:32])[0]
        f_off = struct.unpack('>I', data[fl_off + 39*32 + 12 : fl_off + 39*32 + 16])[0]
        c_sz = struct.unpack('>I', data[fl_off + 39*32 + 8 : fl_off + 39*32 + 12])[0]
        from sllz import decompress_sllz
        decomp = decompress_sllz(data[f_off : f_off + c_sz])
        hdr = decomp[:128]
    else:
        with open(hdr_path, 'rb') as f:
            hdr = f.read(128)

    replacements = {}
    catfight_dir = "/tmp/fr_catfight"
    for i in range(5):
        fn_base = f"rule_catfight0{i}"
        png_path = os.path.join(catfight_dir, f"{fn_base}.png")
        if not os.path.isfile(png_path):
            print(f"[ERREUR] Image PNG introuvable : {png_path}")
            sys.exit(1)
        
        print(f"[*] Encodage DXT1 de {png_path}...")
        dds_raw = encode_png_to_dxt1(png_path, hdr)
        replacements[f"{fn_base}.dds"] = (dds_raw, 0x80000000)

    # Rebuild
    rebuild_minigame_par(target_par, target_par, replacements)

    # Validate
    print("[*] Validation d'intégrité de l'archive...")
    v = ParValidator(target_par)
    v.validate()
    if v.issues:
        print("[ERREUR] Erreurs détectées lors de la validation :")
        for iss in v.issues:
            print("  -", iss)
        sys.exit(1)
    else:
        print("[SUCCÈS] minigame.par est 100% conforme et intègre !")


if __name__ == '__main__':
    main()
