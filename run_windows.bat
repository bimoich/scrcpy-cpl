@echo off
title scrcpy-cpl
cd /d "%~dp0"

:: 1. Check if pythonw / python is available (Zero extra install if user has Python)
where pythonw >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" pythonw "%~dp0scrcpy_cpl.py"
    exit /b 0
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" python "%~dp0scrcpy_cpl.py"
    exit /b 0
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" py -3 "%~dp0scrcpy_cpl.py"
    exit /b 0
)

echo ============================================================
echo   Python 3 is not installed on your Windows system.
echo ============================================================
echo.
echo   To run scrcpy_cpl.py directly from source, please install
echo   Python 3 (or download the standalone scrcpy-cpl.exe release):
echo.
echo   [1] Install Python 3 via Winget (winget install Python.Python.3.12)
echo   [2] Open python.org/downloads
echo   [3] Exit
echo.
set /p choice="Select [1-3]: "
if "%choice%"=="1" (
    winget install --exact --id Python.Python.3.12
    pause
)
if "%choice%"=="2" (
    start https://www.python.org/downloads/
)
exit /b 0
