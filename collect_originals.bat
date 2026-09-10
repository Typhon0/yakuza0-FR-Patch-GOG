@echo off
chcp 65001 >nul
echo ========================================================
echo   Yakuza 0 GOG - Collecteur de Fichiers et Logs
echo ========================================================
echo.

REM 1. Detection du repertoire du jeu
if "%~1"=="" (
    if exist "data\wdr_par_c\wdr.par" (
        set "GAMEDIR=%CD%"
    ) else if exist "..\data\wdr_par_c\wdr.par" (
        set "GAMEDIR=%CD%\.."
    ) else (
        echo [ERREUR] Impossible de trouver le dossier du jeu.
        echo Placez ce script dans le dossier de Yakuza 0 ou specifiez le chemin :
        echo   collect_originals.bat "D:\GOG Games\Yakuza 0"
        echo.
        pause
        exit /b 1
    )
) else (
    set "GAMEDIR=%~1"
)

echo [*] Dossier du jeu : %GAMEDIR%
echo.

REM 2. Execution via Python embarque ou systeme
set "PYTHON="
if exist "%~dp0python\python.exe" (
    set "PYTHON=%~dp0python\python.exe"
) else if exist "%GAMEDIR%\python\python.exe" (
    set "PYTHON=%GAMEDIR%\python\python.exe"
) else (
    where python >nul 2>&1
    if not errorlevel 1 set "PYTHON=python"
)

if defined PYTHON (
    echo [*] Execution de la collecte via Python...
    if exist "%~dp0tools\collect_originals.py" (
        "%PYTHON%" "%~dp0tools\collect_originals.py" "%GAMEDIR%"
        goto :end
    ) else if exist "%~dp0collect_originals.py" (
        "%PYTHON%" "%~dp0collect_originals.py" "%GAMEDIR%"
        goto :end
    )
)

REM 3. Fallback autonome PowerShell
echo [*] Python non detecte, utilisation du collecteur PowerShell natif...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command " = '%GAMEDIR%';  = Join-Path  'yakuza0_diagnostics.zip'; if (Test-Path ) { Remove-Item  -Force };  = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString()); New-Item -ItemType Directory -Path  | Out-Null; Write-Host '[1/3] Collecte des logs et crash dumps...'; Get-ChildItem -Path  -Filter '*.log' -Recurse | Where-Object { xxd.FullName -notmatch '\python\' -and xxd.FullName -notmatch '\\.git\' } | ForEach-Object {  = Join-Path  (Join-Path 'crash_logs' xxd.Name); New-Item -ItemType Directory -Path (Split-Path ) -Force | Out-Null; Copy-Item xxd.FullName  -Force; Write-Host ('  + Inclus: ' + xxd.Name) }; Write-Host '[2/3] Collecte des fichiers de sauvegarde .bak...'; Get-ChildItem -Path  -Filter '*.bak' -Recurse | ForEach-Object {  = xxd.FullName.Substring(.Length).TrimStart('\');  = Join-Path  (Join-Path 'backups_originaux' ); New-Item -ItemType Directory -Path (Split-Path ) -Force | Out-Null; Copy-Item xxd.FullName  -Force; Write-Host ('  + Inclus: ' + ) }; Write-Host '[3/3] Collecte des archives cibles actives...'; @('data\wdr_par_c\wdr.par', 'data\wdr_par_c\common.par', 'data\bootpar\boot.par', 'data\staypar\stay.par') | ForEach-Object {  = Join-Path  xxd; if (Test-Path ) {  = Join-Path  (Join-Path 'current_active_par' xxd); New-Item -ItemType Directory -Path (Split-Path ) -Force | Out-Null; Copy-Item   -Force; Write-Host ('  + Inclus: ' + xxd) } }; Write-Host '[*] Creation du fichier ZIP...'; Compress-Archive -Path (Join-Path  '*') -DestinationPath  -Force; Remove-Item -Recurse -Force ; Write-Host ''; Write-Host '======================================================'; Write-Host ('[+] Fichier genere avec succes : ' + ); Write-Host '======================================================'"

:end
echo.
pause
exit /b 0
