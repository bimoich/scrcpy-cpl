@echo off
title scrcpy Light Launcher
cd /d "%~dp0"

:: 1. Check if pythonw / python is available (Zero extra install if user has Python)
where pythonw >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" pythonw "%~dp0scrcpy_launcher.py"
    exit /b 0
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" python "%~dp0scrcpy_launcher.py"
    exit /b 0
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" py -3 "%~dp0scrcpy_launcher.py"
    exit /b 0
)

echo ============================================================
echo   Python 3 belum terinstall di Windows kamu.
echo ============================================================
echo.
echo   Untuk menjalankan scrcpy_launcher.py (Cross-Platform GUI),
echo   silakan install Python 3 terlebih dahulu:
echo.
echo   [1] Install Python 3 resmi via Winget (winget install Python.Python.3.12)
echo   [2] Buka website resmi python.org/downloads
echo   [3] Keluar
echo.
set /p choice="Pilih [1-3]: "
if "%choice%"=="1" (
    winget install --exact --id Python.Python.3.12
    pause
)
if "%choice%"=="2" (
    start https://www.python.org/downloads/
)
exit /b 0
