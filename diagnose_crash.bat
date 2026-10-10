@echo off
chcp 65001 >nul
title Diagnostic de Crash Instantane - Yakuza 0 GOG FR

echo ======================================================================
echo   DIAGNOSTIC DE CRASH INSTANTANÉ (RUST) — YAKUZA 0 GOG FR
echo ======================================================================
echo.

if not exist "rgg_preflight.exe" (
    if exist "release_gog\rgg_preflight.exe" (
        copy /y "release_gog\rgg_preflight.exe" "rgg_preflight.exe" >nul
    ) else (
        echo [-] rgg_preflight.exe est introuvable.
        pause
        exit /b 1
    )
)

set LOG_FILE=logs\crash.log
if not exist "%LOG_FILE%" (
    if exist "crash.log" (
        set LOG_FILE=crash.log
    ) else (
        echo [!] Aucun fichier 'logs\crash.log' trouve.
        echo Assurez-vous d'avoir Special K ou un rapport de crash actif.
        echo.
        pause
        exit /b 1
    )
)

rgg_preflight.exe crash "%LOG_FILE%" data Yakuza0.exe

echo.
pause
