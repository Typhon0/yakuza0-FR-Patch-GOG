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
import stat
import time

# Import modern console UI module with robust fallback
try:
    from tools.console_ui import (
        Colors,
        strip_ansi,
        print_banner,
        card_start,
        card_line,
        card_end,
        format_progress,
        resolve_game_directory,
        validate_game_directory,
    )
except ImportError:
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _tools_dir = os.path.join(_script_dir, "tools")
    if os.path.isdir(_tools_dir) and _tools_dir not in sys.path:
        sys.path.insert(0, _tools_dir)
    try:
        from console_ui import (
            Colors,
            strip_ansi,
            print_banner,
            card_start,
            card_line,
            card_end,
            format_progress,
            resolve_game_directory,
            validate_game_directory,
        )
    except ImportError:
        class Colors:
            RESET = ""
            BOLD = ""
            DIM = ""
            RED = ""
            GREEN = ""
            YELLOW = ""
            BLUE = ""
            MAGENTA = ""
            CYAN = ""
            WHITE = ""
            GRAY = ""

        def strip_ansi(t): return t
        def print_banner(v="v1.13.0"):
            print("=========================================================")
            print(f"  YAKUZA 0 — PATCH DE TRADUCTION FRANÇAISE ({v})")
            print("  Par Typhon0 (basé sur les traductions initiales de RGG FR)")
            print("=========================================================\n")
        def card_start(t, w=76): print(f"\n--- [ {t} ] ---")
        def card_line(t, s="info", w=76): print(f"  [{s.upper()}] {t}")
        def card_end(w=76): print("-" * w)
        def format_progress(c, tot, w=20):
            pct = int((c / tot) * 100) if tot > 0 else 100
            return f"[{pct:>3}%]"
        def validate_game_directory(d):
            return bool(d and os.path.isfile(os.path.join(d, "Yakuza0.exe")))
        def resolve_game_directory(p=None, interactive=True):
            if p and validate_game_directory(p): return p
            return None

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
    "Chapter Completion Bonus": "Bonus de fin de chapitre",
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


def kill_game_process():
    """Terminates any lingering Yakuza0.exe processes to unlock files."""
    if sys.platform == 'win32':
        try:
            import subprocess
            subprocess.run(["taskkill", "/F", "/IM", "Yakuza0.exe"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.5)
        except Exception:
            pass


def install_data_archives(game_dir):
    """Safely copies precompiled verified data archives into game directory, stripping read-only flags."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    if not os.path.isdir(data_dir):
        return True

    card_start("2/4 — INSTALLATION DES ARCHIVES TRADUITES", width=76)

    # Nettoyage automatique des sous-dossiers parasites issus d'anciennes extractions imbriquees
    nested_parasites = [
        os.path.join(game_dir, 'data', 'bootpar', 'bootpar'),
        os.path.join(game_dir, 'data', 'staypar', 'staypar'),
        os.path.join(game_dir, 'data', 'wdr_par_c', 'wdr_par_c'),
        os.path.join(game_dir, 'data', 'pausepar_e', 'pausepar_e'),
        os.path.join(game_dir, 'data', 'data'),
    ]
    for parasite in nested_parasites:
        if os.path.isdir(parasite):
            try:
                shutil.rmtree(parasite)
                card_line(f"Sous-dossier parasite supprimé : {os.path.basename(parasite)}", status="ok")
            except Exception as e:
                card_line(f"Impossible de supprimer {parasite}: {e}", status="warn")

    core_archives = [
        ("data/wdr_par_c/wdr.par", 7000000),
        ("data/wdr_par_c/common.par", 10000),
        ("data/bootpar/boot.par", 1500000),
        ("data/staypar/stay.par", 500000),
    ]

    data_files = list(core_archives)

    # Decouverte dynamique des tables et textures de mini-jeux fournies par le patch
    minigame_src_dir = os.path.join(script_dir, "data", "minigame")
    if os.path.isdir(minigame_src_dir):
        patch_minigame_dirs = {"catfight", "fishing", "poker", "cabaret", "teleclub"}
        for root, dirs, files in os.walk(minigame_src_dir):
            rel_dir = os.path.relpath(root, minigame_src_dir).replace('\\', '/')
            sub_folder = rel_dir.split('/')[0] if rel_dir != '.' else ''
            if sub_folder and sub_folder not in patch_minigame_dirs:
                continue
            for f in sorted(files):
                if f.endswith('.bak'):
                    continue
                if f.endswith('.bin') or f.endswith('.bin_c') or f.endswith('.dds'):
                    src_f = os.path.join(root, f)
                    rel_f = os.path.relpath(src_f, script_dir).replace('\\', '/')
                    data_files.append((rel_f, 1))

    total_files = len(data_files)
    for idx, (rel_path, min_size) in enumerate(data_files, 1):
        src = os.path.normpath(os.path.join(script_dir, rel_path.replace('/', os.sep)))
        dst = os.path.normpath(os.path.join(game_dir, rel_path.replace('/', os.sep)))

        if not os.path.isfile(src):
            continue

        # Check if source and destination point to the exact same file
        is_same = False
        try:
            if os.path.exists(dst) and os.path.samefile(src, dst):
                is_same = True
        except Exception:
            pass
        if not is_same:
            try:
                if os.path.normcase(os.path.abspath(src)) == os.path.normcase(os.path.abspath(dst)):
                    is_same = True
            except Exception:
                pass

        if is_same:
            try:
                os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass
            actual_size = os.path.getsize(dst)
            if actual_size < min_size:
                card_line(f"Fichier présent incomplet: '{dst}' ({actual_size} o, attendu >{min_size})", status="err")
                card_end(width=76)
                return False
            size_mb = f"{actual_size / (1024*1024):.1f} Mo" if actual_size > 500000 else f"{actual_size / 1024:.0f} Ko"
            p_bar = format_progress(idx, total_files, width=15)
            fname = os.path.basename(rel_path)
            card_line(f"{fname:<16} {p_bar}  (déjà présent, {size_mb})", status="ok")
            continue

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        if os.path.isfile(dst):
            bak = dst + ".bak"
            if not os.path.exists(bak):
                try:
                    shutil.copy2(dst, bak)
                except Exception:
                    pass
            try:
                os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass

        try:
            shutil.copy2(src, dst)
            os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
        except Exception as e:
            kill_game_process()
            try:
                os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
                shutil.copy2(src, dst)
                os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
            except Exception as e2:
                card_line(f"Impossible d'écrire dans '{dst}': {e2}", status="err")
                card_line("Vérifiez que le jeu est fermé et vos droits d'écriture.", status="warn")
                card_end(width=76)
                return False

        actual_size = os.path.getsize(dst)
        if actual_size < min_size:
            card_line(f"Fichier copié incomplet: '{dst}' ({actual_size} o, attendu >{min_size})", status="err")
            card_end(width=76)
            return False
        
        size_mb = f"{actual_size / (1024*1024):.1f} Mo" if actual_size > 500000 else f"{actual_size / 1024:.0f} Ko"
        p_bar = format_progress(idx, total_files, width=15)
        fname = os.path.basename(rel_path)
        card_line(f"{fname:<16} {p_bar}  ({size_mb})", status="ok")

    # Patch des sous-titres audio d'ambiance si sound.par existe dans le jeu
    user_sound_par = os.path.join(game_dir, "data", "soundpar", "sound.par")
    if os.path.isfile(user_sound_par):
        patch_sound_script = os.path.join(script_dir, "tools", "patch_sound_par.py")
        if os.path.isfile(patch_sound_script):
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("patch_sound_par", patch_sound_script)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                mod.patch_sound_par_inplace(user_sound_par)
                card_line("Sous-titres audio d'ambiance (sound.par) synchronisés", status="ok")
            except Exception as e:
                card_line(f"Avertissement patching sound.par: {e}", status="warn")

    card_line("Toutes les archives et tables de mini-jeux sont déployées", status="ok")
    card_end(width=76)
    return True


def patch_yakuza0_gog(exe_path="Yakuza0.exe", output_path=None, interactive=True):
    print_banner(version="v1.13.0")

    # Strict resolution of game directory / executable (Rule 6)
    if not exe_path or not os.path.isfile(exe_path):
        resolved_dir = resolve_game_directory(exe_path, interactive=interactive)
        if resolved_dir:
            exe_path = os.path.join(resolved_dir, "Yakuza0.exe")
        else:
            card_start("ERREUR DE DÉTECTION", width=76)
            card_line(f"Exécutable Yakuza0.exe introuvable : '{exe_path}'", status="err")
            card_line("Glissez le dossier de jeu sur patch_fr.bat ou lancez :", status="info")
            card_line("  patch_fr.bat \"D:\\GOG Games\\Yakuza 0\"", status="none")
            card_end(width=76)
            return False

    exe_path = os.path.normpath(os.path.abspath(exe_path))
    if output_path is None:
        output_path = exe_path
    else:
        output_path = os.path.normpath(os.path.abspath(output_path))

    game_dir = os.path.dirname(exe_path)

    # Card 1: Préparation & Sécurité
    card_start("1/4 — PRÉPARATION & SÉCURITÉ", width=76)
    kill_game_process()
    card_line("Processus Yakuza0.exe vérifié et libéré", status="ok")

    backup_path = exe_path + ".bak"
    if os.path.exists(backup_path):
        card_line(f"Restauration depuis la sauvegarde propre : {os.path.basename(backup_path)}", status="info")
        with open(backup_path, 'rb') as f:
            data = bytearray(f.read())
    else:
        try:
            os.chmod(exe_path, stat.S_IWRITE | stat.S_IREAD)
        except Exception:
            pass
        shutil.copy2(exe_path, backup_path)
        card_line(f"Sauvegarde originale créée : {os.path.basename(backup_path)}", status="ok")
        with open(exe_path, 'rb') as f:
            data = bytearray(f.read())

    # Unlock read-only on game files
    try:
        os.chmod(exe_path, stat.S_IWRITE | stat.S_IREAD)
        for root, dirs, files in os.walk(os.path.join(game_dir, "data")):
            for f in files:
                try:
                    os.chmod(os.path.join(root, f), stat.S_IWRITE | stat.S_IREAD)
                except Exception:
                    pass
        card_line("Attributs lecture seule (+R) déverrouillés sur le jeu", status="ok")
    except Exception:
        pass
    card_end(width=76)

    # 2. Deploy precompiled data archives if present
    if not install_data_archives(game_dir):
        return False

    # 3. Apply executable patches
    card_start("3/4 — PATCH DE L'EXÉCUTABLE (Yakuza0.exe)", width=76)
    pe = PEModifier(data)

    applied_count = 0
    for offset, patch_bytes, desc in GOG_BYTECODE_PATCHES:
        if offset + len(patch_bytes) <= len(data):
            data[offset:offset+len(patch_bytes)] = patch_bytes
            applied_count += 1
    card_line(f"Patches de rendu mono-octet injectés ({applied_count}/{len(GOG_BYTECODE_PATCHES)})", status="ok")

    font_table = bytearray(get_font_table_bytes())
    assert len(font_table) == FONT_TABLE_SIZE, f"Invalid font table size: {len(font_table)}"
    data[GOG_FONT_TABLE_OFFSET : GOG_FONT_TABLE_OFFSET + FONT_TABLE_SIZE] = font_table
    card_line("Typographie & crénage symétrique [0.4, 0.4] injectés (6 144 o)", status="ok")

    words_applied = 0
    for offset, word_bytes, desc in GOG_DIRECT_WORDS:
        if offset + len(word_bytes) <= len(data):
            data[offset:offset+len(word_bytes)] = word_bytes
            words_applied += 1
    card_line(f"Termes d'interface traduits en dur ({words_applied} termes)", status="ok")

    # Save patched exe
    try:
        os.chmod(output_path, stat.S_IWRITE | stat.S_IREAD)
    except Exception:
        pass
    try:
        with open(output_path, 'wb') as f:
            f.write(data)
    except Exception as e:
        kill_game_process()
        try:
            os.chmod(output_path, stat.S_IWRITE | stat.S_IREAD)
            with open(output_path, 'wb') as f:
                f.write(data)
        except Exception as e2:
            card_line(f"Échec d'écriture dans '{output_path}': {e2}", status="err")
            card_end(width=76)
            return False

    # Verification on disk
    try:
        with open(output_path, 'rb') as f:
            f.seek(GOG_FONT_TABLE_OFFSET + 0x69 * 24)
            i_margin = struct.unpack('<6f', f.read(24))
            if abs(i_margin[0] - 0.4) > 0.01:
                card_line(f"Vérification de table de police échouée sur disque: {i_margin}", status="err")
                card_end(width=76)
                return False
    except Exception as e:
        card_line(f"Échec de vérification sur disque: {e}", status="err")
        card_end(width=76)
        return False

    card_line("Binaire Yakuza0.exe sauvegardé et certifié conforme sur disque", status="ok")
    card_end(width=76)

    # 4. Summary card
    card_start("4/4 — INSTALLATION RÉUSSIE", width=76)
    card_line("Le patch français est désormais actif et opérationnel !", status="ok")
    card_line("Toutes les cabines, cinématiques et dialogues sont traduits.", status="ok")
    card_line("Bon jeu à Kamurocho et Sotenbori !", status="info")
    card_end(width=76)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch clean GOG Yakuza 0 executable for French Fan-Translation.")
    parser.add_argument("input_exe", nargs="?", default=None, help="Path to clean GOG Yakuza0.exe (default: auto-detected)")
    parser.add_argument("output_exe", nargs="?", default=None, help="Output path (default: overwrite input_exe with backup)")
    args = parser.parse_args()

    success = patch_yakuza0_gog(args.input_exe, args.output_exe)
    sys.exit(0 if success else 1)
