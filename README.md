# scrcpy-cpl

A lightweight, **zero-dependency**, cross-platform GUI control panel & launcher for [`scrcpy`](https://github.com/Genymobile/scrcpy) (v5.0+).
Works natively on **Windows**, **Linux**, and **macOS** using only Python's standard library (`tkinter`).

## Key Features

- **Clean Control Panel Applet Design (`.cpl` Inspired)**:
  - Fixed-width static geometry (zero layout shift when switching presets).
  - **Light Mode** default (Windows Control Panel style) + one-click **Dark Mode** toggle.
  - Built-in **EN / ID** language switcher in the top-right corner (English by default).
- **Zero-Trust / Transparent Dependency Detection**:
  - Never downloads binaries silently in the background.
  - Automatically collapses the dependency banner into a single-line status indicator once `scrcpy` and `adb` are detected.
  - When missing, provides transparent buttons to:
    - Install both `scrcpy` + `adb` via official package managers (`winget`, `brew`, `apt`/`pacman`/`dnf`) or an automatic **PowerShell Official Release Installer** fallback (for Windows systems without `winget`).
    - Select a custom portable folder (`Folder...`).
    - Open official [scrcpy GitHub Releases](https://github.com/Genymobile/scrcpy/releases) or [Official Google ADB Platform-Tools](https://developer.android.com/tools/releases/platform-tools).
- **Smart Presets + Automatic `Custom` Profile**:
  - 6 one-click presets (`Standard`, `Gaming 120`, `Screen Off`, `Virtual Desk`, `Camera`, `OTG Input`) + `Custom`.
  - Remembers your last selected preset across launches.
  - Modifying any option in the collapsible **Advanced Video, Audio & Control Settings** automatically switches to `Custom` and saves your custom configuration.
- **Comprehensive 3-Tab Advanced Panel (Collapsed by Default)**:
  - **Video & Display**: Source, Max Size (`-m`), Max FPS, **Bit Rate (`-b`)**, Video Codec (`h265`/`h264`/`av1`), Capture Orientation, Camera Facing (`back`/`front`/`external`), Flex Virtual Display (`-x`), MP4 Recording.
  - **Audio & Input**: Audio Source (`output`/`playback`/`mic`/`voice-call`), Audio Codec (`opus`/`aac`/`flac`/`raw`), Audio Duplication (`--audio-dup`), Keyboard/Mouse/Gamepad modes (`sdk`/`uhid`/`aoa`), Read-Only mode (`-n`).
  - **Device & Window**: Turn Screen Off (`-S`), Stay Awake (`-w`), Power Off on Close, Show Touches (`-t`), Always on Top, Fullscreen (`-f`), Borderless Window, Disable PC Screensaver, and custom Extra Flags.
- **0 MB RAM Overhead During Mirroring**:
  - Spawns `scrcpy` as an independent detached process and automatically closes the panel on launch.

---

## How to Run

### 1. Download Standalone Executable (No Python Required)
Grab the latest pre-built executable for **Windows** (`scrcpy-cpl.exe`), **Linux** (`scrcpy-cpl`), or **macOS** (`scrcpy-cpl-macos.zip`) from the [**Releases**](https://github.com/bimoich/scrcpy-cpl/releases) page.

> **Windows SmartScreen Note**: Because this is a free open-source binary without a paid commercial code-signing certificate, Windows Defender SmartScreen may show a *"Windows protected your PC"* prompt when downloaded via a web browser. Click **More info** -> **Run anyway**, or download and launch directly via PowerShell (which avoids browser Mark-of-the-Web flags):
> ```powershell
> irm https://github.com/bimoich/scrcpy-cpl/releases/latest/download/scrcpy-cpl.exe -OutFile scrcpy-cpl.exe; .\scrcpy-cpl.exe
> ```

### 2. Run Directly from Source (Python 3)
```bash
python3 scrcpy_cpl.py
```
- **Windows**: Double-click `run_windows.bat`
- **Linux / macOS**: Run `./run_unix.sh`

*(Note for Linux users: ensure `python3-tk` is installed via your package manager, e.g., `sudo apt install python3-tk`).*

### 3. Build Standalone Executable Locally
```bash
python generate_icon.py
pyinstaller --onefile --windowed --clean --icon=scrcpy_cpl.ico --version-file=version_info.txt --name "scrcpy-cpl" scrcpy_cpl.py
```

---

## License

Licensed under the [MIT License](LICENSE). Copyright (c) 2026 **bmolab**.
