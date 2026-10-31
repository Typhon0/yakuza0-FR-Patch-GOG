# -*- coding: utf-8 -*-
"""
tests/test_i18n_cli.py
----------------------
Unit tests for the tools/i18n.py command-line interface.
"""

import os
import sys
import subprocess
import unittest


class TestI18nCli(unittest.TestCase):
    def test_cli_help(self):
        res = subprocess.run(
            [sys.executable, "tools/i18n.py", "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("extract", res.stdout)
        self.assertIn("validate", res.stdout)
        self.assertIn("compile", res.stdout)
        self.assertIn("status", res.stdout)

    def test_cli_subcommand_help(self):
        for subcmd in ["extract", "validate", "compile", "status"]:
            res = subprocess.run(
                [sys.executable, "tools/i18n.py", subcmd, "--help"],
                capture_output=True,
                text=True
            )
            self.assertEqual(res.returncode, 0, f"Subcommand '{subcmd}' --help failed")


if __name__ == '__main__':
    unittest.main()
