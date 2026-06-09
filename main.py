#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOM管理系统 - 主入口
功能：成品信息管理、成品BOM查询、系统设置
V1.0.0 基于采购助手架构构建
"""

import sys
import os
import traceback
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
import ctypes

from version import __version__, __version_date__, check_for_updates_async

DEFAULT_DATA_DIR = os.path.join(os.path.expanduser("~"), "BOM管理系统数据")

LOG_FILE = ""


def _log_exception(exc_type, exc_value, exc_tb):
    if not LOG_FILE:
        return
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.writelines(tb_lines)
        f.write("\n")

sys.excepthook = _log_exception

try:
    import customtkinter as ctk
except ImportError:
    messagebox.showerror("依赖缺失", "请先安装 customtkinter：pip install customtkinter")
    sys.exit(1)

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from database import Database
from pages.product_info_page import ProductInfoPage
from pages.product_bom_page import ProductBomPage
from pages.settings_page import SettingsPage, load_settings

try:
    import pystray
    from PIL import Image as PILImage
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False

settings = load_settings()
_data_dir = settings.get("data_dir", "")
if not _data_dir:
    _data_dir = DEFAULT_DATA_DIR
os.makedirs(_data_dir, exist_ok=True)
LOG_FILE = os.path.join(_data_dir, "error.log")

ctk.set_appearance_mode(settings.get("appearance_mode", "light"))
ctk.set_default_color_theme("blue")

# ── 莫兰迪暖色调色板 ──────────────────────────
COLORS = {
    "primary":         "#C1816D",
    "primary_hover":   "#A86B58",
    "primary_light":   "#FDF2EE",
    "success":         "#8FA882",
    "warning":         "#C9A96E",
    "danger":          "#B56A6A",
    "bg":              "#F5F0EB",
    "card":            "#FFFAF5",
    "sidebar":         "#F0EBE3",
    "sidebar_text":    "#5D4E37",
    "sidebar_active":  "#E8D5C4",
    "sidebar_active_text": "#8B5E3C",
    "sidebar_hover":   "#E8DDD0",
    "text":            "#4A3728",
    "text_secondary":  "#8B7355",
    "border":          "#D4C5B2",
    "divider":         "#E8DDD0",
}


def _get_resource_path(rel_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)


ICO_PATH  = _get_resource_path("assets/同仁堂企业LOGO.ico")
LOGO_PATH = _get_resource_path("assets/同仁堂企业LOGO.png")

NAV_ICON_PATHS = {
    "product_info": _get_resource_path("assets/nav_product_info.png"),
    "product_bom":  _get_resource_path("assets/nav_product_bom.png"),
    "settings":     _get_resource_path("assets/nav_settings.png"),
}


def _add_tooltip(widget, text):
    tip = None

    def _enter(event):
        nonlocal tip
        if tip:
            return
        x = widget.winfo_rootx() + widget.winfo_width() // 2
        y = widget.winfo_rooty() + widget.winfo_height() + 2
        tip = tk.Toplevel(widget)
        tip.wm_overrideredirect(True)
        tip.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            tip, text=text,
            background="#FFFFCC", foreground="#333333",
            font=("Microsoft YaHei", 10),
            relief="solid", borderwidth=1, padx=6, pady=2,
        )
        label.pack()

    def _leave(event):
        nonlocal tip
        if tip:
            tip.destroy()
            tip = None

    widget.bind("<Enter>", _enter, add="+")
    widget.bind("<Leave>", _leave, add="+")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BOM管理系统")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg"])

        if os.path.exists(ICO_PATH):
            try:
                self.iconbitmap(ICO_PATH)
            except Exception:
                pass

        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        self.geometry(f"1280x800+{(w-1280)//2}+{(h-800)//2}")

        self.db = Database(_data_dir)
        self.current_page = None

        self._tray_enabled = settings.get("tray_enabled", "0") == "1"
        self._tray_icon = None
        self._tray_thread = None

        self._build_ui()
        self._switch_page("product_info")

        if PYSTRAY_AVAILABLE:
            self._start_tray()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(800, self._check_version_updates)

    def _check_version_updates(self):
        def on_checked(result):
            if not result["has_update"]:
                return
            self.after(0, lambda: self._show_update_dialog(result))

        check_for_updates_async(on_checked)

    def _show_update_dialog(self, result):
        current = result["current_version"]
        latest = result["latest_version"]
        notes = result.get("release_notes", "")
        url = result.get("download_url", "")

        notes_short = notes[:500] + "..." if len(notes) > 500 else notes

        dialog = tk.Toplevel(self)
        dialog.title("发现新版本")
        dialog.geometry("520x420")
        dialog.resizable(False, False)
        dialog.configure(bg="#FFFAF5")
        dialog.transient(self)
        dialog.grab_set()

        dialog.update_idletasks()
        dw, dh = 520, 420
        sw = dialog.winfo_screenwidth()
        sh = dialog.winfo_screenheight()
        dialog.geometry(f"{dw}x{dh}+{(sw-dw)//2}+{(sh-dh)//2}")

        header = tk.Frame(dialog, bg="#C1816D", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="🎉  发现新版本！",
            font=("Microsoft YaHei", 18, "bold"),
            fg="white", bg="#C1816D",
        ).pack(pady=(14, 0))

        tk.Label(
            header, text=f"BOM管理系统 V{latest} 已发布",
            font=("Microsoft YaHei", 11),
            fg="#FFFAF5", bg="#C1816D",
        ).pack()

        content = tk.Frame(dialog, bg="#FFFAF5", padx=24, pady=16)
        content.pack(fill="both", expand=True)

        ver_frame = tk.Frame(content, bg="#FFFAF5")
        ver_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            ver_frame, text=f"当前版本：V{current}",
            font=("Microsoft YaHei", 12),
            fg="#8B7355", bg="#FFFAF5",
        ).pack(side="left")

        tk.Label(
            ver_frame, text="→",
            font=("Microsoft YaHei", 12, "bold"),
            fg="#C1816D", bg="#FFFAF5",
        ).pack(side="left", padx=12)

        tk.Label(
            ver_frame, text=f"最新版本：V{latest}",
            font=("Microsoft YaHei", 12, "bold"),
            fg="#4A3728", bg="#FFFAF5",
        ).pack(side="left")

        if notes_short.strip():
            tk.Label(
                content, text="更新内容：",
                font=("Microsoft YaHei", 11, "bold"),
                fg="#4A3728", bg="#FFFAF5",
                anchor="w",
            ).pack(fill="x", pady=(8, 4))

            notes_text = tk.Text(
                content, height=7, width=54,
                font=("Microsoft YaHei", 10),
                fg="#4A3728", bg="#FDF2EE",
                relief="flat", borderwidth=0,
                padx=10, pady=8, wrap="word",
            )
            notes_text.insert("1.0", notes_short)
            notes_text.configure(state="disabled")
            notes_text.pack(fill="x")

        btn_frame = tk.Frame(dialog, bg="#FFFAF5", padx=24, pady=16)
        btn_frame.pack(fill="x")

        def go_download():
            if url:
                webbrowser.open(url)
            dialog.destroy()

        def remind_later():
            dialog.destroy()

        download_btn = tk.Button(
            btn_frame, text="前往下载",
            font=("Microsoft YaHei", 12, "bold"),
            bg="#C1816D", fg="white",
            activebackground="#A86B58", activeforeground="white",
            relief="flat", padx=32, pady=10,
            cursor="hand2",
            command=go_download,
        )
        download_btn.pack(side="right", padx=(10, 0))

        later_btn = tk.Button(
            btn_frame, text="暂不更新",
            font=("Microsoft YaHei", 12),
            bg="#F0EBE3", fg="#5D4E37",
            activebackground="#E8DDD0", activeforeground="#5D4E37",
            relief="flat", padx=24, pady=10,
            cursor="hand2",
            command=remind_later,
        )
        later_btn.pack(side="right")

    def _build_ui(self):
        # ── 侧边栏 ──────────────────────────────────────
        self.sidebar = ctk.CTkFrame(
            self, width=90, fg_color=COLORS["sidebar"],
            corner_radius=0, border_width=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.divider = tk.Frame(self, bg=COLORS["border"], width=1)
        self.divider.pack(side="left", fill="y")

        self._nav_icon_images = {}
        if PIL_AVAILABLE:
            for key, path in NAV_ICON_PATHS.items():
                if os.path.exists(path):
                    try:
                        img = Image.open(path)
                        self._nav_icon_images[key] = ctk.CTkImage(
                            light_image=img, size=(28, 28))
                    except Exception:
                        self._nav_icon_images[key] = None
                else:
                    self._nav_icon_images[key] = None

        self.nav_area = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_area.pack(side="top", fill="both", expand=True)

        nav_items = [
            ("product_info", "成品信息"),
            ("product_bom",  "成品BOM"),
        ]
        self.nav_buttons = {}
        for key, label in nav_items:
            icon = self._nav_icon_images.get(key)
            btn = ctk.CTkButton(
                self.nav_area,
                text=label,
                image=icon,
                compound="top",
                font=ctk.CTkFont(family="Microsoft YaHei", size=12),
                fg_color="transparent",
                text_color=COLORS["sidebar_text"],
                hover_color=COLORS["sidebar_hover"],
                anchor="center",
                height=58,
                corner_radius=6,
                command=lambda k=key: self._switch_page(k),
            )
            btn.pack(fill="x", padx=8, pady=1, expand=True)
            self.nav_buttons[key] = btn

        # 设置按钮（放在导航区最后）
        settings_icon = self._nav_icon_images.get("settings")
        self.settings_btn = ctk.CTkButton(
            self.nav_area,
            text="设置",
            image=settings_icon,
            compound="top",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            fg_color="transparent",
            text_color=COLORS["sidebar_text"],
            hover_color=COLORS["sidebar_hover"],
            anchor="center",
            height=58,
            corner_radius=6,
            command=self._open_settings,
        )
        self.settings_btn.pack(fill="x", padx=8, pady=1, expand=True)

        # ── 主内容区域 ──
        self.main_area = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.main_area.pack(side="left", fill="both", expand=True)

    def _switch_page(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=COLORS["sidebar_active"],
                    text_color=COLORS["sidebar_active_text"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["sidebar_text"],
                )
        self.settings_btn.configure(fg_color="transparent", text_color=COLORS["sidebar_text"])

        for widget in self.main_area.winfo_children():
            widget.destroy()

        if key == "product_info":
            self.current_page = ProductInfoPage(self.main_area, self.db, COLORS)
        elif key == "product_bom":
            self.current_page = ProductBomPage(self.main_area, self.db, COLORS)
        elif key == "settings":
            self.current_page = SettingsPage(self.main_area, self.db, COLORS)

        if self.current_page:
            self.current_page.pack(fill="both", expand=True)

    def _open_settings(self):
        self._switch_page("settings")
        for k, btn in self.nav_buttons.items():
            btn.configure(fg_color="transparent", text_color=COLORS["sidebar_text"])
        self.settings_btn.configure(
            fg_color=COLORS["sidebar_active"],
            text_color=COLORS["sidebar_active_text"],
        )

    def _on_closing(self):
        self.withdraw()

    def _start_tray(self):
        if self._tray_icon is not None:
            return
        self._tray_thread = threading.Thread(target=self._run_tray, daemon=True)
        self._tray_thread.start()

    def _run_tray(self):
        try:
            if os.path.exists(ICO_PATH):
                img = PILImage.open(ICO_PATH)
                img = img.resize((64, 64), PILImage.LANCZOS)
            else:
                img = PILImage.new("RGBA", (64, 64), (193, 129, 109, 255))

            menu = pystray.Menu(
                pystray.MenuItem(
                    "显示窗口",
                    self._on_tray_restore,
                    default=True,
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    "退出应用",
                    self._on_tray_quit,
                ),
            )

            self._tray_icon = pystray.Icon(
                "BOM管理系统",
                img,
                f"BOM管理系统 V{__version__}",
                menu,
            )
            self._tray_icon.run()
        except Exception:
            self.after(0, self._do_restore)

    def _on_tray_restore(self, icon=None, item=None):
        self.after(0, self._do_restore)

    def _on_tray_quit(self, icon=None, item=None):
        if self._tray_icon:
            self._tray_icon.stop()
            self._tray_icon = None
        self.after(0, self._quit_app)

    def _do_restore(self):
        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

    def _quit_app(self):
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
            self._tray_icon = None

        try:
            self.db.close()
        except Exception:
            pass

        self.destroy()
        try:
            sys.exit(0)
        except SystemExit:
            pass


if __name__ == "__main__":
    MUTEX_NAME = "Global\\BOM管理系统Mutex_EastSeaO_2026"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
    last_error = ctypes.windll.kernel32.GetLastError()
    if last_error == 183:
        ctypes.windll.user32.MessageBoxW(
            None,
            "BOM管理系统已经在运行中，不能同时启动多个实例。",
            "提示",
            0x40 | 0x0
        )
        sys.exit(0)

    app = App()
    app.mainloop()

    ctypes.windll.kernel32.ReleaseMutex(mutex)
    ctypes.windll.kernel32.CloseHandle(mutex)
