# -*- coding: utf-8 -*-
"""
tools/i18n_compiler.py
-----------------------
Compiles translation YAML catalogs into bit-compatible, verified Python data modules
for the Yakuza 0 GOG patch build pipeline.
"""

import os
import sys
import pprint
from typing import Dict, List, Tuple, Any, Optional

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False
    import json

from tools.i18n_validator import validate_catalog_file, validate_catalog_entry


def load_catalog_file(file_path: str, validate: bool = True) -> List[Dict[str, Any]]:
    """Loads a catalog YAML/JSON file and returns the list of entries."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Catalog file not found: {file_path}")

    if validate:
        count, errors = validate_catalog_file(file_path)
        if errors:
            raise ValueError(f"Catalog validation failed with {len(errors)} error(s):\n" + "\n".join(errors[:5]))

    with open(file_path, "r", encoding="utf-8") as f:
        if HAVE_YAML and (file_path.endswith(".yaml") or file_path.endswith(".yml")):
            data = yaml.safe_load(f)
        else:
            import json
            data = json.load(f)

    return data.get("entries", [])


def format_python_repr(text: str) -> str:
    """Formats a python string representation with clean multiline or raw quotes."""
    return repr(text)


def compile_shops(catalog_path: str, output_path: str) -> bool:
    """
    Compiles shops YAML catalog into tools/shop_translations_data.py.
    Preserves exact (shop_file, slot_idx): (item_id, fr_desc) dictionary format.
    """
    entries = load_catalog_file(catalog_path, validate=True)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    lines = [
        "# -*- coding: utf-8 -*-",
        '"""',
        "tools/shop_translations_data.py",
        "-------------------------------",
        f"Master repository of {len(entries)} verified French item descriptions across all shop files.",
        "Par Typhon0 (basé sur les traductions initiales de RGG FR).",
        "Generated automatically from translations/shops/items.yaml by tools/i18n.py.",
        '"""',
        "",
        "SHOP_ITEM_TRANSLATIONS = {",
    ]

    for entry in entries:
        shop_file = entry.get("file", "")
        slot = entry.get("slot", 0)
        item_id = entry.get("item_id", 0)
        fr_text = entry.get("fr", "")
        lines.append(f"    ({repr(shop_file)}, {slot}): ({item_id}, {repr(fr_text)}),")

    lines.append("}")
    lines.append("")

    # Also generate ITEM_ID_TRANSLATIONS fallback dictionary required by rebuild_all_shops_clean.py
    item_id_map = {}
    for entry in entries:
        item_id = entry.get("item_id")
        fr_text = entry.get("fr", "")
        if item_id and item_id not in item_id_map:
            item_id_map[item_id] = fr_text

    lines.append("ITEM_ID_TRANSLATIONS = {")
    for item_id in sorted(item_id_map.keys()):
        lines.append(f"    {item_id}: {repr(item_id_map[item_id])},")
    lines.append("}")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return True


def compile_subtitles(catalog_path: str, output_path: str) -> bool:
    """
    Compiles street subtitles catalog into tools/sound_subtitles_data.py.
    Format: SOUND_SUBTITLES = { en: fr, ... }
    """
    entries = load_catalog_file(catalog_path, validate=True)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    lines = [
        "# -*- coding: utf-8 -*-",
        '"""',
        "tools/sound_subtitles_data.py",
        "-------------------------------",
        f"Calibrated French translations for {len(entries)} street voice encounter subtitles (.mfp in sound.par).",
        "Par Typhon0 (basé sur les traductions initiales de RGG FR).",
        "Generated automatically from translations/subtitles/ambient_voices.yaml by tools/i18n.py.",
        '"""',
        "",
        "SOUND_SUBTITLES = {",
    ]

    for entry in entries:
        en_text = entry.get("en", "")
        fr_text = entry.get("fr", "")
        lines.append(f"    {repr(en_text)}: {repr(fr_text)},")

    lines.append("}")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return True


def compile_dict_module(catalog_path: str, output_path: str, dict_var_name: str, docstring: str = "") -> bool:
    """
    Generic compiler for standard en -> fr dictionaries.
    """
    entries = load_catalog_file(catalog_path, validate=True)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    lines = [
        "# -*- coding: utf-8 -*-",
        '"""',
        f"{docstring}",
        "Par Typhon0 (basé sur les traductions initiales de RGG FR).",
        f"Generated automatically from {os.path.basename(catalog_path)} by tools/i18n.py.",
        '"""',
        "",
        f"{dict_var_name} = {{",
    ]

    for entry in entries:
        en_text = entry.get("en", "")
        fr_text = entry.get("fr", "")
        if en_text:
            lines.append(f"    {repr(en_text)}: {repr(fr_text)},")

    lines.append("}")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return True


def compile_all(translations_dir: str = "translations", output_tools_dir: str = "tools") -> Dict[str, int]:
    """
    Compiles all domain catalogs into the corresponding Python modules under tools/.
    Returns a dict of module -> count of compiled entries.
    """
    results: Dict[str, int] = {}

    # 1. Shops
    shops_yaml = os.path.join(translations_dir, "shops", "items.yaml")
    if os.path.isfile(shops_yaml):
        shop_py = os.path.join(output_tools_dir, "shop_translations_data.py")
        compile_shops(shops_yaml, shop_py)
        results["shop_translations_data.py"] = len(load_catalog_file(shops_yaml, validate=False))

    # 2. Subtitles
    subs_yaml = os.path.join(translations_dir, "subtitles", "ambient_voices.yaml")
    if os.path.isfile(subs_yaml):
        sub_py = os.path.join(output_tools_dir, "sound_subtitles_data.py")
        compile_subtitles(subs_yaml, sub_py)
        results["sound_subtitles_data.py"] = len(load_catalog_file(subs_yaml, validate=False))

    # 3. Minigames & Cabaret (stay_translations_data.py)
    stay_yaml = os.path.join(translations_dir, "minigames", "cabaret_and_tiger.yaml")
    if os.path.isfile(stay_yaml):
        stay_py = os.path.join(output_tools_dir, "stay_translations_data.py")
        compile_dict_module(
            stay_yaml,
            stay_py,
            dict_var_name="STAY_TRANSLATIONS",
            docstring="Yakuza 0 GOG - Cabaret Club & Dragon and Tiger translations"
        )
        results["stay_translations_data.py"] = len(load_catalog_file(stay_yaml, validate=False))

    # 4. Story: Merge phone booths and substories into wdr_translations_data.py
    booth_yaml = os.path.join(translations_dir, "story", "phone_booths.yaml")
    story_yaml = os.path.join(translations_dir, "story", "substories.yaml")
    
    combined_story_entries = []
    if os.path.isfile(booth_yaml):
        combined_story_entries.extend(load_catalog_file(booth_yaml, validate=True))
    if os.path.isfile(story_yaml):
        combined_story_entries.extend(load_catalog_file(story_yaml, validate=True))

    if combined_story_entries:
        wdr_py = os.path.join(output_tools_dir, "wdr_translations_data.py")
        lines = [
            "# -*- coding: utf-8 -*-",
            '"""',
            "tools/wdr_translations_data.py",
            "-------------------------------",
            "Story, Substories, and Phone Booth save prompt translations.",
            "Par Typhon0 (basé sur les traductions initiales de RGG FR).",
            "Generated automatically by tools/i18n.py.",
            '"""',
            "",
            "WDR_TRANSLATIONS = {",
        ]
        for e in combined_story_entries:
            en = e.get("en", "")
            fr = e.get("fr", "")
            if en:
                lines.append(f"    {repr(en)}: {repr(fr)},")
        lines.append("}")
        lines.append("")
        with open(wdr_py, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        results["wdr_translations_data.py"] = len(combined_story_entries)

    return results

