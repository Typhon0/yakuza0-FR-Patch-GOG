# Yakuza 0 - French Translation (VOSTFR) for GOG Edition

[![Platform](https://img.shields.io/badge/Platform-GOG_Galaxy_%7C_Windows_%7C_Linux_%7C_Steam_Deck-blue.svg)](#)
[![Version](https://img.shields.io/badge/Patch_Version-v1.12.9--gog-green.svg)](#)
[![Status](https://img.shields.io/badge/Status-100%25_Playable_%26_Crash--Free-success.svg)](#)
[![PAR Verification](https://img.shields.io/badge/PAR_Integrity-131%2F131_PASS-brightgreen.svg)](#)
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

Complete, standalone port and technical remaster of the unofficial French fan-translation (**VOSTFR Rev 1.10 / 1.11** by **Byce61 & the Yakuza RGG France team**), adapted, hardened and optimized specifically for the **DRM-free GOG release** of **Yakuza 0** (Build 3642285 / v1.015a).

#### Why was this port needed?
The original community patch was compiled strictly for the Steam release:
1. **DRM & Executable Incompatibility**: Distributing a modified Steam `Yakuza0.exe` broke launching on GOG, crashing or triggering infinite loops on the Chapter 1 pager message.
2. **Font Kerning Degradation**: Steam font injection overwrote Sega's native single-byte character metrics, causing narrow ASCII glyphs like `i` and `l` to collapse or vanish (*"Batte"* instead of *"Battle"*, *"Busness"* instead of *"Business"*).
3. **Encoding Glitches in Data Archives**: The original data archives contained typographic curved apostrophes exported in UTF-8 (`\xE2\x80\x99`), which the game engine read as Windows-1252 `\x99`, displaying ugly **Trade Mark `™`** symbols across dialogues and descriptions (`c™est`, `j™ai`, `d™argent`). Several files also suffered from UTF-8 accent mojibake (`Ã©`, `Ã¨`, `Ã `) and unsupported `œ` ligatures.
4. **Untranslated Content & Loose Files**: All 35 shop files, numerous minigames, cabaret club dialogue, battle banners, street ambient popups, and telephone save prompts remained in English or caused engine faults when modified naively.

#### What this project delivers:
* **Automated 64-bit PE Patcher (`patch_gog.py`)**: Seamlessly patches your legitimate GOG `Yakuza0.exe` in-place while keeping its 100% DRM-free status.
* **Vanilla ASCII Kerning Preservation**: Preserves native Sega metrics (`0x00–0x7F`) so all standard English letters and digits remain perfectly spaced, while injecting full French accented metrics (`0x80–0xFF`: `é`, `è`, `ê`, `à`, `ç`, `î`, `ï`, etc.) at `0xD488F0`.
* **100% Complete Localization Across All Game Archives**: Over 6,600 files across all archives (`boot.par`, `wdr.par`, `stay.par`, `pause.par`, `common.par`, `minigame/`) translated into natural French.
* **100% Localized Shops & Convenience Stores**: Injected 558 French item descriptions and shop UI dialogues across all 35 in-game stores (Poppo, Don Quijote, Kotobuki Drug, Ebisu Pawn, arms merchants) while preserving critical Pocket Circuit sub-tables.
* **Hardened Anti-Crash Engine & Bit-Exact Verification**:
  - **131/131 PAR Archives Certified**: 100% PASS via [`tools/verify_patch.py`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/tools/verify_patch.py).
  - **Zero Sectorial Drift**: 2,048-byte sector alignment strictly enforced across all archives, eliminating Kotobuki Drugstore crash `0x234B0` and save-load crash `0xA4526`.
  - **27 Standalone Loose Minigame Tables Normalized**: Raw RGG binary format (`0x20070319`) with twin `.bin` and `.bin_c` files, eliminating fishing crash `0x37177C` and strike crash `0x1093A4`.
  - **Length-Safe Scripts**: Space-padding and byte-exact offsets for telephone save booths (58 ASCII chars) and Bob Utsunomiya (27,575 bytes), preventing softlocks.
* **1-Click Portable Launcher**: Windows batch script with embedded standalone Python 3.12 (no Python installation required by the user) and Linux / Steam Deck shell script.

---

### 🎮 Translated Content (v1.12.9)

* **Main Story & Cutscenes**: 100% of story cutscenes, prerendered cinematics, and dialogues subtitled in natural French.
* **Combat & Progression**: 100% of abilities, battle styles (Brawler, Rush, Beast, Dragon of Dojima / Thug, Slugger, Breaker, Mad Dog of Shimano), all Heat Actions (*Essence of...*), masters, and combat evaluation ranks.
* **Substories & Side Content**: All 100 side quests fully translated for Kiryu and Majima (including Chapter 13 Oda cutscene and Substory 49 fixes).
* **Business & Management**: 100% localized Real Estate Royale (all 33 employees & Five Billionaires) and Cabaret Club Czar (all 30 hostesses & rival clubs).
* **In-Game Menus & UI**: Inventory, Equipment, CP Virtue Shrines, Pager messages, Controller overlays, System Settings, Save/Load.
* **Shops & Dining**: 100% of all 35 stores (Poppo, Don Quijote, Kotobuki Drug, Ebisu Pawn, arms dealers) with 558 translated item descriptions and merchant barks.
* **Minigames**: Pocket Circuit (parts & descriptions), Catfight Club, Poker opponents, and Fishing (inventory & capture popups).

#### 📌 Terms and Tables Intentionally Kept in Original Format (By Design & Safety):
To guarantee lore fidelity, respect official licensing, and prevent engine memory faults:
1. **Sega Arcade Classics**: Official titles and arcade cabinets (*Out Run*, *Space Harrier*, *Super Hang-On*, *Fantasy Zone*, *UFO Catcher*) preserve their worldwide commercial names.
2. **Licensed Music Tracks**: Licensed Disco songs and audio tracks (*I Wanna Take You Home*, *Friday Night*, etc.) preserve their original titles.
3. **Traditional Games Terminology**: Official Japanese/international rules and calls for Mahjong (*Riichi, Ippatsu, Ron, Tsumo, Dora*) and Shogi.
4. **Real-Life AV Idols**: Collectible cards and cast profiles preserve the authentic Japanese stage names of real-life actresses.
5. **Anti-Crash Engine Preservations**: Internal management tables for Cabaret Club Czar (`caba_cast_info.bin_c`, `cabaret_island_area.bin_c` in `stay.par`) and physical fish hitbox parameters (`fishing_fish_info.bin`) preserve original Sega GOG table layouts to permanently prevent memory access violations (`0x37177C`, `0x3711DB`, `0x1093A4`).

---

### 📥 Download

Choose between two distribution packages:

1. **Standard All-in-One Package (Recommended)**:
   - Includes embedded portable Python 3.12: **no prerequisites, zero setup**.
   - Archive: **`Yakuza0_FR_Patch_GOG_v1.12.9.zip`**
   - Available on **[GitHub Releases](../../releases/latest)** *(Primary Mirror)*

2. **Nexus Mods Pure Assets Edition**:
   - Guaranteed **100% pure assets (zero `.exe` bundled)** to eliminate antivirus false positives.
   - Requires Python 3 installed on Windows, or use manual drag-and-drop.
   - Archive: **`Yakuza0_FR_Patch_GOG_v1.12.9_Nexus_PureAssets_NoExe.zip`**
   - Available on **[Nexus Mods](https://www.nexusmods.com/yakuza0)**

---

### 🛠️ Installation Instructions

#### On Windows
1. Locate your Yakuza 0 GOG installation directory (e.g. `C:\GOG Games\Yakuza 0\` or via GOG Galaxy: *Manage Installation* $\rightarrow$ *Show folder*).
2. Extract the contents of **`Yakuza0_FR_Patch_GOG_v1.12.9.zip`** directly into the game root folder (where `Yakuza0.exe` is located), replacing files when prompted.
3. Double-click **`patch_gog.bat`**.
   - An automatic backup (`Yakuza0.exe.bak`) is created.
   - Read-only attributes (`+R`) are automatically unlocked.
   - The game executable is patched in seconds.
4. Launch Yakuza 0 through GOG Galaxy or directly via `Yakuza0.exe`. Enjoy!

#### On Linux / Steam Deck
1. Extract the archive into your game directory (e.g. `~/.local/share/Steam/steamapps/common/Yakuza 0/` or your Heroic / Lutris prefix).
2. Open a terminal in the folder and execute:
   ```bash
   chmod +x patch_gog.sh
   ./patch_gog.sh
   ```
3. Launch the game normally.

---

### 🔍 Verification & Diagnostics

The patch comes with built-in verification and diagnostic utilities:

* **Integrity Verifier**: Double-click `verify_patch.bat` (or run `python tools/verify_patch.py data`) to verify all 131 archives in under 30 seconds.
* **Instant Crash Diagnostic**: If you encounter an unexpected crash with Special K, run `diagnose_crash.bat` to run the native Rust diagnostic engine and identify the exact faulting instruction and table.

---

<a name="français"></a>
## 🇫🇷 Français

### 📖 À propos de ce projet

Portage complet, autonome, sécurisé et techniquement remastérisé de la traduction française non officielle (**VOSTFR Rev 1.10 / 1.11** par **Byce61 & l'équipe Yakuza RGG France**), adapté spécifiquement pour la version **GOG sans DRM** de **Yakuza 0** (Build 3642285 / v1.015a).

#### Pourquoi ce projet était-il nécessaire ?
La traduction originale avait été compilée exclusivement pour la version Steam :
1. **Incompatibilité DRM & Exécutable** : L'exécutable Steam fourni écrasait l'exécutable GOG, causant l'échec du lancement ou des freezes au Chapitre 1 lors de la réception du premier bipeur de Kiryu.
2. **Dégradation du Kerning de police** : L'injection Steam écrasait les métriques ASCII natives de Sega, provoquant la disparition ou l'écrasement des lettres étroites comme `i` et `l` (*« Batte »* au lieu de *« Battle »*, *« Busness »* au lieu de *« Business »*).
3. **Imperfections d'encodage dans les archives de données** : Des apostrophes courbes exportées en UTF-8 (`\xE2\x80\x99`) étaient interprétées en Windows-1252 comme `\x99`, affichant le symbole **Trade Mark `™`** dans les dialogues et descriptions (`c™est`, `j™ai`, `d™argent`). Plusieurs fichiers comportaient également du mojibake UTF-8 (`Ã©`, `Ã¨`, `Ã `) et des ligatures `œ` non gérées.
4. **Boutiques & Fichiers isolés non traduits** : Les 35 fichiers de boutiques (`shop0000.bin`–`shop0034.bin`) étaient laissés en anglais. Modifier ces fichiers ou les archives sans préserver les structures Sega provoquait des crashs bloquants (`0x234B0` à Kotobuki, `0x6EA328` aux cabines, `0x37177C` à la pêche).

#### Ce que propose ce dépôt :
* **Patcher PE 64-bit automatisé (`patch_gog.py`)** : Modifie proprement votre `Yakuza0.exe` GOG en conservant son statut 100% DRM-free.
* **Préservation intégrale du Kerning ASCII Sega** : Maintient les métriques Sega natives (`0x00–0x7F`) pour un espacement parfait des lettres et chiffres anglais, tout en injectant les métriques accentuées françaises (`0x80–0xFF` : `é`, `è`, `ê`, `à`, `ç`, `î`, `ï`, etc.) à l'offset `0xD488F0`.
* **Boutiques & Supérettes 100% localisées** : Injection de 558 descriptions d'objets françaises et des textes de dialogues d'achat/vente dans les 35 magasins du jeu (Poppo, Don Quijote, Kotobuki Drug, prêteurs sur gages Ebisu, marchands d'armes) tout en conservant les tables annexes indispensables du Pocket Circuit.
* **Traduction intégrale de toutes les archives de données** : Plus de 6 600 fichiers dans `boot.par`, `wdr.par`, `stay.par`, `pause.par`, `common.par`, et les mini-jeux traduits en français naturel.
* **Blindage Anti-Crash et Validation Bit-Exacte** :
  - **131/131 archives PAR certifiées conformes** (100% PASS via `tools/verify_patch.py`).
  - **Alignement sectoriel 2 048 octets strict** : élimine définitivement les crashs de streaming asynchrone (`0x234B0` en pharmacie, `0xA4526` au chargement).
  - **27 tables de mini-jeux isolées normalisées** : format binaire RGG brut (`0x20070319`) avec versions jumelles `.bin` et `.bin_c` (anti-crash pêche `0x37177C` et ferrage `0x1093A4`).
  - **Scripts à longueur protégée** : padding par espaces pour les cabines téléphoniques (58 caractères ASCII) et Bob Utsunomiya (27 575 octets), évitant les softlocks de machine à écrire Sega.
* **Lanceurs 1-clic** : Fichier batch Windows autonome (avec Python 3.12 portable embarqué, rien à installer) et script shell Linux / Steam Deck.

---

### 🎮 Contenu traduit (v1.12.9)

* **Histoire principale & cinématiques** : 100 % des cinématiques, vidéos animées et dialogues sous-titrés en français naturel.
* **Combat & Progression** : 100 % des arbres de compétences, styles de combat (Bagarreur, Fonceur, Brute, Dragon de Dojima / Voyou, Batteur, Danseur, Chien enragé de Shimano), toutes les Actions Heat (*Essence de...*), maîtres et évaluations de combat.
* **Quêtes secondaires (Substories)** : L'intégralité des 100 intrigues secondaires traduites pour Kiryu et Majima (correctifs de la cinématique d'Oda au Chapitre 13 et de la quête 49 inclus).
* **Gestion & Affaires** : 100 % de l'Immobilier de Kiryu (les 33 employés et les Cinq Rois) et du Cabaret Club Sunshine de Majima (les 30 hôtesses et les clubs rivaux).
* **Menu pause & Interface Système** : Inventaire, Équipement, Sanctuaire de Vertu (boutique CP), Bipeur, Commandes manette, Paramètres et Sauvegardes.
* **Boutiques & Restaurants** : 100 % des 35 commerces (Poppo, Don Quijote, Kotobuki Drug, Ebisu Pawn, marchands d'armes) avec 558 descriptions d'objets françaises et répliques de commerçants.
* **Mini-jeux** : Pocket Circuit (pièces et descriptions), Catfight Club, adversaires de Poker, et Pêche (inventaire et notifications de capture).

#### 📌 Éléments conservés en version originale (Par conception & sécurité) :
Pour respecter la fidélité au lore, les licences officielles et la stabilité absolue du moteur de jeu :
1. **Bornes & Classiques Arcade Sega** : Les titres officiels de jeux d'arcade (*Out Run*, *Space Harrier*, *Super Hang-On*, *Fantasy Zone*, *UFO Catcher*) conservent leurs noms commerciaux internationaux.
2. **Morceaux musicaux sous licence** : Les chansons sous licence du Disco (*I Wanna Take You Home*, *Friday Night*, etc.) conservent leurs titres originaux.
3. **Terminologie officielle des jeux traditionnels** : Les annonces et combinaisons officielles de Mahjong (*Riichi, Ippatsu, Ron, Tsumo, Dora*) et les règles de Shogi.
4. **Cartes d'Idoles réelles (AV)** : Les cartes de collection et fiches conservent les véritables noms de scène japonais des actrices.
5. **Tables sécurisées anti-crash** : Les tables internes de gestion du Cabaret Sunshine (`caba_cast_info.bin_c`, `cabaret_island_area.bin_c` dans `stay.par`) et les paramètres physiques des poissons (`fishing_fish_info.bin`) conservent leurs gabarits Sega d'origine pour éliminer définitivement les violations d'accès mémoire (`0x37177C`, `0x3711DB`, `0x1093A4`).

---

### 📥 Téléchargement

Deux packages de distribution sont disponibles :

1. **Package Tout-en-Un Standard (Recommandé)** :
   - Inclut Python 3.12 portable embarqué : **aucun prérequis, zéro installation**.
   - Fichier : **`Yakuza0_FR_Patch_GOG_v1.12.9.zip`**
   - Disponible sur **[Releases GitHub](../../releases/latest)** *(Lien direct)*

2. **Édition Pure Assets Nexus Mods** :
   - Garanti **100% fichiers de données (zéro `.exe` tiers)** pour éliminer les faux positifs d'antivirus.
   - Nécessite Python 3 installé sur Windows ou un simple copier-coller des dossiers.
   - Fichier : **`Yakuza0_FR_Patch_GOG_v1.12.9_Nexus_PureAssets_NoExe.zip`**
   - Disponible sur **[Nexus Mods](https://www.nexusmods.com/yakuza0)**

---

### 🛠️ Instructions d'installation

#### Sur Windows
1. Rendez-vous dans le dossier d'installation de votre jeu Yakuza 0 GOG (ex. `C:\GOG Games\Yakuza 0\` ou clic droit sur le jeu dans GOG Galaxy $\rightarrow$ *Gérer l'installation* $\rightarrow$ *Afficher le dossier*).
2. Extrayez le contenu de **`Yakuza0_FR_Patch_GOG_v1.12.9.zip`** directement à la racine du jeu (là où se trouve `Yakuza0.exe`), en remplaçant les fichiers existants si demandé.
3. Double-cliquez sur **`patch_gog.bat`**.
   - Une sauvegarde automatique (`Yakuza0.exe.bak`) est générée.
   - Les attributs de lecture seule (`+R`) sont levés automatiquement.
   - L'exécutable est patché en quelques secondes.
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

### 🔍 Vérification & Diagnostic

Le patch intègre des outils d'audit et de diagnostic autonomes :

* **Vérificateur d'intégrité** : Double-cliquez sur `verify_patch.bat` (ou exécutez `python tools/verify_patch.py data`) pour tester l'intégralité des 131 archives en moins de 30 secondes.
* **Diagnostic de crash instantané** : Si vous rencontrez un crash inattendu avec Special K, lancez `diagnose_crash.bat` pour identifier immédiatement l'instruction x86-64 en faute et la table RGG associée via le moteur d'analyse Rust `rgg_preflight`.

---

## 📁 Repository Structure / Structure du Dépôt

```
yakuza0-FR-Patch-GOG/
├── docs/                             # Documentation technique et guides
│   ├── DEBUG_KNOWLEDGE_BASE.md       # Base de connaissances de reverse engineering & solutions des crashs
│   ├── REVERSE_ENGINEERING_ATLAS.md  # Atlas technique d'architecture mémoire du moteur RGG (x86-64)
│   ├── INSTALLATION_FR.md            # Guide d'installation détaillé en français
│   ├── INSTALLATION_EN.md            # Detailed English installation guide
│   ├── TECHNICAL_SPEC.md             # Spécifications techniques & rétro-ingénierie (FR)
│   ├── TECHNICAL_SPEC_EN.md          # Technical specifications & reverse engineering (EN)
│   └── NEXUS_MOD_DESCRIPTION.md      # Fiche de présentation Nexus Mods (Bilingue)
│
├── patcher/                          # Fichiers sources du patcher exécutable
│   ├── patch_gog.py                  # Patcher binaire PE 64-bit autonome
│   ├── patch_gog.bat                 # Lanceur Windows 1-clic
│   ├── patch_gog.sh                  # Lanceur Linux / Steam Deck 1-clic
│   └── font_table_french.bin         # Table de crénage des métriques de police (0x80-0xFF)
│
├── tools/                            # Outils de développement, d'audit et de build
│   ├── build_release.py              # Générateur de release autonome avec test E2E intégré
│   ├── verify_patch.py               # Validateur autonome des 131 archives PAR
│   ├── crash_analyzer.py             # Analyseur intelligent de logs de crash Special K / RGG
│   ├── rgg_preflight/                # Crate Rust haute performance pour l'audit et le diagnostic
│   ├── rebuild_clean_boot_append.py  # Générateur propre de boot.par (modèle append-only 2048)
│   ├── rebuild_clean_stay_append.py  # Générateur propre de stay.par
│   ├── rebuild_clean_wdr_append.py   # Générateur propre de wdr.par
│   ├── translate_all_minigames.py    # Traducteur des tables de mini-jeux isolées (format brut)
│   ├── rebuild_all_shops_clean.py    # Reconstructeur de boutiques avec tables Pocket Circuit
│   └── sllz.py                       # Compresseur/décompresseur SLLZ pur Python optimisé
│
├── diagnose_crash.bat                # Lanceur Windows pour le diagnostic de crash rapide
├── .gitignore                        # Règles d'exclusion Git
├── LICENSE                           # Licence MIT
└── README.md                         # Documentation du projet (Bilingue EN/FR)
```

---

## 👏 Credits & Acknowledgements / Crédits

* **Byce61 & l'équipe Yakuza RGG France** : Projet original de traduction française (VOSTFR Rev 1.10).
  * [Chaîne YouTube Yakuza RGG France](https://www.youtube.com/channel/UCVhH_lJSjvyH_njkHQNxfBA)
* **Kaijin** : Édition graphique de l'interface, trames narratives, listes d'objets.
* **Sytchev_ & Kaplas** : Outils d'extraction et contributions techniques fondamentales.
* **SEGA / Ryu Ga Gotoku Studio** : Créateurs et développeurs de la saga Yakuza / Like a Dragon.
* **Typhon0** : Rétro-ingénierie PE x86-64, portage binaire GOG, moteur de crénage de police, alignement sectoriel PAR, normalisation des tables RGG et suite de diagnostic anti-crash.

---

## ⚖️ Legal Disclaimer / Mentions Légales

This project is an unofficial fan-translation port created strictly for educational, preservation, and non-commercial purposes. It is not affiliated with, endorsed, or sponsored by SEGA, Ryu Ga Gotoku Studio, or GOG. If you enjoy Yakuza 0, please support the franchise by purchasing the official game on GOG or Steam!
