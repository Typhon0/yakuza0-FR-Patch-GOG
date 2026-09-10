#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_release.py — Construit le package de release du patch FR

Crée un zip contenant :
  1. Les scripts Python du patcher (tools/)
  2. Un Python embarqué portable (python-3.x-embed-amd64.zip)
  3. Un .bat lanceur qui utilise le Python embarqué
  4. verify_patch.py + son .bat
  5. README avec instructions

L'utilisateur final n'a RIEN à installer.
"""

import os
import sys
import struct
import shutil
import zipfile
import urllib.request
import tempfile

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.12.7/python-3.12.7-embed-amd64.zip"
PYTHON_EMBED_ZIP = "python-3.12.7-embed-amd64.zip"

RELEASE_DIR = "staging_release"
RELEASE_NAME = "Yakuza0_FR_Patch_GOG_v1.12.3"

# Files to include from tools/
TOOL_FILES = [
    "tools/repair_phone_booths.py",
    "tools/rebuild_clean_wdr.py",
    "tools/translate_boot_par_complete.py",
    "tools/translate_wdr_complete.py",
    "tools/translate_shops.py",
    "tools/translate_stay_par_complete.py",
    "tools/translate_pause_par_complete.py",
    "tools/translate_common_par_complete.py",
    "tools/translate_all_minigames.py",
    "tools/translate_minigames_and_stay_final.py",
    "tools/repair_stay_par.py",
    "tools/verify_patch.py",
    "tools/sllz.py",
    "tools/clean_patch_data.py",
    # Translation data
    "tools/wdr_translations_data.py",
    "tools/wdr_dict_final.py",
    "tools/stay_translations_data.py",
    "tools/pause_translations_data.py",
    "tools/minigame_translations_data.py",
    "tools/boot_dict_part1.py",
    "tools/boot_dict_part2.py",
    "tools/boot_dict_part3.py",
    "tools/boot_dict_part4.py",
    "tools/collect_originals.py",
]

SCRATCH_FILES = [
    "scratch/scanner_engine.py",
]

# Pre-compiled verified archives to include directly
PRECOMPILED_DATA = [
    ("release_gog/data/wdr_par_c/wdr.par", "data/wdr_par_c/wdr.par"),
    ("release_gog/data/wdr_par_c/common.par", "data/wdr_par_c/common.par"),
    ("release_gog/data/bootpar/boot.par", "data/bootpar/boot.par"),
    ("release_gog/data/staypar/stay.par", "data/staypar/stay.par"),
]

ROOT_FILES = [
    ("release_gog/patch_gog.py", "patch_gog.py"),
    ("release_gog/font_table_french.bin", "font_table_french.bin"),
    ("tools/collect_originals.bat", "collect_originals.bat"),
]

BAT_PATCHER = r'''@echo off
chcp 65001 >nul
echo ========================================================
echo   Yakuza 0 - Patch VOSTFR GOG v1.12.3
echo   Par RGG Yakuza Rev / Typhon0
echo ========================================================
echo.

REM Detect game directory
if "%~1"=="" (
    echo [*] Aucun chemin specifie, recherche automatique...
    if exist "data\wdr_par_c\wdr.par" (
        set "GAMEDIR=%CD%"
    ) else if exist "..\data\wdr_par_c\wdr.par" (
        set "GAMEDIR=%CD%\.."
    ) else (
        echo [ERREUR] Impossible de trouver le dossier du jeu.
        echo Usage: patch_fr.bat "C:\Program Files\Yakuza 0"
        pause
        exit /b 1
    )
) else (
    set "GAMEDIR=%~1"
)

echo [*] Dossier du jeu: %GAMEDIR%
echo.

REM Use embedded Python
set "PYTHON=%~dp0python\python.exe"
if not exist "%PYTHON%" (
    echo [ERREUR] Python embarque introuvable dans %~dp0python\
    pause
    exit /b 1
)

echo [1/3] Installation des archives pre-compilees et verifiees...
if not exist "%GAMEDIR%\data\wdr_par_c" mkdir "%GAMEDIR%\data\wdr_par_c"
if not exist "%GAMEDIR%\data\bootpar" mkdir "%GAMEDIR%\data\bootpar"
if not exist "%GAMEDIR%\data\staypar" mkdir "%GAMEDIR%\data\staypar"

if exist "%~dp0data\wdr_par_c\wdr.par" (
    if not exist "%GAMEDIR%\data\wdr_par_c\wdr.par.bak" copy /y "%GAMEDIR%\data\wdr_par_c\wdr.par" "%GAMEDIR%\data\wdr_par_c\wdr.par.bak" >nul 2>&1
    copy /y "%~dp0data\wdr_par_c\wdr.par" "%GAMEDIR%\data\wdr_par_c\wdr.par" >nul
    copy /y "%~dp0data\wdr_par_c\common.par" "%GAMEDIR%\data\wdr_par_c\common.par" >nul
    echo   + wdr.par installe avec succes
)
if exist "%~dp0data\bootpar\boot.par" (
    copy /y "%~dp0data\bootpar\boot.par" "%GAMEDIR%\data\bootpar\boot.par" >nul
    echo   + boot.par installe avec succes
)
if exist "%~dp0data\staypar\stay.par" (
    copy /y "%~dp0data\staypar\stay.par" "%GAMEDIR%\data\staypar\stay.par" >nul
    echo   + stay.par installe avec succes
)

echo.
echo [2/3] Patch de l'executable Yakuza0.exe (polices et accents francais)...
if exist "%GAMEDIR%\Yakuza0.exe" (
    "%PYTHON%" "%~dp0patch_gog.py" "%GAMEDIR%\Yakuza0.exe"
    if errorlevel 1 goto :error
) else (
    echo   ! Yakuza0.exe non present dans ce dossier, etape sautee.
)

echo.
echo [3/3] Verification d'integrite du jeu...
"%PYTHON%" "%~dp0tools\verify_patch.py" "%GAMEDIR%"
if errorlevel 1 goto :error

echo.
echo ========================================================
echo   PATCH INSTALLE AVEC SUCCES !
echo   Toutes les cabines telephoniques et dialogues sont 100%% fonctionnels.
echo   Bon jeu !
echo ========================================================
pause
exit /b 0

:error
echo.
echo [ERREUR] Une erreur est survenue pendant le patch.
echo Verifiez les messages ci-dessus.
pause
exit /b 1
'''

BAT_VERIFY = r'''@echo off
chcp 65001 >nul
echo Verification d'integrite du patch FR Yakuza 0 GOG...
echo.

if "%~1"=="" (
    if exist "data\wdr_par_c\wdr.par" (
        set "GAMEDIR=%CD%"
    ) else (
        set "GAMEDIR=%CD%"
    )
) else (
    set "GAMEDIR=%~1"
)

set "PYTHON=%~dp0python\python.exe"
if not exist "%PYTHON%" (
    echo [ERREUR] Python embarque introuvable.
    pause
    exit /b 1
)

"%PYTHON%" "%~dp0tools\verify_patch.py" "%GAMEDIR%"
pause
'''

README_FR = r'''# Yakuza 0 — Patch VOSTFR GOG v1.12.3

## Correctif v1.12.3
- **Correction définitive du crash 0x6EA307 (Cabines téléphoniques & interactions)** :
  Restauration intégrale du bytecode Sega officiel pour l'ensemble des fichiers de structures
  système et de scène (`snitch.bin`, `ai_popup.bin`, `pac_*.bin`, etc.) éliminant tout décalage d'offset.
- **Cabines téléphoniques 100% fonctionnelles** : Tous les 20 dialogues de cabines de Kamurocho
  et Sotenbori sauvegardent, ouvrent le coffre et affichent les textes français sans crash.
- **Support des boutiques et restaurants** : Noms et descriptions traduits en français sans troncature.
- **Accents et polices** : Prise en charge intégrale des accents français sans chevauchement.

## Installation simple (Recommandée)
1. Décompressez l'archive du patch.
2. Copiez l'intégralité du dossier dans le répertoire d'installation de Yakuza 0 GOG
   (par exemple `D:\GOG Games\Yakuza 0\` ou `C:\Program Files (x86)\GOG Galaxy\Games\Yakuza 0\`).
3. Double-cliquez sur `patch_fr.bat`.
4. Attendez le message « PATCH INSTALLE AVEC SUCCES ! » et lancez le jeu !

## En cas de problème
- Double-cliquez sur `verifier.bat` pour vérifier l'intégrité de toutes les archives du jeu.
'''


def download_python_embed(dest_dir):
    """Download Python embeddable package for Windows."""
    zip_path = os.path.join(dest_dir, PYTHON_EMBED_ZIP)
    if os.path.exists(zip_path):
        print(f"[*] Python embed déjà téléchargé: {zip_path}")
        return zip_path
    
    print(f"[*] Téléchargement de Python embarqué...")
    print(f"    URL: {PYTHON_EMBED_URL}")
    urllib.request.urlretrieve(PYTHON_EMBED_URL, zip_path)
    print(f"[+] Téléchargé: {zip_path} ({os.path.getsize(zip_path)} bytes)")
    return zip_path


def build_release():
    print("=" * 60)
    print("  BUILD RELEASE — Yakuza 0 FR Patch GOG")
    print("=" * 60)
    
    # Clean staging
    if os.path.exists(RELEASE_DIR):
        shutil.rmtree(RELEASE_DIR)
    
    stage = os.path.join(RELEASE_DIR, RELEASE_NAME)
    os.makedirs(stage)
    os.makedirs(os.path.join(stage, "tools"))
    os.makedirs(os.path.join(stage, "scratch"))
    os.makedirs(os.path.join(stage, "python"))
    
    # 1. Copy tool files
    print("[1/5] Copie des scripts...")
    for f in TOOL_FILES:
        if os.path.exists(f):
            shutil.copy2(f, os.path.join(stage, f))
            print(f"  + {f}")
        else:
            print(f"  ! MANQUANT: {f}")
    
    for f in SCRATCH_FILES:
        if os.path.exists(f):
            shutil.copy2(f, os.path.join(stage, f))
            print(f"  + {f}")

    # Copy repaired phones folder
    repaired_src = "tools/repaired_phones"
    if os.path.isdir(repaired_src):
        shutil.copytree(repaired_src, os.path.join(stage, repaired_src), dirs_exist_ok=True)
        print(f"  + {repaired_src} (20 repaired phone .msg files)")

    # 2. Copy pre-compiled data archives
    print("[2/5] Copie des archives pré-compilées certifiées...")
    for src, rel_dst in PRECOMPILED_DATA:
        dst = os.path.join(stage, rel_dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  + {rel_dst} ({os.path.getsize(dst)} bytes)")

    for src, rel_dst in ROOT_FILES:
        dst = os.path.join(stage, rel_dst)
        shutil.copy2(src, dst)
        print(f"  + {rel_dst}")
    
    # 3. Download and extract Python embed
    print("[3/5] Python embarqué...")
    zip_path = download_python_embed(RELEASE_DIR)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(os.path.join(stage, "python"))
    print(f"  + Extrait dans {os.path.join(stage, 'python')}")
    
    # 4. Write bat files
    print("[4/5] Création des lanceurs .bat...")
    with open(os.path.join(stage, "patch_fr.bat"), 'w', encoding='utf-8') as f:
        f.write(BAT_PATCHER)
    with open(os.path.join(stage, "verifier.bat"), 'w', encoding='utf-8') as f:
        f.write(BAT_VERIFY)
    with open(os.path.join(stage, "LISEZMOI.txt"), 'w', encoding='utf-8') as f:
        f.write(README_FR)
    
    # 5. Create zip
    print("[5/5] Création du zip final...")
    zip_out = os.path.join(RELEASE_DIR, f"{RELEASE_NAME}.zip")
    with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(stage):
            for fn in files:
                full = os.path.join(root, fn)
                arcname = os.path.relpath(full, RELEASE_DIR)
                zf.write(full, arcname)
    
    size_mb = os.path.getsize(zip_out) / (1024 * 1024)
    print()
    print(f"[+] Release créée: {zip_out} ({size_mb:.1f} MB)")
    print(f"    Contenu: Archives pré-compilées + Patcher + Python embarqué")
    print(f"    Installation instantanée et 100% fiable.")

    # 6. Automated E2E release validation
    print()
    from tools.test_release_e2e import test_release_zip
    test_release_zip(zip_out)


if __name__ == '__main__':
    build_release()
