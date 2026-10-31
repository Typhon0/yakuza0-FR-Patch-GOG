# -*- coding: utf-8 -*-
"""
tools/i18n_extractor.py
-----------------------
Extracts existing Python translation dictionaries into structured YAML catalog
files under translations/ with domain splitting, metadata tagging, and Golden Rule
constraint annotations.
"""

import os
import sys
import re
from typing import Dict, List, Tuple, Any, Optional

try:
    import yaml
    HAVE_YAML = True

    class CleanYamlDumper(yaml.SafeDumper):
        pass

    def _str_representer(dumper, data):
        # Use block scalar style '|' for multiline strings if they have clean newlines
        if '\n' in data and '\r' not in data and data.rstrip() == data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    CleanYamlDumper.add_representer(str, _str_representer)

except ImportError:
    HAVE_YAML = False
    import json


def sanitize_id(text: str, max_words: int = 4) -> str:
    """Generates a clean identifier from a text string."""
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    words = cleaned.split()[:max_words]
    return "_".join(words) if words else "entry"


def extract_dict_to_entries(data_dict: Dict[str, str], prefix: str = "msg") -> List[Dict[str, Any]]:
    """Converts a standard English->French dictionary into structured entries."""
    entries: List[Dict[str, Any]] = []
    seen_ids = set()

    for idx, (en, fr) in enumerate(data_dict.items()):
        base_id = f"{prefix}_{sanitize_id(en)}"
        entry_id = base_id
        suffix = 1
        while entry_id in seen_ids:
            entry_id = f"{base_id}_{suffix}"
            suffix += 1
        seen_ids.add(entry_id)

        entry = {
            "id": entry_id,
            "en": en,
            "fr": fr,
        }
        entries.append(entry)

    return entries


def extract_shops_to_entries(shop_data: Dict[Tuple[str, int], Tuple[int, str]]) -> List[Dict[str, Any]]:
    """Converts SHOP_ITEM_TRANSLATIONS into structured catalog entries."""
    entries: List[Dict[str, Any]] = []
    
    # Sort by shop file name, then slot index
    sorted_items = sorted(shop_data.items(), key=lambda x: (x[0][0], x[0][1]))

    for (shop_file, slot_idx), (item_id, fr_desc) in sorted_items:
        base_file = os.path.splitext(shop_file)[0]
        entry_id = f"{base_file}_slot{slot_idx:02d}"
        
        entry = {
            "id": entry_id,
            "file": shop_file,
            "slot": slot_idx,
            "item_id": item_id,
            "context": f"Item description in {shop_file} (slot {slot_idx})",
            "en": "",  # Populated or edited
            "fr": fr_desc,
        }
        entries.append(entry)

    return entries


def write_yaml_catalog(entries: List[Dict[str, Any]], output_file: str, header_comment: str = "", domain: str = "") -> None:
    """Writes a catalog file in YAML (or JSON fallback)."""
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    catalog = {
        "domain": domain,
        "total_entries": len(entries),
        "entries": entries,
    }

    if HAVE_YAML and (output_file.endswith(".yaml") or output_file.endswith(".yml")):
        with open(output_file, "w", encoding="utf-8") as f:
            if header_comment:
                for line in header_comment.strip().split("\n"):
                    f.write(f"# {line}\n")
                f.write("\n")
            yaml.dump(catalog, f, Dumper=CleanYamlDumper, default_flow_style=False, allow_unicode=True, sort_keys=False)
    else:
        import json
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)


def extract_all(target_dir: str = "translations") -> Dict[str, int]:
    """
    Extracts all legacy translation dictionaries from tools/ into the target directory.
    Returns a dictionary of domain -> count of extracted entries.
    """
    results: Dict[str, int] = {}
    
    # Add tools/ to sys.path
    tools_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)

    # 1. Shops (shop_translations_data.py)
    try:
        from shop_translations_data import SHOP_ITEM_TRANSLATIONS
        shop_entries = extract_shops_to_entries(SHOP_ITEM_TRANSLATIONS)
        shop_out = os.path.join(target_dir, "shops", "items.yaml")
        header = (
            "Yakuza 0 GOG - Shop Item Descriptions Catalog\n"
            "558 item descriptions across all 35 shop files (shop0000.bin - shop0034.bin).\n"
            "Golden Rule 1: shop0013.bin (24 bytes) and shop0029.bin (20 bytes) Pocket Circuit\n"
            "side tables are strictly preserved by the rebuild tool."
        )
        write_yaml_catalog(shop_entries, shop_out, header_comment=header, domain="shops")
        results["shops"] = len(shop_entries)
    except Exception as e:
        results["shops_error"] = str(e)

    # 2. Story: Phone booths & Substories
    # Special phone booth entries with Golden Rule 2 strict constraints
    booth_entries = [
        {
            "id": "phone_booth_save_telephones",
            "context": "Phone booth save prompt (Chapter 1-17)",
            "exact_len": 58,
            "ascii_only": True,
            "pad_type": "space",
            "en": "You can save the game and use the Item Box at\r\ntelephones.",
            "fr": "Sauvegardez et utilisez le coffre depuis une\r\ncabine.     "
        },
        {
            "id": "phone_booth_save_payphones",
            "context": "Phone booth save prompt variant (pay phones)",
            "exact_len": 58,
            "ascii_only": True,
            "pad_type": "space",
            "en": "You can save the game and use the Item Box at\r\npay phones.",
            "fr": "Sauvegardez et utilisez le coffre depuis une\r\ncabine.     "
        }
    ]
    booth_out = os.path.join(target_dir, "story", "phone_booths.yaml")
    booth_header = (
        "Yakuza 0 GOG - Phone Booth Save Prompts Catalog\n"
        "Golden Rule 2: Strictly 58 ASCII characters with space padding.\n"
        "Never use accented characters (é, è) - multi-byte UTF-8 breaks Sega\n"
        "typewriter routine (0x140396783) and causes game softlock at 0x08F8."
    )
    write_yaml_catalog(booth_entries, booth_out, header_comment=booth_header, domain="story")
    results["phone_booths"] = len(booth_entries)

    # General story & substories from wdr_dict_final / wdr_translations_data
    try:
        from wdr_translations_data import WDR_TRANSLATIONS
        story_dict = {k: v for k, v in WDR_TRANSLATIONS.items() if "telephones" not in k and "pay phones" not in k}
        story_entries = extract_dict_to_entries(story_dict, prefix="wdr")
        story_out = os.path.join(target_dir, "story", "substories.yaml")
        write_yaml_catalog(story_entries, story_out, header_comment="Yakuza 0 GOG - Story, Substories & Street NPCs Catalog", domain="story")
        results["story"] = len(story_entries)
    except Exception as e:
        results["story_error"] = str(e)

    # 3. Subtitles (sound_subtitles_data.py)
    try:
        from sound_subtitles_data import SOUND_SUBTITLES
        sub_entries = []
        for idx, (en, fr) in enumerate(SOUND_SUBTITLES.items()):
            sub_entries.append({
                "id": f"sub_{idx:04d}",
                "context": "Street ambient voice subtitle (.mfp in sound.par)",
                "max_len": len(en),  # Sound subtitles require len(FR) <= len(EN) for bit-exact patching
                "en": en,
                "fr": fr,
            })
        sub_out = os.path.join(target_dir, "subtitles", "ambient_voices.yaml")
        sub_header = (
            "Yakuza 0 GOG - Street Ambient Voice Subtitles Catalog\n"
            "Calibrated French subtitles for 540 street voice encounters (.mfp in sound.par).\n"
            "Requires len(FR) <= len(EN) for bit-exact in-place sound.par patching."
        )
        write_yaml_catalog(sub_entries, sub_out, header_comment=sub_header, domain="subtitles")
        results["subtitles"] = len(sub_entries)
    except Exception as e:
        results["subtitles_error"] = str(e)

    # 4. Minigames & Cabaret (stay_translations_data.py)
    try:
        from stay_translations_data import STAY_TRANSLATIONS
        stay_entries = extract_dict_to_entries(STAY_TRANSLATIONS, prefix="stay")
        stay_out = os.path.join(target_dir, "minigames", "cabaret_and_tiger.yaml")
        stay_header = "Yakuza 0 GOG - Cabaret Club Hostesses & Dragon and Tiger Agents Catalog"
        write_yaml_catalog(stay_entries, stay_out, header_comment=stay_header, domain="minigames")
        results["minigames"] = len(stay_entries)
    except Exception as e:
        results["minigames_error"] = str(e)

    # 5. Combat & Abilities (boot_dict_part1..5.py via build_boot_dict.py)
    try:
        import build_boot_dict
        boot_dict = build_boot_dict.build_all_boot_translations()
        boot_entries = extract_dict_to_entries(boot_dict, prefix="boot")
        boot_out = os.path.join(target_dir, "combat", "abilities.yaml")
        boot_header = "Yakuza 0 GOG - Combat Abilities, Heat Actions & Style Names Catalog"
        write_yaml_catalog(boot_entries, boot_out, header_comment=boot_header, domain="combat")
        results["combat"] = len(boot_entries)
    except Exception as e:
        results["combat_error"] = str(e)

    # 6. System & Tutorials (tutorial_translations_data.py + pause_translations_data.py)
    try:
        from tutorial_translations_data import TUTORIAL_TRANSLATIONS
        from pause_translations_data import PAUSE_TRANSLATIONS
        sys_dict = {}
        sys_dict.update(TUTORIAL_TRANSLATIONS)
        sys_dict.update(PAUSE_TRANSLATIONS)
        sys_entries = extract_dict_to_entries(sys_dict, prefix="sys")
        sys_out = os.path.join(target_dir, "system", "tutorials_and_pause.yaml")
        sys_header = "Yakuza 0 GOG - Pause Menus, Tutorials & Tooltips Catalog"
        write_yaml_catalog(sys_entries, sys_out, header_comment=sys_header, domain="system")
        results["system"] = len(sys_entries)
    except Exception as e:
        results["system_error"] = str(e)

    return results
