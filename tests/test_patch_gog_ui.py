#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import os
import sys
import tempfile
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import release_gog.patch_gog as patch_gog


class TestPatchGogUI(unittest.TestCase):
    def test_missing_executable_handling(self):
        # Should gracefully return False and not crash
        captured = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            res = patch_gog.patch_yakuza0_gog("/nonexistent/path/Yakuza0.exe", interactive=False)
            self.assertFalse(res)
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        # Verify it mentions the missing executable
        self.assertTrue("introuvable" in output.lower() or "not found" in output.lower() or "invalide" in output.lower())

    def test_ui_components_imported(self):
        # Verify that patch_gog has access to console_ui functions
        self.assertTrue(hasattr(patch_gog, 'card_start'))
        self.assertTrue(hasattr(patch_gog, 'card_line'))
        self.assertTrue(hasattr(patch_gog, 'card_end'))
        self.assertTrue(hasattr(patch_gog, 'print_banner'))


if __name__ == "__main__":
    unittest.main()
