===================================================================
  FRENCH TRANSLATION PATCH (VOSTFR) FOR YAKUZA 0 - GOG EDITION (Rev 1.10)
===================================================================

Original Translation (Steam): Byce61 & Yakuza RGG France team
Original Tools: Kaplas80 (TranslationFramework2)
GOG Port Research: L@Zar0 (author of the Spanish GOG port)
GOG Patcher & Adaptation: Antigravity & the community

This mod adapts the complete French fan-translation (Rev 1.10) of Yakuza 0
for the GOG DRM-free edition (v1.015a / Build 3642285), featuring full
support for Western accented characters (é, è, à, ç, etc.) and complete stability.

-------------------------------------------------------------------
INSTALLATION (WINDOWS)
-------------------------------------------------------------------

1. Open your Yakuza 0 GOG game installation folder.
   (Default: C:\GOG Games\Yakuza 0\)

2. Extract and copy all contents of this archive:
   - "data" folder
   - "patch_gog.py"
   - "patch_gog.bat"
   - "patch_gog.sh"
   - "font_table_french.bin"
   directly into your Yakuza 0 game root directory (where Yakuza0.exe is located).
   
   When prompted, choose to OVERWRITE / REPLACE all existing files.

3. Double-click "patch_gog.bat" (or run: python patch_gog.py Yakuza0.exe).
   
   The patcher will automatically:
   - Create a safe backup: "Yakuza0.exe.bak"
   - Inject the French font UV coordinate table
   - Apply the assembly bytecode patches for single-byte ANSI font rendering
   - Configure French menus and chapter titles

4. Launch the game normally via GOG Galaxy or directly through Yakuza0.exe!

-------------------------------------------------------------------
INSTALLATION (LINUX / STEAM DECK)
-------------------------------------------------------------------

1. Copy the patch files into your game directory in your Wine / Heroic / Lutris prefix.
2. Open a terminal in the folder and run:
   ./patch_gog.sh
3. Launch the game through your launcher.

-------------------------------------------------------------------
NOTES
-------------------------------------------------------------------
- Never overwrite Yakuza0.exe with a Steam executable; the Steam binary requires
  Steamworks dependencies that do not exist on GOG. Always use the provided patcher.
- 5 to 6 in-game dynamic arcade banners ("Ability Acquired", "Congratulations!"
  on UFO Catchers, "GAME ON!" in Darts) remain in English due to hardcoded
  letter-by-letter rendering in the 2D engine.
- To revert to vanilla, delete Yakuza0.exe and rename Yakuza0.exe.bak to Yakuza0.exe.
