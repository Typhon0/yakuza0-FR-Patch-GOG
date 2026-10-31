# -*- coding: utf-8 -*-
"""
tests/test_i18n_validator.py
----------------------------
Unit tests for tools/i18n_validator.py.
Validates font character set compliance, Golden Rule 2 phone booth constraints,
schema consistency, and error reporting.
"""

import os
import unittest
from tools.i18n_validator import (
    is_char_supported_by_font,
    validate_text_chars,
    validate_catalog_entry,
    validate_catalog_file,
    SUPPORTED_EXTENDED_CHARS,
)


class TestI18nValidator(unittest.TestCase):
    def test_ascii_and_french_chars_support(self):
        # Basic ASCII printable
        self.assertTrue(is_char_supported_by_font('A'))
        self.assertTrue(is_char_supported_by_font('z'))
        self.assertTrue(is_char_supported_by_font('0'))
        self.assertTrue(is_char_supported_by_font(' '))
        self.assertTrue(is_char_supported_by_font('\n'))
        self.assertTrue(is_char_supported_by_font('\r'))

        # Standard French characters used in the game
        for char in "éèêëàâäçîïôöùûüÉÈÀÇ«»°¥":
            self.assertTrue(is_char_supported_by_font(char), f"Character '{char}' should be supported")

        # Unsupported characters that cause game font corruption or crashes
        self.assertFalse(is_char_supported_by_font('…'))  # Horizontal ellipsis (U+2026) -> use "..."
        self.assertFalse(is_char_supported_by_font('’'))  # Right curly apostrophe (U+2019) -> use "'"
        self.assertFalse(is_char_supported_by_font('—'))  # Em-dash (U+2014) -> use "-"
        self.assertFalse(is_char_supported_by_font('\xa0'))  # Non-breaking space -> use normal space

    def test_validate_text_chars(self):
        ok, invalid = validate_text_chars("Bonjour ! C'est l'heure du combat.")
        self.assertTrue(ok)
        self.assertEqual(invalid, [])

        ok, invalid = validate_text_chars("Attendez… c’est interdit —")
        self.assertFalse(ok)
        self.assertIn('…', invalid)
        self.assertIn('’', invalid)
        self.assertIn('—', invalid)

    def test_validate_entry_phone_booth_golden_rule(self):
        # Golden Rule 2: Strict ASCII, exactly 58 characters
        valid_booth = {
            "id": "phone_booth_save",
            "en": "You can save the game and use the Item Box at\r\ntelephones.",
            "fr": "Sauvegardez et utilisez le coffre depuis une\r\ncabine.     ",
            "exact_len": 58,
            "ascii_only": True
        }
        errors = validate_catalog_entry(valid_booth, domain="story")
        self.assertEqual(errors, [])

        # Fails if contains accented char (multi-byte UTF-8 breaks typewriter length counter at 0x140396783)
        invalid_accent_booth = {
            "id": "phone_booth_save",
            "en": "You can save the game and use the Item Box at\r\ntelephones.",
            "fr": "Sauvegardez et utilisez le coffre depuis une\r\ntéléphone.  ",
            "exact_len": 58,
            "ascii_only": True
        }
        errors = validate_catalog_entry(invalid_accent_booth, domain="story")
        self.assertTrue(any("ascii" in e.lower() or "accent" in e.lower() for e in errors))

        # Fails if wrong length
        wrong_len_booth = {
            "id": "phone_booth_save",
            "en": "Save",
            "fr": "Sauvegardez votre partie.",
            "exact_len": 58,
            "ascii_only": True
        }
        errors = validate_catalog_entry(wrong_len_booth, domain="story")
        self.assertTrue(any("exact_len" in e.lower() or "length" in e.lower() for e in errors))

    def test_validate_entry_max_length(self):
        entry = {
            "id": "subtitle_01",
            "en": "Short text",
            "fr": "Ceci est un texte beaucoup trop long pour la limite",
            "max_len": 20
        }
        errors = validate_catalog_entry(entry)
        self.assertTrue(any("max_len" in e.lower() for e in errors))

    def test_validate_entry_schema_missing_fields(self):
        # Missing 'id'
        entry_no_id = {"en": "Hello", "fr": "Bonjour"}
        errors = validate_catalog_entry(entry_no_id)
        self.assertTrue(any("id" in e.lower() for e in errors))

        # Missing 'fr'
        entry_no_fr = {"id": "msg_01", "en": "Hello"}
        errors = validate_catalog_entry(entry_no_fr)
        self.assertTrue(any("fr" in e.lower() for e in errors))


if __name__ == '__main__':
    unittest.main()

