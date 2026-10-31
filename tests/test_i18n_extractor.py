# -*- coding: utf-8 -*-
"""
tests/test_i18n_extractor.py
----------------------------
Unit tests for tools/i18n_extractor.py.
Verifies dictionary extraction, metadata tagging, multiline string formatting,
and domain catalog generation.
"""

import os
import shutil
import tempfile
import unittest

from tools.i18n_extractor import (
    extract_dict_to_entries,
    extract_shops_to_entries,
    write_yaml_catalog,
    extract_all,
)


class TestI18nExtractor(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_extract_dict_to_entries(self):
        sample = {
            "First aid item": "Objet de premier secours",
            "Complex line\nSecond line": "Ligne complexe\nDeuxième ligne"
        }
        entries = extract_dict_to_entries(sample, prefix="item")
        self.assertEqual(len(entries), 2)
        # Check that ids are unique and entries preserve exact strings
        ids = [e["id"] for e in entries]
        self.assertEqual(len(ids), len(set(ids)))
        
        entry_map = {e["en"]: e["fr"] for e in entries}
        self.assertEqual(entry_map["First aid item"], "Objet de premier secours")
        self.assertEqual(entry_map["Complex line\nSecond line"], "Ligne complexe\nDeuxième ligne")

    def test_extract_shops_to_entries(self):
        sample_shops = {
            ('shop0000.bin', 0): (12, "Le Staminan X recharge la santé."),
            ('shop0013.bin', 1): (481, "Morceau de bois de combat.")
        }
        entries = extract_shops_to_entries(sample_shops)
        self.assertEqual(len(entries), 2)
        e0 = entries[0]
        self.assertEqual(e0["file"], "shop0000.bin")
        self.assertEqual(e0["slot"], 0)
        self.assertEqual(e0["item_id"], 12)
        self.assertEqual(e0["fr"], "Le Staminan X recharge la santé.")

    def test_write_and_read_yaml_catalog(self):
        entries = [
            {
                "id": "booth_01",
                "context": "Phone booth save prompt",
                "exact_len": 58,
                "ascii_only": True,
                "en": "You can save the game and use the Item Box at\r\ntelephones.",
                "fr": "Sauvegardez et utilisez le coffre depuis une\r\ncabine.     "
            },
            {
                "id": "ability_01",
                "en": "Dragon Style\nMastery",
                "fr": "Style Dragon\nMaîtrise"
            }
        ]
        out_path = os.path.join(self.test_dir, "test_catalog.yaml")
        write_yaml_catalog(entries, out_path, header_comment="Test Catalog Header", domain="test_domain")
        self.assertTrue(os.path.exists(out_path))

        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Test Catalog Header", content)
        self.assertIn("domain: test_domain", content)
        self.assertIn("booth_01", content)
        self.assertIn("Sauvegardez et utilisez", content)

    def test_extract_all_creates_directories(self):
        results = extract_all(target_dir=self.test_dir)
        self.assertIn("shops", results)
        self.assertIn("story", results)
        self.assertIn("subtitles", results)
        
        # Verify YAML files created
        self.assertTrue(os.path.isfile(os.path.join(self.test_dir, "shops", "items.yaml")))
        self.assertTrue(os.path.isfile(os.path.join(self.test_dir, "story", "phone_booths.yaml")))
        self.assertTrue(os.path.isfile(os.path.join(self.test_dir, "subtitles", "ambient_voices.yaml")))


if __name__ == '__main__':
    unittest.main()

