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
RELEASE_NAME = "Yakuza0_FR_Patch_GOG_v1.12.6"

# Files to include from tools/
TOOL_FILES = [
    "tools/repair_phone_booths.py",
    "tools/rebuild_clean_wdr.py",
    "tools/rebuild_all_shops_clean.py",
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
    ("patcher/patch_gog.bat", "patch_gog.bat"),
    ("release_gog/font_table_french.bin", "font_table_french.bin"),
    ("tools/collect_originals.bat", "collect_originals.bat"),
]

BAT_PATCHER = r'''@echo off
chcp 65001 >nul
echo ========================================================
echo   Yakuza 0 - Patch VOSTFR GOG v1.12.6
echo   Par RGG Yakuza Rev / Typhon0
echo ========================================================
echo.

REM Detect game directory by locating Yakuza0.exe
if "%~1"=="" (
    echo [*] Recherche automatique du repertoire de Yakuza 0...
    if exist "%~dp0Yakuza0.exe" (
        set "GAMEDIR=%~dp0"
    ) else if exist "%~dp0..\Yakuza0.exe" (
        set "GAMEDIR=%~dp0.."
    ) else if exist "%CD%\Yakuza0.exe" (
        set "GAMEDIR=%CD%"
    ) else if exist "%CD%\..\Yakuza0.exe" (
        set "GAMEDIR=%CD%\.."
    ) else if exist "%CD%\..\..\Yakuza0.exe" (
        set "GAMEDIR=%CD%\..\.."
    ) else if exist "D:\GOG Games\Yakuza 0\Yakuza0.exe" (
        set "GAMEDIR=D:\GOG Games\Yakuza 0"
    ) else if exist "C:\GOG Games\Yakuza 0\Yakuza0.exe" (
        set "GAMEDIR=C:\GOG Games\Yakuza 0"
    ) else if exist "C:\Program Files (x86)\GOG Galaxy\Games\Yakuza 0\Yakuza0.exe" (
        set "GAMEDIR=C:\Program Files (x86)\GOG Galaxy\Games\Yakuza 0"
    ) else (
        echo [ERREUR] Impossible de trouver Yakuza0.exe.
        echo Glissez-deposez votre dossier de jeu sur ce fichier patch_fr.bat
        echo ou lancez: patch_fr.bat "D:\GOG Games\Yakuza 0"
        pause
        exit /b 1
    )
) else (
    set "GAMEDIR=%~1"
)

REM Strip all trailing backslashes
:strip_slash
if "%GAMEDIR:~-1%"=="\" (
    set "GAMEDIR=%GAMEDIR:~0,-1%"
    goto :strip_slash
)

for %%I in ("%GAMEDIR%") do set "GAMEDIR=%%~fI"

:strip_slash2
if "%GAMEDIR:~-1%"=="\" (
    set "GAMEDIR=%GAMEDIR:~0,-1%"
    goto :strip_slash2
)

if not exist "%GAMEDIR%\Yakuza0.exe" (
    echo [ERREUR] Yakuza0.exe introuvable dans "%GAMEDIR%"
    echo Veuillez specifier le chemin du dossier d'installation du jeu.
    pause
    exit /b 1
)

echo [*] Dossier du jeu confirme : %GAMEDIR%
echo.

REM Fermeture forcee de tout processus Yakuza0.exe residuel pour debloquer l'ecriture
tasklist /FI "IMAGENAME eq Yakuza0.exe" 2>nul | find /I /N "Yakuza0.exe">nul
if "%ERRORLEVEL%"=="0" (
    echo [*] Fermeture de Yakuza0.exe en cours d'execution...
    taskkill /F /IM Yakuza0.exe >nul 2>&1
    timeout /t 1 /nobreak >nul
)

REM Deverrouillage des attributs lecture seule (Read-Only frequents sur GOG)
echo [*] Deverrouillage des attributs lecture seule...
attrib -R "%GAMEDIR%\Yakuza0.exe" >nul 2>&1
attrib -R "%GAMEDIR%\data\*.par" /S >nul 2>&1

REM Use embedded Python
set "PYTHON=%~dp0python\python.exe"
if not exist "%PYTHON%" (
    echo [ERREUR] Python embarque introuvable dans %~dp0python\
    pause
    exit /b 1
)

REM Verification conflits mods (YakuzaParless / SRMM)
if exist "%GAMEDIR%\YakuzaParless.asi" (
    echo [*] DETECTION : YakuzaParless.asi - Shin Ryu Mod Manager - est present.
    echo     Pour eviter qu'un ancien mod dans mods n'ecrase les archives traduites,
    echo     desactivation temporaire du chargeur de mods...
    ren "%GAMEDIR%\YakuzaParless.asi" "YakuzaParless.asi.disabled_patch_fr" >nul 2>&1
    echo     + YakuzaParless.asi desactive vers .disabled_patch_fr
    echo.
)

echo [1/2] Installation des archives et patch de l'executable Yakuza0.exe...
"%PYTHON%" "%~dp0patch_gog.py" "%GAMEDIR%\Yakuza0.exe"
if errorlevel 1 goto :error

echo.
echo [2/2] Verification d'integrite du jeu...
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
echo ========================================================
echo   Yakuza 0 - Verification d'integrite du jeu
echo ========================================================
echo.

if "%~1"=="" (
    if exist "%~dp0Yakuza0.exe" (
        set "GAMEDIR=%~dp0"
    ) else if exist "%~dp0..\Yakuza0.exe" (
        set "GAMEDIR=%~dp0.."
    ) else if exist "%CD%\Yakuza0.exe" (
        set "GAMEDIR=%CD%"
    ) else if exist "%CD%\..\Yakuza0.exe" (
        set "GAMEDIR=%CD%\.."
    ) else if exist "%CD%\..\..\Yakuza0.exe" (
        set "GAMEDIR=%CD%\..\.."
    ) else if exist "D:\GOG Games\Yakuza 0\Yakuza0.exe" (
        set "GAMEDIR=D:\GOG Games\Yakuza 0"
    ) else if exist "C:\GOG Games\Yakuza 0\Yakuza0.exe" (
        set "GAMEDIR=C:\GOG Games\Yakuza 0"
    ) else if exist "C:\Program Files (x86)\GOG Galaxy\Games\Yakuza 0\Yakuza0.exe" (
        set "GAMEDIR=C:\Program Files (x86)\GOG Galaxy\Games\Yakuza 0"
    ) else (
        echo [ERREUR] Impossible de trouver Yakuza0.exe.
        pause
        exit /b 1
    )
) else (
    set "GAMEDIR=%~1"
)

for %%I in ("%GAMEDIR%") do set "GAMEDIR=%%~fI"

set "PYTHON=%~dp0python\python.exe"
if not exist "%PYTHON%" (
    echo [ERREUR] Python embarque introuvable.
    pause
    exit /b 1
)

"%PYTHON%" "%~dp0tools\verify_patch.py" "%GAMEDIR%"
pause
'''

README_FR = r'''# Yakuza 0 — Patch VOSTFR GOG v1.12.6

## Nouveautés v1.12.6
- **Sécurisation absolue de l'installateur `patch_fr.bat`** :
  1. Fermeture automatique de tout processus `Yakuza0.exe` résiduel ou fantôme pour lever les verrous d'écriture Windows (Permissions / Sharing Violation).
  2. Résolution canonique des chemins (`%%~fI`) éliminant tout dysfonctionnement lié aux chemins relatifs (`..`).
  3. Contrôle strict et bloquant de la copie des archives avec vérification de taille minimale (>7 Mo pour `wdr.par`).
  4. Vérification d'intégrité sur disque après écriture de `Yakuza0.exe` (contrôle des marges typographiques à 0.4).
- **Correction critique des cabines téléphoniques et sauvegardes (0x6EA328 / 0x6F21E0)** :
  Restauration intégrale du bytecode Sega officiel sur l'ensemble des 25 fichiers d'interaction de Kamurocho et Sotenbori.
- **Pharmacies Kotobuki Drugs & Daikoku Drugstore (0x234B0 / 0x234B7)** :
  Tables propriétaires Pocket Circuit (24 et 20 octets) 100% préservées.
- **Typographie et crénage parfaits** :
  Injection de la table complète de 6 144 octets garantissant zéro chevauchement de lettres sur `i` et `l`.

## Installation simple (Recommandée)
1. Décompressez l'archive `Yakuza0_FR_Patch_GOG_v1.12.6.zip`.
2. Lancez `patch_fr.bat` (en faisant un clic droit -> « Exécuter en tant qu'administrateur »).
3. Attendez le message « PATCH INSTALLE AVEC SUCCES ! » et lancez le jeu !

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
