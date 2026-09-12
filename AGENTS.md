# Directives Générales pour les Agents IA — Yakuza 0 GOG FR Patch

> **AVERTISSEMENT OBLIGATOIRE POUR TOUT AGENT IA TRAVAILLANT SUR CE DÉPÔT**  
> Ce dépôt contient les outils, correctifs et données du patch de traduction française pour **Yakuza 0 version GOG** (v1.015a).  
> Avant de modifier le moindre fichier, d'exécuter un script de recompilation ou de générer du code, vous **DEVEZ IMPÉRATIVEMENT** consulter et respecter la base de connaissances :  
> 👉 [**`docs/DEBUG_KNOWLEDGE_BASE.md`**](file:///home/dev/repos/yakuza0-FR-Patch-GOG/docs/DEBUG_KNOWLEDGE_BASE.md)

---

## 1. Règles d'Or Inviolables (Ne Jamais Reproduire Ces Erreurs)

### 🚫 Règle 1 : Ne JAMAIS tronquer les fichiers de boutique (`shop*.bin`)
* **Piège :** Les fichiers `shop0013.bin` (Kotobuki Drugs) et `shop0029.bin` (Daikoku Drugstore) contiennent des tables propriétaires de catégories Pocket Circuit (respectivement **24** et **20 octets**) situées après la liste d'articles.
* **Conséquence si violée :** Crash instantané `0x234B7` (`EXCEPTION_ACCESS_VIOLATION`) à l'ouverture du menu d'achat.
* **Action :** Utiliser exclusivement [`tools/rebuild_all_shops_clean.py`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/tools/rebuild_all_shops_clean.py) qui conserve rigoureusement ces tables annexes.

### 🚫 Règle 2 : Ne JAMAIS tronquer ou null-padder les dialogues dans les scripts `.msg` (Bob & Cabines)
* **Piège :** 
  1. **Bob Utsunomiya 0 (`uid00331696.msg`, `uid003316a2.msg`) :** Les scripts `.msg` contiennent des offsets de sauts de bytecode compilés. Modifier la taille du fichier ou utiliser un padding nul `\x00` dans les chaînes de dialogue provoque un softlock permanent lors de la réplique *« Mais c'est offert pour toi, tu sais ? »*.
  2. **Cabines téléphoniques (`uid033317d1.msg` à `uid033317e4.msg`) :**  
     - Le nœud de dialogue encode en dur la longueur exacte attendue en caractères (ex : **58 caractères** pour *"You can save the game and use the Item Box at\r\ntelephones."* ou *"...pay phones."*).
     - **Piège fatal du multi-octets UTF-8 :** La routine de calcul de longueur de Sega (`0x140396783`) interprète les octets `\x80` et `\xE0`+ (comme `é` = `\xE9` dans `téléphone`) comme le début de séquences multi-octets UTF-8 et saute les 2 octets suivants, faussant le décompte (`54` au lieu de `58`).
     - Si la longueur n'est pas atteinte ou si complétée par des octets nuls `\x00`, le moteur attend indéfiniment la fin de l'effet machine à écrire et ne déclenche **JAMAIS** le menu de sauvegarde (`0x08F8`), figeant le joueur en softlock permanent.
* **Action :** 
  - Les fichiers décompressés de Bob doivent faire **exactement 27 575 octets**.
  - Pour les cabines téléphoniques, utiliser exclusivement la formule pure ASCII sans accents complétée par des espaces de fin :  
    `"Sauvegardez et utilisez le coffre depuis une\r\ncabine.     "` (pile 58 caractères ASCII).
  - Toujours utiliser du **space-padding** (`b' '`) pour les dialogues et du *null-padding* (`\x00`) strictement pour les mots-clés d'interface (`Save`, `Cancel`, `Yes`...).

### 🚫 Règle 3 : Respecter l'alignement sectoriel de 2 048 octets dans les archives PAR
* **Piège :** Les archives PAR Sega (`stay.par`, `boot.par`, `wdr.par`) stockent des données de streaming audio/stage (`response_wanderer.bin_c`) qui dépendent d'alignements stricts. Une recompilation séquentielle standard corrompt les pointeurs et fait crasher le chargement des sauvegardes (`0xA4526` / `SOUND_ID`).
* **Action :** Utiliser le modèle **Append-Only** : conserver les fichiers Sega d'origine intacts au début de l'archive, et ajouter les fichiers modifiés à la fin, chacun aligné sur un multiple strict de 2 048 octets (`(offset + 2047) & ~2047`).

### 🚫 Règle 4 : Ne JAMAIS laisser les métriques Sega Vanilla `[0.0, 1.17, ...]` sur `i` et `l`
* **Piège :** La routine de crénage (`0x140397020`) applique une translation négative proportionnelle à la marge droite. Avec la valeur native Sega de `1.17`, l'avance est réduite de 11.76 px, écrasant les lettres suivantes sur `i` et `l` (*« utilisez »*, *« depuis »*).
* **Action :** Toujours injecter la table calibrée de 6 144 octets ([`release_gog/font_table_french.bin`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/release_gog/font_table_french.bin)) dans `Yakuza0.exe` à l'offset `0xD488F0`. Les marges de `i`, `l`, `I` et de leurs variantes accentuées doivent être symétriques à `[0.4, 0.4, 0.4, 0.4, 0.4, 0.4]`.

### 🚫 Règle 5 : Toujours compresser en SLLZ avec `flags = 0x80000000`
* **Piège :** Les fichiers compressés dans les archives PAR requièrent l'en-tête de flag `0x80000000`. Si non compressé ou mal marqué (ex: `ai_popup.bin`), le jeu bascule sur l'anglais par défaut.
* **Action :** Utiliser [`tools/sllz.py`](file:///home/dev/repos/yakuza0-FR-Patch-GOG/tools/sllz.py) (`compress_sllz`).

### 🚫 Règle 6 : Détecter EXCLUSIVEMENT le répertoire de jeu via `Yakuza0.exe`
* **Piège :** Tester un sous-dossier ou un fichier de données générique (ex: `if exist "data\wdr_par_c\wdr.par"`).  
  Le package de release contient lui-même cette arborescence `data/wdr_par_c/wdr.par`. Si l'utilisateur extrait l'archive dans un sous-dossier (ex : `D:\GOG Games\Yakuza 0\Yakuza0_FR_Patch_GOG_v1.12.5\`), le script d'installation s'auto-détecte comme étant le jeu, copie les fichiers sains sur eux-mêmes dans le dossier temporaire, ignore silencieusement `Yakuza0.exe`, et prétend que l'installation a réussi ! Le joueur lance ensuite le jeu qui tourne toujours sur les anciennes archives corrompues ou tronquées.
* **Conséquence si violée :** Faux sentiment de résolution, persistance du crash `0x6EA328` (boucle infinie de bswap de 529 Mo) ou de softlocks, et perte de temps colossale à chercher un bug dans le code alors que le fichier n'a tout simplement jamais été copié dans le jeu.
* **Action :**  
  - Dans TOUS les scripts (`.bat`, `.py`, PowerShell), la seule et unique preuve de la racine du jeu est la présence de **`Yakuza0.exe`**.
  - Si `Yakuza0.exe` est introuvable, **ARRÊT IMMÉDIAT ET BLOQUANT** (`exit /b 1` / `sys.exit(1)`). Il est formellement interdit de continuer ou de sauter l'étape en silence.
  - Toujours afficher et logger en clair le chemin absolu du dossier de jeu détecté avant d'entamer la copie.

### 🚫 Règle 7 : Ne JAMAIS tronquer les archives PAR (`wdr.par`, etc.)
* **Piège :** Reconstruire une archive PAR en omettant les fichiers originaux Sega non traduits ou en utilisant un dictionnaire incomplet (ex: ancien bug de `translate_shops.py` qui réduisait `wdr.par` de 7,3 Mo à 2 Mo).
* **Conséquence si violée :** Lors du chargement d'un script `.msg` (ex: cabines téléphoniques `uid033317d1.msg`), le pointeur de table de nœuds à l'offset `0x14` lit au-delà de la fin de fichier dans de la mémoire non allouée. Le registre `%r10` charge des octets résiduels corrompus (ex: `0x262924ff`), lançant la boucle de bswap de 529 Mo sur 33 millions d'itérations qui se termine par un crash `mov %ecx, -0x8(%r9)` à `Yakuza0.exe+0x6EA328h`.
* **Action :**  
  - `release_gog/data/wdr_par_c/wdr.par` DOIT contenir **exactement 241 fichiers** et peser **plus de 7 Mo** (~7,3 Mo).
### 🚫 Règle 8 : Ne JAMAIS se fier à `copy /y` pour écraser des fichiers de jeu (Lecture seule & double antislash)
* **Piège :** 
  1. Si `%GAMEDIR%` conserve un antislash final (`D:\GOG Games\Yakuza 0\`), la commande `copy /y ... "%GAMEDIR%\data\..."` produit `0\\data` avec un double antislash, ce qui fait échouer `cmd.exe` avec une erreur de syntaxe ou accès refusé.
  2. Les installeurs GOG appliquent très souvent l'attribut **Lecture Seule (`+R`)** sur les archives `.par`. La commande `copy /y` **refuse catégoriquement** d'écraser un fichier en lecture seule, même si l'utilisateur est Administrateur !
  3. Rediriger `>nul` masque le message réel de Windows et induit en erreur en affichant un message générique.
* **Action :**  
  - Toujours retirer préalablement l'attribut lecture seule : `attrib -R "%GAMEDIR%\data\*.par" /S`.
  - Nettoyer agressivement les antislashs finaux dans les scripts.
  - Déléguer la copie à Python (`shutil.copy2` avec `os.chmod(dst, stat.S_IWRITE)`) qui normalise nativement les chemins et lève les verrous de lecture seule.

### 🚫 Règle 9 : AUCUNE release publique GitHub sans demande explicite de l'utilisateur
* **Piège :** Lancer automatiquement `gh release create` à chaque modification ou correctif intermédiaire.
* **Conséquence :** Pollue les releases publiques avec des versions non stabilisées et contredit les consignes de déploiement de l'utilisateur.
* **Action :** Valider et tester exclusivement en local (`tools/test_release_e2e.py`). Attendre **STRICTEMENT** l'instruction explicite de l'utilisateur avant toute publication sur GitHub.

---

## 2. Protocole de Validation Obligatoire

Avant de clore toute tâche, de livrer un fichier à l'utilisateur ou de créer une release :

1. **Vérifier l'intégralité des 131 archives PAR :**
   ```bash
   python3 tools/verify_patch.py release_gog
   ```
   *Exigence :* **131/131 OK (100% PASS, 0 erreurs)**.
2. **Tester les composants sensibles connus :**
   - Cabines de sauvegarde : 25/25 fichiers vérifiés, 58 caractères ASCII stricts, padding espaces.
   - Bob Utsunomiya 0 : `uid00331696.msg` = exactement 27 575 octets décompressés.
   - Boutiques : `shop0013.bin` (24 octets) et `shop0029.bin` (20 octets) préservés.
   - Taille de `wdr.par` : $\ge 7\text{ Mo}$ et 241 fichiers.
   - Détection de jeu : Présence obligatoire de `Yakuza0.exe` dans tous les scripts.
3. **Reconstruire le package autonome et valider l'End-to-End local :**
   ```bash
   python3 tools/build_release.py
   ```
   *Exigence :* Le test End-to-End intégré doit afficher **SUCCÈS TOTAL**.
4. **Attendre l'accord de l'utilisateur avant TOUTE publication publique.**

---

## 3. Catalogue des Anti-Patterns Récurrents des Agents IA

Voici la liste des erreurs types commises de manière répétée par les agents IA sur ce projet, à bannir définitivement :

| Anti-Pattern de l'Agent IA | Pourquoi c'est une faute grave | Règle de Conduite Immédiate |
|---|---|---|
| **Publier une release sans autorisation** | Pollue le dépôt public avec des versions intermédiaires. | Valider en local et attendre l'accord explicite de l'utilisateur. |
| **Utiliser `copy /y` sans gérer la lecture seule (`+R`)** | `copy /y` échoue avec 'Accès refusé' sur les fichiers GOG en lecture seule. | Utiliser Python (`os.chmod`) ou `attrib -R` avant d'écraser. |
| **Laisser un double antislash `\\` dans les chemins** | Fait échouer les commandes internes `cmd.exe`. | Nettoyer les antislashs terminaux en boucle. |
| **Supposer que le patch est copié** sans vérifier la détection de `Yakuza0.exe` | Le batch s'exécute dans le dossier extrait et ne copie rien dans le jeu. | Exiger `Yakuza0.exe` et bloquer avec code d'erreur si absent. |
| **Accuser un script `.msg` lors d'un crash à `0x6EA328`** au lieu de vérifier la taille de `wdr.par` | `0x6EA328` est le symptôme direct d'une lecture au-delà de la fin de fichier causée par un `wdr.par` tronqué ou non déployé. | Vérifier la taille physique de `wdr.par` (~7.3 Mo) dans le dossier du jeu. |
| **Mettre des accents dans les textes à longueur stricte** (Cabines) | `é` encode 2 octets UTF-8 (`\xC3\xA9`), faussant le compteur de machine à écrire Sega (`0x140396783`) et provoquant un softlock. | Garder un texte 100% ASCII complété par des espaces (`b' '`). |
| **Utiliser du null-padding (`\x00`) dans les dialogues** | `\x00` est interprété comme un terminateur de script de dialogue, coupant l'exécution avant le don d'objet ou le retour de contrôle (softlock Bob). | Space-padding (`b' '`) pour les phrases, `\x00` uniquement pour les mots d'interface courts. |
| **Recompiler un PAR séquentiellement** sans préserver les offsets Sega originaux | Corrompt les offsets absolus de streaming audio/stage (`response_wanderer.bin_c`), crash au chargement de sauvegarde `0xA4526`. | Utiliser strictement le modèle Append-Only aligné à 2 048 octets. |
| **Faire des hypothèses sans lire le crash log** | Fait perdre des heures en conjectures erronées. | Lire l'adresse RIP, désassembler l'instruction et calculer les deltas de registres (%r10, %r9...). |

---

## 4. Communication

* **Rigueur technique :** Expliquer les causes racines des bugs sur la base du reverse engineering réel (adresses d'instructions x86-64, structures de données PE/PAR/SLLZ) sans faire de suppositions non vérifiées.
