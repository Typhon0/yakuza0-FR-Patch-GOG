#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/collect_originals.py

Script de collecte et diagnostic pour Yakuza 0 GOG.
Collecte l'ensemble des fichiers nécessaires pour analyse :
  1. Archives de jeu et sauvegardes originales (.bak et .par) :
     - wdr.par et wdr.par.bak
     - common.par et common.par.bak
     - boot.par et boot.par.bak
     - stay.par et stay.par.bak
  2. Tous les crash logs et rapports d'erreurs récents (Special K, dxgi, etc.)
  3. L'exécutable Yakuza0.exe et/ou Yakuza0.exe.bak (ou ses métadonnées/en-têtes)
  4. Un manifeste complet de sommes de contrôle (MD5 + tailles) de toutes les archives .par du jeu.

Le tout est compressé dans une archive ZIP unique : yakuza0_diagnostics.zip
"""

import os
import sys
import zipfile
import hashlib
import json
import shutil
from datetime import datetime

def compute_md5(filepath, chunk_size=65536):
    h = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def find_game_dir(start_dir):
    candidates = [
        start_dir,
        os.path.join(start_dir, '..'),
        os.path.join(start_dir, '..', '..'),
        r"D:\GOG Games\Yakuza 0",
        r"C:\GOG Games\Yakuza 0",
        r"C:\Program Files (x86)\GOG Galaxy\Games\Yakuza 0",
        r"D:\Games\Yakuza 0",
    ]
    # Strict check: locate directory containing Yakuza0.exe
    for c in candidates:
        if os.path.isfile(os.path.join(c, 'Yakuza0.exe')):
            return os.path.abspath(c)
    return None

def collect_diagnostics(game_dir, output_zip_path=None):
    if output_zip_path is None:
        output_zip_path = os.path.join(game_dir, "yakuza0_diagnostics.zip")

    print("======================================================================")
    print("  COLLECTEUR DE DIAGNOSTIC ET ARCHIVES ORIGINALES — Yakuza 0 GOG")
    print("======================================================================")
    print(f"[*] Dossier du jeu détecté : {game_dir}")
    print(f"[*] Destination du ZIP     : {output_zip_path}")
    print()

    data_dir = os.path.join(game_dir, "data")
    if not os.path.isdir(data_dir):
        print(f"[ERREUR] Le sous-dossier 'data' est introuvable dans {game_dir}")
        sys.exit(1)

    collected_files = []
    
    # 1. Collecter tous les crash logs
    print("[1/4] Recherche des crash logs et rapports d'erreur...")
    crash_log_names = ['crash.log', 'dxgi.log', 'd3d11.log', 'SpecialK.log', 'game_output.log', 'modules.log']
    for root, dirs, files in os.walk(game_dir):
        # Ne pas fouiller dans python\ ou d'éventuels dossiers de backup externes
        if 'python' in root or '.git' in root:
            continue
        for f in files:
            lower = f.lower()
            if lower in crash_log_names or 'crash' in lower and lower.endswith('.log'):
                full_path = os.path.join(root, f)
                arc_name = os.path.join("crash_logs", os.path.relpath(full_path, game_dir))
                collected_files.append((full_path, arc_name))
                print(f"  + Trouvé : {arc_name} ({os.path.getsize(full_path)} octets)")

    # 2. Collecter les archives .bak (sauvegardes originales avant patch)
    print("\n[2/4] Recherche des sauvegardes originales (*.bak)...")
    bak_count = 0
    for root, dirs, files in os.walk(game_dir):
        if 'python' in root or '.git' in root:
            continue
        for f in files:
            if f.endswith('.bak'):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, game_dir)
                arc_name = os.path.join("backups_originaux", rel_path)
                collected_files.append((full_path, arc_name))
                bak_count += 1
                print(f"  + Trouvé : {rel_path} ({os.path.getsize(full_path)} octets)")

    if bak_count == 0:
        print("  ! Aucun fichier .bak trouvé (la sauvegarde originale n'a pas été créée ou a été écrasée).")

    # 3. Collecter les archives cibles actives actuelles
    print("\n[3/4] Collecte des archives clés actives...")
    target_archives = [
        os.path.join("data", "wdr_par_c", "wdr.par"),
        os.path.join("data", "wdr_par_c", "common.par"),
        os.path.join("data", "bootpar", "boot.par"),
        os.path.join("data", "staypar", "stay.par"),
    ]
    for rel_path in target_archives:
        full_path = os.path.join(game_dir, rel_path)
        if os.path.isfile(full_path):
            arc_name = os.path.join("current_active_par", rel_path)
            collected_files.append((full_path, arc_name))
            print(f"  + Inclus : {rel_path} ({os.path.getsize(full_path)} octets)")

    # 4. Manifeste d'intégrité de toutes les archives .par
    print("\n[4/4] Analyse d'intégrité de toutes les archives du jeu...")
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "game_dir": game_dir,
        "files": {}
    }
    
    total_par = 0
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            if f.endswith('.par'):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, game_dir)
                sz = os.path.getsize(full_path)
                # Calcule MD5 pour les archives principales et un échantillon des autres
                is_key = any(k in rel_path.replace('\\', '/') for k in ['wdr_par_c', 'bootpar', 'staypar', 'pausepar_e', '2dpar'])
                md5 = compute_md5(full_path) if is_key or total_par < 50 else None
                manifest["files"][rel_path] = {
                    "size": sz,
                    "md5": md5
                }
                total_par += 1

    print(f"  + {total_par} archives .par indexées dans le manifeste.")

    # Vérification de Yakuza0.exe
    exe_path = os.path.join(game_dir, "Yakuza0.exe")
    if os.path.isfile(exe_path):
        manifest["exe_info"] = {
            "size": os.path.getsize(exe_path),
            "md5": compute_md5(exe_path)
        }
        print(f"  + Yakuza0.exe : {os.path.getsize(exe_path)} octets (MD5: {manifest['exe_info']['md5']})")

    manifest_json = json.dumps(manifest, indent=2)

    # 5. Création de l'archive ZIP
    print(f"\n[*] Compression de {len(collected_files)} fichiers dans {output_zip_path}...")
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        # Écriture du manifeste
        zipf.writestr("manifeste_systeme.json", manifest_json)
        
        # Écriture de chaque fichier
        for full_path, arc_name in collected_files:
            try:
                zipf.write(full_path, arc_name)
            except Exception as e:
                print(f"  [AVERTISSEMENT] Impossible d'ajouter {full_path}: {e}")

    zip_size_mb = os.path.getsize(output_zip_path) / (1024 * 1024)
    print("======================================================================")
    print("  COLLECTE TERMINÉE AVEC SUCCÈS !")
    print("======================================================================")
    print(f"[*] Fichier généré : {output_zip_path} ({zip_size_mb:.2f} Mo)")
    print()
    print("Vous pouvez maintenant envoyer ce fichier 'yakuza0_diagnostics.zip' pour analyse.")
    print("======================================================================")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else find_game_dir(os.getcwd())
    if not target or not os.path.isfile(os.path.join(target, 'Yakuza0.exe')):
        print(f"[ERREUR] Impossible de trouver Yakuza0.exe dans '{target or 'aucun dossier'}'")
        print("Veuillez specifier le chemin du repertoire d'installation du jeu Yakuza 0 :")
        print("  python collect_originals.py \"D:\\GOG Games\\Yakuza 0\"")
        sys.exit(1)
    collect_diagnostics(target)
