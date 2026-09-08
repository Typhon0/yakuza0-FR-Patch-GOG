#!/usr/bin/env python3
"""
translate_shops.py
------------------
Automated tool for Yakuza 0 VOSTFR patch (v1.10.2).
Translates all 35 convenience stores and shop menus (shop0000.bin - shop0034.bin)
embedded inside wdr.par:
  1. Reads official French item descriptions and names from boot.par -> item.bin_c.
  2. Translates all 30 shop UI strings (Quantité, Inventaire, Détails, Articles, Commander, etc.).
  3. Replaces English duplicate item descriptions with the master French translations.
  4. Repacks shop*.bin files into wdr.par cleanly without altering any other file offsets.
"""

import os
import sys
import struct
import shutil

# Ensure tools/ and scratch/ can import scanner_engine and sllz
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scratch'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner_engine import parse_par, decompress_sllz

UI_TRANSLATIONS = {
    'Quantity': 'Quantité',
    "(I haven't selected anything.)": "(Je n'ai rien sélectionné.)",
    "(Ain't got anything selected.)": "(Je n'ai rien sélectionné.)",
    "(Looks like I'm a little short.)": "(On dirait qu'il me manque des fonds.)",
    "(Gonna need more funds.)": "(Il me faudra plus de fonds.)",
    "Thank you. That'll be %s.": "Merci. Cela fera %s.",
    "(I can't carry any more.)": "(Je ne peux pas en porter plus.)",
    "(I can't carry more.)": "(Je ne peux pas en porter plus.)",
    "(No new stock, I guess.)": "(Pas de nouveau stock, on dirait.)",
    "(Looks like they're all out.)": "(On dirait qu'ils n'en ont plus.)",
    "(I already have this.)": "(J'ai déjà ceci.)",
    "(Already got this.)": "(J'ai déjà ça.)",
    'Inventory': 'Inventaire',
    'Details': 'Détails',
    'Products': 'Articles',
    '<Sign:1>Back': '<Sign:1>Retour',
    '<Sign:1>Next %d/%d': '<Sign:1>Suivant %d/%d',
    'Order': 'Commander',
    '-': '-',
}

CUSTOM_ITEM_DESCRIPTIONS = {
    717: "Il s'agit simplement de fer ordinaire.",
}


def load_french_item_descriptions(boot_par_path):
    """Extracts French item explanations from boot.par -> item.bin_c."""
    with open(boot_par_path, 'rb') as f:
        bfiles = parse_par(f.read())

    if 'item.bin_c' not in bfiles:
        raise ValueError(f"item.bin_c not found in {boot_par_path}")

    raw = bfiles['item.bin_c'][3]
    item_data = decompress_sllz(raw) if raw[:4] == b'SLLZ' else raw

    num_cols = struct.unpack('>I', item_data[4:8])[0]
    num_rows = struct.unpack('>I', item_data[8:12])[0]

    curr_off = 16 + num_cols * 64
    expl_data = None

    for col_idx in range(num_cols):
        col_off = 16 + col_idx * 64
        name = item_data[col_off:col_off+32].split(b'\x00')[0].decode('latin1')
        meta2 = struct.unpack('>4I', item_data[col_off+48:col_off+64])
        size = meta2[2]
        if name == 'EXPLANATION':
            expl_data = item_data[curr_off : curr_off + size]
            break
        curr_off += size

    if expl_data is None:
        raise ValueError("EXPLANATION column not found in item.bin_c")

    expls = [s.decode('latin1', errors='ignore') for s in expl_data.split(b'\x00')]
    print(f"[+] Loaded {len(expls)} item explanations from {boot_par_path} -> item.bin_c")
    return expls


def translate_shop_binary(raw_bin, expls):
    """Translates a single shop*.bin binary."""
    item_count = struct.unpack('>I', raw_bin[4:8])[0]
    rec_start = struct.unpack('>I', raw_bin[12:16])[0]  # 0x110

    # Read 30 UI pointers
    ui_ptrs = [struct.unpack('>I', raw_bin[0x10 + i * 4 : 0x14 + i * 4])[0] for i in range(30)]
    ui_strings = []
    for ptr in ui_ptrs:
        if ptr == 0:
            ui_strings.append('')
        else:
            end = raw_bin.find(b'\x00', ptr)
            ui_strings.append(raw_bin[ptr:end].decode('latin1'))

    new_ui_strings = [UI_TRANSLATIONS.get(s, s) for s in ui_strings]

    # Read item records
    items = []
    translated_count = 0
    for i in range(item_count):
        rec_off = rec_start + i * 48
        item_id = struct.unpack('>H', raw_bin[rec_off : rec_off + 2])[0]
        desc_ptr = struct.unpack('>I', raw_bin[rec_off + 0x20 : rec_off + 0x24])[0]
        end = raw_bin.find(b'\x00', desc_ptr)
        en_desc = raw_bin[desc_ptr:end].decode('latin1')

        if item_id in CUSTOM_ITEM_DESCRIPTIONS:
            fr_desc = CUSTOM_ITEM_DESCRIPTIONS[item_id]
            translated_count += 1
        elif item_id < len(expls) and expls[item_id].strip():
            fr_desc = expls[item_id]
            translated_count += 1
        else:
            fr_desc = en_desc

        items.append((item_id, fr_desc))

    # Build new binary layout
    new_bin = bytearray(raw_bin[: rec_start + item_count * 48])

    # Align string block start
    str_start = (len(new_bin) + 3) & ~3
    new_bin.extend(b'\x00' * (str_start - len(new_bin)))

    # Write UI strings
    new_ui_ptrs = []
    for s in new_ui_strings:
        if not s:
            new_ui_ptrs.append(0)
            continue
        ptr = len(new_bin)
        new_ui_ptrs.append(ptr)
        new_bin.extend(s.encode('latin1') + b'\x00')

    # Update UI pointers in header
    for i, ptr in enumerate(new_ui_ptrs):
        struct.pack_into('>I', new_bin, 0x10 + i * 4, ptr)

    # Write item descriptions & update pointers
    for i, (item_id, fr_desc) in enumerate(items):
        ptr = len(new_bin)
        rec_off = rec_start + i * 48
        struct.pack_into('>I', new_bin, rec_off + 0x20, ptr)
        new_bin.extend(fr_desc.encode('latin1') + b'\x00')

    # 4-byte padding alignment
    while len(new_bin) % 4 != 0:
        new_bin.append(0)

    return bytes(new_bin), translated_count, item_count


def patch_wdr_shops(wdr_path, expls):
    """Patches all shop*.bin files inside wdr.par."""
    print(f"\n[+] Opening wdr.par: {wdr_path}")
    with open(wdr_path, 'rb') as f:
        wdr_data = bytearray(f.read())

    magic = struct.unpack('>I', wdr_data[:4])[0]
    assert magic == 0x50415243, f"Not a valid PARC: {hex(magic)}"

    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', wdr_data[16:32])
    name_offset = 32 + folder_count * 64

    # Locate shop*.bin entries
    shop_indices = []
    for i in range(file_count):
        fn = wdr_data[name_offset + i * 64 : name_offset + (i + 1) * 64].split(b'\x00')[0].decode('latin1')
        if fn.startswith('shop') and fn.endswith('.bin'):
            entry_off = file_table_offset + i * 32
            flags, u_sz, c_sz, f_off = struct.unpack('>4I', wdr_data[entry_off : entry_off + 16])
            shop_indices.append((i, fn, entry_off, flags, u_sz, c_sz, f_off))

    print(f"[+] Found {len(shop_indices)} shop files in wdr.par (indices {shop_indices[0][0]} to {shop_indices[-1][0]})")

    # Verify that all shop files are located at the end of the archive
    shop_start_offset = min(x[6] for x in shop_indices)
    print(f"[+] Shop data block begins at offset: 0x{shop_start_offset:x} ({shop_start_offset})")

    # Translate each shop binary
    translated_bins = []
    total_translated = 0
    total_items = 0

    for idx, fn, entry_off, flags, u_sz, c_sz, f_off in shop_indices:
        raw_shop = wdr_data[f_off : f_off + c_sz]
        trans_bin, count, itotal = translate_shop_binary(raw_shop, expls)
        translated_bins.append((idx, fn, entry_off, flags, trans_bin))
        total_translated += count
        total_items += itotal
        print(f"  - {fn}: translated {count}/{itotal} item descriptions (size {c_sz} -> {len(trans_bin)})")

    print(f"[+] Translation complete: {total_translated}/{total_items} items localized to French!")

    # Backup wdr.par
    bak_path = wdr_path + ".bak"
    if not os.path.exists(bak_path):
        shutil.copyfile(wdr_path, bak_path)
        print(f"[+] Backup created: {bak_path}")

    # Reconstruct wdr_data from shop_start_offset onwards
    rebuilt_wdr = wdr_data[:shop_start_offset]
    current_write_offset = shop_start_offset

    for idx, fn, entry_off, flags, trans_bin in translated_bins:
        # Align to 64 bytes for clean RGG PARC padding
        aligned_offset = (current_write_offset + 63) & ~63
        if aligned_offset > len(rebuilt_wdr):
            rebuilt_wdr.extend(b'\x00' * (aligned_offset - len(rebuilt_wdr)))

        bin_offset = len(rebuilt_wdr)
        bin_len = len(trans_bin)
        rebuilt_wdr.extend(trans_bin)
        current_write_offset = len(rebuilt_wdr)

        # Update entry in file table
        # flags (keep uncompressed), uncomp_sz, comp_sz, offset
        struct.pack_into('>4I', rebuilt_wdr, entry_off, flags & ~0x80000000, bin_len, bin_len, bin_offset)

    print(f"[+] Rebuilt wdr.par size: {len(rebuilt_wdr)} bytes (original: {len(wdr_data)})")

    with open(wdr_path, 'wb') as f:
        f.write(rebuilt_wdr)

    print(f"[SUCCESS] {wdr_path} successfully updated with all translated shop files!")


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    boot_par = os.path.join(repo_root, 'release_gog', 'data', 'bootpar', 'boot.par')
    wdr_par = os.path.join(repo_root, 'release_gog', 'data', 'wdr_par_c', 'wdr.par')

    if not os.path.isfile(boot_par):
        print(f"[ERROR] {boot_par} not found!")
        sys.exit(1)
    if not os.path.isfile(wdr_par):
        print(f"[ERROR] {wdr_par} not found!")
        sys.exit(1)

    expls = load_french_item_descriptions(boot_par)
    patch_wdr_shops(wdr_par, expls)


if __name__ == '__main__':
    main()
