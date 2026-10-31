# -*- coding: utf-8 -*-
"""
tools/i18n_validator.py
-----------------------
Validates translation catalogs (YAML/JSON) for Yakuza 0 GOG FR Patch.
Enforces:
  1. Font character set compatibility (0xD488F0 single-byte font table).
  2. Game engine length and padding constraints (Golden Rule 2: Phone booths 58 ASCII chars, Bob Utsunomiya).
  3. Proper schema consistency across translation domains.
"""

import os
import sys
from typing import Dict, List, Tuple, Any, Optional

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False
    import json

# Extended French characters mapped in font_table_french.bin (0x80 - 0xFF)
# and verified in-game texts.
SUPPORTED_EXTENDED_CHARS = set(
    "éèêëàâäçîïôöùûüÉÈÊËÀÂÄÇÎÏÔÖÙÛÜ«»°¥ò„†‡¸¼½"
)

# Common forbidden Unicode characters that must be converted or avoided
FORBIDDEN_CHAR_REPLACEMENTS = {
    '…': '...',
    '’': "'",
    '‘': "'",
    '“': '"',
    '”': '"',
    '—': '-',
    '–': '-',
    '\xa0': ' ',  # non-breaking space
    'œ': 'oe',
    'Œ': 'OE',
}


def is_char_supported_by_font(char: str) -> bool:
    """
    Checks if a character is supported by the Yakuza 0 GOG single-byte rendering engine:
      - Standard ASCII printable (0x20 to 0x7E)
      - Control characters: \\n, \\r, \\t
      - Verified French extended characters mapped in font_table_french.bin
    """
    if len(char) != 1:
        return False

    code = ord(char)
    # Basic ASCII printable & standard whitespace
    if (0x20 <= code <= 0x7E) or char in ('\n', '\r', '\t'):
        return True

    # Extended French font table characters
    if char in SUPPORTED_EXTENDED_CHARS:
        return True

    return False


def validate_text_chars(text: str) -> Tuple[bool, List[str]]:
    """
    Checks all characters in a text string.
    Returns (is_valid, list_of_unsupported_chars).
    """
    if not text:
        return True, []

    unsupported = []
    for c in text:
        if not is_char_supported_by_font(c) and c not in unsupported:
            unsupported.append(c)

    return (len(unsupported) == 0), unsupported


def validate_catalog_entry(entry: Dict[str, Any], domain: str = "") -> List[str]:
    """
    Validates a single catalog entry against the schema and engine rules.
    Returns a list of error descriptions (empty list if entry is completely valid).
    """
    errors: List[str] = []

    # 1. Schema check
    entry_id = entry.get("id")
    if not entry_id:
        errors.append("Entry missing required field 'id'")

    if "en" not in entry:
        errors.append(f"Entry '{entry_id}' missing required field 'en'")

    if "fr" not in entry:
        errors.append(f"Entry '{entry_id}' missing required field 'fr'")
        return errors  # Cannot validate further without 'fr'

    fr_text = entry.get("fr", "")
    en_text = entry.get("en", "")

    # 2. Character set validation
    ok, bad_chars = validate_text_chars(fr_text)
    if not ok:
        bad_summary = ", ".join(f"'{c}' (U+{ord(c):04X})" for c in bad_chars)
        errors.append(f"Entry '{entry_id}' contains unsupported character(s) not in font table: {bad_summary}")

    # 3. ASCII-only constraint (Golden Rule 2: Cabines de sauvegarde)
    if entry.get("ascii_only", False):
        non_ascii = [c for c in fr_text if ord(c) >= 128]
        if non_ascii:
            bad_summary = ", ".join(f"'{c}' (U+{ord(c):04X})" for c in set(non_ascii))
            errors.append(
                f"Entry '{entry_id}' violates ascii_only constraint with accented/multi-byte chars: {bad_summary}. "
                "Multi-byte UTF-8 breaks Sega typewriter length counter (0x140396783) and causes softlock."
            )

    # 4. Exact length constraint (Golden Rule 2)
    if "exact_len" in entry:
        expected_len = int(entry["exact_len"])
        actual_len = len(fr_text)
        if actual_len != expected_len:
            errors.append(
                f"Entry '{entry_id}' has exact_len={expected_len} but actual length is {actual_len} "
                f"(diff: {actual_len - expected_len:+d})"
            )

    # 5. Max length constraint
    if "max_len" in entry:
        max_len = int(entry["max_len"])
        actual_len = len(fr_text)
        if actual_len > max_len:
            errors.append(
                f"Entry '{entry_id}' exceeds max_len={max_len} (actual length: {actual_len})"
            )

    # 6. Null padding check in dialogues (Golden Rule 2: Bob Utsunomiya)
    if "\x00" in fr_text and not entry.get("allow_null_padding", False):
        errors.append(
            f"Entry '{entry_id}' contains null-byte (\\x00). Null-padding in dialogue strings cuts execution "
            "and causes softlock. Use space-padding (' ') instead."
        )

    return errors


def validate_catalog_file(file_path: str) -> Tuple[int, List[str]]:
    """
    Reads a YAML/JSON catalog file and validates every entry.
    Returns (valid_entries_count, error_list).
    """
    if not os.path.isfile(file_path):
        return 0, [f"File not found: {file_path}"]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if HAVE_YAML and (file_path.endswith(".yaml") or file_path.endswith(".yml")):
                data = yaml.safe_load(f)
            else:
                import json
                data = json.load(f)
    except Exception as e:
        return 0, [f"Failed to parse {file_path}: {e}"]

    if not isinstance(data, dict):
        return 0, [f"Root of {file_path} must be a dictionary"]

    domain = data.get("domain", "")
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        return 0, [f"'entries' in {file_path} must be a list"]

    all_errors: List[str] = []
    valid_count = 0

    seen_ids = set()
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            all_errors.append(f"Entry at index {idx} in {file_path} is not a dictionary")
            continue

        entry_id = entry.get("id")
        if entry_id in seen_ids:
            all_errors.append(f"Duplicate entry id '{entry_id}' at index {idx} in {file_path}")
        elif entry_id:
            seen_ids.add(entry_id)

        entry_errors = validate_catalog_entry(entry, domain=domain)
        if entry_errors:
            all_errors.extend(f"{os.path.basename(file_path)}: {err}" for err in entry_errors)
        else:
            valid_count += 1

    return valid_count, all_errors
