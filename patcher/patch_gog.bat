@echo off
chcp 65001 >nul
title Yakuza 0 GOG - Patcher Traduction Francaise
echo ===================================================================
echo   Yakuza 0 GOG - Patcher Traduction Francaise
echo ===================================================================
echo.

REM Fermeture forcee de tout processus Yakuza0.exe residuel
tasklist /FI "IMAGENAME eq Yakuza0.exe" 2>nul | find /I /N "Yakuza0.exe">nul
if "%ERRORLEVEL%"=="0" (
    echo [*] Fermeture de Yakuza0.exe en cours d'execution...
    taskkill /F /IM Yakuza0.exe >nul 2>&1
    timeout /t 1 /nobreak >nul
)

REM Tester si 'python' fonctionne
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python patch_gog.py Yakuza0.exe
    goto :fin
)

REM Tester si 'py -3' fonctionne
py -3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    py -3 patch_gog.py Yakuza0.exe
    goto :fin
)

echo.
echo [ERREUR] Python n'a pas pu etre detecte sur votre machine.
echo Assurez-vous que Python 3 est installe sur votre PC (ex: via python.org ou Microsoft Store).
echo Si Python est deja installe, lancez directement :
echo    python patch_gog.py Yakuza0.exe

:fin
echo.
pause
