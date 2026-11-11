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

    def test_verify_patch_no_banner_flag(self):
        # Verify that verify_patch respects --no-banner and YAKUZA_NO_BANNER
        import subprocess

        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "verify_patch.py"))
        tmp_cwd = tempfile.gettempdir()

        # Test with --no-banner
        res = subprocess.run(
            [sys.executable, script_path, "--no-banner", "/invalid_game_dir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=tmp_cwd
        )
        self.assertNotIn("YAKUZA 0 — PATCH DE TRADUCTION", res.stdout)
        self.assertIn("ERREUR DE DÉTECTION DU JEU", res.stdout)

        # Test with YAKUZA_NO_BANNER env var
        env = os.environ.copy()
        env["YAKUZA_NO_BANNER"] = "1"
        res_env = subprocess.run(
            [sys.executable, script_path, "/invalid_game_dir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=tmp_cwd
        )
        self.assertNotIn("YAKUZA 0 — PATCH DE TRADUCTION", res_env.stdout)
        self.assertIn("ERREUR DE DÉTECTION DU JEU", res_env.stdout)

        # Test normal invocation displays banner
        res_normal = subprocess.run(
            [sys.executable, script_path, "/invalid_game_dir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=tmp_cwd
        )
        self.assertIn("YAKUZA 0 — PATCH DE TRADUCTION", res_normal.stdout)
        self.assertIn("ERREUR DE DÉTECTION DU JEU", res_normal.stdout)


if __name__ == "__main__":
    unittest.main()
