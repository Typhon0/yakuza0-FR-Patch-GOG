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

### 2.2. Anomalie de Kerning de Police (Écrasement des caractères étroits `i` et `l`)

#### Cause Racine
Dans le moteur graphique de Yakuza 0, la table de coordonnées UV et de marges de glyphes est stockée dans la section `.data` de l'exécutable GOG à l'adresse `0xD488F0`. Chaque caractère ASCII (0x00 à 0xFF) dispose d'une entrée de **24 octets** (6 valeurs flottantes 32-bit `float` en IEEE-754 little-endian) :
```
[top_left_margin, top_right_margin, mid_left_margin, mid_right_margin, bot_left_margin, bot_right_margin]
```

Dans la version Sega Vanilla (GOG) :
* Pour `i` (`0x69`) : `[0.0, 1.17, 0.0, 1.17, 0.0, 1.17]`
* Pour `l` (`0x6C`) : `[0.0, 1.17, 0.0, 1.17, 0.0, 1.17]`

Dans l'exécutable Steam de Byce61, la table avait été intégralement générée avec des marges artificielles :
* `[0.6875, 0.75, 0.6875, 0.75, 0.6875, 0.75]`

Sur l'exécutable GOG, cette valeur `0.6875` sur un glyphe étroit comme `i` déclenchait un calcul de translation négative de plus de 16 pixels vers la gauche. En conséquence :
* Les caractères `i`, `l`, `I` étaient dessinés directement par-dessus la lettre précédente (*« Batte »* pour *« Battle »*, *« Busness »*, *« Substores »*, etc.).

#### Solution
Le patcher préserve **intégralement** la table Sega Vanilla pour la plage ASCII standard (**`0x00` à `0x7F`**) et n'injecte la table française que pour la plage étendue (**`0x80` à `0xFF`**). De plus, les caractères accentués dérivés de `i` (`î` `0xEE`, `ï` `0xEF`, etc.) voient leurs marges réajustées à `[0.0, 1.17, ...]` pour un rendu typographique parfait.

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
