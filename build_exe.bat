@echo off
title Build scrcpy-cpl.exe
cd /d "%~dp0"

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not detected in your Windows PATH.
    echo Please install Python first or use GitHub Actions for automatic builds.
    pause
    exit /b 1
)

echo [1/3] Ensuring PyInstaller is installed...
python -m pip install --upgrade pip pyinstaller

echo.
echo [2/3] Generating custom scrcpy_cpl.ico...
python generate_icon.py

echo.
echo [3/3] Compiling scrcpy_launcher.py into standalone scrcpy-cpl.exe...
python -m PyInstaller --onefile --windowed --clean --icon=scrcpy_cpl.ico --name "scrcpy-cpl" scrcpy_launcher.py

echo.
if exist "dist\scrcpy-cpl.exe" (
    echo ============================================================
    echo   SUCCESS! Standalone executable created at:
    echo   %~dp0dist\scrcpy-cpl.exe
    echo ============================================================
) else (
    echo [ERROR] Failed to build executable.
)
pause
