#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import os
import sys
import tempfile
import io

# Add tools to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.console_ui import (
    Colors,
    strip_ansi,
    print_banner,
    card_start,
    card_line,
    card_end,
    format_progress,
    resolve_game_directory,
    validate_game_directory,
)


class TestConsoleUI(unittest.TestCase):
    def test_strip_ansi(self):
        text_with_ansi = f"{Colors.CYAN}{Colors.BOLD}Hello World{Colors.RESET}"
        self.assertEqual(strip_ansi(text_with_ansi), "Hello World")

    def test_banner_content(self):
        captured = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            print_banner(version="v1.13.0")
        finally:
            sys.stdout = old_stdout
        
        output = strip_ansi(captured.getvalue())
        self.assertIn("YAKUZA", output.upper())
        self.assertIn("Typhon0", output)
        self.assertIn("RGG FR", output)

    def test_card_structure(self):
        captured = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            card_start("TEST CARD", width=60)
            card_line("Operation successful", status="ok", width=60)
            card_line("Operation in progress", status="action", width=60)
            card_line("Something to note", status="info", width=60)
            card_line("Warning encountered", status="warn", width=60)
            card_line("Critical error", status="err", width=60)
            card_end(width=60)
        finally:
            sys.stdout = old_stdout

        lines = [strip_ansi(line) for line in captured.getvalue().splitlines() if line.strip()]
        self.assertTrue(lines[0].startswith("╭─") or lines[0].startswith("+--"))
        self.assertTrue(lines[-1].startswith("╰─") or lines[-1].startswith("+--"))
        for line in lines[1:-1]:
            self.assertTrue(line.startswith("│") or line.startswith("|"))

    def test_format_progress(self):
        p0 = format_progress(0, 100, width=10)
        p50 = format_progress(50, 100, width=10)
        p100 = format_progress(100, 100, width=10)
        
        self.assertIn("0%", p0)
        self.assertIn("50%", p50)
        self.assertIn("100%", p100)

    def test_validate_game_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Without Yakuza0.exe -> should be False (Rule 6)
            self.assertFalse(validate_game_directory(tmpdir))
            
            # With Yakuza0.exe -> should be True
            exe_path = os.path.join(tmpdir, "Yakuza0.exe")
            with open(exe_path, "wb") as f:
                f.write(b"MZdummy")
            self.assertTrue(validate_game_directory(tmpdir))

            # Test quote and slash stripping in resolve_game_directory with initial_path
            quoted_path = f'"{tmpdir}/"'
            resolved = resolve_game_directory(quoted_path, interactive=False)
            self.assertEqual(os.path.normpath(resolved), os.path.normpath(tmpdir))


if __name__ == "__main__":
    unittest.main()
