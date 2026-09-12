# Base de Connaissances Technique & Retex de Débogage — Yakuza 0 GOG

> **DOCUMENT DE RÉFÉRENCE CRITIQUE POUR LES AGENTS IA ET DÉVELOPPEURS**  
> Ce document consigne l'intégralité des découvertes, causes racines, rétro-ingénieries et règles impératives établies lors des sessions de débogage du portage du patch FR sur la version GOG de Yakuza 0 (v1.015a).  
> **IL EST FORMELLEMENT INTERDIT DE REPRODUIRE LES ERREURS DOCUMENTÉES CI-DESSOUS.**

---

## Sommaire
1. [Crash Pharmacie / Drugstore (`0x234B7`)](#1-crash-pharmacie--drugstore-0x234b7)
2. [Crash Chargement de Sauvegarde & Streaming (`0xA4526` / `SOUND_ID`)](#2-crash-chargement-de-sauvegarde--streaming-0xa4526--sound_id)
3. [Softlock de Bob Utsunomiya 0 (`uid00331696.msg` & `uid003316a2.msg`)](#3-softlock-de-bob-utsunomiya-0-uid00331696msg--uid003316a2msg)
4. [Anomalie de Typographie & Crénage de Police (`0x140397020`)](#4-anomalie-de-typographie--crénage-de-police-0x140397020)
5. [Bulles d'Ambiance de Rue (`ai_popup.bin`)](#5-bulles-dambiance-de-rue-ai_popupbin)
6. [Résumés de Quête du Menu Pause & Bannières (`boot.par`)](#6-résumés-de-quête-du-menu-pause--bannières-bootpar)
7. [Architecture des Archives PAR & Règle des 2048 Octets](#7-architecture-des-archives-par--règle-des-2048-octets)
8. [Crash Boucle Infinie des Cabines & Faux Déploiement (`0x6EA328`)](#8-crash-boucle-infinie-des-cabines--faux-déploiement-0x6ea328)
9. [Matrice des Commandes de Validation](#9-matrice-des-commandes-de-validation)
10. [Catalogue des Anti-Patterns & Erreurs Récurrentes d'Agents IA](#10-catalogue-des-anti-patterns--erreurs-récurrentes-dagents-ia)

---

## 1. Crash Pharmacie / Drugstore (`0x234B7`)

### Symptômes
Crash instantané `EXCEPTION_ACCESS_VIOLATION` à `Yakuza0.exe+0x234B7` dès que Kiryu entre dans la pharmacie Kotobuki Drugs (ou Daikoku Drugstore) et que le menu d'achat s'ouvre.

### Cause Racine
Les fichiers de boutique (`shop0000.bin` à `shop0034.bin`, `ex_shop0000.bin`) ne contiennent pas uniquement une liste d'articles :
* Deux boutiques en particulier contiennent une table annexe propriétaire de catégories Pocket Circuit immédiatement après la liste d'articles :
  - **`shop0013.bin` (Kotobuki Drugs) :** Table annexe de **24 octets**.
  - **`shop0029.bin` (Daikoku Drugstore) :** Table annexe de **20 octets**.
* L'ancien script de traduction considérait que tous les fichiers de boutique avaient une structure plate. Il tronquait les fichiers ou écrasait ces octets avec du texte français.
* Le moteur de rendu de boutique interprétait les octets de texte ASCII comme des identifiants de textures. Il passait un pointeur `NULL` à la routine de décompression SLLZ pour charger `2d_yk_staminan_lite.dds`, déclenchant le crash à `0x234B7`.

### Règle Impérative & Solution
* **NE JAMAIS tronquer les fichiers de boutique.**
* Utiliser exclusivement le générateur dédié [`tools/rebuild_all_shops_clean.py`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/tools/rebuild_all_shops_clean.py) qui préserve à l'octet près les tables annexes de 24 et 20 octets.
* Recompresser les boutiques en SLLZ natif avec l'indicateur compressé `flags = 0x80000000` (les fichiers non compressés dans l'original Sega restent non compressés avec `flags = 0x0`).

---

## 2. Crash Chargement de Sauvegarde & Streaming (`0xA4526` / `SOUND_ID`)

### Symptômes
Crash `EXCEPTION_ACCESS_VIOLATION` à `Yakuza0.exe+0xA4526` ou erreur critique de lecture audio (`SOUND_ID` invalide) lors du chargement d'une partie sauvegardée ou lors du passage de scènes avec des PNJ errants.

### Cause Racine
* L'archive [`stay.par`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/release_gog/data/staypar/stay.par) contient des fichiers audio de streaming et des tables de réponse (`response_wanderer.bin_c` positionné à l'offset exact `0x9a000`).
* Les outils tiers qui recompilent naïvement les archives PAR de manière séquentielle compactent les données et décalent les offsets internes des fichiers non modifiés.
* Dès que le moteur graphique et sonore tente de streamer `response_wanderer.bin_c` via DMA/mmap en se fiant à un offset absolu ou sectoriel, il lit de la mémoire non alignée ou un autre fichier, provoquant le crash.

### Règle Impérative & Solution
* **Architecture Append-Only alignée sur 2 048 octets :**
  - Conserver les données d'origine Sega **rigoureusement intactes** dans les premiers secteurs de l'archive.
  - Tous les fichiers modifiés sont ajoutés à la fin de l'archive (`append-only`), chacun aligné sur une frontière de secteur de **2 048 octets** :
    $$\text{offset\_aligné} = (\text{offset} + 2047) \ \& \sim 2047$$
  - Mettre à jour la table d'en-tête (32 octets par fichier) avec le nouvel offset et la taille compressée/décompressée.
* Scripts validés : [`tools/rebuild_clean_stay_append.py`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/tools/rebuild_clean_stay_append.py) et [`tools/rebuild_clean_boot_append.py`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/tools/rebuild_clean_boot_append.py).

---

## 3. Softlock de Bob Utsunomiya 0 (`uid00331696.msg` & `uid003316a2.msg`)

### Symptômes
Bob Utsunomiya 0 parle en français, mais lorsqu'il prononce la réplique *« Mais c'est offert pour toi, tu sais ? »*, le jeu se bloque complètement : aucune boîte de dialogue suivante n'apparaît, le joueur est figé en cinématique (softlock).

### Cause Racine
* Les fichiers de script de dialogue (`.msg`) contiennent du bytecode compilé avec des offsets d'adresses relatifs 32-bit pour les sauts conditionnels (`JMP`, `CALL`) et les appels d'événements de distribution d'objets.
* Le patch Steam d'origine de Byce61 avait augmenté la taille de `uid00331696.msg` de +36 octets, décalant les pointeurs de saut du script. L'interpréteur de dialogue atterrissait sur un opcode invalide.
* **Le piège du null-padding (`\x00`) :** Si l'on remplace une réplique anglaise par une réplique française plus courte en complétant avec des octets nuls `\x00`, le moteur interprète `\x00` comme la fin prématurée du flux de script (`EOF`/`TERMINATE`) avant d'exécuter l'instruction qui donne l'objet et rend le contrôle au joueur.

### Règle Impérative & Solution
* **Taille décompressée bit-exacte :** Le fichier décompressé doit faire **exactement 27 575 octets** pour `uid00331696.msg` (Kiryu) et pour `uid003316a2.msg` (Majima).
* **Remplacement avec Space-Padding (`b' '`) :** Pour les dialogues de Bob, les chaînes françaises plus courtes doivent être complétées par des espaces (`0x20`), suivis d'un unique octet nul `\x00` :
  ```python
  padded = fr_bytes + b' ' * (len(en_bytes) - len(fr_bytes)) + b'\x00'
  ```
* Seuls les mots-clés d'interface stricts (`Save`, `Cancel`, `Use the Item Box`, `Yes`, `Create`, `Caution!`) utilisent un null-padding direct.
* Recompresser en SLLZ natif (`flags = 0x80000000`).

---

## 4. Anomalie de Typographie & Crénage de Police (`0x140397020`)

### Symptômes
1. Les lettres étroites `i` et `l` se chevauchent et s'écrasent sur la lettre suivante (ex : *« utilisez »* avec `il` et `is` superposés, *« depuis »* avec `is` collé).
2. Trous visuels disproportionnés autour des lettres accentuées et des points (ex : *« té  léphone . »*).

### Cause Racine (Reverse Engineering du Moteur Graphique)
Dans `Yakuza0.exe` (section `.rdata` à l'offset `0xD488F0`), la table de métriques de police stocke 6 valeurs flottantes 32-bit pour chaque caractère ASCII (`0x00` à `0xFF`) :
```
[top_left, top_right, mid_left, mid_right, bot_left, bot_right]
```
La fonction de crénage proportionnel (`0x140397020`) calcule la translation appliquée entre deux caractères consécutifs $C_1$ et $C_2$ :
$$\text{min\_gap} = \min(R_{\text{top}}(C_1) + L_{\text{top}}(C_2),\; R_{\text{mid}}(C_1) + L_{\text{mid}}(C_2),\; R_{\text{bot}}(C_1) + L_{\text{bot}}(C_2))$$
$$\text{réduction} = \text{min\_gap} \times 0.5 \times \frac{\text{font\_size}}{2}$$
$$\text{Avance}(C_1 \to C_2) = \text{Base\_Advance (16.0 px)} - \text{réduction}$$

* **Le bug de Sega Vanilla GOG :**
  Pour `i` (`0x69`) et `l` (`0x6C`), Sega avait défini : `[0.0, 1.17, 0.0, 1.17, 0.0, 1.17]`.
  - Le `Right = 1.17` était énorme : sur le caractère suivant, la réduction atteignait **11.76 px**, ne laissant que **4.2 px** d'avance sur une cellule de 16 px. La lettre suivante s'imprimait directement par-dessus le `i` !
  - Le `Left = 0.0` empêchait le caractère précédent d'approcher (avance gonflée à 15 px), créant un vide anormal à gauche.
* **Le bug du patch partiel :**
  En ne patchant que `0x80-0xFF` avec les métriques Steam de Byce61, `é` (Byce61) suivi de `l` (Sega Vanilla à $L=0.0$) donnait une avance de **14.8 px** (trou visible dans `té  léphone`), tandis que le point `.` sans marge gauche inférieure créait un vide avant la ponctuation.

### Règle Impérative & Solution
* **Table typographique étalonnée complète (6 144 octets, `0x00` à `0xFF`) :**
  - **`i`, `l`, `I`** : Centrer symétriquement les marges à `[0.4, 0.4, 0.4, 0.4, 0.4, 0.4]`. L'avance est alors stable entre **9.6 px et 11.6 px** (zéro chevauchement, lisibilité parfaite).
  - **Variantes accentuées (`î`, `ï`, `ì`, `í`, `Î`, `Ï`, `Ì`, `Í`)** : Calibrées à l'identique à `[0.4, 0.4, 0.4, 0.4, 0.4, 0.4]`.
  - **Voyelles accentuées (`é`, `è`, `ê`, `à`, `ç`...)** : Métriques calquées sur leurs bases non accentuées (`e`, `a`...).
  - **Point `.` (`0x2E`)** : Marge inférieure gauche fixée à `0.4` pour coller naturellement aux fins de phrases.
  - **Cabines téléphoniques (`wdr.par`)** : Utiliser impérativement du space-padding (`b' '`) avec la formule sans accents (ex : `"Sauvegardez et utilisez le coffre depuis une\r\ncabine.     "`) pour atteindre pile les 58 caractères sans déclencher le piège UTF-8.
* Le fichier [`release_gog/font_table_french.bin`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/release_gog/font_table_french.bin) et [`patcher/patch_gog.py`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/patcher/patch_gog.py) appliquent cette table sur l'intégralité des 256 caractères.

---

## 4b. Softlock des Cabines Téléphoniques (`uid033317d1.msg` à `uid033317e4.msg`)

### Symptômes
En approchant d'une cabine téléphonique, Kiryu déclenche la première réplique d'aide (*« Sauvegardez et utilisez le coffre... »*). Le glyphe `[E]` apparaît en bas à droite, mais le jeu refuse d'avancer : le menu de choix (*Sauv / Ouvrir le coffre / Retour*) ne s'ouvre jamais et le joueur reste coincé devant la cabine (softlock permanent).

### Cause Racine (Ingénierie Inverse du Bytecode Sega et du Compteur Machine)
1. **Longueur en dur dans les nœuds de dialogue :**  
   Chaque nœud de dialogue du script `.msg` (12 octets par entrée) encode dans ses 2 premiers octets (`uint16_be`) le nombre exact de caractères attendus (ex: `0x003A` = 58 pour *"You can save the game and use the Item Box at\r\ntelephones."* ou *"...pay phones."*).
2. **Effet machine à écrire non terminé :**  
   Tant que le compteur interne de l'animation de frappe n'a pas atteint cette longueur, le moteur considère le dialogue comme « en cours ». Une pression sur la touche d'action tente d'accélérer l'animation jusqu'au caractère 58. Si le flux s'est arrêté avant (null-padding `\x00` ou octets sautés), le compte de 58 n'est jamais atteint et l'instruction suivante `0x08F8` (ouverture du menu) n'est jamais appelée.
3. **Le piège fatal des octets `>= 0xE0` (accents Windows-1252) :**  
   Dans la routine de décompte de caractères de Sega à l'adresse `0x140396783` :
   ```assembly
   396783: cmp $0xe0, %al
   396785: jb  0x39678d
   396787: add $0x2, %rbx    ; Saut de 2 octets supplémentaires (séquence UTF-8 3-octets)
   ```
   L'accent français `é` (`0xE9` en Windows-1252) est supérieur à `0xE0`. La routine l'interprète à tort comme un en-tête UTF-8 multi-octets et saute les 2 octets suivants (`l` et `é` dans `téléphone`). Le moteur compte alors **54 caractères au lieu de 58**, provoquant un softlock immédiat sur les cabines 1, 2 et 3 (`uid033317d1` à `uid033317d3`).

### Règle Impérative & Solution
* Pour toutes les cabines téléphoniques, utiliser exclusivement la formule pure ASCII sans accents complétée par 5 espaces de fin :
  ```python
  'Sauvegardez et utilisez le coffre depuis une\r\ncabine.     '  # Pile 58 octets ASCII
  ```
* Appliquer du **space-padding** (`b' '`) sur tous les dialogues et du **null-padding** (`\x00`) strictement sur les mots-clés d'options de menu (`Sauv`, `Ouvrir le coffre`, `Retour`).

---

## 5. Bulles d'Ambiance de Rue (`ai_popup.bin`)

### Symptômes
Les passants dans Kamurocho et Sotenbori parlent en anglais dans leurs bulles d'ambiance au-dessus de leur tête, même avec un patch français installé.

### Cause Racine
Le moteur recherche `ai_popup.bin` dans [`data/wdr_par_c/wdr.par`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/release_gog/data/wdr_par_c/wdr.par) et dans [`data/wdr_par_c/common.par`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/release_gog/data/wdr_par_c/common.par).
* Si `ai_popup.bin` n'est pas compressé en SLLZ avec le flag exact `0x80000000`, ou si sa taille dépasse le slot alloué dans `common.par` (offset `0x800`), le moteur ignore le fichier et affiche les chaînes de repli hardcodées en anglais.

### Règle Impérative & Solution
* Compresser `ai_popup.bin` (7 146 octets décompressés) en SLLZ natif avec `flags = 0x80000000` (taille compressée : **3 048 octets**).
* Dans `common.par`, insérer le payload compressé à l'offset exact `0x800` (taille disponible : 3 073 octets, 3048 $\le$ 3073, parfait remplacement in-place).
* Synchroniser le même `ai_popup.bin` compressé dans `wdr.par`.

---

## 6. Résumés de Quête du Menu Pause & Bannières (`boot.par`)

### Fichiers Critiques dans `boot.par`
1. **`explanation_main_scenario.bin_c` :** 18 titres de chapitres et 199 résumés d'étapes de quête principale (Col 0 `TITLE`, Col 2 `EXPLANATION`). Taille décompressée stricte : **23 772 octets**.
2. **`explanation_sub_story.bin_c` :** 100 titres et résumés de quêtes secondaires. Taille décompressée stricte : **58 232 octets**.
3. **`caption.bin_c` :** 146 objectifs affichés en bandeau à l'écran, bannières de combat et de rencontre. Taille décompressée stricte : **15 376 octets**.
4. **`item.bin_c` & `string_tbl.bin_c` :** Descriptions complètes des objets, armes et équipements.

### Cause Racine de Crash Possible (`0x371324`)
Si l'un de ces fichiers décompressés dépasse sa taille mémoire d'origine lors de la décompression au démarrage ou lors de l'ouverture du menu pause, le buffer alloué dans le tas du jeu déborde, provoquant un crash à `Yakuza0.exe+0x371324`.

### Règle Impérative
* Traduire strictement in-place avec un calibrage exact de la longueur des tampons.
* Recompresser avec `compress_sllz` (`flags = 0x80000000`).

---

## 7. Architecture des Archives PAR & Règle des 2048 Octets

### Structure d'une Archive PARC Sega
```
Offset 0x00: Magic 'PARC' (0x50415243)
Offset 0x04: 3 entiers 32-bit big-endian de statut
Offset 0x10: folder_count, folder_table_offset, file_count, file_table_offset (big-endian)
Offset 0x20: Table des noms de dossiers (folder_count * 64 octets)
Suivant    : Table des noms de fichiers (file_count * 64 octets, terminés par \x00)
Suivant    : Table des attributs de fichiers (file_count * 32 octets) :
             [flags (0x80000000=SLLZ), uncomp_size, comp_size, offset, unk1, unk2, unk3, unk4]
```

### Règle d'Or de l'Alignement Sectoriel (2 048 octets)
Pour toute écriture ou ajout de fichier dans un `.par` :
```python
aligned_offset = (current_offset + 2047) & ~2047
```
* **Tout payload de fichier DOIT démarrer à un multiple strict de 2 048 octets (`0x800`).**
* **La taille totale du fichier archive `.par` DOIT être un multiple strict de 2 048 octets.** Compléter la fin du fichier avec des octets nuls `\x00` si nécessaire.

---

## 8. Crash Boucle Infinie des Cabines & Faux Déploiement (`0x6EA328`)

### Symptômes
Crash brutal `EXCEPTION_ACCESS_VIOLATION` (c0000005) à `Yakuza0.exe+0x6EA328h` dès que Kiryu approche d'une cabine téléphonique ou tente d'interagir avec elle.
Dans le crash log :
```text
[ FaultMod ]  * RIP Addr.: Yakuza0.exe+00000000006EA328h
[StackFrame] <-> Rip=0001406ea328h, Rsp=00000014f8d0h, Rbp=7ff4d429d2e0h
[  GP Reg  ]   rax:    0x000000000000    rbx:    0x7ff4de442814
[  GP Reg  ]   rcx:    0x000000000003    rdx:    0x000000000000
[  GP Reg  ]   r8:     0x000000000000    r9:     0x7ff4fdd30005
[  GP Reg  ]   r10:    0x00001e45729f    r11:    0xffffffffe945f930
[  GP Reg  ]   r12:    0x7ff4de443685    r13:    0x7ff4de442800
[  GP Reg  ]   r14:    0x7ff4de443675    r15:    0x7ff4de442804
```

### Cause Racine (Reverse Engineering du Relocateur Sega)
1. **La routine de décalage et d'endianness `.msg` (`0x1406ea0e0`) :**
   Lors du chargement d'un script d'interaction de cabine (`uid033317d1.msg` à `uid033317e4.msg`), le moteur lit à l'offset `0x14` (offset 20) un pointeur relatif vers la table de nœuds (offset 3701 pour `uid033317d1.msg`).
   À l'adresse `0x1406ea2e2`, il lit le nombre d'entrées de la table dans `%r10d` (`mov (%r14), %r10d`).
2. **Le piège du fichier tronqué :**
   Si `wdr.par` est tronqué ou incomplet (ex: ancien bug de `translate_shops.py` réduisant l'archive à ~2 Mo au lieu de 7,3 Mo), ou si le fichier de cabine dépasse la taille physique disponible, le moteur lit de la mémoire non initialisée.
   Dans le crash ci-dessus, `%r10d` a été lu avec une valeur résiduelle corrompue `0x262924ff`.
3. **La boucle infinie de 529 Mo :**
   La routine applique une boucle d'endianness (`1406ea300` à `1406ea337`) qui décrémente `%r10d` de 4 et avance `%r9` de 16 octets à chaque tour :
   ```assembly
   1406ea300: mov (%r9), %r8d
              ...
              add $0xfffffffc, %r10d
              add $0x10, %r9
              ...
              test $0xfffffffc, %r10d
              jne 1406ea300
   ```
   Avec `r10_start = 0x262924ff`, la boucle a tourné pendant **33 millions d'itérations**, tentant d'inverser **529 Mo** (`0x1f8ec980` octets) en mémoire jusqu'à ce que `%r9` atteigne l'adresse non mappée `0x7ff4fdd30005`, déclenchant le crash immédiat à `0x1406ea328` (`mov %ecx, -0x8(%r9)`).
4. **Le piège du faux déploiement dans les installateurs `.bat` :**
   Le patch peut être 100% correct sur le dépôt, mais l'utilisateur subit quand même ce crash si l'installateur (`patch_fr.bat`) utilise une mauvaise condition de détection de dossier de jeu :
   - Tester `if exist "data\wdr_par_c\wdr.par"` est fatal : le package de release extrait contient lui-même un dossier `data\wdr_par_c\wdr.par`.
   - Si l'utilisateur extrait l'archive dans un sous-dossier (ex: `D:\GOG Games\Yakuza 0\Yakuza0_FR_Patch_GOG_v1.12.4\`), le script croit que **ce sous-dossier est le jeu**.
   - Il copie les archives saines sur elles-mêmes dans le dossier temporaire, ignore le vrai jeu (`Yakuza0.exe non présent, étape sautée`), et laisse l'ancien `wdr.par` tronqué dans le jeu réel !

### Règles Impératives & Solutions
* **Règle 1 :** Tout crash à `Yakuza0.exe+0x6EA328h` prouve à 100% que l'archive `wdr.par` chargée par le jeu est incomplète, tronquée ou n'a pas été déployée dans le bon répertoire.
* **Règle 2 :** Dans tous les scripts d'installation (`patch_fr.bat`, `verifier.bat`, scripts Python), détecter **EXCLUSIVEMENT** le répertoire du jeu via la présence de `Yakuza0.exe` (qui n'existe JAMAIS dans le package de release).
* **Règle 3 :** Bloquer impérativement l'exécution si `Yakuza0.exe` est introuvable (`exit /b 1`) au lieu de sauter l'étape en silence.
* **Règle 4 :** Afficher et logger en clair le chemin absolu du dossier de jeu détecté avant toute copie.

---

## 9. Matrice des Commandes de Validation

Avant de déclarer un correctif ou une archive valide, exécuter impérativement la suite de tests automatisés :

| Test | Commande | Critère de Succès |
|---|---|---|
| **Intégrité Globale** | `python3 tools/verify_patch.py release_gog` | **131/131 archives OK (100% PASS, 0 erreurs)** |
| **Vérification End-to-End** | `python3 tools/build_release.py` | Package ZIP créé et tests E2E validés |
| **Crénage Typographique** | `python3 scratch/verify_y0_ft.py` | Marges `i`, `l`, `I` à 0.4 et `.` à 0.4 |
| **Absence Softlock Bob** | Contrôle taille `uid00331696.msg` | Exactement **27 575 octets** décompressés |
| **Boutiques Non Tronquées** | Contrôle tables `shop0013.bin` & `shop0029.bin` | 24 octets et 20 octets préservés |
| **Détection Dossier Jeu** | Test présence `Yakuza0.exe` dans scripts | `Yakuza0.exe` exigé, pas de test sur `data\` seul |
| **Archive WDR Intègre** | Contrôle taille `wdr.par` | $\ge 7\text{ Mo}$ et 241 fichiers |

---

## 10. Catalogue des Anti-Patterns & Erreurs Récurrentes d'Agents IA

Ce chapitre répertorie les erreurs méthodologiques récurrentes constatées lors des interventions successives d'agents IA sur ce dépôt. Tout agent IA intervenant doit impérativement s'auto-évaluer contre cette liste :

### 1. L'illusion du "Patch Réussi" (Auto-Ciblage du Script d'Installation)
* **Mécanisme de l'erreur :** L'agent conçoit un script `.bat` ou Python qui vérifie `if exist "data\wdr_par_c\wdr.par"`. Comme le package extrait contient cette sous-arborescence, le script prend le dossier d'extraction pour le jeu. Il copie les fichiers sur eux-mêmes, n'injecte rien dans `Yakuza0.exe` (considérant l'exécutable absent comme optionnel), et affiche un message triomphal *"Patch appliqué avec succès !"*.
* **Résultat désastreux :** L'utilisateur lance son jeu qui continue d'exécuter d'anciennes archives tronquées ou buguées. L'agent perd alors un temps précieux à chercher un problème dans ses fichiers de patch alors que ceux-ci n'ont jamais atteint le jeu.
* **Règle absolue :** La **SEULE** condition valable pour identifier le dossier de jeu est la présence physique de `Yakuza0.exe`. Si `Yakuza0.exe` n'est pas présent, le script **DOIT** échouer immédiatement (`exit /b 1`).

### 2. Le Réflexe d'Accuser le Bytecode au lieu de l'Intégrité de l'Archive (`0x6EA328`)
* **Mécanisme de l'erreur :** Face à un crash à `0x6EA328` (`mov %ecx, -0x8(%r9)`), l'agent suppose immédiatement qu'un dialogue ou un opcode `.msg` est mal formaté et tente de modifier le texte.
* **Réalité d'ingénierie inverse :** L'adresse `0x1406ea0e0` est le décalage de pointeurs de Sega. Si `%r10` contient `0x262924ff` (ou toute valeur absurde), c'est parce que le fichier est lu au-delà de la fin de l'archive `wdr.par` ! Une archive `wdr.par` tronquée (ex: 2 Mo au lieu de 7.3 Mo) ou non copiée dans le jeu est la cause racine dans 100% des cas.
* **Règle absolue :** Avant d'éditer le moindre fichier de dialogue, vérifier que le `wdr.par` présent dans le jeu fait bien ~7,3 Mo et compte 241 fichiers.

### 3. La Confusion Entre Null-Padding (`\x00`) et Space-Padding (`b' '`)
* **Mécanisme de l'erreur :** Remplacer une chaîne anglaise par une chaîne française plus courte et remplir le reste avec des octets nuls `\x00`.
* **Réalité d'ingénierie inverse :** Dans les scripts de dialogue Sega, `\x00` marque la fin absolue d'une commande. Dans le dialogue de Bob Utsunomiya, insérer un `\x00` au milieu de la réplique coupe la séquence avant l'instruction qui attribue l'objet au joueur, provoquant un softlock.
* **Règle absolue :** Remplir les phrases de dialogue avec des espaces ASCII (`b' '`). Les octets `\x00` sont strictement réservés aux chaînes d'interface fixes (labels de menus).

### 4. Le Piège des Accents UTF-8 sur les Textes à Longueur Fixe
* **Mécanisme de l'erreur :** Traduire les indications de cabine avec des accents (*« Sauvegardez et utilisez le coffre depuis une cabine téléphonique »*).
* **Réalité d'ingénierie inverse :** La fonction `0x140396783` interprète les octets `\xE9` (`é`) comme des indicateurs UTF-8 multi-octets et saute des octets dans le décompte de caractères. Le nombre de caractères comptés devient inférieur à la longueur fixe attendue par le nœud de script (58 caractères). Le jeu attend indéfiniment la fin de l'animation de frappe et ne déclenche jamais le menu de sauvegarde (softlock cabine).
* **Règle absolue :** Les cabines exigent une chaîne purement ASCII complétée par des espaces (`"Sauvegardez et utilisez le coffre depuis une\r\ncabine.     "` pile 58 caractères).

### 5. La Troncature des Données Propriétaires de Boutiques
* **Mécanisme de l'erreur :** Traiter les fichiers de boutique (`shop*.bin`) comme de simples tableaux d'articles homogènes et tronquer la fin du fichier.
* **Réalité d'ingénierie inverse :** `shop0013.bin` et `shop0029.bin` contiennent des tables de catégories Pocket Circuit (24 et 20 octets). Les écraser ou les supprimer corrompt le chargement des textures et provoque le crash immédiat `0x234B7`.
* **Règle absolue :** Toujours utiliser `tools/rebuild_all_shops_clean.py` qui préserve ces tables annexes au bit près.

### 6. Le Piège du Double Antislash (`\\`) et de la Lecture Seule (`+R`) dans Windows Batch
* **Mécanisme de l'erreur :** 
  1. Si la variable `%GAMEDIR%` conserve un antislash final (`D:\GOG Games\Yakuza 0\`), la concaténation `%GAMEDIR%\data\...` produit un chemin avec double antislash `\\` (`0\\data`). La commande interne `copy` de Windows `cmd.exe` échoue avec une erreur de syntaxe ou accès refusé.
  2. Les installations GOG marquent fréquemment les archives du jeu (`wdr.par`, `boot.par`...) avec l'attribut **Lecture Seule (`+R`)**. Sous Windows, la commande `copy /y` **refuse d'écraser un fichier en lecture seule** et échoue avec `Accès refusé` même en mode Administrateur !
  3. Rediriger `copy ... >nul` masque le message réel de Windows, affichant un message générique trompeur.
* **Règle absolue :** 
  - Nettoyer agressivement les antislashs terminaux via des boucles de détection (`if "%GAMEDIR:~-1%"=="\" set "GAMEDIR=%GAMEDIR:~0,-1%"`).
  - Retirer systématiquement l'attribut lecture seule (`attrib -R "%GAMEDIR%\data\*.par" /S`).
  - Déléguer la copie à Python (`shutil.copy2` combiné à `os.chmod(dst, stat.S_IWRITE)`) qui normalise nativement les séparateurs de dossiers et lève les verrous de lecture seule.

### 7. Règle de Livraison : Aucune Release Publique Sans Autorisation
* **Mécanisme de l'erreur :** Créer un tag git et une release publique GitHub (`gh release create`) à chaque itération ou correctif intermédiaire.
* **Règle absolue :** Il est **formellement interdit** de publier une release GitHub sans que l'utilisateur n'en donne l'ordre explicite et direct. Toutes les étapes de test et de validation doivent se faire localement dans le dépôt.
