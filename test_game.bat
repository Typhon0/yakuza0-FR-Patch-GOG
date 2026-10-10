@echo off
chcp 65001 >nul
title Yakuza 0 GOG FR Patch — One-Click Test Runner

echo ======================================================================
echo   YAKUZA 0 GOG FR PATCH — TESTEUR RAPIDE 1-CLIC
echo ======================================================================

set "GAMEDIR=D:\GOG Games\Yakuza 0"

REM 1. Fermer le jeu s'il est en cours d'exécution
echo [*] Fermeture de Yakuza 0 si le jeu tourne...
taskkill /F /IM Yakuza0.exe 2>nul

REM 2. Déverrouiller les fichiers de jeu contre les verrous de lecture seule GOG
echo [*] Levée des verrous de lecture seule (+R)...
attrib -R "%GAMEDIR%\data\*.par" /S 2>nul

REM 3. Synchronisation intelligente des archives patchées
echo [*] Synchronisation des fichiers patchés vers le jeu...
python tools/sync_to_game.py "%GAMEDIR%"
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Échec de la synchronisation. Vérifie que Yakuza0.exe est bien dans %GAMEDIR%.
    pause
    exit /b 1
)

REM 4. Lancement du jeu
echo.
echo [*] Lancement de Yakuza 0...
start "" "%GAMEDIR%\Yakuza0.exe"

REM 5. Surveillance active des crash logs
echo.
echo [*] Surveillance active du crash log en cours...
echo     Si le jeu se ferme brutalement, l'analyse s'affichera immédiatement ici !
echo     (Appuie sur Ctrl+C pour arrêter le testeur à tout moment)
echo.
python tools/crash_analyzer.py --watch "%GAMEDIR%\logs\crash.log"

pause
