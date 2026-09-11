@echo off
chcp 65001 >nul
echo ========================================================
echo   Yakuza 0 GOG - Collecteur de Fichiers et Logs
echo ========================================================
echo.

REM 1. Detection du repertoire du jeu
if "%~1"=="" (
    if exist "%~dp0Yakuza0.exe" (
        set "GAMEDIR=%~dp0"
    ) else if exist "%~dp0..\Yakuza0.exe" (
        set "GAMEDIR=%~dp0.."
    ) else if exist "%CD%\Yakuza0.exe" (
        set "GAMEDIR=%CD%"
    ) else if exist "%CD%\..\Yakuza0.exe" (
        set "GAMEDIR=%CD%\.."
    ) else if exist "%CD%\..\..\Yakuza0.exe" (
        set "GAMEDIR=%CD%\..\.."
    ) else if exist "D:\GOG Games\Yakuza 0\Yakuza0.exe" (
        set "GAMEDIR=D:\GOG Games\Yakuza 0"
    ) else if exist "C:\GOG Games\Yakuza 0\Yakuza0.exe" (
        set "GAMEDIR=C:\GOG Games\Yakuza 0"
    ) else if exist "C:\Program Files (x86)\GOG Galaxy\Games\Yakuza 0\Yakuza0.exe" (
        set "GAMEDIR=C:\Program Files (x86)\GOG Galaxy\Games\Yakuza 0"
    ) else (
        echo [ERREUR] Impossible de trouver Yakuza0.exe.
        echo Placez ce script dans le dossier de Yakuza 0 ou specifiez le chemin :
        echo   collect_originals.bat "D:\GOG Games\Yakuza 0"
        echo.
        pause
        exit /b 1
    )
) else (
    set "GAMEDIR=%~1"
)

if "%GAMEDIR:~-1%"=="\" set "GAMEDIR=%GAMEDIR:~0,-1%"

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
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$gamedir = \"%GAMEDIR%\"; $zip = Join-Path $gamedir 'yakuza0_diagnostics.zip'; if (Test-Path $zip) { Remove-Item $zip -Force }; $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString()); New-Item -ItemType Directory -Path $tmp | Out-Null; Write-Host '[1/3] Collecte des logs et crash dumps...'; Get-ChildItem -Path $gamedir -Filter '*.log' -Recurse | Where-Object { $_.FullName -notmatch '\\python\\' -and $_.FullName -notmatch '\\\.git\\' } | ForEach-Object { $dst = Join-Path $tmp (Join-Path 'crash_logs' $_.Name); New-Item -ItemType Directory -Path (Split-Path $dst) -Force | Out-Null; Copy-Item $_.FullName $dst -Force; Write-Host ('  + Inclus: ' + $_.Name) }; Write-Host '[2/3] Collecte des fichiers de sauvegarde .bak...'; Get-ChildItem -Path $gamedir -Filter '*.bak' -Recurse | ForEach-Object { $rel = $_.FullName.Substring($gamedir.Length).TrimStart('\\'); $dst = Join-Path $tmp (Join-Path 'backups_originaux' $rel); New-Item -ItemType Directory -Path (Split-Path $dst) -Force | Out-Null; Copy-Item $_.FullName $dst -Force; Write-Host ('  + Inclus: ' + $rel) }; Write-Host '[3/3] Collecte des archives cibles actives...'; @('data\\wdr_par_c\\wdr.par', 'data\\wdr_par_c\\common.par', 'data\\bootpar\\boot.par', 'data\\staypar\\stay.par') | ForEach-Object { $f = Join-Path $gamedir $_; if (Test-Path $f) { $dst = Join-Path $tmp (Join-Path 'current_active_par' $_); New-Item -ItemType Directory -Path (Split-Path $dst) -Force | Out-Null; Copy-Item $f $dst -Force; Write-Host ('  + Inclus: ' + $_) } }; Write-Host '[*] Creation du fichier ZIP...'; Compress-Archive -Path (Join-Path $tmp '*') -DestinationPath $zip -Force; Remove-Item -Recurse -Force $tmp; Write-Host ''; Write-Host '======================================================'; Write-Host ('[+] Fichier genere avec succes : ' + $zip); Write-Host '======================================================'"

:end
echo.
pause
exit /b 0
