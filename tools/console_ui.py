#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/console_ui.py — Moteur d'interface console moderne & ergonomique pour Yakuza 0 FR Patch
Créé par Typhon0 (basé sur les traductions initiales de RGG FR).
"""

import os
import sys
import re
import stat
import subprocess
import shutil

# Try enabling Virtual Terminal Processing on Windows
_VT_ENABLED = False
if os.name == 'nt':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        h_stdout = kernel32.GetStdHandle(-11) # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(h_stdout, ctypes.byref(mode)):
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            if kernel32.SetConsoleMode(h_stdout, mode.value | 0x0004):
                _VT_ENABLED = True
    except Exception:
        _VT_ENABLED = False
else:
    _VT_ENABLED = True


class Colors:
    """ANSI color and formatting codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    
    # Background colors
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"
    BG_DARK = "\033[40m"


ANSI_REGEX = re.compile(r'\033\[[0-9;]*m')


def strip_ansi(text: str) -> str:
    """Removes ANSI formatting sequences from text for accurate width calculation."""
    return ANSI_REGEX.sub('', text)


def supports_color() -> bool:
    """Check if the current terminal supports ANSI color output."""
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    if os.name == 'nt' and not _VT_ENABLED:
        return 'ANSICON' in os.environ or 'WT_SESSION' in os.environ
    return True


_USE_COLOR = supports_color()


def c(color_code: str, text: str) -> str:
    """Wrap text with color if color is supported."""
    if _USE_COLOR:
        return f"{color_code}{text}{Colors.RESET}"
    return text


def print_banner(version: str = "v1.13.0"):
    """Displays the stylized ASCII banner for Yakuza 0 FR Patch."""
    banner_lines = [
        r"  ██╗   ██╗ █████╗ ██╗  ██╗██╗   ██╗███████╗ █████╗      ██████╗ ",
        r"  ╚██╗ ██╔╝██╔══██╗██║ ██╔╝██║   ██║╚══███╔╝██╔══██╗    ██╔═████╗",
        r"   ╚████╔╝ ███████║█████╔╝ ██║   ██║  ███╔╝ ███████║    ██║██╔██║",
        r"    ╚██╔╝  ██╔══██║██╔═██╗ ██║   ██║ ███╔╝  ██╔══██║    ████╔╝██║",
        r"     ██║   ██║  ██║██║  ██╗╚██████╔╝███████╗██║  ██║    ╚██████╔╝",
        r"     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝     ╚═════╝ ",
    ]
    
    print("\n" + c(Colors.CYAN, "╭" + "─" * 74 + "╮"))
    for line in banner_lines:
        padding = 74 - len(strip_ansi(line))
        left_pad = padding // 2
        right_pad = padding - left_pad
        print(c(Colors.CYAN, "│") + c(Colors.RED + Colors.BOLD, " " * left_pad + line + " " * right_pad) + c(Colors.CYAN, "│"))
    
    sep = "─" * 68
    print(c(Colors.CYAN, "│  " + c(Colors.GRAY, sep) + "  │"))
    
    title = f"YAKUZA 0 — PATCH DE TRADUCTION FRANÇAISE (GOG {version})"
    author = "Par Typhon0 (basé sur les traductions initiales de RGG FR)"
    
    p1 = 74 - len(title)
    p2 = 74 - len(author)
    print(c(Colors.CYAN, "│") + c(Colors.WHITE + Colors.BOLD, " " * (p1 // 2) + title + " " * (p1 - p1 // 2)) + c(Colors.CYAN, "│"))
    print(c(Colors.CYAN, "│") + c(Colors.YELLOW, " " * (p2 // 2) + author + " " * (p2 - p2 // 2)) + c(Colors.CYAN, "│"))
    print(c(Colors.CYAN, "╰" + "─" * 74 + "╯") + "\n")


def card_start(title: str, width: int = 76):
    """Prints the top border of a stylized card."""
    formatted_title = f" [ {title} ] "
    remain = max(0, width - 2 - len(formatted_title))
    left = 2
    right = max(0, remain - left)
    print(c(Colors.CYAN, "╭" + "─" * left) + c(Colors.WHITE + Colors.BOLD, formatted_title) + c(Colors.CYAN, "─" * right + "╮"))


def card_line(text: str, status: str = "info", width: int = 76):
    """
    Prints a formatted card content line with a colored status badge.
    Status can be: 'ok', 'action', 'info', 'warn', 'err', or 'none'.
    """
    badges = {
        "ok": c(Colors.GREEN + Colors.BOLD, " [✓] "),
        "action": c(Colors.CYAN + Colors.BOLD, " [⚡] "),
        "info": c(Colors.BLUE + Colors.BOLD, " [ℹ] "),
        "warn": c(Colors.YELLOW + Colors.BOLD, " [!] "),
        "err": c(Colors.RED + Colors.BOLD, " [✗] "),
        "none": "     ",
    }
    badge = badges.get(status, badges["info"])
    
    # Calculate visible length
    raw_content = f"{strip_ansi(badge)}{strip_ansi(text)}"
    pad_len = max(0, width - 2 - len(raw_content))
    
    print(c(Colors.CYAN, "│ ") + badge + text + " " * pad_len + c(Colors.CYAN, "│"))


def card_end(width: int = 76):
    """Prints the bottom border of a card."""
    print(c(Colors.CYAN, "╰" + "─" * (width - 2) + "╯"))


def format_progress(current: int, total: int, width: int = 20) -> str:
    """Returns a visual progress bar string: [████████░░] 80%"""
    if total <= 0:
        pct = 100
        filled = width
    else:
        pct = max(0, min(100, int((current / total) * 100)))
        filled = int(width * (pct / 100))
    empty = max(0, width - filled)
    
    bar = c(Colors.GREEN, "█" * filled) + c(Colors.GRAY, "░" * empty)
    return f"[{bar}] {c(Colors.WHITE + Colors.BOLD, f'{pct:>3}%')}"


def validate_game_directory(game_dir: str) -> bool:
    """
    Checks strictly if the provided directory contains Yakuza0.exe (Rule 6).
    """
    if not game_dir or not os.path.isdir(game_dir):
        return False
    exe_path = os.path.join(game_dir, "Yakuza0.exe")
    return os.path.isfile(exe_path)


def sanitize_path(raw_path: str) -> str:
    """Strips quotes, extra spaces, and trailing slashes."""
    if not raw_path:
        return ""
    p = raw_path.strip().strip('"').strip("'").strip()
    while p.endswith('/') or p.endswith('\\'):
        p = p[:-1]
    return os.path.normpath(p)


def prompt_folder_dialog_powershell() -> str | None:
    """Opens a native Windows FolderBrowserDialog via a lightweight PowerShell call."""
    if os.name != 'nt':
        return None
    ps_cmd = (
        "[System.Reflection.Assembly]::LoadWithPartialName('System.windows.forms') | Out-Null; "
        "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
        "$f.Description = 'Selectionnez le dossier d''installation de Yakuza 0 (contenant Yakuza0.exe)'; "
        "if ($f.ShowDialog() -eq 'OK') { Write-Host $f.SelectedPath }"
    )
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=60)
        chosen = res.stdout.strip()
        if chosen and os.path.isdir(chosen):
            return sanitize_path(chosen)
    except Exception:
        pass
    return None


def scan_drives_for_game() -> str | None:
    """Scans common directories and drive letters for Yakuza0.exe."""
    common_subdirs = [
        "GOG Games/Yakuza 0",
        "Program Files (x86)/GOG Galaxy/Games/Yakuza 0",
        "Program Files/GOG Galaxy/Games/Yakuza 0",
        "Games/Yakuza 0",
        "Jeux/Yakuza 0",
        "SteamLibrary/steamapps/common/Yakuza 0",
        "Program Files (x86)/Steam/steamapps/common/Yakuza 0",
    ]
    
    # Check drives on Windows
    drives = []
    if os.name == 'nt':
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
    else:
        drives = ["/"]

    for drive in drives:
        for sub in common_subdirs:
            candidate = os.path.normpath(os.path.join(drive, sub))
            if validate_game_directory(candidate):
                return candidate

    return None


def resolve_game_directory(initial_path: str = None, interactive: bool = True) -> str | None:
    """
    Resolves and strictly validates the Yakuza 0 game directory (Rule 6).
    If not found and interactive is True, prompts user for selection.
    """
    is_tty = hasattr(sys.stdin, 'isatty') and sys.stdin.isatty()
    can_interact = interactive and is_tty

    if initial_path:
        sanitized = sanitize_path(initial_path)
        if validate_game_directory(sanitized):
            return sanitized
        # If user passed a file pointing to Yakuza0.exe
        if os.path.isfile(sanitized) and os.path.basename(sanitized).lower() == "yakuza0.exe":
            parent = os.path.dirname(sanitized)
            if validate_game_directory(parent):
                return parent
        # An explicit invalid path was provided: do not silently use candidate_locations
        if not can_interact:
            return None
        card_start("CHEMIN SPÉCIFIÉ INVALIDE", width=76)
        card_line(f"Le chemin spécifié ne contient pas Yakuza0.exe :", status="err")
        card_line(f"  '{sanitized}'", status="none")
        card_end(width=76)

    # If no initial path was provided, check common relative and installation paths
    if not initial_path:
        candidate_locations = [
            os.getcwd(),
            os.path.join(os.getcwd(), ".."),
            os.path.join(os.getcwd(), "..", ".."),
            os.path.dirname(os.path.abspath(__file__)),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."),
            "C:\\GOG Games\\Yakuza 0",
            "D:\\GOG Games\\Yakuza 0",
            "E:\\GOG Games\\Yakuza 0",
            "C:\\Program Files (x86)\\GOG Galaxy\\Games\\Yakuza 0",
        ]
        
        for cand in candidate_locations:
            norm = os.path.normpath(cand)
            if validate_game_directory(norm):
                return norm

    if not can_interact:
        return None

    # Interactive flow
    card_start("RÉSOLUTION DU DOSSIER DE JEU", width=76)
    card_line("Yakuza0.exe n'a pas été détecté automatiquement dans les dossiers usuels.", status="warn")
    card_line("Veuillez indiquer où est installé votre jeu Yakuza 0 :", status="info")
    card_line("  [1] Recherche automatique sur tous vos disques durs", status="none")
    card_line("  [2] Parcourir avec la fenêtre Windows (sélection de dossier)", status="none")
    card_line("  [3] Coller ou glisser-déposer le chemin du dossier ici", status="none")
    card_line("  [Q] Quitter l'installation", status="none")
    card_end(width=76)

    while True:
        try:
            choice = input("\n" + c(Colors.CYAN + Colors.BOLD, " Votre choix [1/2/3/Q] : ")).strip().lower()
        except (KeyboardInterrupt, EOFError):
            return None

        if choice == '1':
            print(c(Colors.CYAN, " [*] Analyse des disques en cours..."))
            found = scan_drives_for_game()
            if found:
                print(c(Colors.GREEN + Colors.BOLD, f" [✓] Jeu détecté : {found}"))
                return found
            else:
                print(c(Colors.RED, " [✗] Yakuza0.exe introuvable via la recherche automatique."))
        elif choice == '2':
            print(c(Colors.CYAN, " [*] Ouverture du sélecteur de dossier Windows..."))
            chosen = prompt_folder_dialog_powershell()
            if chosen and validate_game_directory(chosen):
                print(c(Colors.GREEN + Colors.BOLD, f" [✓] Dossier valide : {chosen}"))
                return chosen
            elif chosen:
                print(c(Colors.RED, f" [✗] Le dossier sélectionné ne contient pas Yakuza0.exe : {chosen}"))
            else:
                print(c(Colors.YELLOW, " [!] Sélection annulée."))
        elif choice == '3':
            try:
                manual_input = input(c(Colors.CYAN, " Entrez ou glissez le dossier du jeu : ")).strip()
            except (KeyboardInterrupt, EOFError):
                return None
            sanitized = sanitize_path(manual_input)
            if validate_game_directory(sanitized):
                return sanitized
            else:
                print(c(Colors.RED, f" [✗] Dossier invalide ou Yakuza0.exe absent : '{sanitized}'"))
        elif choice == 'q':
            return None
        else:
            print(c(Colors.YELLOW, " Choix non reconnu. Entrez 1, 2, 3 ou Q."))
