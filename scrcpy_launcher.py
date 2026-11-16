#!/usr/bin/env python3
"""
scrcpy-cpl
A lightweight, zero-dependency, cross-platform GUI control panel for scrcpy (v5.0+).
Works natively on Windows, Linux, and macOS using Python's built-in tkinter.
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

APP_NAME = "scrcpy-cpl"
APP_VERSION = "1.1.0"
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".scrcpy_cpl.json")
OFFICIAL_RELEASES_URL = "https://github.com/Genymobile/scrcpy/releases"

IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

WINDOW_WIDTH = 540

PRESET_DEFS = {
    "standard": {
        "source": "display",
        "max_size": "1920",
        "fps": "60",
        "codec": "h265",
        "screen_off": False,
        "stay_awake": True,
        "no_audio": False,
        "uhid_kb": False,
        "uhid_gamepad": False,
        "always_on_top": False,
        "fullscreen": False,
        "record": False,
    },
    "gaming": {
        "source": "display",
        "max_size": "1920",
        "fps": "120",
        "codec": "h265",
        "screen_off": False,
        "stay_awake": True,
        "no_audio": False,
        "uhid_kb": True,
        "uhid_gamepad": True,
        "always_on_top": False,
        "fullscreen": False,
        "record": False,
    },
    "privacy": {
        "source": "display",
        "max_size": "1920",
        "fps": "60",
        "codec": "h265",
        "screen_off": True,
        "stay_awake": True,
        "no_audio": False,
        "uhid_kb": False,
        "uhid_gamepad": False,
        "always_on_top": False,
        "fullscreen": False,
        "record": False,
    },
    "dex": {
        "source": "new-display",
        "max_size": "1920",
        "fps": "60",
        "codec": "h265",
        "screen_off": False,
        "stay_awake": True,
        "no_audio": False,
        "uhid_kb": True,
        "uhid_gamepad": False,
        "always_on_top": False,
        "fullscreen": False,
        "record": False,
    },
    "camera": {
        "source": "camera",
        "max_size": "1920",
        "fps": "60",
        "codec": "h265",
        "screen_off": False,
        "stay_awake": False,
        "no_audio": False,
        "uhid_kb": False,
        "uhid_gamepad": False,
        "always_on_top": False,
        "fullscreen": False,
        "record": False,
    },
    "otg": {
        "source": "otg",
        "max_size": "0",
        "fps": "60",
        "codec": "h265",
        "screen_off": False,
        "stay_awake": False,
        "no_audio": False,
        "uhid_kb": False,
        "uhid_gamepad": False,
        "always_on_top": False,
        "fullscreen": False,
        "record": False,
    },
}

I18N = {
    "en": {
        "scrcpy_ok": "scrcpy detected",
        "scrcpy_missing": "scrcpy not installed",
        "adb_ok": "adb detected",
        "adb_missing": "adb not installed",
        "folder_btn": "Folder...",
        "recheck_btn": "Re-check",
        "missing_desc": "No silent downloads. Install via official package manager or select your portable folder:",
        "install_winget": "Install via Winget (Terminal)",
        "install_brew": "Install via Homebrew (Terminal)",
        "install_linux": "Linux Install Commands",
        "github_releases": "GitHub Releases ↗",
        "select_folder_title": "Select folder containing scrcpy / adb",
        "target_device": "Target Android Device",
        "wireless_btn": "Wireless TCP/IP",
        "refresh_btn": "Refresh",
        "no_adb_device_list": "(adb not detected — unable to read device list)",
        "auto_device": "Automatic (Any connected device)",
        "operating_mode": "Operating Mode",
        "click_profile_hint": "Click a profile or customize",
        "p_standard": "Standard",
        "p_gaming": "Gaming 120",
        "p_privacy": "Screen Off",
        "p_dex": "Virtual Desk",
        "p_camera": "Camera",
        "p_otg": "OTG Input",
        "p_custom": "Custom",
        "adv_title": "Advanced Video & Control Settings",
        "expand": "[+] Expand",
        "collapse": "[-] Collapse",
        "lbl_source": "Source",
        "lbl_res": "Max Size",
        "lbl_fps": "Max FPS",
        "lbl_codec": "Codec",
        "chk_screen_off": "Turn physical screen off (-S)",
        "chk_stay_awake": "Stay awake (--stay-awake)",
        "chk_no_audio": "Disable audio (--no-audio)",
        "chk_uhid_kb": "Physical UHID Keyboard (-K)",
        "chk_uhid_gp": "Physical UHID Gamepad (-G)",
        "chk_top": "Always on top (--always-on-top)",
        "chk_full": "Fullscreen (-f)",
        "chk_rec": "Record to MP4 (--record)",
        "lbl_extra": "Extra Flags:",
        "auto_close": "Close panel after launch (0 MB RAM)",
        "start_btn": "Start Mirroring",
        "wifi_title": "Wireless Connection (ADB TCP/IP)",
        "wifi_header": "Connect Android over Wi-Fi",
        "wifi_opt1": "Option 1: Connect via USB first, then append automatic --tcpip flag:",
        "wifi_auto_btn": "Use Automatic --tcpip Flag",
        "wifi_opt2": "Option 2: Enter device IP address manually (e.g. 192.168.1.15:5555):",
        "wifi_conn_btn": "Connect ADB",
        "winget_confirm_title": "Official Install via Winget",
        "winget_confirm_msg": "Open CMD and run the official Microsoft Winget command?\n\n    {cmd}\n\nThis installs official scrcpy and adb from Genymobile.",
    },
    "id": {
        "scrcpy_ok": "scrcpy terdeteksi",
        "scrcpy_missing": "scrcpy belum terinstall",
        "adb_ok": "adb terdeteksi",
        "adb_missing": "adb belum terinstall",
        "folder_btn": "Pilih Folder...",
        "recheck_btn": "Cek Ulang",
        "missing_desc": "Tidak mengunduh diam-diam. Install resmi via package manager atau pilih folder portable:",
        "install_winget": "Install via Winget (Terminal)",
        "install_brew": "Install via Homebrew (Terminal)",
        "install_linux": "Perintah Install Linux",
        "github_releases": "GitHub Resmi ↗",
        "select_folder_title": "Pilih folder tempat scrcpy / adb berada",
        "target_device": "Perangkat Android",
        "wireless_btn": "Koneksi WiFi",
        "refresh_btn": "Muat Ulang",
        "no_adb_device_list": "(adb belum terdeteksi — tidak bisa membaca daftar device)",
        "auto_device": "Otomatis (Device yang terhubung)",
        "operating_mode": "Mode Operasi",
        "click_profile_hint": "Pilih profil atau kustomisasi",
        "p_standard": "Standar",
        "p_gaming": "Gaming 120",
        "p_privacy": "Layar Mati",
        "p_dex": "Virtual Desk",
        "p_camera": "Kamera",
        "p_otg": "Mode OTG",
        "p_custom": "Kustom",
        "adv_title": "Pengaturan Lanjutan Video & Kontrol",
        "expand": "[+] Buka",
        "collapse": "[-] Tutup",
        "lbl_source": "Sumber",
        "lbl_res": "Resolusi",
        "lbl_fps": "Maks FPS",
        "lbl_codec": "Codec",
        "chk_screen_off": "Matikan layar fisik HP (-S)",
        "chk_stay_awake": "Cegah HP terkunci (--stay-awake)",
        "chk_no_audio": "Matikan suara (--no-audio)",
        "chk_uhid_kb": "Keyboard Fisik UHID (-K)",
        "chk_uhid_gp": "Gamepad Fisik UHID (-G)",
        "chk_top": "Selalu di atas (--always-on-top)",
        "chk_full": "Layar penuh (-f)",
        "chk_rec": "Rekam ke MP4 (--record)",
        "lbl_extra": "Flag Ekstra:",
        "auto_close": "Tutup panel setelah jalan (0 MB RAM)",
        "start_btn": "Mulai Mirroring",
        "wifi_title": "Koneksi Wireless (ADB TCP/IP)",
        "wifi_header": "Sambungkan Android via Wi-Fi",
        "wifi_opt1": "Opsi 1: Colok USB dulu, lalu gunakan flag otomatis --tcpip:",
        "wifi_auto_btn": "Gunakan Flag Otomatis --tcpip",
        "wifi_opt2": "Opsi 2: Masukkan IP HP secara manual (contoh: 192.168.1.15:5555):",
        "wifi_conn_btn": "Sambungkan ADB",
        "winget_confirm_title": "Install Resmi via Winget",
        "winget_confirm_msg": "Buka CMD dan jalankan perintah resmi Microsoft Winget?\n\n    {cmd}\n\nPaket ini berisi scrcpy dan adb resmi dari Genymobile.",
    },
}

THEMES = {
    "light": {
        "bg_main": "#f3f3f3",
        "bg_header": "#ffffff",
        "bg_card": "#ffffff",
        "bg_input": "#fafafa",
        "bg_cmd": "#f5f5f5",
        "fg_main": "#1c1c1c",
        "fg_muted": "#616161",
        "border": "#e0e0e0",
        "input_border": "#d1d1d1",
        "accent": "#1f7a54",
        "accent_fg": "#ffffff",
        "preset_idle_bg": "#fbfbfb",
        "preset_idle_fg": "#292524",
        "preset_idle_border": "#d4d4d4",
        "preset_active_bg": "#ecfdf5",
        "preset_active_fg": "#14532d",
        "preset_active_border": "#1f7a54",
        "ok": "#15803d",
        "err": "#b91c1c",
        "missing_bg": "#fff5f5",
        "missing_border": "#fecaca",
    },
    "dark": {
        "bg_main": "#09090b",
        "bg_header": "#121215",
        "bg_card": "#121215",
        "bg_input": "#09090b",
        "bg_cmd": "#09090b",
        "fg_main": "#f4f4f5",
        "fg_muted": "#a1a1aa",
        "border": "#27272a",
        "input_border": "#27272a",
        "accent": "#1f7a54",
        "accent_fg": "#ffffff",
        "preset_idle_bg": "#18181b",
        "preset_idle_fg": "#a1a1aa",
        "preset_idle_border": "#27272a",
        "preset_active_bg": "#f4f4f5",
        "preset_active_fg": "#09090b",
        "preset_active_border": "#f4f4f5",
        "ok": "#4ade80",
        "err": "#f87171",
        "missing_bg": "#1f1215",
        "missing_border": "#7f1d1d",
    },
}


def create_jade_cpl_photoimage(size: int = 32) -> tk.PhotoImage:
    """
    Renders the custom scrcpy-cpl icon (Option 1: Official scrcpy Jade & Charcoal,
    combining the Style 2 Phone Mirror Frame + Style 1 Control Panel Sliders)
    directly into a tk.PhotoImage with zero external asset dependencies.
    """
    img = tk.PhotoImage(width=size, height=size)
    s = size / 24.0

    def fill_rect(x0, y0, x1, y1, color):
        ix0 = max(0, int(round(x0 * s)))
        iy0 = max(0, int(round(y0 * s)))
        ix1 = min(size, int(round(x1 * s)))
        iy1 = min(size, int(round(y1 * s)))
        if ix1 > ix0 and iy1 > iy0:
            img.put(color, to=(ix0, iy0, ix1, iy1))

    # 1. Rounded Jade Base (#1f7a54) with subtle border (#166534)
    fill_rect(1, 1, 23, 23, "#166534")
    fill_rect(2, 2, 22, 22, "#1f7a54")

    # 2. Style 2: Phone Mirror Frame (white outline + dark jade screen)
    fill_rect(3.5, 3.0, 14.5, 20.5, "#ffffff")
    fill_rect(4.8, 4.3, 13.2, 19.2, "#134e35")
    # Speaker notch
    fill_rect(7.2, 5.2, 10.8, 6.1, "#ffffff")

    # 3. Style 1: Control Panel Sliders Badge overlapping right (#18181b with white border)
    fill_rect(9.2, 7.5, 21.2, 19.5, "#ffffff")
    fill_rect(10.2, 8.5, 20.2, 18.5, "#18181b")

    # Slider tracks (#71717a)
    fill_rect(11.6, 10.4, 18.8, 11.4, "#71717a")
    fill_rect(11.6, 13.1, 18.8, 14.1, "#71717a")
    fill_rect(11.6, 15.8, 18.8, 16.8, "#71717a")

    # Slider knobs (Jade green #4ade80 and crisp white #ffffff)
    fill_rect(13.0, 9.7, 15.2, 12.1, "#4ade80")
    fill_rect(16.0, 12.4, 18.2, 14.8, "#ffffff")
    fill_rect(13.8, 15.1, 16.0, 17.5, "#4ade80")

    return img


class ScrcpyCplApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_NAME)
        self.root.resizable(False, False)

        self.config = self.load_config()
        self.lang = self.config.get("lang", "en")
        if self.lang not in I18N:
            self.lang = "en"

        self.theme_name = self.config.get("theme", "light")
        if self.theme_name not in THEMES:
            self.theme_name = "light"

        self.custom_bin_dir = self.config.get("custom_bin_dir", "")
        self.scrcpy_path = None
        self.adb_path = None
        self.scrcpy_version = ""
        self.devices = []

        # Saved custom preset state
        default_custom = dict(PRESET_DEFS["standard"])
        self.custom_profile = self.config.get("custom_profile", default_custom)

        # Active preset: None only on very first launch if no config exists yet;
        # once user selects anything, it is persisted and auto-selected on future opens.
        self.active_preset = self.config.get("active_preset", None)
        self.adv_expanded = False
        self._suppress_trace = False

        # Tkinter Variables
        init_state = (
            self.custom_profile
            if self.active_preset == "custom"
            else PRESET_DEFS.get(self.active_preset or "standard", PRESET_DEFS["standard"])
        )

        self.var_device = tk.StringVar()
        self.var_source = tk.StringVar(value=init_state.get("source", "display"))
        self.var_max_size = tk.StringVar(value=init_state.get("max_size", "1920"))
        self.var_fps = tk.StringVar(value=init_state.get("fps", "60"))
        self.var_codec = tk.StringVar(value=init_state.get("codec", "h265"))

        self.var_screen_off = tk.BooleanVar(value=init_state.get("screen_off", False))
        self.var_stay_awake = tk.BooleanVar(value=init_state.get("stay_awake", True))
        self.var_no_audio = tk.BooleanVar(value=init_state.get("no_audio", False))
        self.var_uhid_kb = tk.BooleanVar(value=init_state.get("uhid_kb", False))
        self.var_uhid_gamepad = tk.BooleanVar(value=init_state.get("uhid_gamepad", False))
        self.var_always_on_top = tk.BooleanVar(value=init_state.get("always_on_top", False))
        self.var_fullscreen = tk.BooleanVar(value=init_state.get("fullscreen", False))
        self.var_record = tk.BooleanVar(value=init_state.get("record", False))
        self.var_record_path = tk.StringVar(value=self.config.get("record_path", "scrcpy_capture.mp4"))
        self.var_extra_args = tk.StringVar(value=self.config.get("extra_args", ""))
        self.var_auto_close = tk.BooleanVar(value=self.config.get("auto_close", True))

        # Set window & header icons
        try:
            self.icon_img_32 = create_jade_cpl_photoimage(32)
            self.icon_img_28 = create_jade_cpl_photoimage(28)
            self.root.iconphoto(True, self.icon_img_32)
        except Exception:
            self.icon_img_28 = None

        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.build_ui()
        self.apply_theme()
        self.apply_language()
        self.check_binaries()
        self.refresh_devices()
        self.update_mode_summary_and_preview()
        self.lock_window_width()

    def t(self, key: str) -> str:
        return I18N.get(self.lang, I18N["en"]).get(key, key)

    def lock_window_width(self):
        self.root.update_idletasks()
        req_h = self.root.winfo_reqheight()
        self.root.geometry(f"{WINDOW_WIDTH}x{req_h}")

    # -------------------------------------------------------------------------
    # UI Construction
    # -------------------------------------------------------------------------
    def build_ui(self):
        # Top Header Bar
        self.header_frame = tk.Frame(self.root, padx=14, pady=10)
        self.header_frame.pack(fill="x")

        header_left = tk.Frame(self.header_frame)
        header_left.pack(side="left")

        if self.icon_img_28:
            self.lbl_icon = tk.Label(header_left, image=self.icon_img_28, bd=0)
            self.lbl_icon.pack(side="left", padx=(0, 9))

        self.lbl_title = tk.Label(header_left, text=APP_NAME, font=("Segoe UI", 12, "bold"))
        self.lbl_title.pack(side="left")

        # Top Right Controls: Theme Toggle + Language Selector (EN | ID)
        self.header_right = tk.Frame(self.header_frame)
        self.header_right.pack(side="right")

        self.btn_theme = tk.Button(
            self.header_right,
            text="☾ Dark",
            command=self.toggle_theme,
            relief="solid",
            bd=1,
            font=("Segoe UI", 8),
            padx=8,
            pady=2,
            cursor="hand2",
        )
        self.btn_theme.pack(side="left", padx=(0, 8))

        self.lang_frame = tk.Frame(self.header_right, bd=1, relief="solid")
        self.lang_frame.pack(side="left")

        self.btn_lang_en = tk.Button(
            self.lang_frame,
            text="EN",
            command=lambda: self.set_language("en"),
            relief="flat",
            bd=0,
            font=("Consolas", 8, "bold"),
            width=3,
             pady=2,
            cursor="hand2",
        )
        self.btn_lang_en.pack(side="left")

        self.btn_lang_id = tk.Button(
            self.lang_frame,
            text="ID",
            command=lambda: self.set_language("id"),
            relief="flat",
            bd=0,
            font=("Consolas", 8, "bold"),
            width=3,
            pady=2,
            cursor="hand2",
        )
        self.btn_lang_id.pack(side="left")

        self.header_sep = tk.Frame(self.root, height=1)
        self.header_sep.pack(fill="x")

        # Main Body Container
        self.body = tk.Frame(self.root, padx=14, pady=12)
        self.body.pack(fill="both", expand=True)

        # 1. Dependency Card (Collapsed 1-line strip when installed, expanded when missing)
        self.dep_card = tk.Frame(self.body, highlightthickness=1, padx=10, pady=6)
        self.dep_card.pack(fill="x", pady=(0, 8))

        self.dep_top_row = tk.Frame(self.dep_card)
        self.dep_top_row.pack(fill="x")

        self.lbl_scrcpy_status = tk.Label(self.dep_top_row, text="", font=("Consolas", 9))
        self.lbl_scrcpy_status.pack(side="left")

        self.lbl_dep_pipe = tk.Label(self.dep_top_row, text="  |  ", font=("Consolas", 9))
        self.lbl_dep_pipe.pack(side="left")

        self.lbl_adb_status = tk.Label(self.dep_top_row, text="", font=("Consolas", 9))
        self.lbl_adb_status.pack(side="left")

        self.btn_recheck = tk.Button(
            self.dep_top_row,
            text="Re-check",
            command=self.on_recheck,
            relief="flat",
            bd=0,
            font=("Segoe UI", 8),
            padx=6,
            pady=1,
            cursor="hand2",
        )
        self.btn_recheck.pack(side="right")

        self.btn_folder = tk.Button(
            self.dep_top_row,
            text="Folder...",
            command=self.browse_bin_folder,
            relief="flat",
            bd=0,
            font=("Segoe UI", 8, "underline"),
            padx=6,
            pady=1,
            cursor="hand2",
        )
        self.btn_folder.pack(side="right", padx=(0, 4))

        # Missing Binaries Action Panel (Auto-collapsed when scrcpy + adb are installed)
        self.missing_panel = tk.Frame(self.dep_card)
        self.lbl_missing_desc = tk.Label(
            self.missing_panel, text="", font=("Segoe UI", 8), anchor="w", justify="left"
        )
        self.lbl_missing_desc.pack(fill="x", pady=(6, 4))

        self.missing_btn_row = tk.Frame(self.missing_panel)
        self.missing_btn_row.pack(fill="x")

        self.btn_pkg_install = tk.Button(
            self.missing_btn_row,
            text="",
            command=self.run_official_package_install,
            relief="flat",
            bd=0,
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=4,
            cursor="hand2",
        )
        self.btn_pkg_install.pack(side="left", padx=(0, 6))

        self.btn_github = tk.Button(
            self.missing_btn_row,
            text="",
            command=lambda: webbrowser.open(OFFICIAL_RELEASES_URL),
            relief="solid",
            bd=1,
            font=("Segoe UI", 8),
            padx=10,
            pady=3,
            cursor="hand2",
        )
        self.btn_github.pack(side="left")

        # 2. Target Android Device Card
        self.dev_card = tk.Frame(self.body, highlightthickness=1, padx=10, pady=8)
        self.dev_card.pack(fill="x", pady=(0, 8))

        self.dev_hdr = tk.Frame(self.dev_card)
        self.dev_hdr.pack(fill="x", pady=(0, 4))

        self.lbl_dev_title = tk.Label(self.dev_hdr, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_dev_title.pack(side="left")

        self.btn_refresh_dev = tk.Button(
            self.dev_hdr,
            text="",
            command=self.refresh_devices,
            relief="flat",
            bd=0,
            font=("Segoe UI", 8),
            padx=4,
            cursor="hand2",
        )
        self.btn_refresh_dev.pack(side="right")

        self.btn_wifi = tk.Button(
            self.dev_hdr,
            text="",
            command=self.open_wifi_dialog,
            relief="flat",
            bd=0,
            font=("Segoe UI", 8, "underline"),
            padx=4,
            cursor="hand2",
        )
        self.btn_wifi.pack(side="right", padx=(0, 4))

        self.cmb_device = ttk.Combobox(
            self.dev_card, textvariable=self.var_device, state="readonly", font=("Consolas", 9)
        )
        self.cmb_device.pack(fill="x", pady=(2, 0))
        self.cmb_device.bind("<<ComboboxSelected>>", lambda e: self.update_mode_summary_and_preview())

        # 3. Operating Mode Card (Fixed uniform grid so buttons NEVER shift width)
        self.mode_card = tk.Frame(self.body, highlightthickness=1, padx=10, pady=8)
        self.mode_card.pack(fill="x", pady=(0, 8))

        self.mode_hdr = tk.Frame(self.mode_card)
        self.mode_hdr.pack(fill="x", pady=(0, 6))

        self.lbl_mode_title = tk.Label(self.mode_hdr, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_mode_title.pack(side="left")

        self.lbl_mode_detail = tk.Label(self.mode_hdr, text="", font=("Consolas", 8))
        self.lbl_mode_detail.pack(side="right")

        # Row 1: 4 uniform columns
        self.preset_row1 = tk.Frame(self.mode_card)
        self.preset_row1.pack(fill="x", pady=(0, 5))
        for col_idx in range(4):
            self.preset_row1.columnconfigure(col_idx, weight=1, uniform="preset_r1")

        # Row 2: 3 uniform columns (Camera, OTG, Custom)
        self.preset_row2 = tk.Frame(self.mode_card)
        self.preset_row2.pack(fill="x")
        for col_idx in range(3):
            self.preset_row2.columnconfigure(col_idx, weight=1, uniform="preset_r2")

        self.preset_buttons = {}
        r1_keys = ["standard", "gaming", "privacy", "dex"]
        for idx, key in enumerate(r1_keys):
            cell = tk.Frame(self.preset_row1, highlightthickness=1, height=32)
            cell.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 3, 0 if idx == 3 else 3))
            cell.pack_propagate(False)
            btn = tk.Button(
                cell,
                text="",
                command=lambda k=key: self.select_preset(k),
                relief="flat",
                bd=0,
                font=("Segoe UI", 8),
                cursor="hand2",
            )
            btn.pack(fill="both", expand=True)
            self.preset_buttons[key] = (cell, btn)

        r2_keys = ["camera", "otg", "custom"]
        for idx, key in enumerate(r2_keys):
            cell = tk.Frame(self.preset_row2, highlightthickness=1, height=32)
            cell.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 3, 0 if idx == 2 else 3))
            cell.pack_propagate(False)
            btn = tk.Button(
                cell,
                text="",
                command=lambda k=key: self.select_preset(k),
                relief="flat",
                bd=0,
                font=("Segoe UI", 8),
                cursor="hand2",
            )
            btn.pack(fill="both", expand=True)
            self.preset_buttons[key] = (cell, btn)

        # 4. Collapsible Advanced Video & Control Settings (Collapsed by default)
        self.adv_card = tk.Frame(self.body, highlightthickness=1, padx=10, pady=6)
        self.adv_card.pack(fill="x", pady=(0, 8))

        self.adv_hdr = tk.Frame(self.adv_card, cursor="hand2")
        self.adv_hdr.pack(fill="x")

        self.lbl_adv_title = tk.Label(self.adv_hdr, text="", font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.lbl_adv_title.pack(side="left")

        self.lbl_adv_toggle = tk.Label(self.adv_hdr, text="", font=("Consolas", 8), cursor="hand2")
        self.lbl_adv_toggle.pack(side="right")

        for w in (self.adv_hdr, self.lbl_adv_title, self.lbl_adv_toggle):
            w.bind("<Button-1>", lambda e: self.toggle_advanced())

        self.adv_body = tk.Frame(self.adv_card, pady=6)

        # Dropdowns row inside Advanced
        self.adv_grid = tk.Frame(self.adv_body)
        self.adv_grid.pack(fill="x", pady=(2, 8))
        for i in range(4):
            self.adv_grid.columnconfigure(i, weight=1, uniform="adv_cols")

        self.lbl_src, self.cmb_src = self._create_adv_combo(
            self.adv_grid, 0, self.var_source, ["display", "new-display", "camera", "otg"]
        )
        self.lbl_res, self.cmb_res = self._create_adv_combo(
            self.adv_grid, 1, self.var_max_size, ["0", "2560", "1920", "1280", "1024"]
        )
        self.lbl_fps, self.cmb_fps = self._create_adv_combo(
            self.adv_grid, 2, self.var_fps, ["30", "60", "90", "120"]
        )
        self.lbl_codec, self.cmb_codec = self._create_adv_combo(
            self.adv_grid, 3, self.var_codec, ["h265", "h264", "av1"]
        )

        # Checkboxes inside Advanced
        self.adv_chk_frame = tk.Frame(self.adv_body)
        self.adv_chk_frame.pack(fill="x")
        self.adv_chk_frame.columnconfigure(0, weight=1, uniform="chk_cols")
        self.adv_chk_frame.columnconfigure(1, weight=1, uniform="chk_cols")

        chk_defs = [
            ("chk_screen_off", self.var_screen_off, 0, 0),
            ("chk_stay_awake", self.var_stay_awake, 0, 1),
            ("chk_no_audio", self.var_no_audio, 1, 0),
            ("chk_uhid_kb", self.var_uhid_kb, 1, 1),
            ("chk_uhid_gp", self.var_uhid_gamepad, 2, 0),
            ("chk_top", self.var_always_on_top, 2, 1),
            ("chk_full", self.var_fullscreen, 3, 0),
            ("chk_rec", self.var_record, 3, 1),
        ]
        self.adv_checkboxes = {}
        for i18n_key, var, r, c in chk_defs:
            cb = tk.Checkbutton(
                self.adv_chk_frame,
                text="",
                variable=var,
                command=self.on_manual_setting_changed,
                font=("Segoe UI", 8),
                anchor="w",
                cursor="hand2",
            )
            cb.grid(row=r, column=c, sticky="ew", pady=1)
            self.adv_checkboxes[i18n_key] = cb

        # Extra flags row inside Advanced
        self.extra_row = tk.Frame(self.adv_body)
        self.extra_row.pack(fill="x", pady=(6, 0))

        self.lbl_extra = tk.Label(self.extra_row, text="", font=("Segoe UI", 8))
        self.lbl_extra.pack(side="left")

        self.ent_extra = tk.Entry(
            self.extra_row,
            textvariable=self.var_extra_args,
            relief="solid",
            bd=1,
            font=("Consolas", 8),
        )
        self.ent_extra.pack(side="left", fill="x", expand=True, padx=(6, 0), ipady=2)
        self.ent_extra.bind("<KeyRelease>", lambda e: self.on_manual_setting_changed())

        # 5. Footer Card: Fixed-Width Command Preview + Auto-Exit Checkbox + Start Button
        self.footer_card = tk.Frame(self.body, highlightthickness=1, padx=10, pady=8)
        self.footer_card.pack(fill="x")

        self.ent_preview = tk.Entry(
            self.footer_card,
            relief="solid",
            bd=1,
            font=("Consolas", 9),
            state="readonly",
        )
        self.ent_preview.pack(fill="x", pady=(0, 8), ipady=4)

        self.footer_bottom = tk.Frame(self.footer_card)
        self.footer_bottom.pack(fill="x")

        self.cb_autoclose = tk.Checkbutton(
            self.footer_bottom,
            text="",
            variable=self.var_auto_close,
            command=self.save_config,
            font=("Segoe UI", 8),
            cursor="hand2",
        )
        self.cb_autoclose.pack(side="left")

        self.btn_start = tk.Button(
            self.footer_bottom,
            text="",
            command=self.launch_scrcpy,
            relief="flat",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            padx=16,
            pady=5,
            cursor="hand2",
        )
        self.btn_start.pack(side="right")

    def _create_adv_combo(self, parent, col, var, values):
        cell = tk.Frame(parent)
        cell.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 3, 0 if col == 3 else 3))
        lbl = tk.Label(cell, text="", font=("Segoe UI", 8))
        lbl.pack(anchor="w")
        cmb = ttk.Combobox(cell, textvariable=var, values=values, state="readonly", font=("Consolas", 8))
        cmb.pack(fill="x", pady=(2, 0))
        cmb.bind("<<ComboboxSelected>>", lambda e: self.on_manual_setting_changed())
        return lbl, cmb

    # -------------------------------------------------------------------------
    # Theme & Language Switching
    # -------------------------------------------------------------------------
    def toggle_theme(self):
        self.theme_name = "dark" if self.theme_name == "light" else "light"
        self.apply_theme()
        self.save_config()

    def apply_theme(self):
        th = THEMES[self.theme_name]
        self.root.configure(bg=th["bg_main"])
        self.body.configure(bg=th["bg_main"])

        # Header
        self.header_frame.configure(bg=th["bg_header"])
        for child in self.header_frame.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=th["bg_header"])
        if self.icon_img_28:
            self.lbl_icon.configure(bg=th["bg_header"])
        self.lbl_title.configure(bg=th["bg_header"], fg=th["fg_main"])
        self.header_sep.configure(bg=th["border"])

        self.btn_theme.configure(
            text="☀ Light" if self.theme_name == "dark" else "☾ Dark",
            bg=th["preset_idle_bg"],
            fg=th["fg_main"],
            activebackground=th["border"],
            activeforeground=th["fg_main"],
        )
        self.lang_frame.configure(bg=th["border"])
        self._style_lang_buttons()

        # Cards
        for card in (self.dev_card, self.mode_card, self.adv_card, self.footer_card):
            card.configure(bg=th["bg_card"], highlightbackground=th["border"])

        for container in (
            self.dev_hdr,
            self.mode_hdr,
            self.preset_row1,
            self.preset_row2,
            self.adv_hdr,
            self.adv_body,
            self.adv_grid,
            self.adv_chk_frame,
            self.extra_row,
            self.footer_bottom,
        ):
            container.configure(bg=th["bg_card"])

        for cell in self.adv_grid.winfo_children():
            cell.configure(bg=th["bg_card"])

        # Labels & Buttons inside cards
        self.lbl_dev_title.configure(bg=th["bg_card"], fg=th["fg_main"])
        self.btn_wifi.configure(bg=th["bg_card"], fg=th["accent"], activebackground=th["bg_card"])
        self.btn_refresh_dev.configure(bg=th["bg_card"], fg=th["fg_muted"], activebackground=th["bg_card"])

        self.lbl_mode_title.configure(bg=th["bg_card"], fg=th["fg_main"])
        self.lbl_mode_detail.configure(bg=th["bg_card"], fg=th["fg_muted"])

        self.lbl_adv_title.configure(bg=th["bg_card"], fg=th["fg_main"])
        self.lbl_adv_toggle.configure(bg=th["bg_card"], fg=th["accent"])

        for lbl in (self.lbl_src, self.lbl_res, self.lbl_fps, self.lbl_codec, self.lbl_extra):
            lbl.configure(bg=th["bg_card"], fg=th["fg_muted"])

        for cb in self.adv_checkboxes.values():
            cb.configure(
                bg=th["bg_card"],
                fg=th["fg_main"],
                selectcolor=th["bg_input"],
                activebackground=th["bg_card"],
                activeforeground=th["fg_main"],
            )

        self.ent_extra.configure(
            bg=th["bg_input"],
            fg=th["fg_main"],
            insertbackground=th["fg_main"],
            highlightbackground=th["input_border"],
        )

        self.ent_preview.configure(
            readonlybackground=th["bg_cmd"],
            fg=th["fg_main"],
        )

        self.cb_autoclose.configure(
            bg=th["bg_card"],
            fg=th["fg_muted"],
            selectcolor=th["bg_input"],
            activebackground=th["bg_card"],
            activeforeground=th["fg_main"],
        )

        # Combobox styling
        self.style.configure(
            "TCombobox",
            fieldbackground=th["bg_input"],
            background=th["bg_card"],
            foreground=th["fg_main"],
            arrowcolor=th["fg_main"],
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", th["bg_input"])],
            selectbackground=[("readonly", th["bg_input"])],
            selectforeground=[("readonly", th["fg_main"])],
        )

        self.style_dep_card()
        self.style_preset_buttons()

    def _style_lang_buttons(self):
        th = THEMES[self.theme_name]
        if self.lang == "en":
            self.btn_lang_en.configure(bg=th["accent"], fg=th["accent_fg"])
            self.btn_lang_id.configure(bg=th["bg_card"], fg=th["fg_muted"])
        else:
            self.btn_lang_id.configure(bg=th["accent"], fg=th["accent_fg"])
            self.btn_lang_en.configure(bg=th["bg_card"], fg=th["fg_muted"])

    def set_language(self, lang_code: str):
        self.lang = lang_code
        self.apply_language()
        self._style_lang_buttons()
        self.check_binaries()
        self.refresh_devices()
        self.update_mode_summary_and_preview()
        self.save_config()

    def apply_language(self):
        self.btn_folder.configure(text=self.t("folder_btn"))
        self.btn_recheck.configure(text=self.t("recheck_btn"))
        self.lbl_missing_desc.configure(text=self.t("missing_desc"))
        self.btn_pkg_install.configure(text=self.get_os_install_button_label())
        self.btn_github.configure(text=self.t("github_releases"))

        self.lbl_dev_title.configure(text=self.t("target_device"))
        self.btn_wifi.configure(text=self.t("wireless_btn"))
        self.btn_refresh_dev.configure(text=self.t("refresh_btn"))

        self.lbl_mode_title.configure(text=self.t("operating_mode"))
        for key, (_, btn) in self.preset_buttons.items():
            btn.configure(text=self.t(f"p_{key}"))

        self.lbl_adv_title.configure(text=self.t("adv_title"))
        self.lbl_adv_toggle.configure(text=self.t("collapse") if self.adv_expanded else self.t("expand"))

        self.lbl_src.configure(text=self.t("lbl_source"))
        self.lbl_res.configure(text=self.t("lbl_res"))
        self.lbl_fps.configure(text=self.t("lbl_fps"))
        self.lbl_codec.configure(text=self.t("lbl_codec"))

        for i18n_key, cb in self.adv_checkboxes.items():
            cb.configure(text=self.t(i18n_key))

        self.lbl_extra.configure(text=self.t("lbl_extra"))
        self.cb_autoclose.configure(text=self.t("auto_close"))
        self.btn_start.configure(text=self.t("start_btn"))

    # -------------------------------------------------------------------------
    # Presets, Custom Memory, & Collapsible Advanced Panel
    # -------------------------------------------------------------------------
    def toggle_advanced(self):
        self.adv_expanded = not self.adv_expanded
        if self.adv_expanded:
            self.adv_body.pack(fill="x", pady=(6, 2))
        else:
            self.adv_body.pack_forget()
        self.lbl_adv_toggle.configure(text=self.t("collapse") if self.adv_expanded else self.t("expand"))
        self.lock_window_width()

    def select_preset(self, key: str):
        self.active_preset = key
        state = self.custom_profile if key == "custom" else PRESET_DEFS[key]

        self._suppress_trace = True
        self.var_source.set(state.get("source", "display"))
        self.var_max_size.set(state.get("max_size", "1920"))
        self.var_fps.set(state.get("fps", "60"))
        self.var_codec.set(state.get("codec", "h265"))
        self.var_screen_off.set(state.get("screen_off", False))
        self.var_stay_awake.set(state.get("stay_awake", True))
        self.var_no_audio.set(state.get("no_audio", False))
        self.var_uhid_kb.set(state.get("uhid_kb", False))
        self.var_uhid_gamepad.set(state.get("uhid_gamepad", False))
        self.var_always_on_top.set(state.get("always_on_top", False))
        self.var_fullscreen.set(state.get("fullscreen", False))
        self.var_record.set(state.get("record", False))
        self._suppress_trace = False

        self.style_preset_buttons()
        self.update_mode_summary_and_preview()
        self.save_config()

    def get_current_form_state(self) -> dict:
        return {
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
        }

    def on_manual_setting_changed(self):
        if self._suppress_trace:
            return
        curr = self.get_current_form_state()
        # Check if current settings match any standard preset
        matched_preset = None
        for p_key, p_val in PRESET_DEFS.items():
            if curr == p_val and not self.var_extra_args.get().strip():
                matched_preset = p_key
                break

        if matched_preset:
            self.active_preset = matched_preset
        else:
            self.active_preset = "custom"
            self.custom_profile = curr

        self.style_preset_buttons()
        self.update_mode_summary_and_preview()
        self.save_config()

    def style_preset_buttons(self):
        th = THEMES[self.theme_name]
        for key, (cell, btn) in self.preset_buttons.items():
            is_sel = key == self.active_preset
            if is_sel:
                cell.configure(bg=th["preset_active_bg"], highlightbackground=th["preset_active_border"])
                btn.configure(
                    bg=th["preset_active_bg"],
                    fg=th["preset_active_fg"],
                    activebackground=th["preset_active_bg"],
                    activeforeground=th["preset_active_fg"],
                )
            else:
                cell.configure(bg=th["preset_idle_bg"], highlightbackground=th["preset_idle_border"])
                btn.configure(
                    bg=th["preset_idle_bg"],
                    fg=th["preset_idle_fg"],
                    activebackground=th["border"],
                    activeforeground=th["fg_main"],
                )

    def build_short_summary(self) -> str:
        if self.active_preset is None:
            return self.t("click_profile_hint")

        st = self.get_current_form_state()
        src = st["source"]
        if src == "otg":
            return "HID Keyboard/Mouse Only • No Mirror"

        parts = []
        if src == "new-display":
            parts.append("Virtual 1080p")
        elif src == "camera":
            parts.append("Camera")
        else:
            parts.append("Native" if st["max_size"] == "0" else f"{st['max_size']}p")

        parts.append(f"{st['fps']}fps")
        parts.append(st["codec"].upper())
        if st["screen_off"] and src == "display":
            parts.append("Screen Off")
        if st["uhid_kb"] or st["uhid_gamepad"]:
            parts.append("UHID")
        return " • ".join(parts)

    # -------------------------------------------------------------------------
    # Binary Detection (scrcpy & adb)
    # -------------------------------------------------------------------------
    def find_binary(self, name: str):
        exe_name = f"{name}.exe" if IS_WINDOWS else name

        # 1. Custom user-selected directory
        if self.custom_bin_dir and os.path.isdir(self.custom_bin_dir):
            cand = os.path.join(self.custom_bin_dir, exe_name)
            if os.path.isfile(cand):
                return cand

        # 2. Same folder as executable/script
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        cand = os.path.join(script_dir, exe_name)
        if os.path.isfile(cand):
            return cand

        # 3. Parent directory
        parent_dir = os.path.dirname(script_dir)
        cand = os.path.join(parent_dir, exe_name)
        if os.path.isfile(cand):
            return cand

        # 4. System PATH
        found = shutil.which(name)
        if found:
            return found

        # 5. Windows Winget / Scoop / Chocolatey package locations
        if IS_WINDOWS:
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            user_profile = os.environ.get("USERPROFILE", "")
            program_data = os.environ.get("ProgramData", "")
            search_roots = [
                os.path.join(local_app_data, "Microsoft", "WinGet", "Links"),
                os.path.join(local_app_data, "Microsoft", "WinGet", "Packages"),
                os.path.join(user_profile, "scoop", "shims"),
                os.path.join(program_data, "chocolatey", "bin"),
            ]
            for root_dir in search_roots:
                if not os.path.isdir(root_dir):
                    continue
                direct = os.path.join(root_dir, exe_name)
                if os.path.isfile(direct):
                    return direct
                if root_dir.endswith("Packages"):
                    try:
                        for entry in os.listdir(root_dir):
                            low = entry.lower()
                            if "scrcpy" in low or "platformtools" in low or "adb" in low:
                                pkg_dir = os.path.join(root_dir, entry)
                                for dirpath, _, filenames in os.walk(pkg_dir):
                                    if exe_name in filenames:
                                        return os.path.join(dirpath, exe_name)
                    except Exception:
                        pass

        return None

    def check_binaries(self):
        self.scrcpy_path = self.find_binary("scrcpy")
        self.adb_path = self.find_binary("adb")

        if self.scrcpy_path:
            ver = self.get_scrcpy_version(self.scrcpy_path)
            ver_txt = f"scrcpy {ver}" if ver else self.t("scrcpy_ok")
            self.lbl_scrcpy_status.configure(text=f"● {ver_txt}")
        else:
            self.lbl_scrcpy_status.configure(text=f"● {self.t('scrcpy_missing')}")

        if self.adb_path:
            self.lbl_adb_status.configure(text=f"● {self.t('adb_ok')}")
        else:
            self.lbl_adb_status.configure(text=f"● {self.t('adb_missing')}")

        # Collapse install area if both are installed
        if self.scrcpy_path and self.adb_path:
            self.missing_panel.pack_forget()
        else:
            self.missing_panel.pack(fill="x", pady=(2, 2))

        self.style_dep_card()
        self.lock_window_width()

    def style_dep_card(self):
        th = THEMES[self.theme_name]
        both_ok = bool(self.scrcpy_path and self.adb_path)
        bg = th["bg_card"] if both_ok else th["missing_bg"]
        border = th["border"] if both_ok else th["missing_border"]

        self.dep_card.configure(bg=bg, highlightbackground=border)
        self.dep_top_row.configure(bg=bg)
        self.missing_panel.configure(bg=bg)
        self.missing_btn_row.configure(bg=bg)
        self.lbl_missing_desc.configure(bg=bg, fg=th["fg_muted"])

        self.lbl_scrcpy_status.configure(bg=bg, fg=th["ok"] if self.scrcpy_path else th["err"])
        self.lbl_dep_pipe.configure(bg=bg, fg=th["border"])
        self.lbl_adb_status.configure(bg=bg, fg=th["ok"] if self.adb_path else th["err"])

        self.btn_folder.configure(bg=bg, fg=th["accent"], activebackground=bg)
        self.btn_recheck.configure(bg=bg, fg=th["fg_muted"], activebackground=bg)
        self.btn_pkg_install.configure(bg=th["accent"], fg=th["accent_fg"], activebackground=th["accent"])
        self.btn_github.configure(bg=th["bg_card"], fg=th["fg_main"], activebackground=th["border"])

        if both_ok:
            self.btn_start.configure(state="normal", bg=th["accent"], fg=th["accent_fg"])
        else:
            self.btn_start.configure(state="disabled", bg=th["border"], fg=th["fg_muted"])

    def get_scrcpy_version(self, path: str) -> str:
        try:
            kwargs = {"capture_output": True, "text": True, "timeout": 3}
            if IS_WINDOWS:
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            res = subprocess.run([path, "--version"], **kwargs)
            first_line = (res.stdout or "").splitlines()
            if first_line:
                parts = first_line[0].split()
                if len(parts) >= 2:
                    return f"v{parts[1]}"
        except Exception:
            pass
        return ""

    def on_recheck(self):
        self.check_binaries()
        self.refresh_devices()
        self.update_mode_summary_and_preview()

    def browse_bin_folder(self):
        folder = filedialog.askdirectory(title=self.t("select_folder_title"))
        if folder:
            self.custom_bin_dir = folder
            self.save_config()
            self.on_recheck()

    def get_os_install_button_label(self) -> str:
        if IS_WINDOWS:
            return self.t("install_winget")
        elif IS_MAC:
            return self.t("install_brew")
        return self.t("install_linux")

    def run_official_package_install(self):
        if IS_WINDOWS:
            cmd_str = "winget install --exact --id Genymobile.scrcpy"
            confirm = messagebox.askyesno(
                self.t("winget_confirm_title"),
                self.t("winget_confirm_msg").format(cmd=cmd_str),
            )
            if confirm:
                subprocess.Popen(
                    ["cmd.exe", "/k", "winget", "install", "--exact", "--id", "Genymobile.scrcpy"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
        elif IS_MAC:
            cmd_str = "brew install scrcpy android-platform-tools"
            confirm = messagebox.askyesno("Homebrew", f"Run in Terminal?\n\n    {cmd_str}")
            if confirm:
                apple_script = f'tell application "Terminal" to do script "{cmd_str}"'
                subprocess.Popen(["osascript", "-e", apple_script])
        else:
            messagebox.showinfo(
                "Linux Install",
                "Debian / Ubuntu:\n  sudo apt install scrcpy adb\n\n"
                "Arch Linux:\n  sudo pacman -S scrcpy android-tools\n\n"
                "Fedora:\n  sudo dnf install scrcpy android-tools",
            )

    # -------------------------------------------------------------------------
    # ADB Devices & Wireless Helper
    # -------------------------------------------------------------------------
    def refresh_devices(self):
        self.devices = []
        if not self.adb_path:
            msg = self.t("no_adb_device_list")
            self.cmb_device["values"] = [msg]
            self.var_device.set(msg)
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

        auto_lbl = self.t("auto_device")
        if not self.devices:
            self.cmb_device["values"] = [auto_lbl]
            self.var_device.set(auto_lbl)
        else:
            items = [auto_lbl]
            for d in self.devices:
                status_tag = "Ready" if d["state"] == "device" else d["state"].upper()
                items.append(f"{d['serial']}  —  {d['model']} ({d['type']} • {status_tag})")
            self.cmb_device["values"] = items
            self.var_device.set(items[1] if len(items) > 1 else items[0])

    def open_wifi_dialog(self):
        if not self.adb_path:
            messagebox.showwarning("ADB", self.t("adb_missing"))
            return

        th = THEMES[self.theme_name]
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("wifi_title"))
        dlg.configure(bg=th["bg_card"], padx=14, pady=12)
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text=self.t("wifi_header"), bg=th["bg_card"], fg=th["fg_main"], font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=(0, 6)
        )
        tk.Label(dlg, text=self.t("wifi_opt1"), bg=th["bg_card"], fg=th["fg_muted"], font=("Segoe UI", 8)).pack(
            anchor="w"
        )

        def auto_tcpip():
            dlg.destroy()
            cur = self.var_extra_args.get().strip()
            if "--tcpip" not in cur:
                self.var_extra_args.set((cur + " --tcpip").strip())
            self.on_manual_setting_changed()

        tk.Button(
            dlg,
            text=self.t("wifi_auto_btn"),
            command=auto_tcpip,
            bg=th["accent"],
            fg=th["accent_fg"],
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=4,
            cursor="hand2",
        ).pack(anchor="w", pady=(4, 10))

        tk.Label(dlg, text=self.t("wifi_opt2"), bg=th["bg_card"], fg=th["fg_muted"], font=("Segoe UI", 8)).pack(
            anchor="w"
        )

        ip_row = tk.Frame(dlg, bg=th["bg_card"])
        ip_row.pack(fill="x", pady=(4, 0))

        ent_ip = tk.Entry(
            ip_row, bg=th["bg_input"], fg=th["fg_main"], insertbackground=th["fg_main"], relief="solid", bd=1, width=28
        )
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
                messagebox.showinfo("ADB Connect", output.strip() or f"Connecting to {ip}")
                dlg.destroy()
                self.refresh_devices()
                self.update_mode_summary_and_preview()
            except Exception as e:
                messagebox.showerror("ADB Error", str(e))

        tk.Button(
            ip_row,
            text=self.t("wifi_conn_btn"),
            command=manual_connect,
            bg=th["accent"],
            fg=th["accent_fg"],
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=3,
            cursor="hand2",
        ).pack(side="left")

    # -------------------------------------------------------------------------
    # Command Assembly & Execution
    # -------------------------------------------------------------------------
    def build_command_args(self) -> list:
        exe = self.scrcpy_path or "scrcpy"
        cmd = [exe]

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

        codec = self.var_codec.get()
        if codec and codec != "h264":
            cmd.append(f"--video-codec={codec}")

        size_val = self.var_max_size.get().strip()
        if size_val.isdigit() and size_val != "0":
            if source == "camera":
                cmd.append(f"--camera-size={size_val}x1080")
            else:
                cmd.append(f"-m{size_val}")

        fps = self.var_fps.get().strip()
        if fps.isdigit():
            cmd.append(f"--max-fps={fps}")

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

    def update_mode_summary_and_preview(self):
        self.lbl_mode_detail.configure(text=self.build_short_summary())
        args = self.build_command_args()
        preview_str = " ".join(["scrcpy"] + args[1:])
        self.ent_preview.configure(state="normal")
        self.ent_preview.delete(0, "end")
        self.ent_preview.insert(0, preview_str)
        self.ent_preview.configure(state="readonly")

    def load_config(self) -> dict:
        if os.path.isfile(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        # If the user hadn't explicitly clicked a preset on first run, persist standard once saved
        persisted_preset = self.active_preset or "standard"
        data = {
            "lang": self.lang,
            "theme": self.theme_name,
            "custom_bin_dir": self.custom_bin_dir,
            "active_preset": persisted_preset,
            "custom_profile": self.custom_profile,
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
            messagebox.showerror(APP_NAME, self.t("scrcpy_missing"))
            return

        if self.active_preset is None:
            self.active_preset = "standard"
        self.save_config()
        args = self.build_command_args()

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
            kwargs = {
                "env": env,
                "stdin": subprocess.DEVNULL,
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
            }
            if IS_WINDOWS:
                kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                kwargs["start_new_session"] = True

            subprocess.Popen(args, **kwargs)

            if self.var_auto_close.get():
                self.root.destroy()
                sys.exit(0)
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))


def main():
    root = tk.Tk()
    ScrcpyCplApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
