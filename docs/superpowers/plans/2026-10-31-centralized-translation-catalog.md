# Centralized Translation Catalog & Compiler (YAML/JSON) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Centralize all fragmented Python translation dictionaries into a modular, human- and AI-friendly YAML catalog under `translations/`, accompanied by a robust linter/compiler CLI tool (`tools/i18n.py`) that strictly enforces binary constraints (font character set, phone booth length, padding rules) while maintaining 100% backwards compatibility with existing build tools.

**Architecture:** A domain-driven YAML layout splits strings into logical subdirectories (`shops/`, `story/`, `combat/`, `minigames/`, `subtitles/`, `system/`). A dedicated validator checks characters against `release_gog/font_table_french.bin` and asserts game engine length/padding rules. An extractor round-trips existing legacy dictionaries, and a compiler regenerates verified Python modules to feed existing PAR rebuild tools (`rebuild_clean_*.py`, `build_release.py`) without introducing regressions or breaking dependencies.

**Tech Stack:** Python 3 (standard library + PyYAML), Git, unittest.

**Spec:** User request: "find a better ways and smarter way to store the translation. It should be easy for AI but also for human to edit the translations. yes approche 1 me va" + `AGENTS.md` (10 Golden Rules) + `docs/DEBUG_KNOWLEDGE_BASE.md`.

## Global Constraints

- **Dependency constraint:** Use Python 3 standard library and `yaml` (`PyYAML`, already present in dev environment); provide safe fallbacks so core extraction/compilation does not crash if PyYAML is unavailable.
- **Credit preservation:** Preserve project credit: `Par Typhon0 (basé sur les traductions initiales de RGG FR)`.
- **Golden Rule 1:** Never truncate `shop*.bin` side tables (24 bytes in `shop0013.bin`, 20 bytes in `shop0029.bin`) nor misalign `pause.par` (strict 2048-byte sector alignment).
- **Golden Rule 2:** Bob Utsunomiya files must remain exactly 27,575 bytes; phone booths must stay strict 58 ASCII chars with space padding (no UTF-8 multi-byte characters like `é`).
- **Golden Rule 3:** Append-Only model with 2048-byte sector boundaries on `stay.par`, `boot.par`, `wdr.par`.
- **Golden Rule 4:** All French characters must be supported by the 6,144-byte font table `release_gog/font_table_french.bin` injected at `0xD488F0`.
- **Golden Rule 6:** Game directory detection must strictly verify `Yakuza0.exe`.
- **Golden Rule 9:** NO public GitHub release (`gh release create`) without explicit user instruction.
- **Backward compatibility:** Existing rebuild tools (`rebuild_all_shops_clean.py`, `rebuild_clean_boot_append.py`, etc.) must continue to function seamlessly either via generated Python bridges or direct catalog loading.

## Review Focus

1. **Unsupported Unicode Characters:** Translators inserting characters absent from `font_table_french.bin` (e.g. curly quotes `’`, ellipsis `…`, non-breaking spaces `\xa0`, em-dash `—`) must be flagged and rejected by the validator before compilation.
2. **Phone Booth Dialogue Softlock:** Any edit to telephone booth text exceeding 58 characters or containing non-ASCII bytes (`é`, `è`) must cause validation failure, preventing typewriter engine lockup at `0x08F8`.
3. **Multiline Formatting & Escaping:** Multiline dialogues containing newline breaks (`\n`) must round-trip losslessly between YAML block scalars (`|`) and binary string tables.
4. **Pocket Circuit Shop Table Integrity:** Compilation of `translations/shops/items.yaml` into `shop_translations_data.py` must retain all 558 verified item translations and match existing shop indexing `(shop_file, slot_idx)`.
5. **Zero Regression in Release Pipeline:** Executing `python3 tools/verify_patch.py release_gog` must continue to report `131/131 OK (100% PASS)` and `tools/test_release_e2e.py` must report `SUCCÈS TOTAL`.

---

### Task 1: Translation Entry Schema & Constraint Validator (`tools/i18n_validator.py`)

**Files:**
- Create: `tools/i18n_validator.py`
- Test: `tests/test_i18n_validator.py`

**Interfaces:**
- Consumes: `release_gog/font_table_french.bin` (for font table character boundary validation)
- Produces:
  - `is_char_supported_by_font(char: str) -> bool`: Checks if a character is valid ASCII (0x20-0x7E) or extended French (0x80-0xFF mapped).
  - `validate_catalog_entry(entry: dict, domain: str = "") -> list[str]`: Validates entry schema (`id`, `en`, `fr`), character set, and constraints (`max_len`, `exact_len`, `ascii_only`, `forbidden_chars`). Returns list of error strings.
  - `validate_catalog_file(file_path: str) -> tuple[int, list[str]]`: Reads a YAML file, validates all entries, returns (entry_count, errors).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_i18n_validator.py
import unittest
from tools.i18n_validator import (
    is_char_supported_by_font,
    validate_catalog_entry,
    validate_catalog_file,
)

class TestI18nValidator(unittest.TestCase):
    def test_valid_ascii_and_french_chars(self):
        self.assertTrue(is_char_supported_by_font('a'))
        self.assertTrue(is_char_supported_by_font('é'))
        self.assertTrue(is_char_supported_by_font('ç'))
        self.assertFalse(is_char_supported_by_font('…'))  # Unicode ellipsis not supported
        self.assertFalse(is_char_supported_by_font('’'))  # Curly apostrophe not supported

    def test_validate_entry_phone_booth_constraints(self):
        # Strict ASCII 58 chars required for phone booths (Golden Rule 2)
        valid_booth = {
            "id": "phone_booth_save",
            "en": "You can save the game and use the Item Box at\r\ntelephones.",
            "fr": "Sauvegardez et utilisez le coffre depuis une\r\ncabine.     ",
            "exact_len": 58,
            "ascii_only": True
        }
        self.assertEqual(validate_catalog_entry(valid_booth, domain="story"), [])

        invalid_booth = {
            "id": "phone_booth_save",
            "en": "Save",
            "fr": "Sauvegardez à la cabine.",
            "exact_len": 58,
            "ascii_only": True
        }
        errors = validate_catalog_entry(invalid_booth, domain="story")
        self.assertTrue(any("exact_len" in e or "length" in e.lower() for e in errors))

    def test_validate_entry_unsupported_chars(self):
        entry = {
            "id": "test_item",
            "en": "Sword...",
            "fr": "Épée… avec « guillemets »" # Contains unsupported '…'
        }
        errors = validate_catalog_entry(entry)
        self.assertTrue(any("unsupported character" in e.lower() or "font" in e.lower() for e in errors))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_i18n_validator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tools.i18n_validator'`

- [ ] **Step 3: Implement `tools/i18n_validator.py`**

Implement character set mapping, entry validation against schema, constraints (`max_len`, `exact_len`, `ascii_only`), and YAML file validator.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_i18n_validator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/i18n_validator.py tests/test_i18n_validator.py
git commit -m "feat(i18n): implement catalog validator with font character set & Golden Rule constraints"
```

---

### Task 2: Translation Extractor Engine (`tools/i18n_extractor.py`)

**Files:**
- Create: `tools/i18n_extractor.py`
- Test: `tests/test_i18n_extractor.py`

**Interfaces:**
- Consumes: Existing Python dictionaries (`tools/shop_translations_data.py`, `tools/stay_translations_data.py`, `tools/sound_subtitles_data.py`, `tools/tutorial_translations_data.py`, `tools/pause_translations_data.py`, `tools/wdr_dict_final.py`)
- Produces:
  - `extract_shops() -> list[dict]`: Converts `SHOP_ITEM_TRANSLATIONS` into structured entries with metadata.
  - `extract_dict_to_entries(data_dict: dict, prefix: str) -> list[dict]`: Converts (en -> fr) dictionaries into structured entries.
  - `write_yaml_catalog(entries: list[dict], output_file: str, header_comment: str = "") -> None`: Writes clean YAML with block scalar multi-line strings (`|`).
  - `extract_all(target_dir: str = "translations") -> dict[str, int]`: Extracts all domains into `translations/shops/`, `translations/story/`, `translations/combat/`, `translations/minigames/`, `translations/subtitles/`, `translations/system/`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_i18n_extractor.py
import unittest
import tempfile
import os
import shutil
from tools.i18n_extractor import (
    extract_shops,
    extract_dict_to_entries,
    write_yaml_catalog,
)

class TestI18nExtractor(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_extract_dict_to_entries(self):
        sample = {
            "Hello world": "Bonjour le monde",
            "Line 1\nLine 2": "Ligne 1\nLigne 2"
        }
        entries = extract_dict_to_entries(sample, prefix="test")
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["en"], "Hello world")
        self.assertEqual(entries[0]["fr"], "Bonjour le monde")

    def test_write_yaml_catalog_roundtrip(self):
        entries = [
            {"id": "msg_01", "en": "Line 1\nLine 2", "fr": "Ligne 1\nLigne 2"}
        ]
        out_path = os.path.join(self.test_dir, "test.yaml")
        write_yaml_catalog(entries, out_path, header_comment="Test Header")
        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Test Header", content)
        self.assertIn("Line 1\nLine 2", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_i18n_extractor.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tools.i18n_extractor'`

- [ ] **Step 3: Implement `tools/i18n_extractor.py`**

Implement extraction routines for all existing translation dictionaries and formatted YAML dumper that preserves multi-line formatting without ugly escape characters.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_i18n_extractor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/i18n_extractor.py tests/test_i18n_extractor.py
git commit -m "feat(i18n): implement extractor engine for legacy translation dictionaries"
```

---

### Task 3: Translation Compiler & Bridge Generator (`tools/i18n_compiler.py`)

**Files:**
- Create: `tools/i18n_compiler.py`
- Test: `tests/test_i18n_compiler.py`

**Interfaces:**
- Consumes: YAML files in `translations/`, `tools/i18n_validator.py`
- Produces:
  - `load_catalog_file(file_path: str) -> list[dict]`: Loads and validates catalog entries.
  - `compile_shops(catalog_path: str, output_path: str) -> bool`: Generates `tools/shop_translations_data.py` bit-compatibly with existing rebuild tools.
  - `compile_dict_module(catalog_path: str, output_path: str, dict_var_name: str, docstring: str) -> bool`: Generates standalone Python dictionary modules.
  - `compile_all(translations_dir: str = "translations", output_tools_dir: str = "tools") -> dict[str, int]`: Synchronizes all Python dictionaries from the YAML catalog.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_i18n_compiler.py
import unittest
import tempfile
import os
import shutil
from tools.i18n_compiler import (
    load_catalog_file,
    compile_dict_module,
)

class TestI18nCompiler(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_compile_dict_module(self):
        yaml_content = """# Test catalog
domain: test
entries:
  - id: test_01
    en: "Staminan X"
    fr: "Staminan X FR"
  - id: test_02
    en: "Health\\nRecovery"
    fr: "Soin\\nDe santé"
"""
        yaml_path = os.path.join(self.test_dir, "test.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        out_py = os.path.join(self.test_dir, "test_output.py")
        ok = compile_dict_module(yaml_path, out_py, dict_var_name="TEST_DICT", docstring="Generated module")
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(out_py))

        # Dynamically import and verify contents
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_output", out_py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.TEST_DICT["Staminan X"], "Staminan X FR")
        self.assertEqual(mod.TEST_DICT["Health\nRecovery"], "Soin\nDe santé")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_i18n_compiler.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tools.i18n_compiler'`

- [ ] **Step 3: Implement `tools/i18n_compiler.py`**

Implement compiler logic that reads YAML entries, runs validation, and generates Python dictionary modules formatted with UTF-8 encoding declarations and preserved structures.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_i18n_compiler.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/i18n_compiler.py tests/test_i18n_compiler.py
git commit -m "feat(i18n): implement catalog compiler generating backwards-compatible Python modules"
```

---

### Task 4: Unified CLI Tool & Console UI Integration (`tools/i18n.py`)

**Files:**
- Create: `tools/i18n.py`
- Test: `tests/test_i18n_cli.py`

**Interfaces:**
- Consumes: `tools/i18n_validator.py`, `tools/i18n_extractor.py`, `tools/i18n_compiler.py`, `tools/console_ui.py`
- Produces: CLI interface supporting:
  - `python3 tools/i18n.py extract`: Extracts all legacy dictionaries into `translations/`.
  - `python3 tools/i18n.py validate`: Validates all YAML files in `translations/` (fonts, lengths, ASCII-only rules).
  - `python3 tools/i18n.py compile`: Compiles all YAML catalogs into `tools/*_data.py`.
  - `python3 tools/i18n.py status`: Shows styled card displaying translation count and percentage completion per domain.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_i18n_cli.py
import unittest
import subprocess
import sys

class TestI18nCli(unittest.TestCase):
    def test_cli_help(self):
        res = subprocess.run([sys.executable, "tools/i18n.py", "--help"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("extract", res.stdout)
        self.assertIn("validate", res.stdout)
        self.assertIn("compile", res.stdout)
        self.assertIn("status", res.stdout)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_i18n_cli.py -v`
Expected: FAIL with file not found or exit code != 0

- [ ] **Step 3: Implement `tools/i18n.py`**

Implement command-line interface using `argparse`, integrate `tools/console_ui.py` cards, colors, and progress indicators for user feedback.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_i18n_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/i18n.py tests/test_i18n_cli.py
git commit -m "feat(i18n): create unified i18n CLI tool with modern console UI reporting"
```

---

### Task 5: Catalog Generation, Full Rebuild Verification & Pipeline Hardening

**Files:**
- Create: `translations/` directory tree with structured YAML files
  - `translations/shops/items.yaml`
  - `translations/story/phone_booths.yaml`
  - `translations/story/substories.yaml`
  - `translations/combat/abilities.yaml`
  - `translations/minigames/cabaret_and_tiger.yaml`
  - `translations/subtitles/ambient_voices.yaml`
  - `translations/system/tutorials_and_pause.yaml`
- Modify: `README.md`, `docs/DEBUG_KNOWLEDGE_BASE.md`

- [ ] **Step 1: Run extraction to build `translations/` catalog**

Run: `python3 tools/i18n.py extract`
Expected: Successfully populates `translations/` with domain-organized YAML files.

- [ ] **Step 2: Run validation on the generated catalog**

Run: `python3 tools/i18n.py validate`
Expected: Validation passes with 0 errors across all domains.

- [ ] **Step 3: Run compilation and verify Python data bridge**

Run: `python3 tools/i18n.py compile`
Expected: All Python data files (`shop_translations_data.py`, `stay_translations_data.py`, etc.) regenerated and bit-compatible.

- [ ] **Step 4: Verify patch integrity against release_gog**

Run: `python3 tools/verify_patch.py release_gog`
Expected: 131/131 OK (100% PASS, 0 errors).

- [ ] **Step 5: Run full test suite & End-to-End release build test**

Run:
```bash
python3 -m unittest discover tests
python3 tools/test_release_e2e.py
```
Expected: All unit tests PASS; End-to-End reports `SUCCÈS TOTAL`.

- [ ] **Step 6: Update documentation in `README.md` and `docs/DEBUG_KNOWLEDGE_BASE.md`**

Document how humans and AI agents can edit translations in `translations/` and use `tools/i18n.py` to validate and compile them.

- [ ] **Step 7: Commit**

```bash
git add translations/ tools/ README.md docs/DEBUG_KNOWLEDGE_BASE.md
git commit -m "feat(i18n): generate complete centralized YAML catalog and document workflow"
```

