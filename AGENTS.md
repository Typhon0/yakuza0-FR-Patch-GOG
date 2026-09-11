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

---

## 2. Protocole de Validation Obligatoire

Avant de clore toute tâche, de livrer un fichier à l'utilisateur ou de créer une release :

1. **Vérifier l'intégralité des 131 archives PAR :**
   ```bash
   python3 tools/verify_patch.py release_gog
   ```
   *Exigence :* **131/131 OK (100% PASS, 0 erreurs)**.
2. **Reconstruire le package de release autonome :**
   ```bash
   python3 tools/build_release.py
   ```
   *Exigence :* Le test End-to-End doit afficher **SUCCÈS TOTAL**.

---

## 3. Communication


* **Rigueur technique :** Expliquer les causes racines des bugs sur la base du reverse engineering réel (adresses d'instructions x86-64, structures de données PE/PAR/SLLZ) sans faire de suppositions non vérifiées.
