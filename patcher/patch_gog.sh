#!/usr/bin/env bash
# Yakuza 0 GOG - Patcher Traduction Française (Linux / Steam Deck)
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==================================================================="
echo "  Yakuza 0 GOG - Patcher Traduction Française (Rev 1.10)"
echo "==================================================================="
echo ""

if [ ! -f "Yakuza0.exe" ]; then
    echo "[ERREUR] Yakuza0.exe est introuvable dans ce répertoire."
    echo "Veuillez copier les fichiers directement dans le dossier d'installation du jeu."
    exit 1
fi

if command -v python3 &>/dev/null; then
    python3 patch_gog.py Yakuza0.exe
elif command -v python &>/dev/null; then
    python patch_gog.py Yakuza0.exe
else
    echo "[ERREUR] Python 3 est introuvable."
    echo "Veuillez installer Python 3 pour exécuter le patcher."
    exit 1
fi

echo ""
echo "Installation terminée avec succès !"
