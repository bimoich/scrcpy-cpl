@echo off
title Build scrcpy-light-launcher.exe
cd /d "%~dp0"

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python belum terdeteksi di PATH Windows kamu.
    echo Silakan install Python terlebih dahulu atau gunakan GitHub Actions untuk build otomatis.
    pause
    exit /b 1
)

echo [1/2] Memastikan PyInstaller terinstall...
python -m pip install --upgrade pip pyinstaller

echo.
echo [2/2] Meng-compile scrcpy_launcher.py menjadi .exe tunggal...
python -m PyInstaller --onefile --windowed --clean --name "scrcpy-light-launcher" scrcpy_launcher.py

echo.
if exist "dist\scrcpy-light-launcher.exe" (
    echo ============================================================
    echo   BERHASIL! File .exe sudah jadi di:
    echo   %~dp0dist\scrcpy-light-launcher.exe
    echo ============================================================
) else (
    echo [ERROR] Gagal membuat file .exe.
)
pause
