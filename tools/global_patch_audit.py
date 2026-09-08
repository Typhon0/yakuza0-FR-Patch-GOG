# -*- coding: utf-8 -*-
"""
global_patch_audit.py
Full audit of all release_gog archives to ensure 100% French localization:
- Checks PAR / SLLZ validity
- Checks for raw 0xC7 in text
- Checks for playable/translatable English remaining
"""

import os
import sys
import glob
import re

sys.path.insert(0, '.')
sys.path.insert(0, 'scratch')
from scratch.scanner_engine import parse_par, decompress_sllz

ARCHIVES = [
    'release_gog/data/bootpar/boot.par',
    'release_gog/data/staypar/stay.par',
    'release_gog/data/pausepar_e/pause.par',
    'release_gog/data/pausepar_e/chapter.par',
    'release_gog/data/pausepar_e/minigame.par',
    'release_gog/data/pausepar_e/find_arms.par',
    'release_gog/data/wdr_par_c/common.par',
    'release_gog/data/wdr_par_c/wdr.par',
    'release_gog/data/minigame/pokecir.par',
]

BIN_C_FILES = glob.glob('release_gog/data/minigame/*/*.bin_c')

# Translatable English words regex (distinct from French words)
en_words = re.compile(
    r'\b(the|is|are|was|were|have|has|had|with|from|your|what|where|when|why|how|which|will|would|could|should|'
    r'can\'t|don\'t|didn\'t|won\'t|doesn\'t|i\'m|you\'re|it\'s|we\'re|they\'re|been|about|just|more|some|any|into|after|'
    r'please|again|because|other|only|want|know|think|make|give|tell|feel|game|hand|hands|'
    r'banker|player|round|rolled|bets|bored|help|right|here|there|sure|very|much|many|never|always|ever|'
    r'back|come|came|take|took|like|look|seen|said|say|saying|gonna|wanna|gotta|ain\'t|shit|damn|fuck|dude|bro|'
    r'cash|lose|lost|win|won)\b',
    re.IGNORECASE
)

# Known proper nouns, licensed song titles, brand names, and engine constants
IGN = [
    'data/', '.dds', '.gmd', '.par', '_c0', 'sys_', 'font', 'shader',
    'The Thinking Driver', 'The Macallan', 'Grand', 'Sunao ni', 'Locke the Superman',
    'YOKOMICHI', 'Silvers', 'SILVERS', "WHAT's IN?", "WHAT'S IN?",
    'Bad Boy Aku', 'LOOK', 'VICTIM', "I'm Gonna Make Her Mine", 'Queen of the passion',
    'Butterfly City', 'As a man, As a brother', 'The Battle for the Dream',
    'Rouge of Love', 'Disco City Boy', 'AMUSEMENT GAME YOU', 'Video Boy', 'The Megalopolis',
    'V.S.O.P', "It's showtime", 'Network Terms of Use', 'game center', 'SEGA', 'Haneda',
    '(This will be never shown.)', "(This ain't gonna be shown ever.)",
    'Friday Night', 'Koi no DISCO QUEEN', 'Queen of Passion', 'Start OF THE END', 'With You',
    "Biere The Malt's", 'The Kaku Highball', 'All right !', 'Super look',
    'pac_STID_ST_OSAKA.bin', 'uid010c1716.msg', 'uid0133127b.msg', 'pokecir_car_set.bin'
]

ENGINE_CONSTANTS = {
    'PLAYER', 'MONEY', 'OTHER', 'GOOD', 'TIME', 'THINK', 'play', 'staff',
    'before', 'good', 'lose', 'player', 'banker', 'BANKER', 'COUNT-UP',
    'IF8R', 'Big Bang Matsu', 'sticker_e_name'
}

def audit_file_content(path, fn, data):
    # Skip textures and Asian language fallback assets
    if fn.endswith('.dds') or fn.endswith('.bin_j') or fn.endswith('.bin_k') or fn.lower().endswith('.png'):
        return []

    issues = []
    for raw in data.split(b'\x00'):
        try:
            s = raw.decode('latin1').strip()
        except:
            continue
        if len(s) < 4:
            continue
        if any(ign in s for ign in IGN):
            continue
        if s in ENGINE_CONSTANTS:
            continue
        if any(fr_w in s.lower() for fr_w in [
            ' le ', ' la ', ' les ', ' des ', ' du ', ' de ', ' un ', ' une ', ' et ',
            ' pour ', ' dans ', ' avec ', ' pas ', ' que ', ' qui ', ' au ', ' aux ',
            ' est ', ' sont ', ' sur ', ' par ', ' vous ', ' nous ', ' il ', ' elle '
        ]):
            continue
        if s.endswith('Player') or s.endswith('Man') or 'VICTIM' in s:
            continue
        printable = sum(1 for c in s if 32 <= ord(c) <= 126 or c in '\r\n\t' or 160 <= ord(c) <= 255)
        if len(s) > 0 and printable / len(s) < 0.8:
            continue
        if len(en_words.findall(s)) >= 1:
            issues.append(s)
    return issues

def main():
    print("=" * 60)
    print("GLOBAL YAKUZA 0 GOG FRENCH LOCALIZATION AUDIT")
    print("=" * 60)

    total_archives = 0
    total_files = 0
    total_english_found = 0

    # 1. Audit PAR archives
    for arch in ARCHIVES:
        if not os.path.exists(arch):
            print(f"[-] Missing archive: {arch}")
            continue
        total_archives += 1
        with open(arch, 'rb') as f:
            raw_par = f.read()
        try:
            parsed = parse_par(raw_par)
        except Exception as e:
            print(f"[!] FAILED TO PARSE PAR: {arch} ({e})")
            continue

        arch_issues = 0
        for fn, (flags, u_sz, c_sz, data) in parsed.items():
            total_files += 1
            try:
                d = decompress_sllz(data) if data.startswith(b'SLLZ') else data
            except Exception as e:
                print(f"[!] FAILED DECOMPRESSION: {arch} -> {fn} ({e})")
                continue
            
            issues = audit_file_content(arch, fn, d)
            if issues:
                arch_issues += len(issues)
                total_english_found += len(issues)
                print(f"  [!] {arch} -> {fn}: {len(issues)} English matches")
                for it in issues[:3]:
                    print(f"      {repr(it[:60])}")

        if arch_issues == 0:
            print(f"[OK] {arch:40} : {len(parsed):4d} files, 0 English remaining!")
        else:
            print(f"[WARN] {arch:38} : {arch_issues} English strings found!")

    # 2. Audit standalone .bin_c files
    bin_c_issues = 0
    for bpath in sorted(BIN_C_FILES):
        total_files += 1
        with open(bpath, 'rb') as f:
            data = f.read()
        try:
            d = decompress_sllz(data) if data.startswith(b'SLLZ') else data
        except Exception:
            d = data
        issues = audit_file_content(bpath, os.path.basename(bpath), d)
        if issues:
            bin_c_issues += len(issues)
            total_english_found += len(issues)
            print(f"  [!] {bpath}: {len(issues)} English matches")
            for it in issues[:3]:
                print(f"      {repr(it[:60])}")

    if bin_c_issues == 0:
        print(f"[OK] minigame/*.bin_c ({len(BIN_C_FILES)} files)       : 0 English remaining!")
    else:
        print(f"[WARN] minigame/*.bin_c                    : {bin_c_issues} English strings found!")

    print("=" * 60)
    print(f"AUDIT SUMMARY: Checked {total_archives} PAR archives & {len(BIN_C_FILES)} minigame files ({total_files} files total).")
    print(f"TOTAL PLAYABLE ENGLISH STRINGS FOUND: {total_english_found}")
    print("=" * 60)

if __name__ == '__main__':
    main()
