# Audit Complet des Imperfections Textuelles & d'Encodage (VOSTFR Yakuza 0 GOG)

Ce rapport dresse le bilan technique exhaustif des anomalies textuelles (caractères `™`, mojibake `Ã©`, `Å“`, apostrophes corrompues, ligatures non supportées) identifiées dans les fichiers du patch français Rev 1.10.

---

## 1. Origine & Mécanismes Techniques

Le moteur de Yakuza 0 sur PC traite les chaînes de caractères en **1 octet** (encodage Windows-1252 / ISO-8859-1) et utilise une table de métriques/largeurs (`font_table_french.bin`) injectée dans le binaire pour afficher les caractères accentués (`0xA1` à `0xFF`).

Trois mécanismes distincts créent les imperfections visibles en jeu :

### A. L'apparition du symbole « ™ » à la place des apostrophes
* **Cause :** Dans les logiciels modernes (Word, bloc-notes avec mise en forme, certains outils de sous-titrage), l'apostrophe typographique courbe `’` (U+2019) est automatiquement insérée au lieu de l'apostrophe droite standard `'` (ASCII `0x27`).
* **Encodage UTF-8 :** `’` s'écrit sur 3 octets : `\xE2\x80\x99`.
* **Interprétation par le moteur du jeu (Windows-1252) :**
  - `\xE2` = lettre `â`
  - `\x80` = non-imprimable / ignoré
  - `\x99` = symbole **Trade Mark `™`** !
* **En jeu :** Le joueur voit littéralement `c™est`, `j™ai`, `d™accord`, `l™homme`, ou `dâ€™argent`.

### B. Les résidus UTF-8 sur les accents (`Ã©`, `Ã¨`, `Ã `, `Ã‰`...)
* **Cause :** Plusieurs fichiers de dialogue (`.msg`) et tables d'objets (`.bin_c`) ont été rédigés ou réenregistrés en encodage UTF-8 au lieu de Windows-1252.
* **Conséquence :** Les caractères accentués sur 2 octets sont lus comme deux caractères distincts :
  - `é` (`\xC3\xA9`) devient `Ã©`
  - `è` (`\xC3\xA8`) devient `Ã¨`
  - `à` (`\xC3\xA0`) devient `Ã `
  - `ê` (`\xC3\xAA`) devient `Ãª`
  - `É` (`\xC3\x89`) devient `Ã‰`

### C. Les ligatures « œ » et « Œ » (`Å“` / carrés vides)
* **Cause :** En Windows-1252, `œ` correspond à l'octet `0x9C` et `Œ` à `0x8C`. Or, dans `font_table_french.bin`, toute la plage `0x80` à `0x9F` a une largeur et des coordonnées UV nulles (`0.0`). De plus, en UTF-8, `œ` s'écrit `\xC5\x93`, ce qui affiche `Å“`.
* **Conséquence :** Le mot `œufs` s'affiche soit `Å“ufs`, soit avec un espace vide/glitch.
* **Correction standard :** Remplacer par `oe` et `OE` (ex. `oeufs`, `soeur`, `coeur`, `oeuvre`).

### D. Le cas de la cédille minuscule « ç » affichée en majuscule « Ç »
* **Cause :** Dans la texture de police originale `hd_hankaku.dds` / `hd2_hankaku.dds` du patch Steam Rev 1.10, la cellule `0xE7` (normalement minuscule `ç`) a été dessinée avec un `Ç` majuscule par Byce61/Kaplas pour éviter que la queue de la cédille ne déborde sur la ligne du dessous.
* **Faisabilité :** Comme vous l'avez noté, retoucher la texture DDS et recalculer les coordonnées UV est une opération graphique plus lourde. En revanche, **toutes les anomalies textuelles A, B et C sont 100% corrigeables au niveau des fichiers texte/données sans toucher aux textures.**

---

## 2. Inventaire Détaillé des Fichiers & Textes Affectés

L'audit automatisé a passé au crible l'ensemble des archives `.par`, sous-archives et fichiers décompressés SLLZ (`.msg`, `.bin_c`, `.bin`). Voici le recensement exact des textes contenant ces anomalies :

### A. Objets & Descriptions Système (`data/bootpar/boot.par`)

Ces textes apparaissent directement dans l'inventaire et les menus de quêtes :

| Fichier interne | Texte corrompu actuel en jeu | Correction proposée |
|---|---|---|
| `item.bin_c` | `Poulet au yuzu et soba dâ€™Ã©pinards` | `Poulet au yuzu et soba d'épinards` |
| `item.bin_c` | `PiÃ¨ce dâ€™OVNI` | `Pièce d'OVNI` |
| `item.bin_c` | `Ses balles ont des effets diffÃ©rents. L'inconvÃ©nient, c'est qu'on ne sait pas ce que c'est avant dâ€™avoir tirer.` | `Ses balles ont des effets différents. L'inconvénient, c'est qu'on ne sait pas ce que c'est avant d'avoir tiré.` |
| `item.bin_c` | `Porter cet encens intrigant vous rend plus susceptible de rencontrer des ennemis ayant beaucoup dâ€™argent.` | `Porter cet encens intrigant vous rend plus susceptible de rencontrer des ennemis ayant beaucoup d'argent.` |
| `item.bin_c` | `Ce fragment de mÃ©tÃ©orite est un objet extrÃªmement rare. Ã‰tant donnÃ© ses origines dâ€™un autre monde, il se vendrait sans doute pour une petite fortune.` | `Ce fragment de météorite est un objet extrêmement rare. Étant donné ses origines d'un autre monde, il se vendrait sans doute pour une petite fortune.` |
| `explanation_sub_story.bin_c` | `J'ai trouvÃ© le yakuza qui a pris Ara-Q3 au voyou qui l'a pris au gamin qui l'a arrachÃ© Ã  Akio Ã  l'origine. â€¦ Trop compliquÃ© ! Quelqu'un va se faire frapper !` | `J'ai trouvé le yakuza qui a pris Ara-Q3 au voyou qui l'a pris au gamin qui l'a arraché à Akio à l'origine. ... Trop compliqué ! Quelqu'un va se faire frapper !` |

---

### B. Dialogues d'Aventure, Rues & Histoires Secondaires (`data/wdr_par_c/wdr.par`)

C'est ici que se trouve le gros des dialogues in-game et des quêtes :

| Fichier interne | Texte corrompu actuel en jeu | Correction proposée |
|---|---|---|
| `uid010c1655.msg` | `Hein ? Rester silencieux pendant lâ€™Ã©vÃ©nement ? Une session sans parler ne serait-elle pas un drame ?` | `Hein ? Rester silencieux pendant l'événement ? Une session sans parler ne serait-elle pas un drame ?` |
| `uid010c1780.msg` | `Câ€™est lâ€™hopital qui se moque de la charitÃ©. Nous sommes faits du même bois, toi et moi.` | `C'est l'hôpital qui se moque de la charité. Nous sommes faits du même bois, toi et moi.` |
| `restaurant0006.bin` | `Cet ensemble propose un sandwich au bacon, aux Å“ufs et Ã  la laitue sur du pain blanc.` | `Cet ensemble propose un sandwich au bacon, aux oeufs et à la laitue sur du pain blanc.` |
| `uid01640005.msg` | `La cote de sÃ©curitÃ© de la zone Leisure King a baissÃ© d'un niveau.` | `La cote de sécurité de la zone Leisure King a baissé d'un niveau.` |
| `uid01640012.msg` | `La cote de sÃ©curitÃ© de la zone Leisure King a baissÃ© d'un niveau. La cote de rÃ©solution de problÃ¨mes du personnel de sÃ©curitÃ© en service a Ã©tÃ© rÃ©duite...` | `La cote de sécurité de la zone Leisure King a baissé d'un niveau. La cote de résolution de problèmes du personnel de sécurité en service a été réduite...` |
| `uid01640013.msg` | `...du personnel de sÃ©curitÃ© en service a Ã©tÃ© rÃ©duite d'un niveau â˜….` | `...du personnel de sécurité en service a été réduite d'un niveau ★.` |
| `uid01640015.msg` | `...de la zone Leisure King a baissÃ© d'un niveau. La note de rÃ©solution de problÃ¨mes...` | `...de la zone Leisure King a baissé d'un niveau. La note de résolution de problèmes...` |
| `uid0164001b.msg` | `...pour le personnel de sÃ©curitÃ© en service a Ã©tÃ© rÃ©duite d'un niveau â˜….` | `...pour le personnel de sécurité en service a été réduite d'un niveau ★.` |

---

### C. Sous-titres des Cinématiques Scénarisées (`data/auth_w64_e/*.par`)

Dans les cinématiques (`auth_w64_e`), les sous-titres sont stockés dans `cmn.par -> cmn.bin` (compressé en SLLZ).
* La grande majorité des répliques est correctement encodée en Windows-1252.
* Les occurrences de `™` proviennent des apostrophes typographiques courbes `\xe2\x80\x99` ou de résidus de ponctuation UTF-8 (`â€¦`) insérés lors de l'export des sous-titres par les traducteurs.

---

## 3. Plan de Correction & Remédiation (Sans toucher aux textures)

Ces imperfections sont **entièrement automatisables et facilement patchables** :

1. **Script de nettoyage des chaînes :**
   Un script Python applique une table de conversion stricte sur les textes décompressés :
   - `\xe2\x80\x99` / `â€™` / `\x99` $\rightarrow$ `'` (ASCII `0x27`)
   - `Ã©` $\rightarrow$ `é` (`0xE9`), `Ã¨` $\rightarrow$ `è` (`0xE8`), `Ã ` $\rightarrow$ `à` (`0xE0`), `Ãª` $\rightarrow$ `ê` (`0xEA`), `Ã§` $\rightarrow$ `ç` (`0xE7`)
   - `Ã‰` $\rightarrow$ `É` (`0xC9`), `Ã€` $\rightarrow$ `À` (`0xC0`)
   - `Å“` / `œ` $\rightarrow$ `oe` ; `Å’` / `Œ` $\rightarrow$ `OE`
   - `â€¦` $\rightarrow$ `...`
   - `Â ` (espace insécable UTF-8) $\rightarrow$ ` ` (espace standard `0x20`)
   - `Â«` / `Â»` $\rightarrow$ `"`
2. **Réencapsulation PAR + SLLZ :**
   Les fichiers modifiés (`.msg`, `.bin_c`, `cmn.bin`) sont réinjectés dans leurs archives PAR respectives sans altérer les offsets ou la structure.
3. **Mise à jour du pack de distribution :**
   Les archives corrigées (`boot.par`, `wdr.par`, et les `.par` de cinématiques concernés) sont intégrées dans le dossier `release_gog/data/`.
