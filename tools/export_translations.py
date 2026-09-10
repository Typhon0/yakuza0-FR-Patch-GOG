#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_translations.py
Exports all translation dictionaries into a compact binary format for the C patcher.

Format: translations.bin
  Header:
    u32 magic = 0x54524E53 ("TRNS")
    u32 section_count
  For each section:
    u32 section_id (0=WDR, 1=BOOT, 2=STAY, 3=PAUSE, 4=MINIGAME, 5=SHOPS_UI)
    u32 entry_count
    For each entry:
      u16 en_len
      u16 fr_len
      bytes en_text[en_len]
      bytes fr_text[fr_len]
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath('.'))

from tools.wdr_translations_data import WDR_TRANSLATIONS
from tools.wdr_dict_final import WDR_FINAL_DICT
from tools.stay_translations_data import STAY_TRANSLATIONS
from tools.pause_translations_data import PAUSE_TRANSLATIONS
from tools.minigame_translations_data import MINIGAME_TRANSLATIONS
from tools.boot_dict_part1 import P1
from tools.boot_dict_part2 import P2
from tools.boot_dict_part3 import P3
from tools.boot_dict_part4 import P4

# Shop UI translations (from translate_shops.py)
SHOPS_UI = {
    'Quantity': 'Quantit\xe9',
    "(I haven't selected anything.)": "(Je n'ai rien s\xe9lectionn\xe9.)",
    "(Ain't got anything selected.)": "(Je n'ai rien s\xe9lectionn\xe9.)",
    "(Looks like I'm a little short.)": "(On dirait qu'il me manque des fonds.)",
    "(Gonna need more funds.)": "(Il me faudra plus de fonds.)",
    "Thank you. That'll be %s.": "Merci. Cela fera %s.",
    "(I can't carry any more.)": "(Je ne peux pas en porter plus.)",
    "(I can't carry more.)": "(Je ne peux pas en porter plus.)",
    "(No new stock, I guess.)": "(Pas de nouveau stock, on dirait.)",
    "(Looks like they're all out.)": "(On dirait qu'ils n'en ont plus.)",
    "(I already have this.)": "(J'ai d\xe9j\xe0 ceci.)",
    "(Already got this.)": "(J'ai d\xe9j\xe0 \xe7a.)",
    'Inventory': 'Inventaire',
    'Details': 'D\xe9tails',
    'Products': 'Articles',
    '<Sign:1>Back': '<Sign:1>Retour',
    '<Sign:1>Next %d/%d': '<Sign:1>Suivant %d/%d',
    'Order': 'Commander',
}

def clean_fr(s):
    """Clean French text: remove problematic chars."""
    return s.replace('\u0153', 'oe').replace('\u0152', 'OE').replace('\xc7a', 'Ca').replace('\xc7A', 'CA').replace('\xc7', 'C')

def write_section(out, section_id, translations):
    """Write one translation section."""
    # Sort by key length descending (longest first) to avoid substring collisions
    sorted_items = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)
    
    # Filter: FR must be <= EN in length, and encodable in latin1
    valid = []
    for en, fr in sorted_items:
        fr_clean = clean_fr(fr)
        try:
            en_b = en.encode('latin1')
            fr_b = fr_clean.encode('latin1')
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        if len(fr_b) <= len(en_b):
            valid.append((en_b, fr_b))
    
    out.write(struct.pack('<II', section_id, len(valid)))
    for en_b, fr_b in valid:
        out.write(struct.pack('<HH', len(en_b), len(fr_b)))
        out.write(en_b)
        out.write(fr_b)

def main():
    # Combine WDR
    wdr = dict(WDR_TRANSLATIONS)
    wdr.update(WDR_FINAL_DICT)
    
    # Combine BOOT
    boot = dict(P1)
    boot.update(P2)
    boot.update(P3)
    boot.update(P4)
    
    sections = [
        (0, 'WDR', wdr),
        (1, 'BOOT', boot),
        (2, 'STAY', STAY_TRANSLATIONS),
        (3, 'PAUSE', PAUSE_TRANSLATIONS),
        (4, 'MINIGAME', MINIGAME_TRANSLATIONS),
        (5, 'SHOPS_UI', SHOPS_UI),
    ]
    
    outpath = 'patcher/translations.bin'
    os.makedirs('patcher', exist_ok=True)
    
    with open(outpath, 'wb') as f:
        f.write(struct.pack('<II', 0x54524E53, len(sections)))
        for sid, name, d in sections:
            write_section(f, sid, d)
    
    size = os.path.getsize(outpath)
    print(f'[+] Exported {outpath} ({size} bytes, {size/1024:.1f} KB)')
    
    # Stats
    for sid, name, d in sections:
        print(f'    Section {sid} ({name}): {len(d)} entries')

if __name__ == '__main__':
    main()
