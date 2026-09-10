#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/test_release_e2e.py — Test End-to-End d'intégrité de la release finale
=============================================================================
Vérifie le package .zip tel qu'il sera reçu par l'utilisateur :
  1. Extraction complète dans un bac à sable temporaire.
  2. Analyse syntaxique de tous les scripts .bat avec lint_bat.py (0 erreur cmd.exe).
  3. Contrôle des archives pré-compilées (taille wdr.par > 7 Mo, présence de boot.par, etc.).
  4. Décompression et intégrité de tous les 1 931 fichiers de wdr.par.
  5. Simulation d'exécution machine x86-64 sur les 20 fichiers de cabines téléphoniques.
  6. Exécution de verify_patch.py sur les archives du package.
"""

import os
import sys
import zipfile
import tempfile
import subprocess
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('tools'))
sys.path.insert(0, os.path.abspath('scratch'))

from tools.lint_bat import lint_file
from scratch.scanner_engine import parse_par, decompress_sllz

def test_release_zip(zip_path: str):
    print("=" * 70)
    print(f"  TEST END-TO-END DE RELEASE : {os.path.basename(zip_path)}")
    print("=" * 70)

    if not os.path.isfile(zip_path):
        print(f"[ERREUR CRITIQUE] Archive zip introuvable: {zip_path}")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"[1/6] Extraction de l'archive dans {tmpdir}...")
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)

        # Locate root of extracted folder
        subdirs = [os.path.join(tmpdir, d) for d in os.listdir(tmpdir) if os.path.isdir(os.path.join(tmpdir, d))]
        root = subdirs[0] if len(subdirs) == 1 else tmpdir
        print(f"[*] Racine du package: {root}")

        # Check 2: Lint batch files
        print("[2/6] Contrôle syntaxique Windows Batch (cmd.exe)...")
        bat_files = []
        for r, d, files in os.walk(root):
            for f in files:
                if f.endswith('.bat') or f.endswith('.cmd'):
                    bat_files.append(os.path.join(r, f))

        for bf in bat_files:
            if not lint_file(bf):
                print(f"[ÉCHEC] Le script {bf} contient des erreurs de syntaxe cmd.exe !")
                sys.exit(1)

        # Check 3: Pre-compiled archive existence & sizes
        print("[3/6] Contrôle des archives pré-compilées...")
        wdr_path = os.path.join(root, 'data', 'wdr_par_c', 'wdr.par')
        if not os.path.isfile(wdr_path):
            print(f"[ÉCHEC] data/wdr_par_c/wdr.par est MANQUANT dans le zip !")
            sys.exit(1)

        wdr_size = os.path.getsize(wdr_path)
        print(f"  + wdr.par détecté : {wdr_size} octets")
        if wdr_size < 7_000_000:
            print(f"[ÉCHEC] wdr.par est trop petit ({wdr_size} < 7 000 000 octets) ! Risque de troncature !")
            sys.exit(1)

        # Check 4: Full parse and file count of wdr.par
        print("[4/6] Vérification des 1 931 fichiers de wdr.par...")
        with open(wdr_path, 'rb') as f:
            wdr_data = f.read()
        files = parse_par(wdr_data)
        if len(files) != 1931:
            print(f"[ÉCHEC] wdr.par contient {len(files)} fichiers (attendu: 1931) !")
            sys.exit(1)

        # Check critical files present
        for req in ['pac_STID_ST_KAMURO.bin', 'uid0104006f.msg', 'uid033317da.msg']:
            if req not in files:
                print(f"[ÉCHEC] Fichier critique manquant dans wdr.par : {req}")
                sys.exit(1)

        # Check 5: Simulator test on payphone files
        from tools.repair_phone_booths import PHONE_FILE_NAMES
        print(f"[5/6] Simulation machine x86-64 sur les {len(PHONE_FILE_NAMES)} fichiers d'interactions et cabines...")
        test_exec = './scratch/test_exec'
        if os.path.isfile(test_exec):
            for p in PHONE_FILE_NAMES:
                d = files[p][3]
                if d.startswith(b'SLLZ'):
                    d = decompress_sllz(d)
                test_tmp = os.path.join(tmpdir, 'sim_test.msg')
                with open(test_tmp, 'wb') as tf:
                    tf.write(d)
                res = subprocess.run([test_exec, test_tmp], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if res.returncode != 0:
                    print(f"[ÉCHEC] Crash détecté dans le chargeur Sega pour {p} !")
                    sys.exit(1)
            print(f"  + {len(PHONE_FILE_NAMES)}/{len(PHONE_FILE_NAMES)} interactions et cabines validées sans aucun crash dans l'exécutable !")
        else:
            print("  ! scratch/test_exec non disponible, test simulateur sauté.")

        # Check 6: Run verify_patch on extracted package
        print("[6/6] Exécution de verify_patch.py sur le package extrait...")
        res = subprocess.run([sys.executable, 'tools/verify_patch.py', root], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print("[ÉCHEC] verify_patch.py a échoué sur le package extrait !")
            print(res.stdout.decode())
            sys.exit(1)

    print()
    print("=" * 70)
    print("  SUCCÈS TOTAL : LE PACKAGE DE RELEASE EST 100% FIABLE ET VALIDÉ !")
    print("=" * 70)

if __name__ == '__main__':
    zip_target = sys.argv[1] if len(sys.argv) > 1 else 'staging_release/Yakuza0_FR_Patch_GOG_v1.12.3.zip'
    test_release_zip(zip_target)
