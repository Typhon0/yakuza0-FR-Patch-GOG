# Yakuza 0 GOG - French Translation Installation Guide (Rev 1.10.2)

This guide explains how to install the French fan-translation (VOSTFR Rev 1.10.2) on the **GOG DRM-free version** of **Yakuza 0**.

---

## 📋 Requirements

* The **Yakuza 0** game installed via **GOG** (GOG Galaxy or offline installer).
* **Python 3** installed on your system (if not already installed, free download from [python.org](https://www.python.org/) or Microsoft Store).
* The patch archive: **`Yakuza_0_Patch_FR_GOG_Rev1.10.1.7z`** (1.70 GB).

---

## 🚀 Windows Installation

1. **Locate your game installation folder**:
   * If using **GOG Galaxy**: Right click *Yakuza 0* in your library $\rightarrow$ *Manage installation* $\rightarrow$ *Show folder*.
   * Default path: `C:\GOG Games\Yakuza 0\` (or `D:\GOG Games\Yakuza 0\`).
   * Confirm that `Yakuza0.exe` is present in this folder.

2. **Extract the patch files**:
   * Open **`Yakuza_0_Patch_FR_GOG_Rev1.10.1.7z`** with 7-Zip or WinRAR.
   * Extract all contents directly into the game root folder.
   * When prompted by Windows, choose **"Replace files in the destination"**.

3. **Run the patcher**:
   * Double-click the file:
     ```cmd
     patch_gog.bat
     ```
   * The script automatically:
     - Backs up your original executable to **`Yakuza0.exe.bak`**.
     - Applies DRM-free instruction and subtitle bytecode patches.
     - Injects the French accented font kerning table (`é`, `è`, `à`, `ç`, `î`, etc.).
     - Preserves native Sega ASCII kerning so narrow glyphs (`i`, `l`) render properly.
     - Injects the PE `.trad` section and redirects UI string pointers to French text.
   * Press any key when prompted to exit.

4. **Launch the game**:
   * Start Yakuza 0 as usual through GOG Galaxy or directly via `Yakuza0.exe`.

---

## 🐧 Linux / Steam Deck Installation

1. Navigate to the game root folder (via Dolphin file manager or terminal).
2. Extract the archive contents into this folder, overwriting existing files when asked.
3. Open a terminal in the folder and run:
   ```bash
   chmod +x patch_gog.sh
   ./patch_gog.sh
   ```
4. The patch applies in seconds. You are now ready to launch the game.

---

## 🔄 Uninstallation / Reverting

To revert back to the unmodified English version:
1. Delete the patched `Yakuza0.exe`.
2. Rename `Yakuza0.exe.bak` back to `Yakuza0.exe`.
3. (Optional) In GOG Galaxy, use the **Verify / Repair** feature to restore all original game files.
