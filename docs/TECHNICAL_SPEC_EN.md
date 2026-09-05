# Technical Specifications & Reverse Engineering

This document records the binary analysis, memory offsets, and reverse engineering that enabled porting the Yakuza 0 French fan-translation to the GOG DRM-free edition (Build 3642285 / v1.015a).

---

## 1. Binary Target

* **Game**: Yakuza 0 (GOG DRM-Free Release)
* **Executable**: `Yakuza0.exe`
* **Version**: v1.015a (Build 3642285)
* **Architecture**: x86_64 (PE32+)
* **Original File Size**: 22,084,096 bytes
* **ImageBase**: `0x140000000`

---

## 2. Steam $\rightarrow$ GOG Compatibility Breakdown

### 2.1. Chapter 1 Freeze & Crash (Kiryu's Pager)
In the community Steam executable, several instructions in the subtitle and text rendering engine had been hijacked using static offsets unique to the Steam build. When applied blindly to the GOG executable, these patches caused a stack corruption during the pager notification system call, resulting in an unrecoverable freeze of the rendering loop.

**Remediation applied to GOG**:
Four single-byte bytecode instructions were reverse-engineered and patched at the exact GOG addresses:

| File Offset | Vanilla GOG Value | Patched Value | Description |
|---|---|---|---|
| `0x2CD804` | `0x0F` | `0x90` | NOP conditional jump in subtitle engine |
| `0x2CD805` | `0x84` | `0xE9` | Redirect unconditional jump |
| `0x2CD879` | `0x0F` | `0x90` | Bypass string length check |
| `0x2CD8B6` | `0x0F` | `0x90` | Direct render of extended text buffer |

---

### 2.2. Font Kerning Distortion (Narrow Characters `i` and `l` Collapsing)

#### Root Cause
In the Yakuza 0 graphics engine, the UV coordinate and glyph margin table is stored within the `.data` section of the GOG executable at offset `0xD488F0`. Each ASCII character (`0x00` to `0xFF`) has a **24-byte entry** consisting of six 32-bit `float` values (IEEE-754 little-endian):
```
[top_left_margin, top_right_margin, mid_left_margin, mid_right_margin, bot_left_margin, bot_right_margin]
```

In Vanilla Sega (GOG):
* For `i` (`0x69`): `[0.0, 1.17, 0.0, 1.17, 0.0, 1.17]`
* For `l` (`0x6C`): `[0.0, 1.17, 0.0, 1.17, 0.0, 1.17]`

In Byce61's Steam executable, the table was entirely overwritten with artificial margins:
* `[0.6875, 0.75, 0.6875, 0.75, 0.6875, 0.75]`

On the GOG binary, applying `0.6875` to narrow glyphs like `i` triggered a negative translation calculation of over 16 pixels to the left. As a result:
* The letters `i`, `l`, `I` were drawn directly on top of the preceding letter (*"Batte"* instead of *"Battle"*, *"Busness"*, *"Substores"*, etc.).

#### Solution
The patcher **fully preserves** the native Sega Vanilla table for standard ASCII (**`0x00` to `0x7F`**) and only injects the French table for the extended range (**`0x80` to `0xFF`**). Furthermore, accented characters derived from `i` (`î` `0xEE`, `ï` `0xEF`, etc.) have their margins recalibrated to `[0.0, 1.17, ...]` for flawless typography.

---

## 3. Dynamic PE Section Injection & String Relocation

### 3.1. Creating the `.trad` PE Section
Rather than overwriting existing buffers in `.rdata` (which would restrict translation length to the exact byte count of original English strings), the patcher extends the PE header:
1. Increments `NumberOfSections` in the `COFF File Header`.
2. Computes the new offset aligned to `FileAlignment` (512 bytes) and `SectionAlignment` (4096 bytes).
3. Writes the 40-byte section header named `.trad\0\0\0` with flags `IMAGE_SCN_MEM_READ | IMAGE_SCN_CNT_INITIALIZED_DATA` (`0x40000040`).
4. Updates `SizeOfImage` in the `Optional Header`.

### 3.2. 64-bit Pointer Redirection
1. Target English strings are located in `.rdata`.
2. French equivalents encoded in `Windows-1252 / ISO-8859-1` are written into the allocated `.trad` section.
3. The patcher scans the pointer tables in `.data` and updates 64-bit absolute virtual addresses (`0x140xxxxxx`) to point directly to the newly allocated strings in `.trad`.

---

## 4. In-Place Archive Text & Encoding Remediation

### 4.1. UTF-8 "Trade Mark" `™` Anomaly
* **Cause**: Typographic curved apostrophes `’` (U+2019) were exported in UTF-8 (`\xE2\x80\x99`).
* **Interpretation**: In Windows-1252, byte `0x99` is the Trademark symbol `™` (`c™est`, `j™ai`, `d™argent`).
* **Fix**: Replaced in-place with straight ASCII apostrophes `'` (`0x27`) padded with null bytes (`\x00`).

### 4.2. Bit-Exact SLLZ Recompression
* Compressed data inside Sega PAR archives (`.bin_c`) requires the proprietary SLLZ compression algorithm.
* The standalone Python implementation ([`tools/sllz.py`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/tools/sllz.py)) recompresses modified files while guaranteeing that the new compressed stream never exceeds the original archive slot size, avoiding any archive offset shifting.
