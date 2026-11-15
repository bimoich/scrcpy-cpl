# scrcpy Light Launcher

A lightweight, **zero-dependency**, cross-platform GUI wrapper for [`scrcpy`](https://github.com/Genymobile/scrcpy) (v5.0+).
Works natively on **Windows**, **Linux**, and **macOS** using only Python's standard library (`tkinter`).

## Why scrcpy Light Launcher?

- **Zero Trust / Security Friendly**: Never silently downloads binaries behind your back. It detects whether `scrcpy` and `adb` are installed on your system (or in a portable folder) and provides transparent options to install them via official package managers (`winget`, `brew`, `apt`/`pacman`/`dnf`) or official GitHub releases.
- **0 MB RAM Overhead During Mirroring**: Once you click **Start Mirroring**, `scrcpy` is spawned as an independent detached process and the launcher automatically closes itself.
- **No `pip install` Needed**: 100% pure Python Standard Library (`tkinter`, `subprocess`, `json`, `shutil`). Easy to audit, read, and modify in a single file (`scrcpy_launcher.py`).
- **One-Click Presets**:
  - **Standard**: H.265, 1080p, 60 FPS
  - **Gaming 120fps**: H.265, 120 FPS, Physical UHID Keyboard (`-K`) & Gamepad (`-G`)
  - **Privacy / Battery Saver**: Turn physical phone screen off (`-S`) + Stay Awake (`--stay-awake`)
  - **Virtual Display (DeX Mode)**: Launch an independent 1080p virtual display (`--new-display=1920x1080`)
  - **Camera Mode**: Mirror your phone camera (`--video-source=camera`)
  - **OTG Only**: Control phone with PC keyboard/mouse without screen mirroring (`--otg`)
- **Persistent Config**: Remembers your last settings and custom `scrcpy` portable folder in `~/.scrcpy_light_launcher.json`.

---

## How to Run

### 1. Direct Python (Windows, Linux, macOS)
```bash
python3 scrcpy_launcher.py
```
- **Windows**: Double-click `run_windows.bat`
- **Linux / macOS**: Run `./run_unix.sh`

*(Note for Linux users: ensure `python3-tk` is installed via your package manager, e.g., `sudo apt install python3-tk`).*

### 2. Optional: Build Standalone Executable (`.exe` / `.app` / Binary)
If you want to distribute standalone binaries on GitHub Releases so end-users don't even need Python installed:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "scrcpy-light-launcher" scrcpy_launcher.py
```

---

## License
Apache-2.0 / MIT
