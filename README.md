# Yakuza 0 - French Translation (VOSTFR) for GOG Edition

[![Platform](https://img.shields.io/badge/Platform-GOG_Galaxy_%7C_Windows_%7C_Linux_%7C_Steam_Deck-blue.svg)](#)
[![Version](https://img.shields.io/badge/Patch_Version-Rev_1.10.2--gog-green.svg)](#)
[![Original Mod](https://img.shields.io/badge/Original_Translation-Byce61_%2F_Yakuza_RGG_France-orange.svg)](https://www.youtube.com/channel/UCVhH_lJSjvyH_njkHQNxfBA)
[![Nexus Mods](https://img.shields.io/badge/Nexus_Mods-Available-lightgrey.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<p align="center">
  <b>Language / Langue :</b><br>
  <a href="#-english">🇬🇧 English</a> &bull;
  <a href="#-français">🇫🇷 Français</a>
</p>

---

<a name="english"></a>
## 🇬🇧 English

### 📖 About This Project

Complete, standalone port and technical remaster of the unofficial French fan-translation (**VOSTFR Rev 1.10** by **Byce61 & the Yakuza RGG France team**), adapted and optimized specifically for the **DRM-free GOG release** of **Yakuza 0** (Build 3642285 / v1.015a).

#### Why was this port needed?
The original community patch was built strictly for the Steam release:
1. **DRM & Executable Incompatibility**: Distributing a modified Steam `Yakuza0.exe` broke launching on GOG, crashing or triggering infinite loops on the Chapter 1 pager message.
2. **Font Kerning Degradation**: Steam font injection overwrote Sega's native single-byte character metrics, causing narrow ASCII glyphs like `i` and `l` to collapse or vanish (*"Batte"* instead of *"Battle"*, *"Busness"* instead of *"Business"*).
3. **Encoding Glitches in Data Archives**: The original data archives contained typographic curved apostrophes exported in UTF-8 (`\xE2\x80\x99`), which the game engine read as Windows-1252 `\x99`, displaying ugly **Trade Mark `™`** symbols across dialogues and descriptions (`c™est`, `j™ai`, `d™argent`). Several files also suffered from UTF-8 accent mojibake (`Ã©`, `Ã¨`, `Ã `) and unsupported `œ` ligatures.
4. **Untranslated In-Store Menus**: The original Steam patch left all 35 shop files (`shop0000.bin`–`shop0034.bin`) 100% in English, leaving convenience stores (Poppo, Don Quijote, pharmacies) with English item descriptions even though the player's inventory was translated.

#### What this project delivers:
* **Automated 64-bit PE Patcher (`patcher/patch_gog.py`)**: Seamlessly patches your legitimate GOG `Yakuza0.exe` in-place while keeping its 100% DRM-free status.
* **Vanilla ASCII Kerning Preservation**: Preserves native Sega metrics (`0x00–0x7F`) so all standard English letters and digits remain perfectly spaced, while injecting full French accented metrics (`0x80–0xFF`: `é`, `è`, `ê`, `à`, `ç`, `î`, `ï`, etc.).
* **100% Localized Shops & Convenience Stores (`tools/translate_shops.py`)**: Injected 558 French item descriptions and shop UI dialogues across all 35 in-game stores (Poppo, Don Quijote, Kotobuki Drug, Ebisu Pawn, arms merchants).
* **Capital Accent Normalization**: Automatically renders `Á` with the proper French grave accent `À` (`À vendre`), correcting legacy character map mismatches.
* **Automated Text & Mojibake Cleaner (`tools/clean_patch_data.py`)**: Corrects all `™` apostrophes, UTF-8 accent residues, truncated ellipsis, and unsupported ligatures directly in the game data archives (`boot.par`, `wdr.par`) with null-padded sentences and bit-exact SLLZ recompression (`tools/sllz.py`).
* **Dynamic `.trad` PE Section**: Injects a custom PE section to relocate localized UI strings via 64-bit pointer redirection.
* **1-Click Launchers**: Batch script for Windows (`patch_gog.bat`) and shell script for Linux / Steam Deck (`patch_gog.sh`).

---

### 🎮 Translated Content (Rev 1.10)

* **Main Story & Cutscenes**: 100% of story cutscenes, prerendered cinematics, and dialogues subtitled in French.
* **Substories**: Over 40 side quests fully translated for Kiryu and Majima.
* **In-Game Menus & UI**: Inventory, Equipment, Abilities, Pager, Completion List, System Settings.
* **Minigames & Side Content**: Real Estate Royale, Cabaret Club Czar, Telephone Club, Pocket Circuit, Fishing, Coliseum, Catfight, Mahjong, and Gambling Dens.
* **Master Training**: Complete combat style training dialogues (Bacchus, Kamoji, Miss Tatsu, Komeki, Fei Hu, Areshi).

---

### 📥 Download

Download the complete ready-to-use patch archive (1.70 GB):
* **[GitHub Releases](../../releases/latest)** *(Primary Mirror)*
* **[Nexus Mods](https://www.nexusmods.com/yakuza0)** *(Mod Page)*

File: **`Yakuza_0_Patch_FR_GOG_Rev1.10.3.7z`**

---

### 🛠️ Installation Instructions

#### On Windows
1. Locate your Yakuza 0 GOG installation directory (e.g. `C:\GOG Games\Yakuza 0\` or via GOG Galaxy: *Manage Installation* $\rightarrow$ *Show folder*).
2. Extract the contents of **`Yakuza_0_Patch_FR_GOG_Rev1.10.3.7z`** directly into the game folder, replacing files when prompted.
3. Double-click **`patch_gog.bat`**. A backup (`Yakuza0.exe.bak`) is created automatically, and the executable is patched in seconds.
4. Launch Yakuza 0 through GOG Galaxy or directly via `Yakuza0.exe`. Enjoy!

#### On Linux / Steam Deck
1. Extract the archive into your game directory (e.g. `~/.local/share/Steam/steamapps/common/Yakuza 0/` or your Heroic / Lutris wineprefix).
2. Open a terminal in the folder and execute:
   ```bash
   chmod +x patch_gog.sh
   ./patch_gog.sh
   ```
3. Launch the game normally.

---

### ⚙️ Technical Architecture

```
[Original GOG Executable]
       │
       ├──> 1. Automatic safety backup (Yakuza0.exe.bak)
       ├──> 2. Instruction bytecode hooks (Western 1-byte char rendering, DRM-free)
       ├──> 3. French font UV injection (0x80-0xFF) with Vanilla ASCII preservation (0x00-0x7F)
       ├──> 4. In-exe localized UI terms (REÇU, PERDU, NIV, N°)
       └──> 5. Append PE .trad section + redirect 64-bit .data pointers
                └──> [Patched & Fully Functional GOG Yakuza0.exe]
```

---

<a name="français"></a>
## 🇫🇷 Français

### 📖 À propos de ce projet

Portage complet, autonome et optimisé de la traduction française non officielle (**VOSTFR Rev 1.10** par **Byce61 & l'équipe Yakuza RGG France**), adapté spécifiquement pour la version **GOG sans DRM** de **Yakuza 0** (Build 3642285 / v1.015a).

#### Pourquoi ce projet était-il nécessaire ?
La traduction originale avait été compilée exclusivement pour la version Steam :
1. **Incompatibilité DRM & Exécutable** : L'exécutable Steam fourni écrasait l'exécutable GOG, causant l'échec du lancement ou des freezes au Chapitre 1 lors de la réception du premier bipeur de Kiryu.
2. **Dégradation du Kerning de police** : L'injection Steam écrasait les métriques ASCII natives de Sega, provoquant la disparition ou l'écrasement des lettres étroites comme `i` et `l` (*« Batte »* au lieu de *« Battle »*, *« Busness »* au lieu de *« Business »*).
3. **Imperfections d'encodage dans les archives de données** : Des apostrophes courbes exportées en UTF-8 (`\xE2\x80\x99`) étaient interprétées en Windows-1252 comme `\x99`, affichant le symbole **Trade Mark `™`** dans les dialogues et descriptions (`c™est`, `j™ai`, `d™argent`). Plusieurs fichiers comportaient également du mojibake UTF-8 (`Ã©`, `Ã¨`, `Ã `) et des ligatures `œ` non gérées.
4. **Boutiques & Supérettes non traduites** : Le patch Steam d'origine laissait les 35 fichiers de boutiques (`shop0000.bin`–`shop0034.bin`) entièrement en anglais. Les supérettes (Poppo, Don Quijote, pharmacies) affichaient des descriptions d'objets en anglais même si l'inventaire du joueur était traduit.

#### Ce que propose ce dépôt :
* **Patcher PE 64-bit automatisé (`patcher/patch_gog.py`)** : Modifie proprement votre `Yakuza0.exe` GOG en conservant son statut 100% DRM-free.
* **Préservation intégrale du Kerning ASCII Sega** : Maintient les métriques Sega natives (`0x00–0x7F`) pour un espacement parfait des lettres et chiffres anglais, tout en injectant les métriques accentuées françaises (`0x80–0xFF` : `é`, `è`, `ê`, `à`, `ç`, `î`, `ï`, etc.).
* **Boutiques & Supérettes 100% localisées (`tools/translate_shops.py`)** : Injection de 558 descriptions d'objets françaises et des textes de dialogues d'achat/vente dans les 35 magasins du jeu (Poppo, Don Quijote, Kotobuki Drug, prêteurs sur gages Ebisu, marchands d'armes).
* **Normalisation des accents majuscules** : Affichage garanti de l'accent grave sur `À` (`À vendre`), corrigeant les coquilles historiques de saisie (`Á`).
* **Nettoyage automatisé des textes & mojibake (`tools/clean_patch_data.py`)** : Corrige tous les `™`, résidus UTF-8, points de suspension et ligatures directement dans les archives PAR (`boot.par`, `wdr.par`) avec null-padding strict et recompression SLLZ bit-exacte (`tools/sllz.py`).
* **Section PE `.trad` dynamique** : Injecte une section PE dédiée pour relocaliser les chaînes d'interface en français via redirection de pointeurs 64-bit dans `.data`.
* **Lanceurs 1-clic** : Fichier batch pour Windows (`patch_gog.bat`) et script shell pour Linux / Steam Deck (`patch_gog.sh`).

---

### 🎮 Contenu traduit (Rev 1.10)

* **Histoire principale & cinématiques** : 100 % des cinématiques, vidéos animées et dialogues sous-titrés en français.
* **Quêtes secondaires (Substories)** : Plus de 40 quêtes secondaires traduites pour Kiryu et Majima.
* **Menu pause en jeu** : Inventaire, Équipement, Aptitudes, Bipeur, Réalisations et paramètres.
* **Mini-jeux & Activités** : L'agence immobilière de Kiryu, le Cabaret Club de Majima, Téléphone Club, Pocket Circuit, pêche, combats clandestins, Mahjong et tripots.
* **Entraînements & Maîtres** : Tous les dialogues d'apprentissage de style (Bacchus, Kamoji, Miss Tatsu, Komeki, Fei Hu, Areshi).

---

### 📥 Téléchargement

Téléchargez l'archive complète du patch (1,70 Go) :
* **[Releases GitHub](../../releases/latest)** *(Lien direct)*
* **[Nexus Mods](https://www.nexusmods.com/yakuza0)** *(Page du mod)*

Fichier : **`Yakuza_0_Patch_FR_GOG_Rev1.10.3.7z`**

---

### 🛠️ Instructions d'installation

#### Sur Windows
1. Rendez-vous dans le dossier d'installation de votre jeu Yakuza 0 GOG (ex. `C:\GOG Games\Yakuza 0\` ou clic droit sur le jeu dans GOG Galaxy $\rightarrow$ *Gérer l'installation* $\rightarrow$ *Afficher le dossier*).
2. Extrayez tout le contenu de **`Yakuza_0_Patch_FR_GOG_Rev1.10.3.7z`** directement à la racine du jeu (acceptez de remplacer les fichiers existants).
3. Double-cliquez sur **`patch_gog.bat`**. Une sauvegarde `Yakuza0.exe.bak` est créée automatiquement et l'exécutable est patché en 2 secondes.
4. Lancez le jeu via GOG Galaxy ou directement via `Yakuza0.exe`. Bon jeu !

#### Sur Linux / Steam Deck
1. Extrayez l'archive dans le dossier du jeu (ex. `~/.local/share/Steam/steamapps/common/Yakuza 0/` ou votre dossier Heroic / Lutris).
2. Ouvrez un terminal dans le dossier et lancez :
   ```bash
   chmod +x patch_gog.sh
   ./patch_gog.sh
   ```
3. Lancez le jeu normalement.

---

## 📁 Repository Structure / Structure du Dépôt

```
yakuza0-FR-Patch-GOG/
├── docs/                             # Technical documentation & guides
│   ├── INSTALLATION_FR.md            # French installation guide
│   ├── INSTALLATION_EN.md            # English installation instructions
│   ├── TECHNICAL_SPEC.md             # Spécifications techniques & rétro-ingénierie (FR)
│   ├── TECHNICAL_SPEC_EN.md          # Technical specifications & reverse engineering (EN)
│   ├── AUDIT_IMPERFECTIONS_TEXTUELLES.md # Audit technique des anomalies de texte & d'encodage (FR)
│   ├── TEXT_ENCODING_AUDIT_EN.md     # Technical audit of encoding defects (TM, mojibake, ligatures) (EN)
│   └── NEXUS_MOD_DESCRIPTION.md      # Nexus Mods presentation template (Bilingual BBCode & Markdown)
│
├── patcher/                          # Core patcher runtime files
│   ├── patch_gog.py                  # Standalone 64-bit PE binary patcher
│   ├── patch_gog.bat                 # 1-click Windows launcher
│   ├── patch_gog.sh                  # 1-click Linux / Steam Deck launcher
│   ├── font_table_french.bin         # Accented character font kerning metrics (0x80-0xFF)
│   ├── INSTALLATION_GOG_FR.txt       # Player installation text guide (French)
│   └── INSTALLATION_GOG_EN.txt       # Player installation text guide (English)
│
├── tools/                            # Developer, research & data cleaning utilities
│   ├── translate_shops.py            # Automated shop & convenience store translator
│   ├── clean_patch_data.py           # Automated text & mojibake cleaner for PAR archives
│   ├── sllz.py                       # Pure Python SLLZ compressor/decompressor (1:1 with Kaplas)
│   ├── research/                     # Reverse engineering, PE disassembly, PAR & font tools
│   ├── diff_y0_gog.diff              # File tree diff between Steam and GOG
│   └── french_patch_files.txt        # Translated asset manifest from original patch
│
├── .gitignore                        # Git exclusion rules
├── LICENSE                           # MIT License
└── README.md                         # Project documentation (Bilingual EN/FR)
```

---

## 👏 Credits & Acknowledgements / Crédits

* **Byce61 & l'équipe Yakuza RGG France** : Original French translation project (VOSTFR Rev 1.10).
  * [YouTube Channel Yakuza RGG France](https://www.youtube.com/channel/UCVhH_lJSjvyH_njkHQNxfBA)
* **Kaijin** : Graphical UI editing, storylines, item lists.
* **Sytchev_ & Kaplas** : Extraction tools and foundational technical contributions.
* **SEGA / Ryu Ga Gotoku Studio** : Creators and developers of the Yakuza / Like a Dragon series.
* **Typhon0** : PE reverse-engineering, GOG binary port, kerning preservation engine, automated text cleaner, and cross-platform patcher.

---

## ⚖️ Legal Disclaimer / Mentions Légales

This project is an unofficial fan-translation port created strictly for educational, preservation, and non-commercial purposes. It is not affiliated with, endorsed, or sponsored by SEGA, Ryu Ga Gotoku Studio, or GOG. If you enjoy Yakuza 0, please support the franchise by purchasing the official game on GOG or Steam!
