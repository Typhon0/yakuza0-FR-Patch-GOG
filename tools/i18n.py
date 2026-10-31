#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/i18n.py
--------------
Unified CLI tool for Yakuza 0 GOG French translation management:
  - extract:  Extracts legacy Python dictionaries into modular YAML catalogs.
  - validate: Lints YAML catalogs against Sega font tables and engine constraints.
  - compile:  Compiles YAML catalogs into backwards-compatible Python modules.
  - status:   Displays translation statistics and completion rates by domain.

Par Typhon0 (basé sur les traductions initiales de RGG FR).
"""

import os
import sys
import argparse
from typing import Dict, List, Tuple

# Ensure tools/ is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from console_ui import (
    Colors,
    print_banner,
    card_start,
    card_line,
    card_end,
    format_progress,
)
from i18n_validator import validate_catalog_file
from i18n_extractor import extract_all
from i18n_compiler import compile_all, load_catalog_file


def cmd_extract(args: argparse.Namespace) -> int:
    print_banner(version="i18n-v1.0")
    card_start("EXTRACTION DES CATALOGUES DE TRADUCTION")
    card_line(f"Dossier cible : {args.out}", status="info")

    results = extract_all(target_dir=args.out)

    for domain, count in results.items():
        if isinstance(count, int):
            card_line(f"Domaine {domain:<18} : {count:>5} entrées extraites", status="ok")
        else:
            card_line(f"Erreur domaine {domain} : {count}", status="err")

    total = sum(v for v in results.values() if isinstance(v, int))
    card_line(f"Total entrées cataloguées : {total}", status="ok")
    card_end()
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    print_banner(version="i18n-v1.0")
    card_start("VALIDATION DES CATALOGUES (LINTING)")
    card_line(f"Vérification du dossier : {args.dir}", status="info")

    if not os.path.isdir(args.dir):
        card_line(f"Dossier introuvable : {args.dir}", status="err")
        card_end()
        return 1

    yaml_files = []
    for root, _, files in os.walk(args.dir):
        for f in sorted(files):
            if f.endswith(".yaml") or f.endswith(".yml"):
                yaml_files.append(os.path.join(root, f))

    if not yaml_files:
        card_line("Aucun fichier YAML trouvé dans le dossier.", status="warn")
        card_end()
        return 0

    total_valid = 0
    total_errors = []

    for file_path in yaml_files:
        rel_path = os.path.relpath(file_path, args.dir)
        count, errors = validate_catalog_file(file_path)
        total_valid += count
        if errors:
            total_errors.extend(errors)
            card_line(f"{rel_path:<36} : {len(errors)} erreur(s)", status="err")
        else:
            card_line(f"{rel_path:<36} : {count:>5} entrées conformes", status="ok")

    if total_errors:
        card_line(f"Total : {len(total_errors)} erreur(s) détectée(s)", status="err")
        card_end()
        print(f"\n{Colors.RED}{Colors.BOLD}Détails des erreurs :{Colors.RESET}")
        for err in total_errors[:15]:
            print(f"  {Colors.YELLOW}•{Colors.RESET} {err}")
        if len(total_errors) > 15:
            print(f"  ... et {len(total_errors) - 15} autres erreurs.")
        return 1
    else:
        card_line(f"Validation réussie : {total_valid} entrées certifiées", status="ok")
        card_end()
        return 0


def cmd_compile(args: argparse.Namespace) -> int:
    print_banner(version="i18n-v1.0")
    card_start("COMPILATION DES CATALOGUES VERS PYTHON")
    card_line(f"Source : {args.dir} -> Destination : {args.out}", status="info")

    if not os.path.isdir(args.dir):
        card_line(f"Dossier source introuvable : {args.dir}", status="err")
        card_end()
        return 1

    try:
        results = compile_all(translations_dir=args.dir, output_tools_dir=args.out)
    except Exception as e:
        card_line(f"Échec de la compilation : {e}", status="err")
        card_end()
        return 1

    for mod_name, count in results.items():
        card_line(f"Généré {mod_name:<28} : {count:>5} entrées", status="ok")

    card_line("Tous les modules Python ont été synchronisés avec succès", status="ok")
    card_end()
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    print_banner(version="i18n-v1.0")
    card_start("STATUT ET COUVERTURE DES TRADUCTIONS")

    if not os.path.isdir(args.dir):
        card_line(f"Dossier introuvable : {args.dir}", status="err")
        card_end()
        return 1

    yaml_files = []
    for root, _, files in os.walk(args.dir):
        for f in sorted(files):
            if f.endswith(".yaml") or f.endswith(".yml"):
                yaml_files.append(os.path.join(root, f))

    if not yaml_files:
        card_line("Aucun catalogue trouvé. Lancez 'python3 tools/i18n.py extract' d'abord.", status="warn")
        card_end()
        return 0

    total_strings = 0
    total_translated = 0
    total_words_fr = 0

    for file_path in yaml_files:
        domain_name = os.path.relpath(file_path, args.dir)
        try:
            entries = load_catalog_file(file_path, validate=False)
        except Exception:
            continue

        file_total = len(entries)
        file_translated = 0
        file_words = 0

        for e in entries:
            fr = e.get("fr", "").strip()
            if fr:
                file_translated += 1
                file_words += len(fr.split())

        total_strings += file_total
        total_translated += file_translated
        total_words_fr += file_words

        bar = format_progress(file_translated, file_total, width=14)
        line = f"{domain_name:<30} {bar} ({file_translated:>4}/{file_total:>4})"
        status = "ok" if file_translated == file_total else "warn"
        card_line(line, status=status)

    pct_global = (total_translated / total_strings * 100) if total_strings > 0 else 100.0
    card_line(f"Total global : {total_translated}/{total_strings} ({pct_global:.1f}%) — {total_words_fr} mots", status="info")
    card_end()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Yakuza 0 GOG - Outil de gestion unifié des traductions (i18n)"
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Commandes disponibles")

    # extract
    p_extract = subparsers.add_parser("extract", help="Extrait les dictionnaires Python existants vers YAML")
    p_extract.add_argument("--out", default="translations", help="Dossier de destination (défaut: translations)")

    # validate / lint
    p_val = subparsers.add_parser("validate", aliases=["lint"], help="Valide la conformité des fichiers YAML")
    p_val.add_argument("--dir", default="translations", help="Dossier des catalogues (défaut: translations)")

    # compile
    p_comp = subparsers.add_parser("compile", help="Compile les fichiers YAML vers les modules Python")
    p_comp.add_argument("--dir", default="translations", help="Dossier source des catalogues (défaut: translations)")
    p_comp.add_argument("--out", default="tools", help="Dossier de destination des modules (défaut: tools)")

    # status
    p_stat = subparsers.add_parser("status", help="Affiche les statistiques de complétion")
    p_stat.add_argument("--dir", default="translations", help="Dossier des catalogues (défaut: translations)")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        return 0

    if args.subcommand == "extract":
        return cmd_extract(args)
    elif args.subcommand in ("validate", "lint"):
        return cmd_validate(args)
    elif args.subcommand == "compile":
        return cmd_compile(args)
    elif args.subcommand == "status":
        return cmd_status(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
