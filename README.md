# scrcpy-cpl

A lightweight, **zero-dependency**, cross-platform GUI control panel & launcher for [`scrcpy`](https://github.com/Genymobile/scrcpy) (v5.0+).
Works natively on **Windows**, **Linux**, and **macOS** using only Python's standard library (`tkinter`).

## Key Features

- **Clean Control Panel Applet Design (`.cpl` Inspired)**:
  - Fixed-width static geometry (zero layout shift when switching presets).
  - **Light Mode** default (Windows 11 Control Panel style) + one-click **Dark Mode** toggle.
  - Built-in **EN / ID** language switcher in the top-right corner (English by default).
- **Zero-Trust / Transparent Dependency Detection**:
  - Never downloads binaries silently behind your back.
  - Automatically collapses the dependency banner into a single-line status indicator once `scrcpy` and `adb` are detected.
  - When missing, provides transparent buttons to install via official package managers (`winget`, `brew`, `apt`/`pacman`/`dnf`), select a portable folder, or open official GitHub Releases.
- **Smart Presets + Automatic `Custom` Profile**:
  - 6 one-click presets (`Standard`, `Gaming 120`, `Screen Off`, `Virtual Desk`, `Camera`, `OTG Input`) + `Custom`.
  - Remembers your last selected preset across launches.
  - Modifying any option in the collapsible **Advanced Video & Control Settings** automatically switches to `Custom` and saves your custom configuration.
- **0 MB RAM Overhead During Mirroring**:
  - Spawns `scrcpy` as an independent detached process and automatically closes the panel on launch.

---

## How to Run

### 1. Download Standalone Executable (No Python Required)
Grab the latest pre-built executable for Windows (`scrcpy-cpl.exe`), Linux, or macOS from the **Actions Artifacts** or **Releases** tab.

### 2. Run Directly via Python
```bash
python3 scrcpy_launcher.py
```
- **Windows**: Double-click `run_windows.bat`
- **Linux / macOS**: Run `./run_unix.sh`

### 3. Build Standalone `.exe` Locally
```bash
python generate_icon.py
pyinstaller --onefile --windowed --clean --icon=scrcpy_cpl.ico --name "scrcpy-cpl" scrcpy_launcher.py
```
