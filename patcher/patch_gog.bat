@echo off
title Yakuza 0 GOG - Patcher Traduction Francaise
echo ===================================================================
echo   Yakuza 0 GOG - Patcher Traduction Francaise (Rev 1.10)
echo ===================================================================
echo.

python patch_gog.py Yakuza0.exe
if %ERRORLEVEL% equ 0 goto :fin

py -3 patch_gog.py Yakuza0.exe
if %ERRORLEVEL% equ 0 goto :fin

echo.
echo [ERREUR] Python n'a pas pu etre execute.
echo Assurez-vous que Python 3 est installe sur votre PC (ex: via python.org ou Microsoft Store).
echo Si Python est deja installe, lancez directement :
echo    python patch_gog.py Yakuza0.exe

:fin
echo.
pause
