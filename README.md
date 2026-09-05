# Yakuza 0 - Patch Français (VOSTFR) pour la version GOG

[![Platform](https://img.shields.io/badge/Platform-GOG_Galaxy_%7C_Windows_%7C_Linux_%7C_Steam_Deck-blue.svg)](#)
[![Version](https://img.shields.io/badge/Patch_Version-Rev_1.10--gog-green.svg)](#)
[![Original Mod](https://img.shields.io/badge/Original_Translation-Byce61_%2F_Yakuza_RGG_France-orange.svg)](https://www.youtube.com/channel/UCVhH_lJSjvyH_njkHQNxfBA)
[![Nexus Mods](https://img.shields.io/badge/Nexus_Mods-Available-lightgrey.svg)](#)

Portage complet et optimisé de la traduction française non-officielle (VOSTFR Rev 1.10) réalisée par **Byce61 & l'équipe Yakuza RGG France**, adapté pour la version **GOG sans DRM** de **Yakuza 0** (Build 3642285 / v1.015a).

---

## 📖 À propos de ce projet

La traduction de Byce61 et de son équipe a été conçue à l'origine exclusivement pour la version Steam du jeu. L'exécutable Steam fourni écrasait l'exécutable GOG, causant l'échec du lancement du jeu (en raison de l'absence des DRM Steam) ou des freezes au Chapitre 1 lors de la réception du premier message sur le bipeur. De plus, une injection naïve des polices Steam écrasait les marges ASCII natives du moteur Sega, provoquant la disparition ou l'écrasement de caractères étroits comme `i` et `l` (*« Batte »* au lieu de *« Battle »*, *« Busness »*, etc.).

Ce dépôt propose :
1. **Un patcher d'exécutable PE 64-bit automatisé** (`patch_gog.py`) qui patche proprement votre `Yakuza0.exe` GOG sans altérer son statut DRM-free.
2. **Un correctif complet de rendu de police (Kerning / UV Table)** : les glyphes ASCII Sega vanilla (0x00–0x7F) sont préservés pour garantir un espacement parfait de toutes les lettres anglaises et chiffres, tandis que l'ensemble des caractères français accentués (0x80–0xFF : `é`, `è`, `ê`, `à`, `ç`, `î`, `ï`, etc.) sont injectés avec les marges de tige corrigées.
3. **Un nettoyage automatisé des imperfections textuelles & d'encodage** : correction intégrale des apostrophes typographiques corrompues affichant le symbole `™` (`c™est`, `j™ai`, `d™argent`), des résidus d'encodage UTF-8 (`Ã©`, `Ã¨`, `Ã `, `Ã‰`), des points de suspension et des ligatures `œ` (`oeufs`).
4. **Une section `.trad` dédiée** : ajoutée dynamiquement dans l'en-tête PE pour relocaliser les chaînes d'interface en français via redirection de pointeurs 64-bit dans `.data`.
5. **Des lanceurs 1-clic** pour Windows (`patch_gog.bat`) et Linux / Steam Deck (`patch_gog.sh`).

---

## 🎮 Contenu traduit (Rev 1.10)

* **Histoire principale & cinématiques** : 100 % des cinématiques, vidéos animées et dialogues sous-titrés en français.
* **Quêtes secondaires (Substories)** : Plus de 40 quêtes secondaires traduites pour Kiryu et Majima.
* **Menu pause en jeu** : Inventaire, Équipement, Aptitudes, Bipeur, Réalisations et aides de jeu.
* **Mini-jeux & Activités** : L'agence immobilière de Kiryu, le Cabaret Club de Majima (scénarios, hôtesses, gestion), Téléphone Club, pêche, combats clandestins, et plus encore.
* **Entraînements & Maîtres** : Tous les dialogues d'apprentissage de style (Bacchus, Kamoji, Miss Tatsu, Komeki, Fei Hu, Areshi).

---

## 📥 Téléchargement

Vous pouvez télécharger l'archive complète du patch (1,74 Go) :
* Sur **[Nexus Mods](https://www.nexusmods.com/yakuza0)** *(Page du mod)*
* Sur la page **[Releases GitHub](../../releases/latest)**

Fichier à télécharger : **`Yakuza_0_Patch_FR_GOG_Rev1.10.7z`**

---

## 🛠️ Instructions d'installation

### Sur Windows

1. Rendez-vous dans le dossier d'installation de votre jeu Yakuza 0 GOG :
   * *Exemple par défaut :* `C:\GOG Games\Yakuza 0\` (ou votre bibliothèque GOG Galaxy).
2. Ouvrez l'archive **`Yakuza_0_Patch_FR_GOG_Rev1.10.7z`** et extrayez tout son contenu directement dans le dossier du jeu :
   * Acceptez de remplacer les fichiers lorsque Windows vous le demande.
3. Double-cliquez sur le fichier **`patch_gog.bat`** :
   * Une sauvegarde de sécurité **`Yakuza0.exe.bak`** est créée automatiquement.
   * L'exécutable GOG est patché en 2 secondes.
4. Lancez le jeu via GOG Galaxy ou directement via `Yakuza0.exe`. Bon jeu !

### Sur Steam Deck / Linux

1. Extrayez l'archive dans le dossier du jeu :
   * *Exemple :* `~/.local/share/Steam/steamapps/common/Yakuza 0/` ou votre dossier Heroic Games / Lutris.
2. Ouvrez un terminal dans le dossier du jeu et exécutez :
   ```bash
   chmod +x patch_gog.sh
   ./patch_gog.sh
   ```
3. Lancez le jeu normalement.

---

## ⚙️ Détails techniques du portage

```
[Exécutable GOG original]
       │
       ├──> 1. Sauvegarde automatique (Yakuza0.exe.bak)
       ├──> 2. Patchs bytecode d'instructions (rendu des sous-titres, DRM-free)
       ├──> 3. Injection table de police (0x80-0xFF) avec préservation ASCII (0x00-0x7F)
       ├──> 4. Patch direct de termes in-exe (REÇU, PERDU, NIV, N°)
       └──> 5. Création section PE .trad + redirection des pointeurs .data
                └──> [Yakuza0.exe GOG Patché & Fonctionnel]
```

### 1. Fix du freeze au Chapitre 1 (Bipeur de Kiryu)
Sur la version Steam, le patch appliquait un hook spécifique qui provoquait une corruption mémoire et un crash instantané lors de l'affichage du premier message sur le bipeur sur la version GOG. Ce patch réécrit les offsets d'instructions pour cibler avec précision la mémoire du binaire GOG 64-bit.

### 2. Préservation du Kerning ASCII (Sega Vanilla)
L'exécutable Steam moddé contenait des marges manuelles (`0.6875` gauche / `0.75` droite) qui provoquaient un décalage de -16px des glyphes étroits sur le binaire GOG, écrasant les lettres `i` et `l`. Le patcher GOG injecte uniquement la table pour les caractères étendus (`0x80` à `0xFF`) et restaure les marges natives `[0.0, 1.17, ...]` pour les `î` et `ï`.

---

## 📁 Structure du Dépôt

```
yakuza0-FR-Patch-GOG/
├── docs/                             # Documentation détaillée & templates
│   ├── AUDIT_IMPERFECTIONS_TEXTUELLES.md # Audit technique des anomalies de texte & d'encodage
│   ├── INSTALLATION_FR.md            # Guide d'installation complet en français
│   ├── INSTALLATION_EN.md            # English installation instructions
│   ├── NEXUS_MOD_DESCRIPTION.md      # Page de présentation Nexus Mods (BBCode & Markdown)
│   └── TECHNICAL_SPEC.md             # Spécifications techniques & rétro-ingénierie
│
├── patcher/                          # Fichiers du patcher & lanceurs
│   ├── patch_gog.py                  # Script Python de modification du PE 64-bit
│   ├── patch_gog.bat                 # Lanceur Windows 1-clic
│   ├── patch_gog.sh                  # Lanceur Linux / Steam Deck
│   ├── font_table_french.bin         # Table de kerning des caractères accentués (0x80-0xFF)
│   ├── INSTALLATION_GOG_FR.txt       # Guide texte pour les joueurs
│   └── README_GOG_EN.txt             # English text readme
│
├── tools/                            # Utilitaires d'analyse, de nettoyage et de recherche
│   ├── clean_patch_data.py           # Nettoyage automatique des textes & mojibake dans les archives PAR
│   ├── sllz.py                       # Compresseur/décompresseur SLLZ pur Python 1:1 Kaplas
│   ├── research/                     # Scripts d'extraction PE, parsing PAR, SLLZ & textures
│   ├── diff_y0_gog.diff              # Diff d'arborescence GOG vs Steam
│   └── french_patch_files.txt        # Liste des fichiers traduits par l'équipe d'origine
│
├── .gitignore                        # Exclusion des assets de 1,8 Go et archives
├── LICENSE                           # Licence MIT & mentions légales fan-traduction
```

---

## 👏 Crédits & Remerciements

* **Byce61 & l'équipe Yakuza RGG France** : Traduction française originale complète (VOSTFR Rev 1.10).
  * [Chaîne YouTube Yakuza RGG France](https://www.youtube.com/channel/UCVhH_lJSjvyH_njkHQNxfBA)
* **Kaijin** : Retouche des interfaces graphiques, scénarios et listes d'objets.
* **Sytchev_ & Kaplas** : Outils d'extraction et contribution initiale au projet de traduction.
* **SEGA / Ryu Ga Gotoku Studio** : Développeurs et éditeurs de l'incroyable chef-d'œuvre Yakuza 0.
* **Typhon0** : Ingénierie inverse PE, portage binaire GOG, fix de kerning de police et patcher multiplateforme.

---

## ⚖️ Mentions légales

Ce projet est une fan-traduction non officielle à but strictement bénévole et non commercial. Il n'est en aucun cas affilié, sponsorisé ou approuvé par SEGA ou Ryu Ga Gotoku Studio. Si vous aimez le jeu, soutenez ses créateurs en achetant la version officielle sur GOG ou Steam !
