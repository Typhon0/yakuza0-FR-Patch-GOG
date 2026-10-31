# -*- coding: utf-8 -*-
"""
tests/test_i18n_compiler.py
---------------------------
Unit tests for tools/i18n_compiler.py.
Verifies compiling YAML catalogs back to bit-compatible Python dictionary modules.
"""

import os
import shutil
import tempfile
import unittest
import importlib.util

from tools.i18n_compiler import (
    load_catalog_file,
    compile_dict_module,
    compile_shops,
    compile_subtitles,
)


def load_module_from_file(mod_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(mod_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
    en: "Health Item"
    fr: "Objet de soin"
  - id: test_02
    en: "Two\\nLines"
    fr: "Deux\\nLignes"
"""
        yaml_path = os.path.join(self.test_dir, "test.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        out_py = os.path.join(self.test_dir, "test_output.py")
        ok = compile_dict_module(yaml_path, out_py, dict_var_name="TEST_DATA", docstring="Generated module")
        self.assertTrue(ok)
        self.assertTrue(os.path.isfile(out_py))

        mod = load_module_from_file("test_output", out_py)
        self.assertEqual(mod.TEST_DATA["Health Item"], "Objet de soin")
        self.assertEqual(mod.TEST_DATA["Two\nLines"], "Deux\nLignes")

    def test_compile_shops(self):
        yaml_content = """# Shops catalog
domain: shops
entries:
  - id: shop0000_slot00
    file: "shop0000.bin"
    slot: 0
    item_id: 12
    en: "Staminan X"
    fr: "Le Staminan X recharge légèrement la santé."
  - id: shop0013_slot01
    file: "shop0013.bin"
    slot: 1
    item_id: 481
    en: "Wood piece"
    fr: "Simple morceau de bois."
"""
        yaml_path = os.path.join(self.test_dir, "shops.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        out_py = os.path.join(self.test_dir, "shop_translations_data.py")
        ok = compile_shops(yaml_path, out_py)
        self.assertTrue(ok)
        self.assertTrue(os.path.isfile(out_py))

        mod = load_module_from_file("test_shop_mod", out_py)
        self.assertIn(('shop0000.bin', 0), mod.SHOP_ITEM_TRANSLATIONS)
        item_id, desc = mod.SHOP_ITEM_TRANSLATIONS[('shop0000.bin', 0)]
        self.assertEqual(item_id, 12)
        self.assertEqual(desc, "Le Staminan X recharge légèrement la santé.")
        # Verify ITEM_ID_TRANSLATIONS fallback dictionary required by rebuild_all_shops_clean.py
        self.assertIn(12, mod.ITEM_ID_TRANSLATIONS)
        self.assertEqual(mod.ITEM_ID_TRANSLATIONS[12], "Le Staminan X recharge légèrement la santé.")
        self.assertIn(481, mod.ITEM_ID_TRANSLATIONS)
        self.assertEqual(mod.ITEM_ID_TRANSLATIONS[481], "Simple morceau de bois.")

    def test_compile_subtitles(self):
        yaml_content = """# Subtitles catalog
domain: subtitles
entries:
  - id: sub_0001
    en: "...So let's have whatever you got."
    fr: "...Alors file-moi tout ce que t'as"
"""
        yaml_path = os.path.join(self.test_dir, "subtitles.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        out_py = os.path.join(self.test_dir, "sound_subtitles_data.py")
        ok = compile_subtitles(yaml_path, out_py)
        self.assertTrue(ok)
        self.assertTrue(os.path.isfile(out_py))

        mod = load_module_from_file("test_sub_mod", out_py)
        self.assertEqual(mod.SOUND_SUBTITLES["...So let's have whatever you got."], "...Alors file-moi tout ce que t'as")


if __name__ == '__main__':
    unittest.main()

