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

PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.12.7/python-3.12.7-embed-amd64.zip"
PYTHON_EMBED_ZIP = "python-3.12.7-embed-amd64.zip"

RELEASE_DIR = "staging_release"
RELEASE_NAME = "Yakuza0_FR_Patch_GOG_v1.12.0"

# Files to include from tools/
TOOL_FILES = [
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
    "tools/translate_shops.py",
]

SCRATCH_FILES = [
    "scratch/scanner_engine.py",
]

BAT_PATCHER = r'''@echo off
chcp 65001 >nul
echo ========================================================
echo   Yakuza 0 - Patch VOSTFR GOG v1.12.0
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

echo [1/7] Patch wdr.par (dialogues, quetes, menus)...
"%PYTHON%" "%~dp0tools\translate_wdr_complete.py" "%GAMEDIR%"
if errorlevel 1 goto :error

echo [2/7] Patch boutiques et restaurants...
"%PYTHON%" "%~dp0tools\translate_shops.py" "%GAMEDIR%"
if errorlevel 1 goto :error

echo [3/7] Patch boot.par (interface, objets, combats)...
"%PYTHON%" "%~dp0tools\translate_boot_par_complete.py" "%GAMEDIR%"
if errorlevel 1 goto :error

echo [4/7] Patch stay.par (descriptions, lieux)...
"%PYTHON%" "%~dp0tools\translate_stay_par_complete.py" "%GAMEDIR%"
if errorlevel 1 goto :error

echo [5/7] Patch pause.par (menus de pause)...
"%PYTHON%" "%~dp0tools\translate_pause_par_complete.py" "%GAMEDIR%"
if errorlevel 1 goto :error

echo [6/7] Patch mini-jeux...
"%PYTHON%" "%~dp0tools\translate_all_minigames.py" "%GAMEDIR%"
if errorlevel 1 goto :error

echo [7/7] Verification d'integrite...
"%PYTHON%" "%~dp0tools\verify_patch.py" "%GAMEDIR%"

echo.
echo ========================================================
echo   PATCH INSTALLE AVEC SUCCES !
echo   Bon jeu ! :)
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

README_FR = '''# Yakuza 0 — Patch VOSTFR GOG v1.12.0

## Installation

### Méthode simple (recommandée)
1. Copiez ce dossier dans le répertoire de votre jeu Yakuza 0
2. Double-cliquez sur `patch_fr.bat`
3. Attendez la fin du processus
4. Jouez ! 🎮

### Vérification
- Double-cliquez sur `verifier.bat` pour vérifier l'intégrité du patch

## Contenu
- `patch_fr.bat` — Lance le patcher automatiquement
- `verifier.bat` — Vérifie l'intégrité de tous les fichiers
- `python/` — Python embarqué (aucune installation requise)
- `tools/` — Scripts de traduction

## Notes
- Ce patch est compatible uniquement avec la version GOG de Yakuza 0
- Aucune installation de Python n'est nécessaire
- Le patch ne modifie que les fichiers de texte, pas le moteur du jeu
- En cas de problème, réinstallez le jeu via GOG Galaxy pour restaurer les originaux

## Crédits
- Patch FR par RGG Yakuza Rev / Typhon0
- Basé sur le travail de la communauté francophone Yakuza
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
    print("[1/4] Copie des scripts...")
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
    
    # 2. Download and extract Python embed
    print("[2/4] Python embarqué...")
    zip_path = download_python_embed(RELEASE_DIR)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(os.path.join(stage, "python"))
    print(f"  + Extrait dans {os.path.join(stage, 'python')}")
    
    # 3. Write bat files
    print("[3/4] Création des lanceurs .bat...")
    with open(os.path.join(stage, "patch_fr.bat"), 'w', encoding='utf-8') as f:
        f.write(BAT_PATCHER)
    with open(os.path.join(stage, "verifier.bat"), 'w', encoding='utf-8') as f:
        f.write(BAT_VERIFY)
    with open(os.path.join(stage, "LISEZMOI.txt"), 'w', encoding='utf-8') as f:
        f.write(README_FR)
    
    # 4. Create zip
    print("[4/4] Création du zip...")
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
    print(f"    Contenu: Python embarqué + scripts + lanceurs .bat")
    print(f"    L'utilisateur n'a RIEN à installer.")


if __name__ == '__main__':
    build_release()
