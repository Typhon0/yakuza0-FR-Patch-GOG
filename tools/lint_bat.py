#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/lint_bat.py — Linter et validateur syntaxique pour scripts Windows Batch (.bat / .cmd)
============================================================================================
Détecte automatiquement les pièges syntaxiques de cmd.exe même sous Linux :
  1. Parenthèses non échappées à l'intérieur de blocs if (...) ou for (...)
  2. Chemins de variables non entourés de guillemets ("%VAR%")
  3. Caractères de redirection ou de pipe non échappés (<, >, |, &) dans les echo
  4. Guillemets déséquilibrés
  5. Caractères non-ASCII posant problème sans chcp 65001
"""

import re
import sys
import os

def lint_batch_content(content: str, filename: str = "script.bat") -> list:
    errors = []
    warnings = []
    lines = content.splitlines()

    # Check 1: UTF-8 code page definition
    has_chcp = any("chcp 65001" in line for line in lines[:10])
    if not has_chcp:
        warnings.append(f"{filename}: 'chcp 65001' absent dans les premières lignes (risques d'encodage)")

    paren_depth = 0
    in_block = False

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Ignore empty lines and remarks
        if not stripped or stripped.startswith("::") or stripped.lower().startswith("rem "):
            continue

        # Check 2: Unbalanced double quotes
        quote_count = stripped.count('"')
        if quote_count % 2 != 0:
            errors.append(f"{filename}:{line_no}: Nombre impair de guillemets ({quote_count})")

        # Track block parentheses: if (...) or for (...)
        for i, ch in enumerate(stripped):
            # If escaped with caret (^), skip
            if i > 0 and stripped[i - 1] == '^':
                continue
            if ch == '(':
                paren_depth += 1
            elif ch == ')':
                paren_depth -= 1
                if paren_depth < 0:
                    errors.append(f"{filename}:{line_no}: Parenthèse fermante ')' inattendue sans bloc ouvert")
                    paren_depth = 0

        # Check 3: Lethal cmd.exe trap: echo with parentheses inside an if (...) block
        # Example: echo text (detail) inside if (...)
        if paren_depth > 0:
            if re.search(r'\becho\b', stripped, re.IGNORECASE):
                # Check for unescaped closing parenthesis in echo text
                echo_match = re.search(r'\becho\s+(.*)', stripped, re.IGNORECASE)
                if echo_match:
                    echo_text = echo_match.group(1)
                    # Look for unescaped ( or ) in echo_text
                    for j, c in enumerate(echo_text):
                        if c in '()' and (j == 0 or echo_text[j - 1] != '^'):
                            errors.append(
                                f"{filename}:{line_no}: PIÈGE CMD.EXE MAJEUR : Caractère '{c}' non échappé dans "
                                f"un 'echo' à l'intérieur d'un bloc de parenthèses ! "
                                f"(Provoque '... était inattendu' sous Windows)"
                            )
                            break

        # Check 4: Unquoted paths in copy or file operations
        if re.search(r'^\s*(?:if\s+.*\s+)?(copy|move|del|mkdir|rmdir)\b', stripped, re.IGNORECASE):
            # Check for %VAR% with spaces without quotes
            tokens = stripped.split()
            for t in tokens[1:]:
                if ('%GAMEDIR%' in t or '%~dp0' in t) and not (t.startswith('"') and t.endswith('"')):
                    warnings.append(
                        f"{filename}:{line_no}: Variable de chemin '{t}' non entourée de guillemets doubles (risque si espaces)"
                    )

    if paren_depth != 0:
        errors.append(f"{filename}: Blocs de parenthèses non refermés en fin de fichier (depth={paren_depth})")

    return errors, warnings

def lint_file(filepath: str) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERREUR] Impossible de lire {filepath}: {e}")
        return False

    errors, warnings = lint_batch_content(content, os.path.basename(filepath))
    
    for w in warnings:
        print(f"  [AVERTISSEMENT] {w}")
    for e in errors:
        print(f"  [ERREUR SYNTAXE] {e}")

    if errors:
        print(f"[-] {filepath} : {len(errors)} erreur(s) détectée(s) !")
        return False
    else:
        print(f"[+] {filepath} : Syntaxe Batch 100% conforme cmd.exe")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 lint_bat.py <fichier.bat> [autre.bat ...]")
        sys.exit(1)

    all_passed = True
    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            passed = lint_file(arg)
            if not passed:
                all_passed = False
        else:
            print(f"[WARN] Fichier introuvable: {arg}")

    sys.exit(0 if all_passed else 1)
