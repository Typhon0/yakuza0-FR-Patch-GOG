#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/sync_to_game.py
---------------------
Safely synchronizes release_gog/data to the user's Yakuza 0 GOG game directory:
1. Validates game root exclusively via Yakuza0.exe (Golden Rule 6).
2. Lifts read-only attributes (+R) using os.chmod (Golden Rule 8).
3. Copies updated archives preserving exact timestamps and permissions.
4. Reports exact status and paths.
"""

import os
import sys
import shutil
import stat

def sync_to_game(game_dir=r"D:\GOG Games\Yakuza 0", src_data="release_gog/data"):
    # Clean trailing slashes
    game_dir = os.path.abspath(game_dir.rstrip(r'\/'))
    exe_path = os.path.join(game_dir, "Yakuza0.exe")

    print("=" * 70)
    print("  SYNCHRONISEUR AUTOMATISÉ — Patch FR Yakuza 0 GOG")
    print("=" * 70)
    print(f"[*] Dossier de jeu cible : {game_dir}")

    # Golden Rule 6: Validate Yakuza0.exe
    if not os.path.isfile(exe_path):
        print(f"\n[ERREUR BLOQUANTE] 'Yakuza0.exe' introuvable dans '{game_dir}' !")
        print("  Vérifie le chemin de ton installation GOG de Yakuza 0.")
        sys.exit(1)

    print(f"[+] 'Yakuza0.exe' détecté ({os.path.getsize(exe_path):,} octets).")

    dst_data = os.path.join(game_dir, "data")
    if not os.path.exists(dst_data):
        os.makedirs(dst_data, exist_ok=True)

    copied = 0
    skipped = 0

    for root, dirs, files in os.walk(src_data):
        rel_dir = os.path.relpath(root, src_data)
        target_dir = os.path.join(dst_data, rel_dir) if rel_dir != '.' else dst_data
        os.makedirs(target_dir, exist_ok=True)

        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(target_dir, f)

            # Check if copy needed
            need_copy = True
            if os.path.exists(dst_file):
                src_sz = os.path.getsize(src_file)
                dst_sz = os.path.getsize(dst_file)
                src_mtime = int(os.path.getmtime(src_file))
                dst_mtime = int(os.path.getmtime(dst_file))
                if src_sz == dst_sz and src_mtime <= dst_mtime:
                    need_copy = False

            if need_copy:
                # Golden Rule 8: Lift read-only lock before overwriting
                if os.path.exists(dst_file):
                    try:
                        os.chmod(dst_file, stat.S_IWRITE | stat.S_IREAD)
                    except Exception:
                        pass
                shutil.copy2(src_file, dst_file)
                # Ensure destination remains writable
                try:
                    os.chmod(dst_file, stat.S_IWRITE | stat.S_IREAD)
                except Exception:
                    pass
                print(f"  [COPIÉ] {os.path.relpath(dst_file, game_dir)} ({os.path.getsize(dst_file):,} octets)")
                copied += 1
            else:
                skipped += 1

    # Copy diagnostic tools to game root
    for tool_name in ["rgg_preflight.exe", "diagnose_crash.bat"]:
        src_tool = os.path.join("release_gog", tool_name)
        if os.path.exists(src_tool):
            dst_tool = os.path.join(game_dir, tool_name)
            try:
                if os.path.exists(dst_tool):
                    os.chmod(dst_tool, stat.S_IWRITE | stat.S_IREAD)
                shutil.copy2(src_tool, dst_tool)
                os.chmod(dst_tool, stat.S_IWRITE | stat.S_IREAD)
                print(f"  [OUTIL] {tool_name} installe a la racine du jeu.")
            except Exception:
                pass

    print(f"\n[SUCCES] Synchronisation terminee : {copied} fichier(s) mis a jour, {skipped} deja a jour.")
    print("=" * 70)
    return True

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else r"D:\GOG Games\Yakuza 0"
    sync_to_game(target)
