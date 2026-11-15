#!/usr/bin/env python3
"""
scrcpy Light Launcher
A lightweight, zero-dependency, cross-platform GUI launcher for scrcpy (v5.0+).
Works on Windows, Linux, and macOS using Python's built-in tkinter.
"""

import json
import os
import platform
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

APP_TITLE = "scrcpy Light Launcher"
APP_VERSION = "1.0.0"
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".scrcpy_light_launcher.json")
OFFICIAL_RELEASES_URL = "https://github.com/Genymobile/scrcpy/releases"
OFFICIAL_DOCS_URL = "https://github.com/Genymobile/scrcpy"

IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


class ScrcpyLauncherApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_TITLE} v{APP_VERSION}")
        self.root.resizable(False, False)

        # State variables
        self.config = self.load_config()
        self.custom_bin_dir = self.config.get("custom_bin_dir", "")
        self.scrcpy_path = None
        self.adb_path = None
        self.scrcpy_version = ""
        self.devices = []  # List of dicts: {"serial": ..., "model": ..., "state": ...}

        # UI Variables
        self.var_device = tk.StringVar()
        self.var_preset = tk.StringVar(value=self.config.get("preset", "standard"))
        self.var_source = tk.StringVar(value=self.config.get("source", "display"))
        self.var_max_size = tk.StringVar(value=self.config.get("max_size", "1920 (1080p)"))
        self.var_fps = tk.StringVar(value=self.config.get("fps", "60"))
        self.var_codec = tk.StringVar(value=self.config.get("codec", "h265"))
        self.var_bitrate = tk.StringVar(value=self.config.get("bitrate", "Default (8M)"))

        self.var_screen_off = tk.BooleanVar(value=self.config.get("screen_off", False))
        self.var_stay_awake = tk.BooleanVar(value=self.config.get("stay_awake", True))
        self.var_no_audio = tk.BooleanVar(value=self.config.get("no_audio", False))
        self.var_uhid_kb = tk.BooleanVar(value=self.config.get("uhid_kb", False))
        self.var_uhid_gamepad = tk.BooleanVar(value=self.config.get("uhid_gamepad", False))
        self.var_always_on_top = tk.BooleanVar(value=self.config.get("always_on_top", False))
        self.var_fullscreen = tk.BooleanVar(value=self.config.get("fullscreen", False))
        self.var_record = tk.BooleanVar(value=self.config.get("record", False))
        self.var_record_path = tk.StringVar(value=self.config.get("record_path", "scrcpy_capture.mp4"))
        self.var_extra_args = tk.StringVar(value=self.config.get("extra_args", ""))
        self.var_auto_close = tk.BooleanVar(value=self.config.get("auto_close", True))

        self.setup_theme()
        self.build_ui()
        self.check_binaries()
        self.refresh_devices()
        self.update_command_preview()

    def setup_theme(self):
        self.bg_main = "#0f172a"
        self.bg_card = "#1e293b"
        self.bg_input = "#0f172a"
        self.fg_main = "#f8fafc"
        self.fg_muted = "#94a3b8"
        self.accent = "#38bdf8"
        self.success = "#22c55e"
        self.danger = "#ef4444"
        self.warning = "#f59e0b"
        self.border = "#334155"

        self.root.configure(bg=self.bg_main)
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=self.bg_main)
        style.configure("Card.TFrame", background=self.bg_card)
        style.configure("TLabel", background=self.bg_main, foreground=self.fg_main, font=("Segoe UI", 9))
        style.configure("Card.TLabel", background=self.bg_card, foreground=self.fg_main, font=("Segoe UI", 9))
        style.configure("Muted.Card.TLabel", background=self.bg_card, foreground=self.fg_muted, font=("Segoe UI", 8))
        style.configure("Header.TLabel", background=self.bg_main, foreground=self.fg_main, font=("Segoe UI", 12, "bold"))
        style.configure("SubHeader.Card.TLabel", background=self.bg_card, foreground=self.accent, font=("Segoe UI", 9, "bold"))

        style.configure(
            "TCombobox",
            fieldbackground=self.bg_input,
            background=self.bg_card,
            foreground=self.fg_main,
            arrowcolor=self.fg_main,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.bg_input)],
            selectbackground=[("readonly", self.bg_input)],
            selectforeground=[("readonly", self.fg_main)],
        )

    def build_ui(self):
        container = tk.Frame(self.root, bg=self.bg_main, padx=14, pady=12)
        container.pack(fill="both", expand=True)

        # 1. Header
        header_frame = tk.Frame(container, bg=self.bg_main)
        header_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            header_frame,
            text="scrcpy Light Launcher",
            bg=self.bg_main,
            fg=self.fg_main,
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left")

        tk.Label(
            header_frame,
            text=f"({platform.system()}) • Zero RAM after launch",
            bg=self.bg_main,
            fg=self.fg_muted,
            font=("Segoe UI", 8),
        ).pack(side="left", padx=(8, 0), pady=(3, 0))

        # 2. Dependency Status Card (scrcpy & adb detection)
        self.status_card = tk.Frame(
            container, bg=self.bg_card, highlightbackground=self.border, highlightthickness=1, padx=10, pady=8
        )
        self.status_card.pack(fill="x", pady=(0, 8))

        status_top = tk.Frame(self.status_card, bg=self.bg_card)
        status_top.pack(fill="x")

        self.lbl_scrcpy_status = tk.Label(
            status_top, text="● Checking scrcpy...", bg=self.bg_card, fg=self.fg_muted, font=("Segoe UI", 9, "bold")
        )
        self.lbl_scrcpy_status.pack(side="left")

        tk.Label(status_top, text="  |  ", bg=self.bg_card, fg=self.border).pack(side="left")

        self.lbl_adb_status = tk.Label(
            status_top, text="● Checking adb...", bg=self.bg_card, fg=self.fg_muted, font=("Segoe UI", 9, "bold")
        )
        self.lbl_adb_status.pack(side="left")

        btn_recheck = tk.Button(
            status_top,
            text="↻ Re-check",
            command=self.on_recheck,
            bg=self.bg_input,
            fg=self.fg_main,
            activebackground=self.border,
            activeforeground=self.fg_main,
            relief="flat",
            font=("Segoe UI", 8),
            padx=6,
            pady=1,
            cursor="hand2",
        )
        btn_recheck.pack(side="right")

        btn_browse_folder = tk.Button(
            status_top,
            text="📁 Pilih Folder scrcpy...",
            command=self.browse_bin_folder,
            bg=self.bg_input,
            fg=self.accent,
            activebackground=self.border,
            activeforeground=self.fg_main,
            relief="flat",
            font=("Segoe UI", 8),
            padx=6,
            pady=1,
            cursor="hand2",
        )
        btn_browse_folder.pack(side="right", padx=(0, 6))

        # Missing binary action bar (only shown when scrcpy or adb is missing)
        self.missing_bar = tk.Frame(self.status_card, bg=self.bg_card)

        self.lbl_missing_hint = tk.Label(
            self.missing_bar,
            text="Aplikasi ini tidak mengunduh binary diam-diam. Silakan install scrcpy/adb resmi atau pilih foldernya:",
            bg=self.bg_card,
            fg=self.fg_muted,
            font=("Segoe UI", 8),
            anchor="w",
        )
        self.lbl_missing_hint.pack(fill="x", pady=(6, 4))

        missing_btns = tk.Frame(self.missing_bar, bg=self.bg_card)
        missing_btns.pack(fill="x")

        install_btn_text = self.get_os_install_button_label()
        tk.Button(
            missing_btns,
            text=install_btn_text,
            command=self.run_official_package_install,
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            padx=8,
            pady=3,
            cursor="hand2",
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            missing_btns,
            text="🌐 Buka GitHub Resmi (Genymobile/scrcpy)",
            command=lambda: webbrowser.open(OFFICIAL_RELEASES_URL),
            bg=self.bg_input,
            fg=self.fg_main,
            activebackground=self.border,
            activeforeground=self.fg_main,
            relief="flat",
            font=("Segoe UI", 8),
            padx=8,
            pady=3,
            cursor="hand2",
        ).pack(side="left")

        # 3. Device Selection Card
        dev_card = tk.Frame(
            container, bg=self.bg_card, highlightbackground=self.border, highlightthickness=1, padx=10, pady=8
        )
        dev_card.pack(fill="x", pady=(0, 8))

        dev_header = tk.Frame(dev_card, bg=self.bg_card)
        dev_header.pack(fill="x", pady=(0, 4))

        tk.Label(
            dev_header, text="PERANGKAT ANDROID (ADB)", bg=self.bg_card, fg=self.accent, font=("Segoe UI", 8, "bold")
        ).pack(side="left")

        tk.Button(
            dev_header,
            text="📶 Connect WiFi (TCP/IP)",
            command=self.open_wifi_dialog,
            bg=self.bg_input,
            fg=self.accent,
            relief="flat",
            font=("Segoe UI", 8),
            padx=6,
            pady=1,
            cursor="hand2",
        ).pack(side="right")

        tk.Button(
            dev_header,
            text="↻ Refresh Device",
            command=self.refresh_devices,
            bg=self.bg_input,
            fg=self.fg_main,
            relief="flat",
            font=("Segoe UI", 8),
            padx=6,
            pady=1,
            cursor="hand2",
        ).pack(side="right", padx=(0, 6))

        self.cmb_device = ttk.Combobox(dev_card, textvariable=self.var_device, state="readonly", width=62)
        self.cmb_device.pack(fill="x", pady=(2, 0))
        self.cmb_device.bind("<<ComboboxSelected>>", lambda e: self.update_command_preview())

        # 4. Quick Presets Bar
        preset_card = tk.Frame(
            container, bg=self.bg_card, highlightbackground=self.border, highlightthickness=1, padx=10, pady=8
        )
        preset_card.pack(fill="x", pady=(0, 8))

        tk.Label(
            preset_card,
            text="PRESET CEPAT (1-KLIK KONFIGURASI)",
            bg=self.bg_card,
            fg=self.accent,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        preset_row = tk.Frame(preset_card, bg=self.bg_card)
        preset_row.pack(fill="x")

        presets = [
            ("🚀 Standard", "standard"),
            ("🎮 Gaming 120fps", "gaming"),
            ("🔋 Layar HP Mati", "privacy"),
            ("🖥️ Virtual Display", "dex"),
            ("📷 Kamera HP", "camera"),
            ("⌨️ OTG Only", "otg"),
        ]
        self.preset_buttons = {}
        for label, key in presets:
            btn = tk.Button(
                preset_row,
                text=label,
                command=lambda k=key: self.apply_preset(k),
                bg=self.bg_input,
                fg=self.fg_main,
                relief="flat",
                font=("Segoe UI", 8),
                padx=7,
                pady=4,
                cursor="hand2",
            )
            btn.pack(side="left", padx=(0, 5))
            self.preset_buttons[key] = btn

        # 5. Video & Options Grid
        opts_card = tk.Frame(
            container, bg=self.bg_card, highlightbackground=self.border, highlightthickness=1, padx=10, pady=8
        )
        opts_card.pack(fill="x", pady=(0, 8))

        tk.Label(
            opts_card,
            text="PENGATURAN VIDEO & KONTROL",
            bg=self.bg_card,
            fg=self.accent,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        grid_top = tk.Frame(opts_card, bg=self.bg_card)
        grid_top.pack(fill="x", pady=(0, 8))

        # Source
        self._add_dropdown(
            grid_top,
            "Mode Sumber:",
            self.var_source,
            ["display", "new-display", "camera", "otg"],
            0,
            width=14,
        )
        # Resolution
        self._add_dropdown(
            grid_top,
            "Resolusi Maks:",
            self.var_max_size,
            ["Asli (Tanpa Batas)", "2560 (1440p)", "1920 (1080p)", "1280 (720p)", "1024 (Ringan)"],
            1,
            width=16,
        )
        # FPS
        self._add_dropdown(
            grid_top,
            "Max FPS:",
            self.var_fps,
            ["Default", "30", "60", "90", "120"],
            2,
            width=10,
        )
        # Codec
        self._add_dropdown(
            grid_top,
            "Video Codec:",
            self.var_codec,
            ["h265", "h264", "av1"],
            3,
            width=10,
        )

        # Checkboxes (2 columns)
        chk_frame = tk.Frame(opts_card, bg=self.bg_card)
        chk_frame.pack(fill="x")

        checks = [
            ("Matikan Layar Fisik HP (-S / --turn-screen-off)", self.var_screen_off, 0, 0),
            ("Cegah HP Terkunci / Sleep (--stay-awake)", self.var_stay_awake, 0, 1),
            ("Matikan Suara / Audio (--no-audio)", self.var_no_audio, 1, 0),
            ("Simulasi Keyboard Fisik UHID (-K)", self.var_uhid_kb, 1, 1),
            ("Simulasi Gamepad UHID (-G)", self.var_uhid_gamepad, 2, 0),
            ("Jendela Selalu di Atas (--always-on-top)", self.var_always_on_top, 2, 1),
            ("Langsung Fullscreen (-f)", self.var_fullscreen, 3, 0),
            ("Rekam Layar ke File MP4 (--record)", self.var_record, 3, 1),
        ]

        for text, var, r, c in checks:
            cb = tk.Checkbutton(
                chk_frame,
                text=text,
                variable=var,
                command=self.update_command_preview,
                bg=self.bg_card,
                fg=self.fg_main,
                selectcolor=self.bg_input,
                activebackground=self.bg_card,
                activeforeground=self.fg_main,
                font=("Segoe UI", 8),
                anchor="w",
                cursor="hand2",
            )
            cb.grid(row=r, column=c, sticky="w", padx=(0, 16), pady=1)

        # Extra Args & Record file
        extra_frame = tk.Frame(opts_card, bg=self.bg_card)
        extra_frame.pack(fill="x", pady=(6, 0))

        tk.Label(extra_frame, text="Flag Tambahan:", bg=self.bg_card, fg=self.fg_muted, font=("Segoe UI", 8)).pack(
            side="left"
        )
        ent_extra = tk.Entry(
            extra_frame,
            textvariable=self.var_extra_args,
            bg=self.bg_input,
            fg=self.fg_main,
            insertbackground=self.fg_main,
            relief="flat",
            font=("Consolas", 8),
        )
        ent_extra.pack(side="left", fill="x", expand=True, padx=(6, 0), ipady=3)
        ent_extra.bind("<KeyRelease>", lambda e: self.update_command_preview())

        # 6. Command Preview & Launch Footer
        footer_card = tk.Frame(
            container, bg=self.bg_card, highlightbackground=self.border, highlightthickness=1, padx=10, pady=8
        )
        footer_card.pack(fill="x")

        tk.Label(
            footer_card,
            text="COMMAND YANG AKAN DIJALANKAN:",
            bg=self.bg_card,
            fg=self.fg_muted,
            font=("Segoe UI", 7, "bold"),
        ).pack(anchor="w")

        self.ent_preview = tk.Entry(
            footer_card,
            bg="#090d16",
            fg="#38bdf8",
            readonlybackground="#090d16",
            relief="flat",
            font=("Consolas", 9),
            state="readonly",
        )
        self.ent_preview.pack(fill="x", pady=(3, 8), ipady=4)

        action_row = tk.Frame(footer_card, bg=self.bg_card)
        action_row.pack(fill="x")

        cb_autoclose = tk.Checkbutton(
            action_row,
            text="Tutup launcher otomatis setelah Start (Hemat 100% RAM)",
            variable=self.var_auto_close,
            bg=self.bg_card,
            fg=self.fg_muted,
            selectcolor=self.bg_input,
            activebackground=self.bg_card,
            activeforeground=self.fg_main,
            font=("Segoe UI", 8),
            cursor="hand2",
        )
        cb_autoclose.pack(side="left")

        self.btn_launch = tk.Button(
            action_row,
            text="▶ Start Mirroring",
            command=self.launch_scrcpy,
            bg="#22c55e",
            fg="#052e16",
            activebackground="#16a34a",
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=5,
            cursor="hand2",
        )
        self.btn_launch.pack(side="right")

        self.highlight_preset_button(self.var_preset.get())

    def _add_dropdown(self, parent, label_text, var, values, col, width=14):
        frame = tk.Frame(parent, bg=self.bg_card)
        frame.grid(row=0, column=col, sticky="w", padx=(0, 12))
        tk.Label(frame, text=label_text, bg=self.bg_card, fg=self.fg_muted, font=("Segoe UI", 8)).pack(anchor="w")
        cmb = ttk.Combobox(frame, textvariable=var, values=values, state="readonly", width=width)
        cmb.pack(pady=(2, 0))
        cmb.bind("<<ComboboxSelected>>", lambda e: self.update_command_preview())

    # -------------------------------------------------------------------------
    # Binary Detection (scrcpy & adb)
    # -------------------------------------------------------------------------
    def find_binary(self, name: str):
        exe_name = f"{name}.exe" if IS_WINDOWS else name

        # 1. Custom user-configured folder
        if self.custom_bin_dir and os.path.isdir(self.custom_bin_dir):
            candidate = os.path.join(self.custom_bin_dir, exe_name)
            if os.path.isfile(candidate):
                return candidate

        # 2. Same folder as this launcher script / executable
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        candidate = os.path.join(script_dir, exe_name)
        if os.path.isfile(candidate):
            return candidate

        # 3. Parent directory (if placed inside a subfolder of a portable release)
        parent_dir = os.path.dirname(script_dir)
        candidate = os.path.join(parent_dir, exe_name)
        if os.path.isfile(candidate):
            return candidate

        # 4. System PATH
        found = shutil.which(name)
        if found:
            return found

        return None

    def check_binaries(self):
        self.scrcpy_path = self.find_binary("scrcpy")
        self.adb_path = self.find_binary("adb")

        # Update scrcpy label
        if self.scrcpy_path:
            ver = self.get_scrcpy_version(self.scrcpy_path)
            ver_str = f" ({ver})" if ver else ""
            self.lbl_scrcpy_status.configure(text=f"● scrcpy terdeteksi{ver_str}", fg=self.success)
        else:
            self.lbl_scrcpy_status.configure(text="● scrcpy belum terinstall", fg=self.danger)

        # Update adb label
        if self.adb_path:
            self.lbl_adb_status.configure(text="● adb terdeteksi", fg=self.success)
        else:
            self.lbl_adb_status.configure(text="● adb belum terinstall", fg=self.danger)

        # Show or hide install helper bar
        if not self.scrcpy_path or not self.adb_path:
            self.missing_bar.pack(fill="x", pady=(4, 0))
            self.btn_launch.configure(state="disabled", bg="#475569", fg="#94a3b8")
        else:
            self.missing_bar.pack_forget()
            self.btn_launch.configure(state="normal", bg="#22c55e", fg="#052e16")

    def get_scrcpy_version(self, path: str) -> str:
        try:
            kwargs = {"capture_output": True, "text": True, "timeout": 3}
            if IS_WINDOWS:
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            res = subprocess.run([path, "--version"], **kwargs)
            first_line = (res.stdout or "").splitlines()
            if first_line:
                # e.g. "scrcpy 5.0.1 <https://...>"
                parts = first_line[0].split()
                if len(parts) >= 2:
                    return f"v{parts[1]}"
        except Exception:
            pass
        return ""

    def on_recheck(self):
        self.check_binaries()
        self.refresh_devices()
        self.update_command_preview()

    def browse_bin_folder(self):
        folder = filedialog.askdirectory(title="Pilih Folder tempat scrcpy / adb berada")
        if folder:
            self.custom_bin_dir = folder
            self.save_config()
            self.on_recheck()

    def get_os_install_button_label(self) -> str:
        if IS_WINDOWS:
            return "📦 Install Resmi via Winget (Terminal)"
        elif IS_MAC:
            return "🍺 Install Resmi via Homebrew (Terminal)"
        else:
            return "🐧 Lihat / Jalankan Perintah Install Linux"

    def run_official_package_install(self):
        if IS_WINDOWS:
            cmd = "winget install --exact --id Genymobile.scrcpy"
            confirm = messagebox.askyesno(
                "Install Resmi via Winget",
                f"Launcher akan membuka jendela CMD dan menjalankan perintah resmi Microsoft Winget:\n\n"
                f"    {cmd}\n\n"
                f"Paket ini sudah termasuk scrcpy dan adb resmi dari Genymobile.\n"
                f"Lanjutkan?",
            )
            if confirm:
                subprocess.Popen(["cmd.exe", "/c", f"start cmd.exe /k \"{cmd} && echo. && echo Selesai! Silakan klik Re-check di Launcher.\""])
        elif IS_MAC:
            cmd = "brew install scrcpy android-platform-tools"
            confirm = messagebox.askyesno(
                "Install via Homebrew",
                f"Jalankan perintah resmi Homebrew berikut di Terminal?\n\n    {cmd}",
            )
            if confirm:
                apple_script = f'tell application "Terminal" to do script "{cmd}"'
                subprocess.Popen(["osascript", "-e", apple_script])
        else:
            messagebox.showinfo(
                "Install scrcpy & adb di Linux",
                "Silakan jalankan perintah sesuai distro Linux kamu di Terminal:\n\n"
                "• Debian / Ubuntu:\n  sudo apt install scrcpy adb\n\n"
                "• Arch Linux:\n  sudo pacman -S scrcpy android-tools\n\n"
                "• Fedora:\n  sudo dnf install scrcpy android-tools\n\n"
                "Atau download rilis terbaru dari GitHub Genymobile/scrcpy.",
            )

    # -------------------------------------------------------------------------
    # ADB Device Discovery & WiFi Helper
    # -------------------------------------------------------------------------
    def refresh_devices(self):
        self.devices = []
        if not self.adb_path:
            self.cmb_device["values"] = ["(adb belum terdeteksi — tidak bisa membaca daftar device)"]
            self.var_device.set(self.cmb_device["values"][0])
            return

        try:
            kwargs = {"capture_output": True, "text": True, "timeout": 4}
            if IS_WINDOWS:
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            res = subprocess.run([self.adb_path, "devices", "-l"], **kwargs)
            lines = (res.stdout or "").strip().splitlines()
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    serial = parts[0]
                    state = parts[1]
                    model = "Android"
                    for p in parts[2:]:
                        if p.startswith("model:"):
                            model = p.split(":", 1)[1]
                    conn_type = "WiFi" if ":" in serial else "USB"
                    self.devices.append({"serial": serial, "model": model, "state": state, "type": conn_type})
        except Exception:
            pass

        if not self.devices:
            self.cmb_device["values"] = ["Otomatis (Semua/Satu-satunya Device yang Terhubung)"]
            self.var_device.set(self.cmb_device["values"][0])
        else:
            items = ["Otomatis (Default scrcpy)"]
            for d in self.devices:
                status_tag = "Ready" if d["state"] == "device" else d["state"].upper()
                items.append(f"{d['serial']}  —  {d['model']} ({d['type']} • {status_tag})")
            self.cmb_device["values"] = items
            # Auto-select first real device if available
            self.var_device.set(items[1] if len(items) > 1 else items[0])

    def open_wifi_dialog(self):
        if not self.adb_path:
            messagebox.showwarning("adb Belum Terinstall", "Fitur koneksi WiFi membutuhkan adb yang terdeteksi.")
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Koneksi Wireless (ADB TCP/IP)")
        dlg.configure(bg=self.bg_card, padx=14, pady=12)
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(
            dlg,
            text="Sambungkan Android via WiFi (Tanpa Kabel)",
            bg=self.bg_card,
            fg=self.accent,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            dlg,
            text="Opsi 1: Colok USB dulu, lalu klik tombol di bawah agar scrcpy otomatis pindah ke WiFi (--tcpip):",
            bg=self.bg_card,
            fg=self.fg_main,
            font=("Segoe UI", 8),
        ).pack(anchor="w")

        def auto_tcpip():
            dlg.destroy()
            self.var_extra_args.set((self.var_extra_args.get() + " --tcpip").strip())
            self.update_command_preview()

        tk.Button(
            dlg,
            text="⚡ Gunakan Flag Otomatis --tcpip",
            command=auto_tcpip,
            bg="#0284c7",
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=4,
            cursor="hand2",
        ).pack(anchor="w", pady=(4, 10))

        tk.Label(
            dlg,
            text="Opsi 2: Masukkan IP Address HP secara manual (contoh: 192.168.1.15:5555):",
            bg=self.bg_card,
            fg=self.fg_main,
            font=("Segoe UI", 8),
        ).pack(anchor="w")

        ip_row = tk.Frame(dlg, bg=self.bg_card)
        ip_row.pack(fill="x", pady=(4, 0))

        ent_ip = tk.Entry(ip_row, bg=self.bg_input, fg=self.fg_main, insertbackground=self.fg_main, relief="flat", width=28)
        ent_ip.insert(0, "192.168.1.")
        ent_ip.pack(side="left", ipady=3, padx=(0, 6))

        def manual_connect():
            ip = ent_ip.get().strip()
            if not ip:
                return
            if ":" not in ip:
                ip += ":5555"
            try:
                kwargs = {"capture_output": True, "text": True, "timeout": 6}
                if IS_WINDOWS:
                    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                res = subprocess.run([self.adb_path, "connect", ip], **kwargs)
                output = (res.stdout or "") + (res.stderr or "")
                messagebox.showinfo("ADB Connect", output.strip() or f"Mencoba terhubung ke {ip}")
                dlg.destroy()
                self.refresh_devices()
                self.update_command_preview()
            except Exception as e:
                messagebox.showerror("Gagal Connect", str(e))

        tk.Button(
            ip_row,
            text="Connect ADB",
            command=manual_connect,
            bg=self.success,
            fg="#052e16",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=3,
            cursor="hand2",
        ).pack(side="left")

    # -------------------------------------------------------------------------
    # Presets & Command Builder
    # -------------------------------------------------------------------------
    def apply_preset(self, preset_key: str):
        self.var_preset.set(preset_key)
        self.highlight_preset_button(preset_key)

        # Reset defaults before applying preset specifics
        self.var_source.set("display")
        self.var_max_size.set("1920 (1080p)")
        self.var_fps.set("60")
        self.var_codec.set("h265")
        self.var_screen_off.set(False)
        self.var_stay_awake.set(True)
        self.var_no_audio.set(False)
        self.var_uhid_kb.set(False)
        self.var_uhid_gamepad.set(False)
        self.var_always_on_top.set(False)
        self.var_fullscreen.set(False)

        if preset_key == "standard":
            pass
        elif preset_key == "gaming":
            self.var_fps.set("120")
            self.var_uhid_kb.set(True)
            self.var_uhid_gamepad.set(True)
        elif preset_key == "privacy":
            self.var_screen_off.set(True)
            self.var_stay_awake.set(True)
        elif preset_key == "dex":
            self.var_source.set("new-display")
            self.var_uhid_kb.set(True)
        elif preset_key == "camera":
            self.var_source.set("camera")
        elif preset_key == "otg":
            self.var_source.set("otg")

        self.update_command_preview()

    def highlight_preset_button(self, active_key: str):
        for key, btn in self.preset_buttons.items():
            if key == active_key:
                btn.configure(bg=self.accent, fg="#0f172a", font=("Segoe UI", 8, "bold"))
            else:
                btn.configure(bg=self.bg_input, fg=self.fg_main, font=("Segoe UI", 8))

    def build_command_args(self) -> list:
        exe = self.scrcpy_path or "scrcpy"
        cmd = [exe]

        # Selected device serial
        dev_str = self.var_device.get()
        if "  —  " in dev_str:
            serial = dev_str.split("  —  ", 1)[0].strip()
            if serial:
                cmd.extend(["-s", serial])

        source = self.var_source.get()
        if source == "otg":
            cmd.append("--otg")
            extra = self.var_extra_args.get().strip()
            if extra:
                cmd.extend(extra.split())
            return cmd

        if source == "new-display":
            cmd.append("--new-display=1920x1080")
        elif source == "camera":
            cmd.append("--video-source=camera")

        # Codec
        codec = self.var_codec.get()
        if codec and codec != "h264":
            cmd.append(f"--video-codec={codec}")

        # Resolution / Camera size
        size_label = self.var_max_size.get()
        size_val = size_label.split()[0] if size_label else ""
        if size_val.isdigit():
            if source == "camera":
                cmd.append(f"--camera-size={size_val}x1080")
            else:
                cmd.append(f"-m{size_val}")

        # FPS
        fps = self.var_fps.get()
        if fps and fps.isdigit():
            cmd.append(f"--max-fps={fps}")

        # Checkboxes
        if self.var_screen_off.get() and source == "display":
            cmd.append("-S")
        if self.var_stay_awake.get() and source == "display":
            cmd.append("--stay-awake")
        if self.var_no_audio.get():
            cmd.append("--no-audio")
        if self.var_uhid_kb.get():
            cmd.append("-K")
        if self.var_uhid_gamepad.get():
            cmd.append("-G")
        if self.var_always_on_top.get():
            cmd.append("--always-on-top")
        if self.var_fullscreen.get():
            cmd.append("-f")
        if self.var_record.get():
            rec_file = self.var_record_path.get().strip() or "scrcpy_capture.mp4"
            cmd.append(f"--record={rec_file}")

        extra = self.var_extra_args.get().strip()
        if extra:
            cmd.extend(extra.split())

        return cmd

    def update_command_preview(self):
        args = self.build_command_args()
        # Use short binary name in preview for readability
        display_args = ["scrcpy"] + args[1:]
        preview_str = " ".join(display_args)
        self.ent_preview.configure(state="normal")
        self.ent_preview.delete(0, "end")
        self.ent_preview.insert(0, preview_str)
        self.ent_preview.configure(state="readonly")

    # -------------------------------------------------------------------------
    # Config Persistence & Process Launch
    # -------------------------------------------------------------------------
    def load_config(self) -> dict:
        if os.path.isfile(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        data = {
            "custom_bin_dir": self.custom_bin_dir,
            "preset": self.var_preset.get(),
            "source": self.var_source.get(),
            "max_size": self.var_max_size.get(),
            "fps": self.var_fps.get(),
            "codec": self.var_codec.get(),
            "screen_off": self.var_screen_off.get(),
            "stay_awake": self.var_stay_awake.get(),
            "no_audio": self.var_no_audio.get(),
            "uhid_kb": self.var_uhid_kb.get(),
            "uhid_gamepad": self.var_uhid_gamepad.get(),
            "always_on_top": self.var_always_on_top.get(),
            "fullscreen": self.var_fullscreen.get(),
            "record": self.var_record.get(),
            "record_path": self.var_record_path.get(),
            "extra_args": self.var_extra_args.get(),
            "auto_close": self.var_auto_close.get(),
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def launch_scrcpy(self):
        if not self.scrcpy_path:
            messagebox.showerror("scrcpy Belum Terinstall", "scrcpy belum terdeteksi di sistem kamu.")
            return

        self.save_config()
        args = self.build_command_args()

        # Ensure the directory containing adb/scrcpy is in PATH for the child process
        env = os.environ.copy()
        extra_paths = []
        if self.scrcpy_path:
            extra_paths.append(os.path.dirname(self.scrcpy_path))
        if self.adb_path:
            adb_dir = os.path.dirname(self.adb_path)
            if adb_dir not in extra_paths:
                extra_paths.append(adb_dir)
        if extra_paths:
            env["PATH"] = os.pathsep.join(extra_paths) + os.pathsep + env.get("PATH", "")

        try:
            kwargs = {"env": env, "stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
            if IS_WINDOWS:
                # Detached background process so closing Python launcher uses 0 MB RAM
                kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                kwargs["start_new_session"] = True

            subprocess.Popen(args, **kwargs)

            if self.var_auto_close.get():
                self.root.destroy()
                sys.exit(0)
        except Exception as e:
            messagebox.showerror("Gagal Menjalankan scrcpy", str(e))


def main():
    root = tk.Tk()
    app = ScrcpyLauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
