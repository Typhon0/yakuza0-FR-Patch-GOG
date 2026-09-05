# Guide d'Installation - Yakuza 0 Patch Français (GOG)

Ce guide détaille l'installation de la traduction française (VOSTFR Rev 1.10) pour l'édition **GOG** de **Yakuza 0**.

---

## 📋 Prérequis

* Le jeu **Yakuza 0** installé via **GOG** (GOG Galaxy ou installateur hors-ligne).
* **Python 3** installé sur votre machine (si ce n'est pas déjà le cas, téléchargeable gratuitement sur [python.org](https://www.python.org/) ou via le Microsoft Store).
* L'archive du patch : **`Yakuza_0_Patch_FR_GOG_Rev1.10.1.7z`** (1,70 Go).

---

## 🚀 Installation sous Windows

1. **Localisez le dossier d'installation du jeu** :
   * Si vous utilisez **GOG Galaxy** : Clic droit sur *Yakuza 0* dans votre bibliothèque $\rightarrow$ *Gérer l'installation* $\rightarrow$ *Afficher le dossier*.
   * Par défaut : `C:\GOG Games\Yakuza 0\` (ou `D:\GOG Games\Yakuza 0\`).
   * Vérifiez que le fichier `Yakuza0.exe` est bien présent dans ce dossier.

2. **Copiez les fichiers du patch** :
   * Ouvrez l'archive **`Yakuza_0_Patch_FR_GOG_Rev1.10.1.7z`** avec 7-Zip ou WinRAR.
   * Extrayez ou glissez-déposez **tout le contenu** de l'archive directement à la racine du jeu.
   * Lorsque Windows demande confirmation pour fusionner les dossiers ou remplacer des fichiers, choisissez **« Remplacer les fichiers dans la destination »**.

3. **Exécutez le patcher** :
   * Dans le dossier du jeu, double-cliquez sur le fichier :
     ```cmd
     patch_gog.bat
     ```
   * Le script effectue automatiquement les opérations suivantes :
     - Création d'une sauvegarde de sécurité **`Yakuza0.exe.bak`**.
     - Application des correctifs de sous-titres et de compatibilité DRM-free.
     - Injection de la table de police des caractères accentués (`é`, `è`, `à`, `ç`, `î`, etc.).
     - Préservation de l'espacement natif des caractères étroits (`i`, `l`).
     - Ajout de la section `.trad` et localisation des menus en français.
   * Un message de confirmation s'affiche : appuyez sur une touche pour fermer.

4. **Lancez le jeu** :
   * Démarrez le jeu normalement via GOG Galaxy ou directement avec `Yakuza0.exe`.

---

## 🐧 Installation sous Linux / Steam Deck

1. Rendez-vous dans le dossier racine du jeu Yakuza 0 (via Dolphin ou terminal) :
   * Exemple Heroic Games Launcher : `~/Games/Heroic/Yakuza 0/`
   * Exemple Lutris : `~/Games/yakuza-0/`
2. Extrayez l'archive dans ce répertoire en acceptant d'écraser les fichiers existants.
3. Ouvrez un terminal dans le dossier et lancez le script :
   ```bash
   chmod +x patch_gog.sh
   ./patch_gog.sh
   ```
4. Le patch s'applique en quelques secondes. Vous pouvez maintenant lancer le jeu.

---

## 🔄 Restauration / Désinstallation

Si vous souhaitez revenir à la version originale en anglais non modifiée :
1. Supprimez le fichier `Yakuza0.exe` patché.
2. Renommez le fichier de sauvegarde `Yakuza0.exe.bak` en `Yakuza0.exe`.
3. (Optionnel) Dans GOG Galaxy, utilisez la fonction **Vérifier / Réparer** pour restaurer l'ensemble des fichiers du jeu d'origine.

---

## ❓ En cas de problème

* **Le jeu crash au lancement** : Assurez-vous d'avoir bien exécuté `patch_gog.bat` sur votre `Yakuza0.exe` GOG d'origine. Ne remplacez jamais votre exécutable par un exécutable venant de Steam.
* **Le script indique "Python n'a pas pu être exécuté"** : Installez Python 3 depuis [python.org](https://www.python.org/) en prenant soin de cocher la case **« Add python.exe to PATH »** lors de l'installation.
