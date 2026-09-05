# Comprehensive Text & Encoding Defect Audit (Yakuza 0 GOG VOSTFR)

This technical report documents all textual anomalies (the `™` trademark symbol, UTF-8 mojibake like `Ã©`, `Å“`, corrupted apostrophes, and unsupported ligatures) identified in the French fan-translation patch (Rev 1.10) and explains their root causes and solutions.

---

## 1. Technical Root Causes

The Yakuza 0 PC engine handles in-game strings as **1-byte encoded text** (Windows-1252 / ISO-8859-1) and uses a metric/UV table injected into the binary to display accented characters (`0xA1` to `0xFF`).

Three distinct mechanisms produced visible defects in-game:

### A. The "™" Symbol Appearing in Place of Apostrophes
* **Cause**: In modern word processors and subtitle editors, curved typographic apostrophes `’` (U+2019) were automatically inserted instead of straight ASCII apostrophes `'` (`0x27`).
* **UTF-8 Byte Sequence**: `’` is written on 3 bytes: `\xE2\x80\x99`.
* **Game Engine Interpretation (Windows-1252)**:
  - `\xE2` = letter `â`
  - `\x80` = non-printable / ignored
  - `\x99` = **Trade Mark symbol `™`**!
* **In-Game Result**: Players literally see `c™est`, `j™ai`, `d™accord`, `d™argent`.

### B. UTF-8 Accent Residues (`Ã©`, `Ã¨`, `Ã `, `Ã‰`...)
* **Cause**: Several dialogue files (`.msg`) and object tables (`.bin_c`) were saved in UTF-8 encoding instead of Windows-1252.
* **In-Game Result**: Multi-byte accents were read as two separate characters:
  - `é` (`\xC3\xA9`) became `Ã©`
  - `è` (`\xC3\xA8`) became `Ã¨`
  - `à` (`\xC3\xA0`) became `Ã `
  - `ê` (`\xC3\xAA`) became `Ãª`
  - `É` (`\xC3\x89`) became `Ã‰`

### C. Unsupported Ligatures `œ` and `Œ` (`Å“` / Empty Boxes)
* **Cause**: In Windows-1252, `œ` is byte `0x9C` and `Œ` is `0x8C`. However, in `font_table_french.bin`, the entire range `0x80` to `0x9F` has zero metrics (`0.0`). Additionally, in UTF-8, `œ` is `\xC5\x93`, which rendered as `Å“`.
* **Correction**: Replaced with standard digraphs `oe` and `OE` (e.g. `oeufs`).

### D. Lowercase `ç` Rendered as Uppercase `Ç`
* **Cause**: In the original texture `hd_hankaku.dds` / `hd2_hankaku.dds` (Rev 1.10), cell `0xE7` (lowercase `ç`) was intentionally drawn as uppercase `Ç` by Byce61/Kaplas to prevent the cedilla tail from clipping into the line below. This is an intentional graphic design choice and does not require touching font DDS textures.

---

## 2. Exhaustive Inventory of Patched Files

All identified defects were cleaned in-place directly within the game data archives using [`tools/clean_patch_data.py`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/tools/clean_patch_data.py):

| Target Archive | Internal File | Defect Before | Cleaned Text |
|---|---|---|---|
| `boot.par` | `item.bin_c` | `Poulet au yuzu et soba dâ€™Ã©pinards` | `Poulet au yuzu et soba d'épinards` |
| `boot.par` | `item.bin_c` | `PiÃ¨ce dâ€™OVNI` | `Pièce d'OVNI` |
| `boot.par` | `item.bin_c` | `...ce que c'est avant dâ€™avoir tirer.` | `...ce que c'est avant d'avoir tiré.` |
| `boot.par` | `item.bin_c` | `...ennemis ayant beaucoup dâ€™argent.` | `...ennemis ayant beaucoup d'argent.` |
| `boot.par` | `item.bin_c` | `...extrÃªmement rare. Ã‰tant donnÃ© ses origines dâ€™un autre monde...` | `...extrêmement rare. Étant donné ses origines d'un autre monde...` |
| `boot.par` | `explanation_sub_story.bin_c` | `J'ai trouvÃ© le yakuza... â€¦ Trop compliquÃ© !` | `J'ai trouvé le yakuza... ... Trop compliqué !` |
| `boot.par` | `tips_tutorial.bin_c` | `La sÃ©curitÃ© a rÃ©solu le conflit...` (★, ★★, ★★★) | `La sécurité a résolu le conflit...` |
| `wdr.par` | `restaurant0006.bin` | `...sandwich au bacon, aux Å“ufs et Ã  la laitue...` | `...sandwich au bacon, aux oeufs et à la laitue...` |
| `wdr.par` | `uid010c1655.msg` | `...pendant lâ€™Ã©vÃ©nement ?...` | `...pendant l'événement ?...` |
| `wdr.par` | `uid010c1780.msg` | `Câ€™est lâ€™hopital qui se moque de la charitÃ©...` | `C'est l'hopital qui se moque de la charité...` |
| `wdr.par` | `uid010c16b0.msg` | Quête Leisure King (sÃ©curitÃ©, baissÃ©, problÃ¨mes) | Textes corrigés en Windows-1252 propre |
| `wdr.par` | `uid010c16be.msg` | Quête Electronics King | Textes corrigés en Windows-1252 propre |
| `wdr.par` | `uid010c16ce.msg` | Quête Gambling King | Textes corrigés en Windows-1252 propre |

---

## 3. Preservation of Offsets & SLLZ Recompression

1. **Full-Sentence Null Padding**: Because clean Windows-1252 strings are strictly shorter than their corrupted multi-byte UTF-8 counterparts, replacing full sentences and padding the difference with `\x00` ensures subsequent pointers and offsets do not shift.
2. **SLLZ Engine**: Compressed `.bin_c` files are recompressed using our bit-exact Python engine ([`tools/sllz.py`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/tools/sllz.py)), guaranteeing that the new stream fits inside the original archive slot size.
3. **PAR Table Synchronization**: The `CompressedSize` field in the PAR archive table is updated to reflect the new stream size, ensuring 100% integrity when read by the game engine.
