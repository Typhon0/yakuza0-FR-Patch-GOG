# Modern Console UI Overhaul for Yakuza 0 FR Patch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Overhaul the French fan-translation installer and verification scripts with a modern, stylized terminal UI featuring an ASCII banner credited to Typhon0 (based on RGG FR initial translations), Unicode card frames, progress bars, interactive game path resolution (with a native Windows folder picker fallback), and full compliance with the 10 Golden Rules.

**Architecture:** A standalone, zero-dependency `tools/console_ui.py` engine handles ANSI terminal colors, Windows virtual terminal processing, Unicode card layouts, and interactive folder resolution (including PowerShell `FolderBrowserDialog` fallback). `patch_gog.py`, `patch_fr.bat`, and `tools/verify_patch.py` consume this UI engine to present a unified, elegant installation experience.

**Tech Stack:** Python 3 (standard library only: `ctypes`, `subprocess`, `sys`, `os`, `shutil`), Windows CMD (`.bat`), Windows PowerShell (lightweight 1-liner fallback for GUI folder picker).

**Spec:** Approved Design Doc (chat conversation & initiative page `kp-142213f12cb64341a69730827661023e`).

## Global Constraints

- Credit signature must read: `Par Typhon0 (basé sur les traductions initiales de RGG FR)`.
- Rule 6: Game directory detection MUST strictly verify the presence of `Yakuza0.exe`.
- Rule 8: Never rely on `copy /y`; always strip trailing backslashes and remove read-only attributes (`attrib -R`, `os.chmod` `stat.S_IWRITE`).
- Rule 9: No public GitHub releases without explicit user instruction.
- Zero external dependencies: Must run on stock Python 3.12 embedded without `pip` or external wheels.
- Golden Rule parity: PAR archives, font table, and bytecode must maintain 131/131 verification pass.

## Review Focus

1. **Non-interactive / CI / piped execution:** If stdin/stdout is not a TTY or cannot render ANSI/Unicode, `console_ui.py` must gracefully fall back to plain ASCII without crashing.
2. **Path with trailing slash / quotes / spaces:** Drag-and-drop on Windows often encloses paths in double quotes or leaves a trailing backslash; `resolve_game_directory` must sanitize quotes and slashes.
3. **Missing `Yakuza0.exe` in selected folder:** Must reject folder immediately with a clear explanatory error card and allow retry rather than exiting blindly.
4. **Console width underflow:** Card frames and progress bars must fit within standard 80-column console windows without wrapping or line glitching.
5. **Read-only (+R) GOG game files:** Unlocking write permissions must happen cleanly before backup and file write operations.

---

### Task 1: Create `tools/console_ui.py` Core Styling and Interactivity Engine

**Files:**
- Create: `tools/console_ui.py`
- Test: `tests/test_console_ui.py`

**Interfaces:**
- Produces:
  - `class Colors`: ANSI constants (`CYAN`, `GREEN`, `YELLOW`, `RED`, `MAGENTA`, `BOLD`, `DIM`, `RESET`)
  - `enable_virtual_terminal() -> bool`
  - `print_banner(version: str = "v1.13.0") -> None`
  - `card_start(title: str, width: int = 76) -> None`
  - `card_line(text: str, status: str = "info", width: int = 76) -> None`
  - `card_end(width: int = 76) -> None`
  - `format_progress(current: int, total: int, width: int = 24) -> str`
  - `resolve_game_directory(initial_path: str = None) -> str | None`

- [ ] **Step 1: Write test for `tools/console_ui.py`**

Write `tests/test_console_ui.py` testing ANSI color disabling in non-TTY, card formatting output length, progress bar calculations, and path sanitation.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_console_ui.py`
Expected: FAIL (module `tools.console_ui` not found).

- [ ] **Step 3: Implement `tools/console_ui.py`**

Implement Windows virtual terminal activation via `ctypes.windll.kernel32`, ASCII art banner crediting Typhon0, card drawing functions, progress bar, and interactive `resolve_game_directory()` with automatic scan, PowerShell folder dialog fallback, and drag-and-drop cleaning.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_console_ui.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/console_ui.py tests/test_console_ui.py
git commit -m "feat(ui): add modern console styling and interactive directory resolver"
```

---

### Task 2: Modernize `patch_gog.py` with Card Layouts and Visual Progress

**Files:**
- Modify: `patcher/patch_gog.py`
- Modify: `release_gog/patch_gog.py`
- Test: `tests/test_patch_gog_ui.py`

**Interfaces:**
- Consumes: `tools.console_ui` (`print_banner`, `card_start`, `card_line`, `card_end`, `format_progress`, `resolve_game_directory`)
- Produces: Enhanced `patch_yakuza0_gog(exe_path, output_path=None)` with 4 organized visual cards:
  1. Preparation & Safety
  2. Translated Archives Installation (with progress bars and byte sizes)
  3. Executable Patching (font table, kerning, bytecode, .trad strings)
  4. Post-installation summary card

- [ ] **Step 1: Write test for modernized `patch_gog.py` flow**

Test dry-run/mock patching behavior with the UI hooks enabled.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_patch_gog_ui.py`
Expected: FAIL.

- [ ] **Step 3: Update `patch_gog.py` in `patcher/` and `release_gog/`**

Integrate `console_ui` into `patch_yakuza0_gog()` with fallback if run as a standalone script without `tools/`. Add visual progress updates during file copying and clear card layouts for all 4 stages.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_patch_gog_ui.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add patcher/patch_gog.py release_gog/patch_gog.py tests/test_patch_gog_ui.py
git commit -m "feat(installer): integrate card layout and progress indicators into patch_gog.py"
```

---

### Task 3: Modernize `tools/verify_patch.py` Output

**Files:**
- Modify: `tools/verify_patch.py`

**Interfaces:**
- Consumes: `tools.console_ui` (`card_start`, `card_line`, `card_end`, `Colors`)
- Produces: Clean, compact card-based verification summary replacing noisy scrolling outputs while keeping detailed error reporting when an archive fails.

- [ ] **Step 1: Implement card-based reporting in `tools/verify_patch.py`**

Wrap the 131 PAR archive checks, dialogue bytecode checks, phone booth checks, and font table checks into clean grouped cards.

- [ ] **Step 2: Run verification against `release_gog`**

Run: `python3 tools/verify_patch.py release_gog`
Expected: PASS (131/131 OK) with elegant card summary.

- [ ] **Step 3: Commit**

```bash
git add tools/verify_patch.py
git commit -m "feat(verify): format verification results with modern card layout"
```

---

### Task 4: Modernize Launcher Scripts and Update `tools/build_release.py`

**Files:**
- Modify: `tools/build_release.py` (update `BAT_PATCHER`, `BAT_VERIFY`, `TOOL_FILES`)
- Modify: `patcher/patch_gog.bat`
- Modify: `release_gog/patch_gog.bat`

**Interfaces:**
- Consumes: `tools/console_ui.py` (included in release packaging)
- Produces: Updated `patch_fr.bat` and `verifier.bat` with UTF-8 encoding, modern titles, clean error fallbacks, and automatic delegation to the Python UI engine.

- [ ] **Step 1: Update batch launcher templates in `tools/build_release.py` and standalone batch files**

Include `tools/console_ui.py` in `TOOL_FILES`. Update `BAT_PATCHER` to have a clean, polished console title and delegate interactive folder prompting directly to `patch_gog.py` if not passed as an argument.

- [ ] **Step 2: Run release build and full validation**

Run: `python3 tools/build_release.py`
Expected: SUCCÈS TOTAL with packages created in `staging_release/`.

- [ ] **Step 3: Commit**

```bash
git add tools/build_release.py patcher/patch_gog.bat release_gog/patch_gog.bat
git commit -m "feat(build): package console_ui.py and update launcher batch scripts"
```

---

### Task 5: End-to-End Verification and Polish

**Files:**
- Test: Full simulation in isolated scratch environment

- [ ] **Step 1: Run complete End-to-End test suite**

Run: `python3 tools/test_release_e2e.py`
Expected: PASS with 100% success.

- [ ] **Step 2: Verify all 131 PAR files and sensitive components**

Run: `python3 tools/verify_patch.py release_gog`
Expected: 131/131 OK.

- [ ] **Step 3: Final check of Golden Rules**

Ensure no GitHub release was created (Rule 9), `Yakuza0.exe` detection is strict (Rule 6), and read-only attributes are handled (Rule 8).
