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
import tempfile
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

APP_NAME = "scrcpy-cpl"
APP_VERSION = "1.2.1"
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".scrcpy_cpl.json")
PORTABLE_INSTALL_DIR = os.path.join(os.path.expanduser("~"), ".scrcpy-cpl-bin")
OFFICIAL_RELEASES_URL = "https://github.com/Genymobile/scrcpy/releases"
OFFICIAL_ADB_URL = "https://developer.android.com/tools/releases/platform-tools"

IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

WINDOW_WIDTH = 550
ADV_TAB_HEIGHT = 172

BASE_STATE = {
    "source": "display",
    "max_size": "1920",
    "fps": "60",
    "bitrate": "Default",
    "codec": "h265",
    "orientation": "Default",
    "camera_facing": "Default",
    "flex_display": False,
    "record": False,
    "audio_source": "output",
    "audio_codec": "opus",
    "no_audio": False,
    "audio_dup": False,
    "kb_mode": "sdk",
    "mouse_mode": "sdk",
    "gamepad_mode": "disabled",
    "no_control": False,
    "screen_off": False,
    "stay_awake": True,
    "power_off_close": False,
    "show_touches": False,
    "always_on_top": False,
    "fullscreen": False,
    "borderless": False,
    "no_screensaver": False,
}


def make_preset(**overrides) -> dict:
    d = dict(BASE_STATE)
    d.update(overrides)
    return d


PRESET_DEFS = {
    "standard": make_preset(),
    "gaming": make_preset(
        fps="120",
        bitrate="16M",
        kb_mode="uhid",
        gamepad_mode="uhid",
    ),
    "privacy": make_preset(
        screen_off=True,
        stay_awake=True,
        power_off_close=True,
    ),
    "dex": make_preset(
        source="new-display",
        flex_display=True,
        kb_mode="uhid",
    ),
    "camera": make_preset(
        source="camera",
        camera_facing="back",
        stay_awake=False,
    ),
    "otg": make_preset(
        source="otg",
        max_size="0",
        stay_awake=False,
    ),
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
        "install_winget": "Install scrcpy + adb (Winget)",
        "install_ps_github": "Install scrcpy + adb (PowerShell)",
        "install_brew": "Install scrcpy + adb (Homebrew)",
        "install_linux": "Linux Install Commands",
        "github_releases": "scrcpy GitHub ↗",
        "official_adb": "Official Google ADB ↗",
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
        "adv_title": "Advanced Video, Audio & Control Settings",
        "expand": "[+] Expand",
        "collapse": "[-] Collapse",
        "tab_video": "Video & Display",
        "tab_audio": "Audio & Input",
        "tab_window": "Device & Window",
        "lbl_source": "Source",
        "lbl_res": "Max Size (-m)",
        "lbl_fps": "Max FPS",
        "lbl_bitrate": "Bit Rate (-b)",
        "lbl_codec": "Video Codec",
        "lbl_orient": "Orientation",
        "lbl_cam_face": "Camera Facing",
        "chk_flex": "Flex Virtual Display (-x / resize dynamically)",
        "chk_rec": "Record to MP4:",
        "btn_browse_rec": "Save As...",
        "lbl_aud_src": "Audio Source",
        "lbl_aud_codec": "Audio Codec",
        "lbl_kb_mode": "Keyboard Mode",
        "lbl_mouse_mode": "Mouse Mode",
        "lbl_gp_mode": "Gamepad Mode",
        "chk_no_audio": "Disable Audio (--no-audio)",
        "chk_aud_dup": "Keep Audio on Phone + PC (--audio-dup, Android 13+)",
        "chk_no_ctrl": "Read-Only / No Control (-n / --no-control)",
        "chk_screen_off": "Turn physical screen off (-S)",
        "chk_stay_awake": "Stay awake while plugged in (-w)",
        "chk_poff_close": "Power off screen on close (--power-off-on-close)",
        "chk_touches": "Show physical finger touches (-t)",
        "chk_top": "Window always on top (--always-on-top)",
        "chk_full": "Start in fullscreen (-f)",
        "chk_borderless": "Borderless window (--window-borderless)",
        "chk_nosaver": "Disable PC screensaver (--disable-screensaver)",
        "lbl_extra": "Extra Flags:",
        "copy_btn": "Copy",
        "copied_btn": "Copied ✓",
        "auto_close": "Close panel after launch (0 MB RAM)",
        "start_btn": "Start Mirroring",
        "launch_err_title": "scrcpy Failed to Start",
        "launch_err_prefix": "scrcpy exited immediately with an error:\n\n",
        "wifi_title": "Wireless Connection (ADB TCP/IP)",
        "wifi_header": "Connect Android over Wi-Fi",
        "wifi_opt1": "Option 1: Connect via USB first, then append automatic --tcpip flag:",
        "wifi_auto_btn": "Use Automatic --tcpip Flag",
        "wifi_opt2": "Option 2: Enter device IP address manually (e.g. 192.168.1.15:5555):",
        "wifi_conn_btn": "Connect ADB",
        "winget_confirm_title": "Official Install via Winget",
        "winget_confirm_msg": "Open CMD and run the official Microsoft Winget command?\n\n    {cmd}\n\nThis installs official scrcpy and adb from Genymobile.",
        "ps_confirm_title": "Official GitHub Release Install (PowerShell)",
        "ps_confirm_msg": "Winget was not detected on this Windows system.\n\nOpen a visible PowerShell window to fetch and extract the latest official release directly from Genymobile/scrcpy on GitHub into:\n\n    {dest}\n\n(Includes both official scrcpy.exe and adb.exe). Continue?",
    },
    "id": {
        "scrcpy_ok": "scrcpy terdeteksi",
        "scrcpy_missing": "scrcpy belum terinstall",
        "adb_ok": "adb terdeteksi",
        "adb_missing": "adb belum terinstall",
        "folder_btn": "Pilih Folder...",
        "recheck_btn": "Cek Ulang",
        "missing_desc": "Tidak mengunduh diam-diam. Install resmi via package manager atau pilih folder portable:",
        "install_winget": "Install scrcpy + adb (Winget)",
        "install_ps_github": "Install scrcpy + adb (PowerShell)",
        "install_brew": "Install scrcpy + adb (Homebrew)",
        "install_linux": "Perintah Install Linux",
        "github_releases": "GitHub scrcpy ↗",
        "official_adb": "Google ADB Resmi ↗",
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
        "adv_title": "Pengaturan Lanjutan Video, Audio & Kontrol",
        "expand": "[+] Buka",
        "collapse": "[-] Tutup",
        "tab_video": "Video & Layar",
        "tab_audio": "Audio & Input",
        "tab_window": "Perangkat & Jendela",
        "lbl_source": "Sumber",
        "lbl_res": "Resolusi (-m)",
        "lbl_fps": "Maks FPS",
        "lbl_bitrate": "Bit Rate (-b)",
        "lbl_codec": "Codec Video",
        "lbl_orient": "Orientasi",
        "lbl_cam_face": "Arah Kamera",
        "chk_flex": "Flex Virtual Display (-x / ukuran layar dinamis)",
        "chk_rec": "Rekam MP4:",
        "btn_browse_rec": "Simpan Ke...",
        "lbl_aud_src": "Sumber Audio",
        "lbl_aud_codec": "Codec Audio",
        "lbl_kb_mode": "Mode Keyboard",
        "lbl_mouse_mode": "Mode Mouse",
        "lbl_gp_mode": "Mode Gamepad",
        "chk_no_audio": "Matikan Suara (--no-audio)",
        "chk_aud_dup": "Suara Tetap Keluar di HP + PC (--audio-dup, Android 13+)",
        "chk_no_ctrl": "Hanya Lihat / Tanpa Kontrol (-n / --no-control)",
        "chk_screen_off": "Matikan layar fisik HP (-S)",
        "chk_stay_awake": "Cegah HP terkunci saat dicas (-w)",
        "chk_poff_close": "Matikan layar HP saat keluar (--power-off-on-close)",
        "chk_touches": "Tampilkan titik sentuhan jari (-t)",
        "chk_top": "Jendela selalu di atas (--always-on-top)",
        "chk_full": "Langsung layar penuh (-f)",
        "chk_borderless": "Jendela tanpa bingkai (--window-borderless)",
        "chk_nosaver": "Cegah screensaver PC (--disable-screensaver)",
        "lbl_extra": "Flag Ekstra:",
        "copy_btn": "Salin",
        "copied_btn": "Tersalin ✓",
        "auto_close": "Tutup panel setelah jalan (0 MB RAM)",
        "start_btn": "Mulai Mirroring",
        "launch_err_title": "scrcpy Gagal Dijalankan",
        "launch_err_prefix": "scrcpy langsung berhenti karena kendala berikut:\n\n",
        "wifi_title": "Koneksi Wireless (ADB TCP/IP)",
        "wifi_header": "Sambungkan Android via Wi-Fi",
        "wifi_opt1": "Opsi 1: Colok USB dulu, lalu gunakan flag otomatis --tcpip:",
        "wifi_auto_btn": "Gunakan Flag Otomatis --tcpip",
        "wifi_opt2": "Opsi 2: Masukkan IP HP secara manual (contoh: 192.168.1.15:5555):",
        "wifi_conn_btn": "Sambungkan ADB",
        "winget_confirm_title": "Install Resmi via Winget",
        "winget_confirm_msg": "Buka CMD dan jalankan perintah resmi Microsoft Winget?\n\n    {cmd}\n\nPaket ini berisi scrcpy dan adb resmi dari Genymobile.",
        "ps_confirm_title": "Install Rilis Resmi GitHub (PowerShell)",
        "ps_confirm_msg": "Winget tidak ditemukan di Windows kamu.\n\nBuka jendela PowerShell transparan untuk mengunduh & mengekstrak rilis resmi terbaru langsung dari GitHub Genymobile/scrcpy ke:\n\n    {dest}\n\n(Sudah termasuk scrcpy.exe dan adb.exe resmi). Lanjutkan?",
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
        "fg_disabled": "#a1a1aa",
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
        "fg_disabled": "#52525b",
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
    Renders the custom scrcpy-cpl icon (Official scrcpy Jade & Charcoal,
    combining the Phone Mirror Frame + 3 Control Panel Sliders)
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

    fill_rect(1, 1, 23, 23, "#166534")
    fill_rect(2, 2, 22, 22, "#1f7a54")

    fill_rect(3.5, 3.0, 14.5, 20.5, "#ffffff")
    fill_rect(4.8, 4.3, 13.2, 19.2, "#134e35")
    fill_rect(7.2, 5.2, 10.8, 6.1, "#ffffff")

    fill_rect(9.2, 7.5, 21.2, 19.5, "#ffffff")
    fill_rect(10.2, 8.5, 20.2, 18.5, "#18181b")

    fill_rect(11.6, 10.4, 18.8, 11.4, "#71717a")
    fill_rect(11.6, 13.1, 18.8, 14.1, "#71717a")
    fill_rect(11.6, 15.8, 18.8, 16.8, "#71717a")

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
        self.devices = []

        saved_custom = dict(BASE_STATE)
        saved_custom.update(self.config.get("custom_profile", {}))
        self.custom_profile = saved_custom

        self.active_preset = self.config.get("active_preset", None)
        self.adv_expanded = False
        self.active_adv_tab = "video"
        self._suppress_trace = False
        self._centered_once = False

        init_state = (
            self.custom_profile
            if self.active_preset == "custom"
            else PRESET_DEFS.get(self.active_preset or "standard", PRESET_DEFS["standard"])
        )

        # Tkinter Variables
        self.var_device = tk.StringVar()

        # Tab 1: Video & Display
        self.var_source = tk.StringVar(value=init_state.get("source", "display"))
        self.var_max_size = tk.StringVar(value=init_state.get("max_size", "1920"))
        self.var_fps = tk.StringVar(value=init_state.get("fps", "60"))
        self.var_bitrate = tk.StringVar(value=init_state.get("bitrate", "Default"))
        self.var_codec = tk.StringVar(value=init_state.get("codec", "h265"))
        self.var_orientation = tk.StringVar(value=init_state.get("orientation", "Default"))
        self.var_camera_facing = tk.StringVar(value=init_state.get("camera_facing", "Default"))
        self.var_flex_display = tk.BooleanVar(value=init_state.get("flex_display", False))
        self.var_record = tk.BooleanVar(value=init_state.get("record", False))
        self.var_record_path = tk.StringVar(value=self.config.get("record_path", "scrcpy_capture.mp4"))

        # Tab 2: Audio & Input
        self.var_audio_source = tk.StringVar(value=init_state.get("audio_source", "output"))
        self.var_audio_codec = tk.StringVar(value=init_state.get("audio_codec", "opus"))
        self.var_no_audio = tk.BooleanVar(value=init_state.get("no_audio", False))
        self.var_audio_dup = tk.BooleanVar(value=init_state.get("audio_dup", False))
        self.var_kb_mode = tk.StringVar(value=init_state.get("kb_mode", "sdk"))
        self.var_mouse_mode = tk.StringVar(value=init_state.get("mouse_mode", "sdk"))
        self.var_gamepad_mode = tk.StringVar(value=init_state.get("gamepad_mode", "disabled"))
        self.var_no_control = tk.BooleanVar(value=init_state.get("no_control", False))

        # Tab 3: Device & Window
        self.var_screen_off = tk.BooleanVar(value=init_state.get("screen_off", False))
        self.var_stay_awake = tk.BooleanVar(value=init_state.get("stay_awake", True))
        self.var_power_off_close = tk.BooleanVar(value=init_state.get("power_off_close", False))
        self.var_show_touches = tk.BooleanVar(value=init_state.get("show_touches", False))
        self.var_always_on_top = tk.BooleanVar(value=init_state.get("always_on_top", False))
        self.var_fullscreen = tk.BooleanVar(value=init_state.get("fullscreen", False))
        self.var_borderless = tk.BooleanVar(value=init_state.get("borderless", False))
        self.var_no_screensaver = tk.BooleanVar(value=init_state.get("no_screensaver", False))
        self.var_extra_args = tk.StringVar(value=self.config.get("extra_args", ""))

        self.var_auto_close = tk.BooleanVar(value=self.config.get("auto_close", True))

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
        self.update_contextual_widget_states()
        self.update_mode_summary_and_preview()
        self.lock_window_width(center=True)

    def t(self, key: str) -> str:
        return I18N.get(self.lang, I18N["en"]).get(key, key)

    def lock_window_width(self, center: bool = False):
        self.root.update_idletasks()
        req_h = self.root.winfo_reqheight()
        if center and not self._centered_once:
            self._centered_once = True
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            x = max(0, (sw - WINDOW_WIDTH) // 2)
            y = max(0, (sh - req_h) // 2 - 30)
            self.root.geometry(f"{WINDOW_WIDTH}x{req_h}+{x}+{y}")
        else:
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

        # 1. Dependency Card
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
            padx=9,
            pady=3,
            cursor="hand2",
        )
        self.btn_github.pack(side="left", padx=(0, 6))

        self.btn_adb_web = tk.Button(
            self.missing_btn_row,
            text="",
            command=lambda: webbrowser.open(OFFICIAL_ADB_URL),
            relief="solid",
            bd=1,
            font=("Segoe UI", 8),
            padx=9,
            pady=3,
            cursor="hand2",
        )
        self.btn_adb_web.pack(side="left")

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

        # 3. Operating Mode Card
        self.mode_card = tk.Frame(self.body, highlightthickness=1, padx=10, pady=8)
        self.mode_card.pack(fill="x", pady=(0, 8))

        self.mode_hdr = tk.Frame(self.mode_card)
        self.mode_hdr.pack(fill="x", pady=(0, 6))

        self.lbl_mode_title = tk.Label(self.mode_hdr, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_mode_title.pack(side="left")

        self.lbl_mode_detail = tk.Label(self.mode_hdr, text="", font=("Consolas", 8))
        self.lbl_mode_detail.pack(side="right")

        self.preset_row1 = tk.Frame(self.mode_card)
        self.preset_row1.pack(fill="x", pady=(0, 5))
        for col_idx in range(4):
            self.preset_row1.columnconfigure(col_idx, weight=1, uniform="preset_r1")

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

        # 4. Collapsible Advanced Settings with Fixed-Height 3 Mini-Tabs
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

        # 3 Mini-Tab Buttons inside Advanced
        self.adv_tab_bar = tk.Frame(self.adv_body)
        self.adv_tab_bar.pack(fill="x", pady=(0, 8))
        for i in range(3):
            self.adv_tab_bar.columnconfigure(i, weight=1, uniform="adv_tabs")

        self.adv_tab_buttons = {}
        for idx, t_key in enumerate(["video", "audio", "window"]):
            cell = tk.Frame(self.adv_tab_bar, highlightthickness=1, height=26)
            cell.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 2, 0 if idx == 2 else 2))
            cell.pack_propagate(False)
            btn = tk.Button(
                cell,
                text="",
                command=lambda tk_name=t_key: self.switch_adv_tab(tk_name),
                relief="flat",
                bd=0,
                font=("Segoe UI", 8),
                cursor="hand2",
            )
            btn.pack(fill="both", expand=True)
            self.adv_tab_buttons[t_key] = (cell, btn)

        # Fixed-Height Viewport so switching tabs NEVER changes window height
        self.adv_tab_viewport = tk.Frame(self.adv_body, height=ADV_TAB_HEIGHT)
        self.adv_tab_viewport.pack(fill="x")
        self.adv_tab_viewport.pack_propagate(False)

        self.adv_checkboxes = {}
        self.adv_labels = {}

        # --- TAB 1: VIDEO & DISPLAY ---
        self.tab_frame_video = tk.Frame(self.adv_tab_viewport)

        self.vid_row1 = tk.Frame(self.tab_frame_video)
        self.vid_row1.pack(fill="x", pady=(0, 6))
        for i in range(4):
            self.vid_row1.columnconfigure(i, weight=1, uniform="vr1")

        self.adv_labels["lbl_source"], self.cmb_source = self._create_adv_combo(
            self.vid_row1, 0, self.var_source, ["display", "new-display", "camera", "otg"]
        )
        self.adv_labels["lbl_res"], self.cmb_res = self._create_adv_combo(
            self.vid_row1, 1, self.var_max_size, ["0", "2560", "1920", "1600", "1280", "1024", "800"]
        )
        self.adv_labels["lbl_fps"], self.cmb_fps = self._create_adv_combo(
            self.vid_row1, 2, self.var_fps, ["15", "30", "60", "90", "120", "144"]
        )
        self.adv_labels["lbl_bitrate"], self.cmb_bitrate = self._create_adv_combo(
            self.vid_row1, 3, self.var_bitrate, ["Default", "2M", "4M", "8M", "12M", "16M", "24M", "32M"]
        )

        self.vid_row2 = tk.Frame(self.tab_frame_video)
        self.vid_row2.pack(fill="x", pady=(0, 6))
        for i in range(3):
            self.vid_row2.columnconfigure(i, weight=1, uniform="vr2")

        self.adv_labels["lbl_codec"], self.cmb_codec = self._create_adv_combo(
            self.vid_row2, 0, self.var_codec, ["h265", "h264", "av1"], max_col=2
        )
        self.adv_labels["lbl_orient"], self.cmb_orient = self._create_adv_combo(
            self.vid_row2, 1, self.var_orientation, ["Default", "0", "90", "180", "270"], max_col=2
        )
        self.adv_labels["lbl_cam_face"], self.cmb_cam_face = self._create_adv_combo(
            self.vid_row2, 2, self.var_camera_facing, ["Default", "back", "front", "external"], max_col=2
        )

        self.vid_chk_frame = tk.Frame(self.tab_frame_video)
        self.vid_chk_frame.pack(fill="x")
        self._add_check(self.vid_chk_frame, "chk_flex", self.var_flex_display, 0, 0)

        # Record row with path entry + Save As button
        self.rec_row = tk.Frame(self.tab_frame_video)
        self.rec_row.pack(fill="x", pady=(2, 0))

        self.cb_rec = tk.Checkbutton(
            self.rec_row,
            text="",
            variable=self.var_record,
            command=self.on_manual_setting_changed,
            font=("Segoe UI", 8),
            anchor="w",
            cursor="hand2",
        )
        self.cb_rec.pack(side="left")
        self.adv_checkboxes["chk_rec"] = self.cb_rec

        self.ent_rec_path = tk.Entry(
            self.rec_row,
            textvariable=self.var_record_path,
            relief="solid",
            bd=1,
            font=("Consolas", 8),
        )
        self.ent_rec_path.pack(side="left", fill="x", expand=True, padx=(6, 6), ipady=2)
        self.ent_rec_path.bind("<KeyRelease>", lambda e: self.on_manual_setting_changed())

        self.btn_browse_rec = tk.Button(
            self.rec_row,
            text="",
            command=self.browse_record_file,
            relief="solid",
            bd=1,
            font=("Segoe UI", 8),
            padx=6,
            pady=1,
            cursor="hand2",
        )
        self.btn_browse_rec.pack(side="right")

        # --- TAB 2: AUDIO & INPUT ---
        self.tab_frame_audio = tk.Frame(self.adv_tab_viewport)

        self.aud_row1 = tk.Frame(self.tab_frame_audio)
        self.aud_row1.pack(fill="x", pady=(0, 6))
        for i in range(2):
            self.aud_row1.columnconfigure(i, weight=1, uniform="ar1")

        self.adv_labels["lbl_aud_src"], self.cmb_aud_src = self._create_adv_combo(
            self.aud_row1, 0, self.var_audio_source, ["output", "playback", "mic", "mic-unprocessed", "voice-call"], max_col=1
        )
        self.adv_labels["lbl_aud_codec"], self.cmb_aud_codec = self._create_adv_combo(
            self.aud_row1, 1, self.var_audio_codec, ["opus", "aac", "flac", "raw"], max_col=1
        )

        self.aud_row2 = tk.Frame(self.tab_frame_audio)
        self.aud_row2.pack(fill="x", pady=(0, 6))
        for i in range(3):
            self.aud_row2.columnconfigure(i, weight=1, uniform="ar2")

        self.adv_labels["lbl_kb_mode"], self.cmb_kb_mode = self._create_adv_combo(
            self.aud_row2, 0, self.var_kb_mode, ["sdk", "uhid", "aoa", "disabled"], max_col=2
        )
        self.adv_labels["lbl_mouse_mode"], self.cmb_mouse_mode = self._create_adv_combo(
            self.aud_row2, 1, self.var_mouse_mode, ["sdk", "uhid", "aoa", "disabled"], max_col=2
        )
        self.adv_labels["lbl_gp_mode"], self.cmb_gp_mode = self._create_adv_combo(
            self.aud_row2, 2, self.var_gamepad_mode, ["disabled", "uhid", "aoa"], max_col=2
        )

        self.aud_chk_frame = tk.Frame(self.tab_frame_audio)
        self.aud_chk_frame.pack(fill="x")
        self._add_check(self.aud_chk_frame, "chk_no_audio", self.var_no_audio, 0, 0)
        self._add_check(self.aud_chk_frame, "chk_aud_dup", self.var_audio_dup, 1, 0)
        self._add_check(self.aud_chk_frame, "chk_no_ctrl", self.var_no_control, 2, 0)

        # --- TAB 3: DEVICE & WINDOW ---
        self.tab_frame_window = tk.Frame(self.adv_tab_viewport)

        self.win_chk_frame = tk.Frame(self.tab_frame_window)
        self.win_chk_frame.pack(fill="x")
        self.win_chk_frame.columnconfigure(0, weight=1, uniform="wchk")
        self.win_chk_frame.columnconfigure(1, weight=1, uniform="wchk")

        win_checks = [
            ("chk_screen_off", self.var_screen_off, 0, 0),
            ("chk_stay_awake", self.var_stay_awake, 0, 1),
            ("chk_poff_close", self.var_power_off_close, 1, 0),
            ("chk_touches", self.var_show_touches, 1, 1),
            ("chk_top", self.var_always_on_top, 2, 0),
            ("chk_full", self.var_fullscreen, 2, 1),
            ("chk_borderless", self.var_borderless, 3, 0),
            ("chk_nosaver", self.var_no_screensaver, 3, 1),
        ]
        for key, var, r, c in win_checks:
            self._add_check(self.win_chk_frame, key, var, r, c)

        self.extra_row = tk.Frame(self.tab_frame_window)
        self.extra_row.pack(fill="x", pady=(8, 0))

        self.adv_labels["lbl_extra"] = tk.Label(self.extra_row, text="", font=("Segoe UI", 8))
        self.adv_labels["lbl_extra"].pack(side="left")

        self.ent_extra = tk.Entry(
            self.extra_row,
            textvariable=self.var_extra_args,
            relief="solid",
            bd=1,
            font=("Consolas", 8),
        )
        self.ent_extra.pack(side="left", fill="x", expand=True, padx=(6, 0), ipady=2)
        self.ent_extra.bind("<KeyRelease>", lambda e: self.on_manual_setting_changed())

        # Show initial tab inside adv_tab_viewport
        self.tab_frame_video.pack(fill="both", expand=True)

        # 5. Footer Card (Command Preview + Copy Button + Auto-Close + Launch)
        self.footer_card = tk.Frame(self.body, highlightthickness=1, padx=10, pady=8)
        self.footer_card.pack(fill="x")

        self.cmd_row = tk.Frame(self.footer_card)
        self.cmd_row.pack(fill="x", pady=(0, 8))

        self.ent_preview = tk.Entry(
            self.cmd_row,
            relief="solid",
            bd=1,
            font=("Consolas", 9),
            state="readonly",
        )
        self.ent_preview.pack(side="left", fill="x", expand=True, ipady=4)

        self.btn_copy_cmd = tk.Button(
            self.cmd_row,
            text="Copy",
            command=self.copy_command_to_clipboard,
            relief="solid",
            bd=1,
            font=("Segoe UI", 8),
            width=8,
            pady=3,
            cursor="hand2",
        )
        self.btn_copy_cmd.pack(side="right", padx=(6, 0))

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

    def _create_adv_combo(self, parent, col, var, values, max_col=3):
        cell = tk.Frame(parent)
        cell.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 3, 0 if col == max_col else 3))
        lbl = tk.Label(cell, text="", font=("Segoe UI", 8))
        lbl.pack(anchor="w")
        cmb = ttk.Combobox(cell, textvariable=var, values=values, state="readonly", font=("Consolas", 8))
        cmb.pack(fill="x", pady=(2, 0))
        cmb.bind("<<ComboboxSelected>>", lambda e: self.on_manual_setting_changed())
        return lbl, cmb

    def _add_check(self, parent, i18n_key, var, row, col):
        cb = tk.Checkbutton(
            parent,
            text="",
            variable=var,
            command=self.on_manual_setting_changed,
            font=("Segoe UI", 8),
            anchor="w",
            cursor="hand2",
        )
        cb.grid(row=row, column=col, sticky="ew", pady=1)
        self.adv_checkboxes[i18n_key] = cb

    def switch_adv_tab(self, tab_key: str):
        self.active_adv_tab = tab_key
        for k, frame in [
            ("video", self.tab_frame_video),
            ("audio", self.tab_frame_audio),
            ("window", self.tab_frame_window),
        ]:
            if k == tab_key:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()
        self.style_adv_tabs()

    def browse_record_file(self):
        path = filedialog.asksaveasfilename(
            title="Save Recording As",
            defaultextension=".mp4",
            initialfile=self.var_record_path.get() or "scrcpy_capture.mp4",
            filetypes=[("MP4 Video", "*.mp4"), ("Matroska Video", "*.mkv"), ("All Files", "*.*")],
        )
        if path:
            self.var_record_path.set(path)
            self.var_record.set(True)
            self.on_manual_setting_changed()

    def copy_command_to_clipboard(self):
        cmd_str = self.ent_preview.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(cmd_str)
        self.btn_copy_cmd.configure(text=self.t("copied_btn"))
        self.root.after(1200, lambda: self.btn_copy_cmd.configure(text=self.t("copy_btn")))

    # -------------------------------------------------------------------------
    # Contextual Widget State Management (UX Improvement #2)
    # -------------------------------------------------------------------------
    def update_contextual_widget_states(self):
        src = self.var_source.get()
        is_otg = src == "otg"
        is_cam = src == "camera"
        is_new_disp = src == "new-display"
        is_disp = src == "display"

        # Video tab contextual states
        for cmb in (self.cmb_res, self.cmb_fps, self.cmb_bitrate, self.cmb_codec, self.cmb_orient):
            cmb.configure(state="disabled" if is_otg else "readonly")

        self.cmb_cam_face.configure(state="readonly" if is_cam else "disabled")
        self.adv_checkboxes["chk_flex"].configure(state="normal" if is_new_disp else "disabled")
        self.cb_rec.configure(state="disabled" if is_otg else "normal")

        rec_enabled = self.var_record.get() and not is_otg
        self.ent_rec_path.configure(state="normal" if rec_enabled else "disabled")
        self.btn_browse_rec.configure(state="normal" if rec_enabled else "disabled")

        # Audio & Input tab contextual states
        no_aud = self.var_no_audio.get() or is_otg
        self.adv_checkboxes["chk_no_audio"].configure(state="disabled" if is_otg else "normal")
        self.adv_checkboxes["chk_aud_dup"].configure(state="disabled" if no_aud else "normal")
        self.cmb_aud_src.configure(
            state="disabled" if (no_aud or self.var_audio_dup.get()) else "readonly"
        )
        self.cmb_aud_codec.configure(state="disabled" if no_aud else "readonly")

        no_ctrl = self.var_no_control.get()
        self.adv_checkboxes["chk_no_ctrl"].configure(state="disabled" if is_otg else "normal")
        for cmb in (self.cmb_kb_mode, self.cmb_mouse_mode, self.cmb_gp_mode):
            cmb.configure(state="disabled" if (no_ctrl or is_otg) else "readonly")

        # Device & Window tab contextual states
        for key in ("chk_screen_off", "chk_stay_awake", "chk_poff_close", "chk_touches"):
            self.adv_checkboxes[key].configure(state="normal" if is_disp else "disabled")
        for key in ("chk_top", "chk_full", "chk_borderless", "chk_nosaver"):
            self.adv_checkboxes[key].configure(state="disabled" if is_otg else "normal")

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

        for card in (self.dev_card, self.mode_card, self.adv_card, self.footer_card):
            card.configure(bg=th["bg_card"], highlightbackground=th["border"])

        for container in (
            self.dev_hdr,
            self.mode_hdr,
            self.preset_row1,
            self.preset_row2,
            self.adv_hdr,
            self.adv_body,
            self.adv_tab_bar,
            self.adv_tab_viewport,
            self.tab_frame_video,
            self.vid_row1,
            self.vid_row2,
            self.vid_chk_frame,
            self.rec_row,
            self.tab_frame_audio,
            self.aud_row1,
            self.aud_row2,
            self.aud_chk_frame,
            self.tab_frame_window,
            self.win_chk_frame,
            self.extra_row,
            self.cmd_row,
            self.footer_bottom,
        ):
            container.configure(bg=th["bg_card"])

        for row_parent in (self.vid_row1, self.vid_row2, self.aud_row1, self.aud_row2):
            for cell in row_parent.winfo_children():
                cell.configure(bg=th["bg_card"])

        self.lbl_dev_title.configure(bg=th["bg_card"], fg=th["fg_main"])
        self.btn_wifi.configure(bg=th["bg_card"], fg=th["accent"], activebackground=th["bg_card"])
        self.btn_refresh_dev.configure(bg=th["bg_card"], fg=th["fg_muted"], activebackground=th["bg_card"])

        self.lbl_mode_title.configure(bg=th["bg_card"], fg=th["fg_main"])
        self.lbl_mode_detail.configure(bg=th["bg_card"], fg=th["fg_muted"])

        self.lbl_adv_title.configure(bg=th["bg_card"], fg=th["fg_main"])
        self.lbl_adv_toggle.configure(bg=th["bg_card"], fg=th["accent"])

        for lbl in self.adv_labels.values():
            lbl.configure(bg=th["bg_card"], fg=th["fg_muted"])

        for cb in self.adv_checkboxes.values():
            cb.configure(
                bg=th["bg_card"],
                fg=th["fg_main"],
                disabledforeground=th["fg_disabled"],
                selectcolor=th["bg_input"],
                activebackground=th["bg_card"],
                activeforeground=th["fg_main"],
            )

        for ent in (self.ent_extra, self.ent_rec_path):
            ent.configure(
                bg=th["bg_input"],
                fg=th["fg_main"],
                disabledbackground=th["bg_card"],
                disabledforeground=th["fg_disabled"],
                insertbackground=th["fg_main"],
                highlightbackground=th["input_border"],
            )

        self.btn_browse_rec.configure(
            bg=th["preset_idle_bg"],
            fg=th["fg_main"],
            activebackground=th["border"],
            activeforeground=th["fg_main"],
        )

        self.ent_preview.configure(
            readonlybackground=th["bg_cmd"],
            fg=th["fg_main"],
        )

        self.btn_copy_cmd.configure(
            bg=th["preset_idle_bg"],
            fg=th["fg_main"],
            activebackground=th["border"],
            activeforeground=th["fg_main"],
        )

        self.cb_autoclose.configure(
            bg=th["bg_card"],
            fg=th["fg_muted"],
            selectcolor=th["bg_input"],
            activebackground=th["bg_card"],
            activeforeground=th["fg_main"],
        )

        self.style.configure(
            "TCombobox",
            fieldbackground=th["bg_input"],
            background=th["bg_card"],
            foreground=th["fg_main"],
            arrowcolor=th["fg_main"],
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", th["bg_input"]), ("disabled", th["bg_card"])],
            selectbackground=[("readonly", th["bg_input"])],
            selectforeground=[("readonly", th["fg_main"])],
            foreground=[("disabled", th["fg_disabled"])],
        )

        self.style_dep_card()
        self.style_preset_buttons()
        self.style_adv_tabs()

    def _style_lang_buttons(self):
        th = THEMES[self.theme_name]
        if self.lang == "en":
            self.btn_lang_en.configure(bg=th["accent"], fg=th["accent_fg"])
            self.btn_lang_id.configure(bg=th["bg_card"], fg=th["fg_muted"])
        else:
            self.btn_lang_id.configure(bg=th["accent"], fg=th["accent_fg"])
            self.btn_lang_en.configure(bg=th["bg_card"], fg=th["fg_muted"])

    def style_adv_tabs(self):
        th = THEMES[self.theme_name]
        for key, (cell, btn) in self.adv_tab_buttons.items():
            is_sel = key == self.active_adv_tab
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
        self.btn_adb_web.configure(text=self.t("official_adb"))

        self.lbl_dev_title.configure(text=self.t("target_device"))
        self.btn_wifi.configure(text=self.t("wireless_btn"))
        self.btn_refresh_dev.configure(text=self.t("refresh_btn"))

        self.lbl_mode_title.configure(text=self.t("operating_mode"))
        for key, (_, btn) in self.preset_buttons.items():
            btn.configure(text=self.t(f"p_{key}"))

        self.lbl_adv_title.configure(text=self.t("adv_title"))
        self.lbl_adv_toggle.configure(text=self.t("collapse") if self.adv_expanded else self.t("expand"))

        for t_key, (_, btn) in self.adv_tab_buttons.items():
            btn.configure(text=self.t(f"tab_{t_key}"))

        for l_key, lbl in self.adv_labels.items():
            lbl.configure(text=self.t(l_key))

        for c_key, cb in self.adv_checkboxes.items():
            cb.configure(text=self.t(c_key))

        self.btn_browse_rec.configure(text=self.t("btn_browse_rec"))
        self.btn_copy_cmd.configure(text=self.t("copy_btn"))
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
        self.var_bitrate.set(state.get("bitrate", "Default"))
        self.var_codec.set(state.get("codec", "h265"))
        self.var_orientation.set(state.get("orientation", "Default"))
        self.var_camera_facing.set(state.get("camera_facing", "Default"))
        self.var_flex_display.set(state.get("flex_display", False))
        self.var_record.set(state.get("record", False))

        self.var_audio_source.set(state.get("audio_source", "output"))
        self.var_audio_codec.set(state.get("audio_codec", "opus"))
        self.var_no_audio.set(state.get("no_audio", False))
        self.var_audio_dup.set(state.get("audio_dup", False))
        self.var_kb_mode.set(state.get("kb_mode", "sdk"))
        self.var_mouse_mode.set(state.get("mouse_mode", "sdk"))
        self.var_gamepad_mode.set(state.get("gamepad_mode", "disabled"))
        self.var_no_control.set(state.get("no_control", False))

        self.var_screen_off.set(state.get("screen_off", False))
        self.var_stay_awake.set(state.get("stay_awake", True))
        self.var_power_off_close.set(state.get("power_off_close", False))
        self.var_show_touches.set(state.get("show_touches", False))
        self.var_always_on_top.set(state.get("always_on_top", False))
        self.var_fullscreen.set(state.get("fullscreen", False))
        self.var_borderless.set(state.get("borderless", False))
        self.var_no_screensaver.set(state.get("no_screensaver", False))
        self._suppress_trace = False

        self.update_contextual_widget_states()
        self.style_preset_buttons()
        self.update_mode_summary_and_preview()
        self.save_config()

    def get_current_form_state(self) -> dict:
        return {
            "source": self.var_source.get(),
            "max_size": self.var_max_size.get(),
            "fps": self.var_fps.get(),
            "bitrate": self.var_bitrate.get(),
            "codec": self.var_codec.get(),
            "orientation": self.var_orientation.get(),
            "camera_facing": self.var_camera_facing.get(),
            "flex_display": self.var_flex_display.get(),
            "record": self.var_record.get(),
            "audio_source": self.var_audio_source.get(),
            "audio_codec": self.var_audio_codec.get(),
            "no_audio": self.var_no_audio.get(),
            "audio_dup": self.var_audio_dup.get(),
            "kb_mode": self.var_kb_mode.get(),
            "mouse_mode": self.var_mouse_mode.get(),
            "gamepad_mode": self.var_gamepad_mode.get(),
            "no_control": self.var_no_control.get(),
            "screen_off": self.var_screen_off.get(),
            "stay_awake": self.var_stay_awake.get(),
            "power_off_close": self.var_power_off_close.get(),
            "show_touches": self.var_show_touches.get(),
            "always_on_top": self.var_always_on_top.get(),
            "fullscreen": self.var_fullscreen.get(),
            "borderless": self.var_borderless.get(),
            "no_screensaver": self.var_no_screensaver.get(),
        }

    def on_manual_setting_changed(self):
        if self._suppress_trace:
            return
        self.update_contextual_widget_states()
        curr = self.get_current_form_state()
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
            parts.append("Flex Display" if st["flex_display"] else "Virtual 1080p")
        elif src == "camera":
            face = st["camera_facing"]
            parts.append(f"Cam ({face})" if face != "Default" else "Camera")
        else:
            parts.append("Native" if st["max_size"] == "0" else f"{st['max_size']}p")

        parts.append(f"{st['fps']}fps")
        if st["bitrate"] != "Default":
            parts.append(st["bitrate"])
        parts.append(st["codec"].upper())
        if st["screen_off"] and src == "display":
            parts.append("Screen Off")
        if st["kb_mode"] != "sdk" or st["gamepad_mode"] != "disabled":
            parts.append("HID/Gamepad")
        return " • ".join(parts)

    # -------------------------------------------------------------------------
    # Binary Detection (scrcpy & adb)
    # -------------------------------------------------------------------------
    def find_binary(self, name: str):
        exe_name = f"{name}.exe" if IS_WINDOWS else name

        if self.custom_bin_dir and os.path.isdir(self.custom_bin_dir):
            cand = os.path.join(self.custom_bin_dir, exe_name)
            if os.path.isfile(cand):
                return cand

        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        cand = os.path.join(script_dir, exe_name)
        if os.path.isfile(cand):
            return cand

        parent_dir = os.path.dirname(script_dir)
        cand = os.path.join(parent_dir, exe_name)
        if os.path.isfile(cand):
            return cand

        found = shutil.which(name)
        if found:
            return found

        if IS_WINDOWS:
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            user_profile = os.environ.get("USERPROFILE", "")
            program_data = os.environ.get("ProgramData", "")
            search_roots = [
                PORTABLE_INSTALL_DIR,
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
                if root_dir == PORTABLE_INSTALL_DIR or root_dir.endswith("Packages"):
                    try:
                        for dirpath, _, filenames in os.walk(root_dir):
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
        self.btn_adb_web.configure(bg=th["bg_card"], fg=th["fg_main"], activebackground=th["border"])

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

    def has_winget(self) -> bool:
        if not IS_WINDOWS:
            return False
        if shutil.which("winget"):
            return True
        win_apps_winget = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "winget.exe")
        return os.path.isfile(win_apps_winget)

    def get_os_install_button_label(self) -> str:
        if IS_WINDOWS:
            return self.t("install_winget") if self.has_winget() else self.t("install_ps_github")
        elif IS_MAC:
            return self.t("install_brew")
        return self.t("install_linux")

    def run_official_package_install(self):
        if IS_WINDOWS:
            if self.has_winget():
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
            else:
                confirm = messagebox.askyesno(
                    self.t("ps_confirm_title"),
                    self.t("ps_confirm_msg").format(dest=PORTABLE_INSTALL_DIR),
                )
                if confirm:
                    ps_script = (
                        "$ErrorActionPreference = 'Stop'; "
                        "Write-Host '=== Official Genymobile/scrcpy Release Installer ===' -ForegroundColor Cyan; "
                        "Write-Host 'Fetching latest release metadata from GitHub API...'; "
                        "$rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/Genymobile/scrcpy/releases/latest'; "
                        "$asset = $rel.assets | Where-Object { $_.name -match 'scrcpy-win64-.*\\.zip$' } | Select-Object -First 1; "
                        "if (-not $asset) { throw 'Could not find win64 zip asset in latest release.' }; "
                        "$zipPath = Join-Path $env:TEMP $asset.name; "
                        "Write-Host ('Downloading ' + $asset.name + ' from ' + $asset.browser_download_url + '...') -ForegroundColor Yellow; "
                        "Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipPath; "
                        f"$dest = '{PORTABLE_INSTALL_DIR}'; "
                        "if (-not (Test-Path $dest)) { New-Item -ItemType Directory -Path $dest | Out-Null }; "
                        "Write-Host ('Extracting to ' + $dest + '...') -ForegroundColor Yellow; "
                        "Expand-Archive -Path $zipPath -DestinationPath $dest -Force; "
                        "Remove-Item $zipPath -Force -ErrorAction SilentlyContinue; "
                        "Write-Host ''; "
                        "Write-Host 'SUCCESS! Official scrcpy and adb installed.' -ForegroundColor Green; "
                        "Write-Host 'Click [Re-check] in scrcpy-cpl to start mirroring!' -ForegroundColor Green;"
                    )
                    subprocess.Popen(
                        ["powershell.exe", "-NoExit", "-Command", ps_script],
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

        # 1. Video & Display Options
        if source == "new-display":
            if self.var_flex_display.get():
                cmd.extend(["--new-display", "-x"])
            else:
                cmd.append("--new-display=1920x1080")
        elif source == "camera":
            cmd.append("--video-source=camera")
            cam_face = self.var_camera_facing.get()
            if cam_face != "Default":
                cmd.append(f"--camera-facing={cam_face}")

        codec = self.var_codec.get()
        if codec and codec != "h264":
            cmd.append(f"--video-codec={codec}")

        size_val = self.var_max_size.get().strip()
        if size_val.isdigit() and size_val != "0" and not (source == "new-display" and self.var_flex_display.get()):
            if source == "camera":
                cmd.append(f"--camera-size={size_val}x1080")
            else:
                cmd.append(f"-m{size_val}")

        fps = self.var_fps.get().strip()
        if fps.isdigit():
            cmd.append(f"--max-fps={fps}")

        bitrate = self.var_bitrate.get().strip()
        if bitrate and bitrate != "Default":
            cmd.append(f"-b{bitrate}")

        orient = self.var_orientation.get().strip()
        if orient and orient != "Default":
            cmd.append(f"--capture-orientation={orient}")

        if self.var_record.get():
            rec_file = self.var_record_path.get().strip() or "scrcpy_capture.mp4"
            cmd.append(f"--record={rec_file}")

        # 2. Audio & Input Options
        if self.var_no_audio.get():
            cmd.append("--no-audio")
        else:
            if self.var_audio_dup.get():
                cmd.append("--audio-dup")
            else:
                aud_src = self.var_audio_source.get()
                if aud_src and aud_src != "output":
                    cmd.append(f"--audio-source={aud_src}")

            aud_codec = self.var_audio_codec.get()
            if aud_codec and aud_codec != "opus":
                cmd.append(f"--audio-codec={aud_codec}")

        if self.var_no_control.get():
            cmd.append("-n")
        else:
            kb = self.var_kb_mode.get()
            if kb == "uhid":
                cmd.append("-K")
            elif kb and kb != "sdk":
                cmd.append(f"--keyboard={kb}")

            mouse = self.var_mouse_mode.get()
            if mouse == "uhid":
                cmd.append("-M")
            elif mouse and mouse != "sdk":
                cmd.append(f"--mouse={mouse}")

            gp = self.var_gamepad_mode.get()
            if gp == "uhid":
                cmd.append("-G")
            elif gp and gp != "disabled":
                cmd.append(f"--gamepad={gp}")

        # 3. Device & Window Options
        if self.var_screen_off.get() and source == "display":
            cmd.append("-S")
        if self.var_stay_awake.get() and source == "display":
            cmd.append("-w")
        if self.var_power_off_close.get() and source == "display":
            cmd.append("--power-off-on-close")
        if self.var_show_touches.get() and source == "display":
            cmd.append("-t")
        if self.var_always_on_top.get():
            cmd.append("--always-on-top")
        if self.var_fullscreen.get():
            cmd.append("-f")
        if self.var_borderless.get():
            cmd.append("--window-borderless")
        if self.var_no_screensaver.get():
            cmd.append("--disable-screensaver")

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
            log_file = os.path.join(tempfile.gettempdir(), "scrcpy_cpl_last.log")
            log_fh = open(log_file, "w+", encoding="utf-8", errors="replace")

            kwargs = {
                "env": env,
                "stdin": subprocess.DEVNULL,
                "stdout": log_fh,
                "stderr": subprocess.STDOUT,
            }
            if IS_WINDOWS:
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                kwargs["start_new_session"] = True

            proc = subprocess.Popen(args, **kwargs)

            # Wait ~0.75s to catch immediate startup errors (e.g. no device connected, unauthorized ADB)
            time.sleep(0.75)
            ret = proc.poll()
            log_fh.close()

            if ret is not None and ret != 0:
                err_text = ""
                try:
                    with open(log_file, "r", encoding="utf-8", errors="replace") as rf:
                        err_text = rf.read().strip()
                except Exception:
                    pass
                messagebox.showerror(
                    self.t("launch_err_title"),
                    self.t("launch_err_prefix") + (err_text or f"Exit code {ret}"),
                )
                return

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
