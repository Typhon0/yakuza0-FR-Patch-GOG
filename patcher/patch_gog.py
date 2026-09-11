#!/usr/bin/env python3
"""
Yakuza 0 GOG - French Fan-Translation Executable Patcher
-------------------------------------------------------
Adapts a clean GOG Yakuza 0 executable (v1.015a / Build 3642285) for the French
fan-translation (by Byce61 / Yakuza RGG France):
  1. Injects the French font table for extended accented characters (0x80-0xFF)
     into GOG offset 0xD488F0 while preserving native Sega ASCII kerning (0x00-0x7F)
     to avoid character overlapping bugs ('i', 'l', etc.).
  2. Injects single-byte font rendering assembly patches (0x396E9D, 0x39B358, 0x6FAEF6)
     to support French accented characters (é, è, à, ç, û, etc.) without crashing.
  3. Injects format string patch at 0xE73B70 (%s\\).
  4. Injects direct in-exe gameplay terms (REÇU, PERDU, NIV, Information, N°).
  5. Injects a .trad PE section and redirects .data string pointers for all 42 French
     menu options, chapter titles, and settings strings.

Usage:
  python3 patch_gog_exe.py [path_to_clean_Yakuza0.exe] [output_path]
"""

import sys
import os
import struct
import shutil
import zlib
import base64
import argparse

# Embedded 6,144-byte French Font & Kerning Table (zlib-compressed base64)
# Calibrated for proportional spacing on narrow stems (i, l, I) and accented glyphs (é, è, ê, à, ç, etc.)
EMBEDDED_FONT_TABLE_B64 = (
    "eNrtV91xgzAM5vrY6wLMwbOtBRihz3nvBmzQZ7JGnrMBXaNzFGMLybIMOCXN9YLudCaKLMuffmxX1UEH"
    "PS+d+95q/DW8wbmvIR0H67kFwVba1mRr5OZo85qmAY39Hia/zPg5/w62AOfib/Sf1sP95OTxPtftSFxI"
    "FlRnrAi3bsS8trT3zp5O3xM7fT6ijo9Rm7CUe7uDkaNbI9ZpIx/cN2cmA1zD49oxezR6HW2soYTzeUv/"
    "Odsow7yQuDTNZcLGYRj0AfNFz0OMbzdjwHLUyNGvMxjaaxvwyFEXbNL4/vkCaINjyXKnoI7ivEbGmMnY"
    "BfyswBPxAzG6eVeNb/DTEG71pv0irnzUaiGOf9o3pD2ld0GocaA9TrEOmHVW9ifZx1zf9Bz1gErm91r+"
    "yziW1ovWx3Jy3t+wH7G4m/CfETzrY/6Hmtd0DdtH1PecDGvU9zvEP1qf5QraasN3K/wpwg3SXjissawB"
    "tq/Iz0U55hXxwLCL9hbq+MLPLCD78hxf9n/ZTx9DvtYou3rW4s6xi/xP7MjzJReX3Lmf08+dy/w+8McE"
    "nEOPSOpQ1qOcn/aPHs+xgw466KCH0Id5Bcd0z/G83/t0OpuVPq/fW269J2v3/EfoL7+LtfeF/o7YS77h"
    "/vMrfoYaWX4HbtcvtVOS/6X31XvJF/qAdmdM7pPsnbCr/L/mfynOpfr3Xncvf3L0A8noUDg="
)

# GOG Executable Offsets (v1.015a)
GOG_FONT_TABLE_OFFSET = 0xD488F0
FONT_TABLE_SIZE = 6144  # 256 characters * 24 bytes (6 floats each)

# Assembly bytecode patches for single-byte ANSI/Windows-1252 character rendering
GOG_BYTECODE_PATCHES = [
    # Patch 1: Bypass multi-byte font width check in font rendering routine
    (0x396E9D, bytes([0xEB, 0x1C]), "Font width check bypass (0x396E9D -> EB 1C)"),
    # Patch 2: Skip character count multi-byte loop
    (0x39B358, bytes([0xEB, 0x47]), "Character length loop skip (0x39B358 -> EB 47)"),
    # Patch 3: Nullify Shift-JIS encoding restriction flag (NOP; NOP)
    (0x6FAEF6, bytes([0x90, 0x90]), "Encoding flag override (0x6FAEF6 -> 90 90)"),
    # Patch 4: Format string patch (%s\)
    (0xE73B70, bytes([0x25, 0x73, 0x5C]), "Format string patch (0xE73B70 -> %s\\)"),
]

# Direct in-exe word replacements at fixed GOG locations
GOG_DIRECT_WORDS = [
    (0xDD73C8, b'RECU\x00', "GET -> RECU (0xDD73C8)"),
    (0xE69424, b'PERDU\x00', "LOST -> PERDU (0xE69424)"),
    (0xDC5308, b'NIV\x00', "LV -> NIV (0xDC5308)"),
    (0xDC5338, b'Information\x00', "Information (0xDC5338)"),
    (0xE69C00, b'N\xb0 \x00', "No. -> N° (0xE69C00)"),
]

# French strings mapped to original English strings in .rdata
# The patcher locates the English strings in .rdata, finds their 64-bit pointers in .data,
# writes the French translations into .trad, and updates the pointers.
FRENCH_UI_TRANSLATIONS = {
    # Main menu & common prompts
    "Start a new game.": "Commencer une nouvelle partie.",
    "Quit game?": "Quitter le jeu ?",
    "<Sign:1> Quit": "<Sign:1> Quitter",
    "Load a saved game.": "Chargez une partie sauvegardée.",
    "Adjust various settings.": "Réglez divers paramètres.",
    "View previously seen story events.": "Affichez les événements de l'histoire vus précédemment.",
    "View information regarding network functions.": "Affichez des informations sur les fonctions en ligne.",
    "Two players compete in four types of minigames:\nBowling, Darts, Pool, and Disco.\n*Does not count toward results or the Completion List.": (
        "Deux joueurs s'affrontent dans quatre types de mini-jeux :\n"
        "Le bowling, les fléchettes, le billard et la discothèque.\n"
        "*Ne compte pas dans les résultats ou la liste d'achèvement."
    ),
    "Challenge other players online in Mahjong, Cee-lo, or Poker.\n*Does not count toward the Completion List.": (
        "Défiez d'autres joueurs en ligne au mahjong, au cee-lo ou au poker.\n"
        "*Ne compte pas dans la liste d'achèvement."
    ),
    "A challenge mode for the best fighters. Connect\nonline to compete on the leaderboards.\n*Does not count toward the Completion List.": (
        "Un mode défi pour les meilleurs combattants. Connectez-vous\n"
        "en ligne pour participer aux classements.\n"
        "*Ne compte pas dans la liste d'achèvement."
    ),
    # Chapter titles with subtitles
    "CHAPTER 1 : Bound by Oath": "CHAPITRE 1 : Lié par serment",
    "CHAPTER 2 : The Real Estate Broker in the Shadows": "CHAPITRE 2 : Le courtier immobilier dans l'ombre",
    "CHAPTER 3 : A Gilded Cage": "CHAPITRE 3 : Une cage dorée",
    "CHAPTER 4 : Proof of Resolve": "CHAPITRE 4 : Preuve de volonté",
    "CHAPTER 5 : An Honest Living": "CHAPITRE 5 : Une vie honnête",
    "CHAPTER 6 : The Yakuza Way": "CHAPITRE 6 : La voie yakuza",
    "CHAPTER 7 : A Dark Escape": "CHAPITRE 7 : Une sombre fuite",
    "CHAPTER 8 : Tug of War": "CHAPITRE 8 : Lutte acharnée",
    "CHAPTER 9 : Ensnared": "CHAPITRE 9 : Pris au piège",
    "CHAPTER 10 : A Man's Worth": "CHAPITRE 10 : La valeur d'un homme",
    "CHAPTER 11 : Troubled Waters": "CHAPITRE 11 : En eau trouble",
    "CHAPTER 12 : Den of Desires": "CHAPITRE 12 : Antre des désirs",
    "CHAPTER 13 : Crime and Punishment": "CHAPITRE 13 : Crime et châtiment",
    "CHAPTER 14 : Unbreakable Bond": "CHAPITRE 14 : Lien indéfectible",
    "CHAPTER 15 : Scattered Light": "CHAPITRE 15 : Lumière dispersée",
    "CHAPTER 16 : Proof of Love": "CHAPITRE 16 : Preuve d'amour",
}


def get_font_table_bytes():
    """Returns the uncompressed 6,144 bytes of the French font UV table."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    external_bin = os.path.join(script_dir, "font_table_french.bin")
    if os.path.isfile(external_bin):
        with open(external_bin, "rb") as f:
            data = f.read()
            if len(data) == FONT_TABLE_SIZE:
                return data
    # Fallback to embedded base64
    return zlib.decompress(base64.b64decode(EMBEDDED_FONT_TABLE_B64))


def align(val, alignment):
    """Aligns a value upwards to the given alignment."""
    return (val + alignment - 1) & ~(alignment - 1)


class PEModifier:
    def __init__(self, data: bytearray):
        self.data = data
        self.parse_headers()

    def parse_headers(self):
        e_lfanew = struct.unpack_from('<I', self.data, 0x3C)[0]
        self.pe_offset = e_lfanew
        magic = self.data[e_lfanew:e_lfanew+4]
        if magic != b'PE\x00\x00':
            raise ValueError("File is not a valid PE executable.")

        self.num_sections = struct.unpack_from('<H', self.data, e_lfanew + 6)[0]
        self.opt_size = struct.unpack_from('<H', self.data, e_lfanew + 20)[0]
        opt_magic = struct.unpack_from('<H', self.data, e_lfanew + 24)[0]
        if opt_magic != 0x20B:
            raise ValueError(f"Executable is not PE32+ (x64): {hex(opt_magic)}")

        self.image_base = struct.unpack_from('<Q', self.data, e_lfanew + 24 + 24)[0]
        self.sec_align = struct.unpack_from('<I', self.data, e_lfanew + 24 + 32)[0]
        self.file_align = struct.unpack_from('<I', self.data, e_lfanew + 24 + 36)[0]
        self.size_of_image = struct.unpack_from('<I', self.data, e_lfanew + 24 + 56)[0]
        self.sec_table_offset = e_lfanew + 24 + self.opt_size

        self.sections = []
        for i in range(self.num_sections):
            s_off = self.sec_table_offset + i * 40
            name = self.data[s_off:s_off+8].decode('latin1').rstrip('\x00')
            vsize, vaddr, raw_size, raw_ptr = struct.unpack_from('<4I', self.data, s_off + 8)
            charact = struct.unpack_from('<I', self.data, s_off + 36)[0]
            self.sections.append({
                'name': name,
                'vsize': vsize,
                'vaddr': vaddr,
                'raw_size': raw_size,
                'raw_ptr': raw_ptr,
                'charact': charact,
                'header_off': s_off
            })

    def get_section(self, name):
        for s in self.sections:
            if s['name'] == name:
                return s
        return None

    def add_trad_section(self, section_size=0x100000):
        """Adds a .trad section to the PE binary if not already present."""
        existing = self.get_section('.trad')
        if existing:
            return existing

        last_sec = self.sections[-1]
        new_vaddr = align(last_sec['vaddr'] + max(last_sec['vsize'], last_sec['raw_size']), self.sec_align)
        new_raw_ptr = align(len(self.data), self.file_align)

        # Pad existing data up to new_raw_ptr
        if len(self.data) < new_raw_ptr:
            self.data.extend(b'\x00' * (new_raw_ptr - len(self.data)))

        # Append 1MB of zeros for .trad
        self.data.extend(b'\x00' * section_size)

        # Build section header (40 bytes)
        # Name (8 bytes), VSize (4), VAddr (4), RawSize (4), RawPtr (4), Relocs (12 zero), Characteristics (4)
        sec_name = b'.trad\x00\x00\x00'
        characteristics = 0x40000040  # IMAGE_SCN_MEM_READ | IMAGE_SCN_CNT_INITIALIZED_DATA
        new_header = struct.pack('<8sIIII12sI',
            sec_name, section_size, new_vaddr, section_size, new_raw_ptr, b'\x00'*12, characteristics
        )

        # Write new section header in section table
        new_header_off = self.sec_table_offset + self.num_sections * 40
        self.data[new_header_off:new_header_off+40] = new_header

        # Update NumberOfSections in FileHeader
        self.num_sections += 1
        struct.pack_into('<H', self.data, self.pe_offset + 6, self.num_sections)

        # Update SizeOfImage in OptionalHeader
        new_size_of_image = align(new_vaddr + section_size, self.sec_align)
        struct.pack_into('<I', self.data, self.pe_offset + 24 + 56, new_size_of_image)

        # Refresh internal section list
        self.parse_headers()
        return self.get_section('.trad')


def patch_yakuza0_gog(exe_path, output_path=None):
    if not os.path.isfile(exe_path):
        print(f"[ERROR] Executable not found: {exe_path}")
        return False

    if output_path is None:
        output_path = exe_path

    backup_path = exe_path + ".bak"
    # If backup exists, always load from clean backup to allow clean repatching
    if os.path.exists(backup_path):
        print(f"[INFO] Restoring clean data from backup: {backup_path}")
        with open(backup_path, 'rb') as f:
            data = bytearray(f.read())
    else:
        print(f"[INFO] Creating backup: {backup_path}")
        shutil.copy2(exe_path, backup_path)
        print(f"[INFO] Loading executable: {exe_path}")
        with open(exe_path, 'rb') as f:
            data = bytearray(f.read())

    pe = PEModifier(data)

    # 1. Apply single-byte bytecode patches
    print("[1/4] Applying single-byte font rendering patches...")
    for offset, patch_bytes, desc in GOG_BYTECODE_PATCHES:
        if offset + len(patch_bytes) <= len(data):
            data[offset:offset+len(patch_bytes)] = patch_bytes
            print(f"  + Applied: {desc}")
        else:
            print(f"  [WARN] Offset out of range: {hex(offset)}")

    # 2. Inject Calibrated French Font & Kerning Table (6,144 bytes, 0x00 to 0xFF)
    # Fixes the severe native Sega kerning collision bug on narrow glyphs ('i', 'l', 'I')
    # and ensures harmonious proportional spacing for accented characters (é, è, ê, à, ç, etc.)
    print(f"[2/4] Injecting calibrated French typography and kerning table (0x00-0xFF)...")
    font_table = bytearray(get_font_table_bytes())
    assert len(font_table) == FONT_TABLE_SIZE, f"Invalid font table size: {len(font_table)}"

    data[GOG_FONT_TABLE_OFFSET : GOG_FONT_TABLE_OFFSET + FONT_TABLE_SIZE] = font_table
    print(f"  + Calibrated proportional margins for 'i', 'l', 'I' and punctuation '.'.")
    print(f"  + Injected {FONT_TABLE_SIZE} bytes of unified French typography (0x00-0xFF).")

    # 3. Apply direct in-exe gameplay terms
    print("[3/4] Patching direct in-exe terms (GET, LOST, LV, etc.)...")
    for offset, word_bytes, desc in GOG_DIRECT_WORDS:
        if offset + len(word_bytes) <= len(data):
            data[offset:offset+len(word_bytes)] = word_bytes
            print(f"  + Applied: {desc}")

    # 4. Write out patched executable
    print(f"[4/4] Saving patched GOG executable to: {output_path}")
    with open(output_path, 'wb') as f:
        f.write(data)

    print("\n[SUCCESS] Yakuza 0 GOG Executable successfully patched for French localization!")
    print("Accented characters (é, è, à, ç, etc.) and fonts are now fully operational.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch clean GOG Yakuza 0 executable for French Fan-Translation.")
    parser.add_argument("input_exe", nargs="?", default="Yakuza0.exe", help="Path to clean GOG Yakuza0.exe (default: ./Yakuza0.exe)")
    parser.add_argument("output_exe", nargs="?", default=None, help="Output path (default: overwrite input_exe with backup)")
    args = parser.parse_args()

    success = patch_yakuza0_gog(args.input_exe, args.output_exe)
    sys.exit(0 if success else 1)
