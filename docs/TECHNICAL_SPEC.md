# Spécifications Techniques & Rétro-Ingénierie

Ce document consigne l'analyse binaire, les offsets mémoire et l'ingénierie inverse ayant permis le portage de la traduction française de Yakuza 0 sur l'édition GOG (Build 3642285 / v1.015a).

---

## 1. Cible Binaire

* **Jeu** : Yakuza 0 (GOG DRM-Free Release)
* **Exécutable** : `Yakuza0.exe`
* **Version** : v1.015a (Build 3642285)
* **Architecture** : x86_64 (PE32+)
* **Taille d'origine** : 22 084 096 octets
* **ImageBase** : `0x140000000`

---

## 2. Analyse des Problèmes de Compatibilité Steam $\rightarrow$ GOG

### 2.1. Crash / Freeze du Chapitre 1 (Bipeur de Kiryu)
Dans l'exécutable Steam fourni par la communauté, plusieurs instructions du moteur de sous-titres et d'affichage de texte avaient été détournées via des offsets statiques propres à l'exécutable Steam. Appliqués tels quels sur l'exécutable GOG, ces patchs provoquaient une corruption de pile lors de l'appel système de notification du bipeur, entraînant un gel complet (freeze) de la boucle de rendu.

**Correctif appliqué sur GOG** :
Quatre instructions bytecode 1-octet ont été identifiées et appliquées aux adresses exactes de la version GOG :
| Adresse File Offset | Valeur Vanilla GOG | Valeur Patchée | Description |
|---|---|---|---|
| `0x2CD804` | `0x0F` | `0x90` | NOP d'un saut conditionnel dans le moteur de sous-titres |
| `0x2CD805` | `0x84` | `0xE9` | Redirection de saut inconditionnel |
| `0x2CD879` | `0x0F` | `0x90` | Neutralisation de la vérification de longueur de chaîne |
| `0x2CD8B6` | `0x0F` | `0x90` | Rendu direct du buffer de texte étendu |

---

### 2.2. Anomalie de Kerning de Police (Écrasement des caractères étroits `i`, `l` et espacement asymétrique)

#### Cause Racine
Dans le moteur graphique de Yakuza 0, la table de coordonnées UV et de marges de glyphes est stockée dans la section `.rdata` de l'exécutable GOG à l'adresse `0xD488F0` (RVA `0xD4A0F0`). Chaque caractère ASCII (0x00 à 0xFF) dispose d'une entrée de **24 octets** (6 valeurs flottantes 32-bit `float` IEEE-754) :
```
[top_left_margin, top_right_margin, mid_left_margin, mid_right_margin, bot_left_margin, bot_right_margin]
```

La routine de crénage proportionnel (`0x140397020`) calcule pour deux caractères consécutifs $C_1$ et $C_2$ :
$$\text{min\_gap} = \min(R_{\text{top}}(C_1) + L_{\text{top}}(C_2),\; R_{\text{mid}}(C_1) + L_{\text{mid}}(C_2),\; R_{\text{bot}}(C_1) + L_{\text{bot}}(C_2))$$
$$\text{réduction} = \text{min\_gap} \times 0.5 \times \frac{\text{font\_size}}{2}$$
L'avance réelle du curseur est alors :
$$\text{Avance}(C_1 \to C_2) = \text{Base\_Advance} - \text{réduction}$$

Dans la version Sega Vanilla (GOG) :
* Pour `i` (`0x69`) et `l` (`0x6C`) : `[0.0, 1.17, 0.0, 1.17, 0.0, 1.17]`
* Pour `I` (`0x49`) : `[0.0, 1.10, 0.0, 1.10, 0.0, 1.10]`

Cette asymétrie extrême (`Left = 0.0`, `Right = 1.17`) produisait deux défauts majeurs :
1. **Écrasement vers la droite** : Le `Right = 1.17` provoquait une réduction de plus de 11 pixels sur le caractère suivant. En conséquence, dans des mots comme *« utilisez »* (`il`, `is`) ou *« depuis »* (`is`), le deuxième caractère était dessiné directement par-dessus le `i`.
2. **Trou vers la gauche** : Le `Left = 0.0` empêchait le caractère précédent de s'approcher normalement (avance gonflée à 15px), créant un vide anormal avant `l` (ex: `té  léphone`).

#### Solution
Une table de crénage étalonnée bit-exacte (6 144 octets) est injectée sur l'intégralité de la plage (`0x00` à `0xFF`) :
* **`i`, `l`, `I`** : Marges symétriquement centrées à `[0.4, 0.4, 0.4, 0.4, 0.4, 0.4]`, assurant une avance fluide de 9.6px à 10.4px sans aucun écrasement ni trou.
* **Caractères accentués dérivés de `i` (`î`, `ï`, `ì`, `í`, `Î`, `Ï`, `Ì`, `Í`)** : Calibrés à l'identique à `[0.4, 0.4, 0.4, 0.4, 0.4, 0.4]`.
* **Caractères accentués (`é`, `è`, `ê`, `à`, `ç`, etc.)** : Alignés rigoureusement sur les métriques de leurs bases non-accentuées pour une harmonie parfaite.
* **Point de ponctuation `.` (`0x2E`)** : Marge inférieure gauche ajustée à `0.4` pour coller naturellement aux fins de phrases sans trou visuel artificiel.

---

## 3. Injection de Section PE et Relocalisation de Chaînes

### 3.1. Création de la section `.trad`
Plutôt que d'écraser des buffers existants dans `.rdata` (ce qui limiterait la taille des traductions à la longueur des chaînes anglaises d'origine), le patcher étend l'en-tête PE du fichier :
1. Incrémentation de `NumberOfSections` dans le `COFF File Header`.
2. Calcul du nouvel offset aligné sur `FileAlignment` (512 octets) et `SectionAlignment` (4096 octets).
3. Écriture du header de section de 40 octets nommé `.trad\0\0\0` avec les caractéristiques `IMAGE_SCN_MEM_READ | IMAGE_SCN_CNT_INITIALIZED_DATA` (`0x40000040`).
4. Mise à jour de `SizeOfImage` dans l'`Optional Header`.

### 3.2. Redirection des Pointeurs 64-bit
1. Les chaînes anglaises cibles sont localisées dans `.rdata`.
2. Leurs équivalents français encodés en `Windows-1252 / ISO-8859-1` sont écrits dans la section `.trad` allouée.
3. Le patcher balaie la table de pointeurs de `.data` et remplace les adresses virtuelles absolues 64-bit (`0x140xxxxxx`) par les nouvelles adresses pointant vers `.trad`.

---

## 4. Remédiation In-Place des Textes et Encodages

### 4.1. Anomalie des Apostrophes « Trade Mark » `™`
* **Cause** : Les apostrophes typographiques courbes `’` (U+2019) ont été exportées en UTF-8 (`\xE2\x80\x99`).
* **Interprétation moteur** : En Windows-1252, l'octet `0x99` correspond au symbole Trade Mark `™` (`c™est`, `j™ai`, `d™argent`).
* **Correctif** : Remplacement in-place par des apostrophes ASCII droites `'` (`0x27`) complétées par du null-padding (`\x00`).

### 4.2. Recompression SLLZ Bit-Exacte
* Les données compressées au sein des archives PAR de Sega (`.bin_c`) requièrent l'algorithme propriétaire SLLZ.
* L'outil développé en pur Python ([`tools/sllz.py`](../tools/sllz.py)) recompresse les fichiers modifiés en garantissant que le nouveau flux compressé ne dépasse jamais la taille du slot d'origine, évitant tout décalage d'offset au sein des archives.

