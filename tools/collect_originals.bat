@echo off
chcp 65001 >nul
echo ========================================================
echo   Yakuza 0 GOG — Collecteur de Fichiers Originaux et Logs
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

REM 2. Tentative avec Python embarque ou systeme
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

REM 3. Fallback autonome PowerShell (sans aucune dependance Python)
echo [*] Python non detecte, utilisation du collecteur PowerShell natif...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$gameDir = \"%GAMEDIR%\"; $zipPath = Join-Path $gameDir 'yakuza0_diagnostics.zip'; if (Test-Path $zipPath) { Remove-Item $zipPath -Force }; $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString()); New-Item -ItemType Directory -Path $tempDir | Out-Null; Write-Host '[1/3] Collecte des logs et crash dumps...'; Get-ChildItem -Path $gameDir -Filter '*.log' -Recurse | Where-Object { $_.FullName -notmatch '\\python\\' -and $_.FullName -notmatch '\\\.git\\' } | ForEach-Object { $dest = Join-Path $tempDir 'crash_logs' $_.Name; New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null; Copy-Item $_.FullName $dest -Force; Write-Host ('  + Inclus: ' + $_.Name) }; Write-Host '[2/3] Collecte des fichiers de sauvegarde .bak...'; Get-ChildItem -Path $gameDir -Filter '*.bak' -Recurse | ForEach-Object { $rel = $_.FullName.Substring($gameDir.Length).TrimStart('\\'); $dest = Join-Path $tempDir (Join-Path 'backups_originaux' $rel); New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null; Copy-Item $_.FullName $dest -Force; Write-Host ('  + Inclus: ' + $rel) }; Write-Host '[3/3] Collecte des archives cibles actives...'; @('data\\wdr_par_c\\wdr.par', 'data\\wdr_par_c\\common.par', 'data\\bootpar\\boot.par', 'data\\staypar\\stay.par') | ForEach-Object { $src = Join-Path $gameDir $_; if (Test-Path $src) { $dest = Join-Path $tempDir (Join-Path 'current_active_par' $_); New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null; Copy-Item $src $dest -Force; Write-Host ('  + Inclus: ' + $_) } }; Write-Host '[*] Creation du fichier ZIP...'; Compress-Archive -Path (Join-Path $tempDir '*') -DestinationPath $zipPath -Force; Remove-Item -Recurse -Force $tempDir; Write-Host ''; Write-Host '======================================================'; Write-Host ('[+] Fichier genere avec succes : ' + $zipPath); Write-Host '======================================================'"

:end
echo.
pause
exit /b 0
