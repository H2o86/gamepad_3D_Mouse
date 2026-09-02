import json
import os
import sys
import threading
import time
import ctypes
from ctypes import c_long, c_ulong, Structure, byref, POINTER, c_int, c_uint
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image
import pystray

from inputs_manager import UnifiedControllerManager
from solidworks_mouse import SolidWorksNavigator, get_foreground_window_info

# Windows API for Global Hotkey (Ctrl+Alt+S)
user32 = ctypes.windll.user32
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
VK_S = 0x53  # 'S' key
HOTKEY_ID = 101


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(get_base_dir(), relative_path)


CONFIG_PATH = os.path.join(get_base_dir(), "config.json")
PRESETS_PATH = get_resource_path("sw_shortcuts.json")
LANG_PATH = get_resource_path("lang.json")
ICON_ICO_PATH = get_resource_path(os.path.join("assets", "icon.ico"))
ICON_PNG_PATH = get_resource_path(os.path.join("assets", "icon.png"))

BUTTON_DEFS_XBOX = [
    ("button_dpad_up", "D-Pad Up"),
    ("button_dpad_down", "D-Pad Down"),
    ("button_dpad_left", "D-Pad Left"),
    ("button_dpad_right", "D-Pad Right"),
    ("button_a", "Button A"),
    ("button_b", "Button B"),
    ("button_x", "Button X"),
    ("button_y", "Button Y"),
    ("button_lb", "Button LB"),
    ("button_rb", "Button RB"),
    ("button_l3", "Button L3 (Left Stick Click)"),
    ("button_r3", "Button R3 (Right Stick Click)"),
    ("button_start", "Button Start"),
    ("button_back", "Button Back / Select"),
]

BUTTON_DEFS_PS = [
    ("button_dpad_up", "D-Pad Up"),
    ("button_dpad_down", "D-Pad Down"),
    ("button_dpad_left", "D-Pad Left"),
    ("button_dpad_right", "D-Pad Right"),
    ("button_a", "Button ❌ (Cross)"),
    ("button_b", "Button ⭕ (Circle)"),
    ("button_x", "Button 🟦 (Square)"),
    ("button_y", "Button 🔺 (Triangle)"),
    ("button_lb", "Button L1"),
    ("button_rb", "Button R1"),
    ("button_l3", "Button L3 (Left Stick Click)"),
    ("button_r3", "Button R3 (Right Stick Click)"),
    ("button_start", "Button Options"),
    ("button_back", "Button Share / Create"),
]

DEFAULT_CONFIG = {
    "device_mode": "auto",
    "language": "en",
    "sensitivity": {"pan": 12.0, "rotate": 10.0, "zoom": 15.0, "roll": 8.0, "gyro": 15.0, "precision_multiplier": 0.3},
    "deadzone": {"left_stick": 0.15, "right_stick": 0.15, "trigger": 0.05},
    "curve": {"exponent": 1.8},
    "polling": {"rate_hz": 120},
    "app_filter": {
        "target_app_only": True,
        "target_keywords": ["SOLIDWORKS", "SLDWORKS.EXE"],
        "lock_cursor_center": True,
    },
    "keymap": {
        "button_dpad_up": "Ctrl+7",
        "button_dpad_down": "Ctrl+8",
        "button_dpad_left": "F",
        "button_dpad_right": "Ctrl+1",
        "button_a": "ESC",
        "button_b": "Ctrl+B",
        "button_x": "D",
        "button_y": "Space",
        "button_lb": "roll_left",
        "button_rb": "roll_right",
        "button_l3": "precision_toggle",
        "button_r3": "pause_toggle",
        "button_start": "S",
        "button_back": "Ctrl+Z",
    },
}

GUIDE_TEXTS = {
    "en": """=== SOLIDMOUSE - 3D SPACEMOUSE FOR SOLIDWORKS ===

1. SYSTEM TRAY & GLOBAL HOTKEY (Ctrl+Alt+S)
--------------------------------------------------
- SolidMouse can run silently in your System Tray (Taskbar notification area).
- Press [Ctrl + Alt + S] anywhere in Windows to toggle showing or hiding the SolidMouse control window!
- Clicking the 'X' button hides the window to the System Tray without stopping 3D navigation.
- Right-click the SolidMouse Tray Icon for quick actions: Open GUI, Pause/Resume, Switch Language, or Exit.

2. OVERVIEW & FEATURES
--------------------------------------------------
SolidMouse converts standard gamepads (Flydigi Dune Fox, Xbox, PS4/PS5) into a dedicated 3D SpaceMouse for SolidWorks.
- Native Low-Latency Control (~1ms XInput API response).
- Seamless Edge Border Wrapping: 100% continuous 3D rotation without cursor border collisions or resets.
- SOLIDWORKS Window Focus Filtering: Automatically suspends control when switching to other apps.
- 6-Axis Gyroscope Navigation: Tilt your PS4/PS5 controller to rotate models physically in 3D space!

3. DEFAULT CONTROL MAPPING
--------------------------------------------------
- Left Analog Stick  : Pan View (Ctrl + Middle Mouse Drag)
- Right Analog Stick : Rotate View 3D (Middle Mouse Drag)
- LT / RT (L2 / R2)  : Zoom Out / Zoom In (Shift + Middle Mouse Drag)
- LB / RB (L1 / R1)  : Roll View Left / Right (Alt + Middle Mouse Drag)
- D-Pad Up           : Isometric View (Ctrl + 7)
- D-Pad Down         : Normal To View (Ctrl + 8)
- D-Pad Left         : Zoom to Fit (F Key)
- D-Pad Right        : Front View (Ctrl + 1)
- Button A / ❌      : Escape (ESC)
- Button B / ⭕      : Rebuild Model (Ctrl + B)
- Button X / 🟦      : Smart Dimension (D Key)
- Button Y / 🔺      : View Orientation Dialog (Spacebar)
- Click L3 Stick     : Toggle Precision Mode (30% Speed for micro-details)
- Click R3 Stick     : Pause / Resume 3D Mouse Control

4. HOW TO CONNECT CONTROLLERS
--------------------------------------------------
- Flydigi Dune Fox / Xbox: Connect via 2.4G USB Dongle or USB Cable (XInput Mode).
- PlayStation PS4 / PS5  : Connect via Bluetooth or USB Cable (DirectInput + Gyro Mode).

5. CUSTOM KEY MAPPER
--------------------------------------------------
Go to '🎮 Key Mapper' tab to rebind any of the 14 buttons to preset SolidWorks 2019 shortcuts or custom hotkeys (e.g., Ctrl+Alt+S, F5, Shift+E).
""",
    "vi": """=== SOLIDMOUSE - TRUNG TÂM ĐIỀU KHIỂN 3D SPACEMOUSE SOLIDWORKS ===

1. CHẠY ẨN KHAY HỆ THỐNG & PHÍM TẮT NHAU (Ctrl+Alt+S)
--------------------------------------------------
- SolidMouse hỗ trợ chạy ẩn ngầm dưới Khay hệ thống (System Tray / Taskbar).
- Nhấn tổ hợp phím [Ctrl + Alt + S] ở bất kỳ đâu trong Windows để bật/tắt nhanh giao diện cài đặt!
- Khi nhấn nút 'X' đóng cửa sổ, phần mềm sẽ ẩn xuống Khay hệ thống mà không làm ngắt điều khiển 3D.
- Click chuột phải vào Icon dưới Taskbar để: Mở giao diện, Tạm dừng/Tiếp tục, Đổi ngôn ngữ, hoặc Thát hẳn.

2. TỔNG QUAN & TÍNH NĂNG
--------------------------------------------------
SolidMouse biến các loại tay cầm chơi game (Flydigi Dune Fox, Xbox, PS4/PS5) thành thiết bị 3D SpaceMouse chuyên dụng cho SolidWorks.
- Phản hồi siêu mượt (~1ms XInput Native API).
- Chống văng viền chuột liền mạch (Seamless Edge Wrapping): Xoay 360° vô tận không bị gián đoạn hay reset góc.
- Tự động lọc cửa sổ SolidWorks: Chỉ kích hoạt khi mở SolidWorks, tự ngắt khi chuyển sang app khác.
- Gyroscope 6DoF: Nghiêng tay cầm PS4/PS5 thực tế để xoay mô hình 3D trực quan trong không gian!

3. SƠ ĐỒ ĐIỀU KHIỂN MẶC ĐỊNH
--------------------------------------------------
- Cần gạt Trái (Left Stick)  : Pan View (Ctrl + Giữ Chuột Giữa)
- Cần gạt Phải (Right Stick) : Rotate View 3D (Giữ Chuột Giữa)
- Cò LT / RT (L2 / R2)       : Zoom Out / Zoom In (Shift + Giữ Chuột Giữa)
- Nút LB / RB (L1 / R1)      : Roll View Trái / Phải (Alt + Giữ Chuột Giữa)
- D-Pad Up                   : Isometric View (Ctrl + 7)
- D-Pad Down                 : Normal To View (Ctrl + 8)
- D-Pad Left                 : Zoom to Fit (Phím F)
- D-Pad Right                : Front View (Ctrl + 1)
- Nút A / ❌                 : Escape (Phím ESC)
- Nút B / ⭕                 : Rebuild Model (Ctrl + B)
- Nút X / 🟦                 : Smart Dimension (Phím D)
- Nút Y / 🔺                 : Mở bảng góc nhìn (Spacebar)
- Nhấn Cần L3                : Bật/Tắt Precision Mode (Giảm 70% tốc độ soi chi tiết nhỏ)
- Nhấn Cần R3                : Tạm dừng / Tiếp tục điều khiển

4. KẾT NỐI TAY CẦM
--------------------------------------------------
- Flydigi Dune Fox / Xbox: Cắm Dongle 2.4G USB hoặc Cáp USB (Chế độ XInput).
- PlayStation PS4 / PS5  : Kết nối Bluetooth hoặc Cáp USB (Chế độ DirectInput + Gyro).

5. GÁN PHÍM TÙY CHỈNH (KEY MAPPER)
--------------------------------------------------
Vào Tab '🎮 Gán Phím Chức Năng' để chọn nhanh phím tắt SolidWorks 2019 hoặc tự gõ tổ hợp phím bất kỳ (VD: Ctrl+Alt+S, F5, Shift+E) cho 14 nút bấm.
""",
    "ja": """=== SOLIDMOUSE - SOLIDWORKS用 3D SPACEMOUSE コントローラー ===

1. システムトレイ & グローバルショートカット (Ctrl+Alt+S)
--------------------------------------------------
- SolidMouseはシステムトレイ（タスクバー通知領域）で非表示実行が可能です。
- Windowsのどこからでも [Ctrl + Alt + S] を押すと、設定画面を即座に表示/非表示できます！
- ウィンドウの 'X' ボタンをクリックすると、3D操作を停止せずにシステムトレイに最小化されます。
""",
    "ko": """=== SOLIDMOUSE - SOLIDWORKS 3D SPACEMOUSE 컨트롤 센터 ===

1. 시스템 트레이 & 단축키 (Ctrl+Alt+S)
--------------------------------------------------
- SolidMouse는 시스템 트레이(작업 표시줄)에서 백그라운드로 실행할 수 있습니다.
- [Ctrl + Alt + S] 단축키를 누르면 언제든지 설정 창을 열거나 닫을 수 있습니다!
- 창의 'X' 버튼을 누르면 3D 제어가 중단되지 않고 트레이로 최소화됩니다.
""",
    "zh": """=== SOLIDMOUSE - SOLIDWORKS 专用 3D SPACEMOUSE 控制中心 ===

1. 系统托盘与全局快捷键 (Ctrl+Alt+S)
--------------------------------------------------
- SolidMouse 支持在系统托盘 (任务栏通知区) 静默后台运行。
- 在 Windows 任何位置按 [Ctrl + Alt + S] 即可快速显示或隐藏设置界面！
- 点击窗口的 'X' 关闭按钮会将窗口最小化到系统托盘，而不会中断 3D 导航。
""",
}


class ApplicationGUI(tk.Tk):
    """Unified Control Center for Flydigi Dune Fox, Xbox & PlayStation PS4/PS5 Controllers with System Tray & Global Hotkey."""

    def __init__(self, start_minimized=False):
        super().__init__()
        self.start_minimized_flag = start_minimized
        self.geometry("780x760")
        self.resizable(True, True)

        if os.path.exists(ICON_ICO_PATH):
            try:
                self.iconbitmap(ICON_ICO_PATH)
            except Exception:
                pass

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.config_data = self.load_config()
        self.lang_code = self.config_data.get("language", "en")
        self.lang_dict = self.load_lang()

        self.presets_data = self.load_presets()
        self.preset_options = self.build_preset_options()

        dev_mode = self.config_data.get("device_mode", "auto")
        self.controller_mgr = UnifiedControllerManager(mode=dev_mode)
        self.navigator = SolidWorksNavigator(self.config_data)

        self.entry_widgets = {}
        self.label_widgets = {}

        self.running = True
        self.service_thread = None
        self.hotkey_thread = None

        self.tray_icon = None
        self.tray_thread = None

        self.title(self.tr("title"))
        self.create_widgets()
        self.start_service()

        self.setup_system_tray()
        self.setup_global_hotkey()

        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

        if self.start_minimized_flag:
            self.withdraw()
            self.after(1000, self.notify_minimized)

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return json.loads(json.dumps(DEFAULT_CONFIG))

    def load_lang(self):
        if os.path.exists(LANG_PATH):
            try:
                with open(LANG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(self.lang_code, data.get("en", {}))
            except Exception:
                pass
        return {}

    def tr(self, key, default=""):
        return self.lang_dict.get(key, default or key)

    def load_presets(self):
        if os.path.exists(PRESETS_PATH):
            try:
                with open(PRESETS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"categories": {}}

    def build_preset_options(self):
        options = {}
        for cat_name, cat_dict in self.presets_data.get("categories", {}).items():
            for cmd_name, shortcut_str in cat_dict.items():
                label = f"{cmd_name} ({shortcut_str})"
                options[label] = shortcut_str
        return options

    # System Tray Implementation
    def setup_system_tray(self):
        try:
            if os.path.exists(ICON_PNG_PATH):
                image = Image.open(ICON_PNG_PATH)
            elif os.path.exists(ICON_ICO_PATH):
                image = Image.open(ICON_ICO_PATH)
            else:
                image = Image.new("RGB", (64, 64), color=(30, 144, 255))

            menu = pystray.Menu(
                pystray.MenuItem(self.tr("tray_show"), self.show_from_tray, default=True),
                pystray.MenuItem(
                    lambda item: self.tr("tray_resume") if self.navigator.paused else self.tr("tray_pause"),
                    self.toggle_pause_from_tray,
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("🌐 Language", pystray.Menu(
                    pystray.MenuItem("English (EN)", lambda: self.change_language("en")),
                    pystray.MenuItem("Tiếng Việt (VI)", lambda: self.change_language("vi")),
                    pystray.MenuItem("日本語 (JA)", lambda: self.change_language("ja")),
                    pystray.MenuItem("한국어 (KO)", lambda: self.change_language("ko")),
                    pystray.MenuItem("中文 (ZH)", lambda: self.change_language("zh")),
                )),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(self.tr("tray_exit"), self.exit_app_from_tray),
            )

            self.tray_icon = pystray.Icon("SolidMouse", image, "SolidMouse - 3D SpaceMouse (Ctrl+Alt+S)", menu)
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
        except Exception as e:
            print(f"[SolidMouse] System Tray Error: {e}")

    def notify_minimized(self):
        if self.tray_icon:
            try:
                self.tray_icon.notify(
                    self.tr("tray_minimized_msg"),
                    title=self.tr("tray_minimized_title"),
                )
            except Exception:
                pass

    def show_from_tray(self, icon=None, item=None):
        self.deiconify()
        self.lift()
        self.focus_force()

    def hide_to_tray(self):
        self.withdraw()

    def toggle_pause_from_tray(self, icon=None, item=None):
        self.navigator.paused = not self.navigator.paused

    def toggle_window_visibility(self):
        if self.state() == "normal":
            self.withdraw()
        else:
            self.show_from_tray()

    # Global Hotkey (Ctrl+Alt+S) Thread
    def setup_global_hotkey(self):
        def hotkey_loop():
            # Register Ctrl+Alt+S globally
            res = user32.RegisterHotKey(0, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_S)
            if not res:
                print("[SolidMouse] Could not register Ctrl+Alt+S hotkey (might be reserved).")

            class MSG(Structure):
                _fields_ = [
                    ("hwnd", c_ulong),
                    ("message", c_uint),
                    ("wParam", c_ulong),
                    ("lParam", c_long),
                    ("time", c_ulong),
                    ("pt_x", c_long),
                    ("pt_y", c_long),
                ]

            msg = MSG()
            while self.running:
                if user32.GetMessageW(byref(msg), 0, 0, 0) != 0:
                    if msg.message == 0x0312:  # WM_HOTKEY
                        if msg.wParam == HOTKEY_ID:
                            self.after(0, self.toggle_window_visibility)
                    user32.TranslateMessage(byref(msg))
                    user32.DispatchMessageW(byref(msg))
                time.sleep(0.01)

            user32.UnregisterHotKey(0, HOTKEY_ID)

        self.hotkey_thread = threading.Thread(target=hotkey_loop, daemon=True)
        self.hotkey_thread.start()

    def exit_app_from_tray(self, icon=None, item=None):
        self.running = False
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.after(0, self.on_close)

    def save_config(self):
        mode_str = self.combo_dev_mode.get()
        if "PlayStation" in mode_str:
            self.config_data["device_mode"] = "playstation"
        elif "Flydigi" in mode_str or "Xbox" in mode_str:
            self.config_data["device_mode"] = "xinput"
        else:
            self.config_data["device_mode"] = "auto"

        self.config_data["language"] = self.lang_code
        self.controller_mgr.set_mode(self.config_data["device_mode"])

        self.config_data["sensitivity"]["pan"] = round(self.slider_pan.get(), 1)
        self.config_data["sensitivity"]["rotate"] = round(self.slider_rotate.get(), 1)
        self.config_data["sensitivity"]["zoom"] = round(self.slider_zoom.get(), 1)
        self.config_data["sensitivity"]["gyro"] = round(self.slider_gyro.get(), 1)
        self.config_data["deadzone"]["left_stick"] = round(self.slider_deadzone.get(), 2)
        self.config_data["curve"]["exponent"] = round(self.slider_curve.get(), 2)

        self.config_data["app_filter"]["target_app_only"] = self.var_target_only.get()
        self.config_data["app_filter"]["lock_cursor_center"] = self.var_lock_cursor.get()

        keymap = {}
        for key_id, _ in BUTTON_DEFS_XBOX:
            val = self.entry_widgets[key_id].get().strip()
            keymap[key_id] = val

        self.config_data["keymap"] = keymap

        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4)
            self.navigator.update_config(self.config_data)
            messagebox.showinfo(self.tr("msg_save_success_title"), self.tr("msg_save_success"))
        except Exception as e:
            messagebox.showerror(self.tr("msg_save_error_title"), f"{self.tr('msg_save_error')}{e}")

    def reset_to_defaults(self):
        if messagebox.askyesno(self.tr("msg_reset_confirm_title"), self.tr("msg_reset_confirm")):
            self.config_data = json.loads(json.dumps(DEFAULT_CONFIG))
            self.config_data["language"] = self.lang_code

            self.combo_dev_mode.set("Auto Detect (Recommended)")
            self.controller_mgr.set_mode("auto")

            self.slider_pan.set(DEFAULT_CONFIG["sensitivity"]["pan"])
            self.slider_rotate.set(DEFAULT_CONFIG["sensitivity"]["rotate"])
            self.slider_zoom.set(DEFAULT_CONFIG["sensitivity"]["zoom"])
            self.slider_gyro.set(DEFAULT_CONFIG["sensitivity"]["gyro"])
            self.slider_deadzone.set(DEFAULT_CONFIG["deadzone"]["left_stick"])
            self.slider_curve.set(DEFAULT_CONFIG["curve"]["exponent"])

            self.var_target_only.set(DEFAULT_CONFIG["app_filter"]["target_app_only"])
            self.var_lock_cursor.set(DEFAULT_CONFIG["app_filter"]["lock_cursor_center"])

            def_keymap = DEFAULT_CONFIG["keymap"]
            for key_id, _ in BUTTON_DEFS_XBOX:
                if key_id in self.entry_widgets:
                    self.entry_widgets[key_id].set(def_keymap.get(key_id, ""))

            try:
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(self.config_data, f, indent=4)
                self.navigator.update_config(self.config_data)
                messagebox.showinfo(self.tr("msg_reset_success_title"), self.tr("msg_reset_success"))
            except Exception as e:
                messagebox.showerror(self.tr("msg_save_error_title"), f"{self.tr('msg_save_error')}{e}")

    def change_language(self, new_lang):
        self.lang_code = new_lang
        self.config_data["language"] = new_lang
        self.lang_dict = self.load_lang()

        lang_map = {"en": "English (EN)", "vi": "Tiếng Việt (VI)", "ja": "日本語 (JA)", "ko": "한국어 (KO)", "zh": "中文 (ZH)"}
        self.combo_lang.set(lang_map.get(new_lang, "English (EN)"))

        self.title(self.tr("title"))
        self.lbl_title.config(text=self.tr("title"))
        self.lbl_dev_mode.config(text=self.tr("device_profile"))
        self.lbl_info.config(text=self.tr("key_info"))

        self.btn_reset1.config(text=self.tr("btn_reset_defaults"))
        self.btn_save.config(text=self.tr("btn_save_keys"))

        self.frame_wf.config(text=self.tr("lbl_app_filter_group"))
        self.chk_target.config(text=self.tr("chk_target_app"))

        self.frame_cl.config(text=self.tr("lbl_cursor_group"))
        self.chk_lock.config(text=self.tr("chk_lock_cursor"))
        self.lbl_lock_info.config(text=self.tr("lbl_lock_info"))

        self.frame_sens.config(text=self.tr("lbl_sensitivity_group"))
        self.lbl_pan_spd.config(text=self.tr("lbl_pan_speed"))
        self.lbl_rot_spd.config(text=self.tr("lbl_rotate_speed"))
        self.lbl_zoom_spd.config(text=self.tr("lbl_zoom_speed"))
        self.lbl_gyro_spd.config(text=self.tr("lbl_gyro_speed"))
        self.lbl_deadzone.config(text=self.tr("lbl_deadzone"))
        self.lbl_curve.config(text=self.tr("lbl_curve"))

        self.btn_reset2.config(text=self.tr("btn_reset_defaults"))
        self.btn_save_opt.config(text=self.tr("btn_save_all"))

        self.notebook.tab(0, text=self.tr("tab_keys"))
        self.notebook.tab(1, text=self.tr("tab_options"))
        self.notebook.tab(2, text=self.tr("tab_guide"))
        self.notebook.tab(3, text=self.tr("tab_monitor"))

        self.txt_guide.config(state="normal")
        self.txt_guide.delete("1.0", tk.END)
        self.txt_guide.insert(tk.END, GUIDE_TEXTS.get(new_lang, GUIDE_TEXTS["en"]))
        self.txt_guide.config(state="disabled")

    def update_button_labels(self, is_playstation=False):
        defs = BUTTON_DEFS_PS if is_playstation else BUTTON_DEFS_XBOX
        for btn_id, btn_name in defs:
            if btn_id in self.label_widgets:
                self.label_widgets[btn_id].config(text=btn_name)

    def create_widgets(self):
        header = ttk.Frame(self, padding=12)
        header.pack(fill="x")

        self.lbl_title = ttk.Label(
            header,
            text=self.tr("title"),
            font=("Segoe UI", 13, "bold"),
        )
        self.lbl_title.pack(anchor="w")

        dev_frame = ttk.Frame(header, padding=(0, 5, 0, 0))
        dev_frame.pack(fill="x")

        self.lbl_dev_mode = ttk.Label(dev_frame, text=self.tr("device_profile"), font=("Segoe UI", 10, "bold"))
        self.lbl_dev_mode.pack(side="left")

        self.combo_dev_mode = ttk.Combobox(
            dev_frame,
            values=[
                "Auto Detect (Recommended)",
                "Xbox / Flydigi Dune Fox (XInput)",
                "PlayStation PS4 DualShock 4 / PS5 DualSense",
            ],
            state="readonly",
            width=36,
        )

        curr_mode = self.config_data.get("device_mode", "auto")
        if curr_mode == "playstation":
            self.combo_dev_mode.set("PlayStation PS4 DualShock 4 / PS5 DualSense")
        elif curr_mode == "xinput":
            self.combo_dev_mode.set("Xbox / Flydigi Dune Fox (XInput)")
        else:
            self.combo_dev_mode.set("Auto Detect (Recommended)")

        self.combo_dev_mode.pack(side="left", padx=5)

        ttk.Label(dev_frame, text="🌐 Language:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(10, 5))
        self.combo_lang = ttk.Combobox(
            dev_frame,
            values=["English (EN)", "Tiếng Việt (VI)", "日本語 (JA)", "한국어 (KO)", "中文 (ZH)"],
            state="readonly",
            width=15,
        )

        lang_map = {"en": "English (EN)", "vi": "Tiếng Việt (VI)", "ja": "日本語 (JA)", "ko": "한국어 (KO)", "zh": "中文 (ZH)"}
        self.combo_lang.set(lang_map.get(self.lang_code, "English (EN)"))
        self.combo_lang.pack(side="left")

        def on_lang_change(event):
            sel = self.combo_lang.get()
            if "English" in sel:
                new_lang = "en"
            elif "Tiếng Việt" in sel:
                new_lang = "vi"
            elif "日本語" in sel:
                new_lang = "ja"
            elif "한국어" in sel:
                new_lang = "ko"
            elif "中文" in sel:
                new_lang = "zh"
            else:
                new_lang = "en"
            self.change_language(new_lang)

        self.combo_lang.bind("<<ComboboxSelected>>", on_lang_change)

        def on_dev_mode_change(event):
            mode_str = self.combo_dev_mode.get()
            is_ps = "PlayStation" in mode_str
            self.update_button_labels(is_playstation=is_ps)

        self.combo_dev_mode.bind("<<ComboboxSelected>>", on_dev_mode_change)

        self.lbl_status = ttk.Label(
            header,
            text=self.tr("status_connecting"),
            font=("Segoe UI", 10),
            foreground="#D97706",
        )
        self.lbl_status.pack(anchor="w", pady=(5, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Tab 1: Keybindings
        tab_keys = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_keys, text=self.tr("tab_keys"))

        self.lbl_info = ttk.Label(
            tab_keys,
            text=self.tr("key_info"),
            font=("Segoe UI", 9, "italic"),
            wraplength=680,
        )
        self.lbl_info.pack(anchor="w", pady=(0, 10))

        canvas_container = ttk.Frame(tab_keys)
        canvas_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        current_keymap = self.config_data.get("keymap", {})
        preset_labels = list(self.preset_options.keys())

        for idx, (btn_id, btn_name) in enumerate(BUTTON_DEFS_XBOX):
            row_frame = ttk.Frame(scrollable_frame, padding=4)
            row_frame.pack(fill="x", expand=True, pady=2)

            lbl_btn = ttk.Label(row_frame, text=btn_name, width=24, font=("Segoe UI", 10, "bold"))
            lbl_btn.pack(side="left")
            self.label_widgets[btn_id] = lbl_btn

            init_val = current_keymap.get(btn_id, "")
            entry_var = tk.StringVar(value=init_val)

            combo = ttk.Combobox(row_frame, values=preset_labels, width=38, state="readonly")
            combo.set(self.tr("preset_placeholder"))
            combo.pack(side="left", padx=5)

            entry = ttk.Entry(row_frame, textvariable=entry_var, width=18, font=("Consolas", 10))
            entry.pack(side="left", padx=5)

            self.entry_widgets[btn_id] = entry_var

            def make_on_select(e_var, c_box):
                def on_select(event):
                    sel = c_box.get()
                    if sel in self.preset_options:
                        e_var.set(self.preset_options[sel])
                return on_select

            combo.bind("<<ComboboxSelected>>", make_on_select(entry_var, combo))

        btn_frame = ttk.Frame(tab_keys, padding=5)
        btn_frame.pack(fill="x", pady=5)

        self.btn_reset1 = ttk.Button(btn_frame, text=self.tr("btn_reset_defaults"), command=self.reset_to_defaults)
        self.btn_reset1.pack(side="left", padx=5)

        self.btn_save = ttk.Button(btn_frame, text=self.tr("btn_save_keys"), command=self.save_config)
        self.btn_save.pack(side="right", padx=5)

        # Tab 2: Settings
        tab_options = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab_options, text=self.tr("tab_options"))

        self.frame_wf = ttk.LabelFrame(tab_options, text=self.tr("lbl_app_filter_group"), padding=10)
        self.frame_wf.pack(fill="x", pady=(0, 10))

        self.var_target_only = tk.BooleanVar(value=self.config_data.get("app_filter", {}).get("target_app_only", True))
        self.chk_target = ttk.Checkbutton(
            self.frame_wf,
            text=self.tr("chk_target_app"),
            variable=self.var_target_only,
        )
        self.chk_target.pack(anchor="w", pady=2)

        self.frame_cl = ttk.LabelFrame(tab_options, text=self.tr("lbl_cursor_group"), padding=10)
        self.frame_cl.pack(fill="x", pady=(0, 10))

        self.var_lock_cursor = tk.BooleanVar(value=self.config_data.get("app_filter", {}).get("lock_cursor_center", True))
        self.chk_lock = ttk.Checkbutton(
            self.frame_cl,
            text=self.tr("chk_lock_cursor"),
            variable=self.var_lock_cursor,
        )
        self.chk_lock.pack(anchor="w", pady=2)

        self.lbl_lock_info = ttk.Label(
            self.frame_cl,
            text=self.tr("lbl_lock_info"),
            font=("Segoe UI", 9, "italic"),
            foreground="#2563EB",
        )
        self.lbl_lock_info.pack(anchor="w", pady=(5, 0))

        self.frame_sens = ttk.LabelFrame(tab_options, text=self.tr("lbl_sensitivity_group"), padding=10)
        self.frame_sens.pack(fill="both", expand=True)

        self.lbl_pan_spd = ttk.Label(self.frame_sens, text=self.tr("lbl_pan_speed"), font=("Segoe UI", 9, "bold"))
        self.lbl_pan_spd.pack(anchor="w")
        self.slider_pan = ttk.Scale(self.frame_sens, from_=2.0, to_=30.0, value=self.config_data["sensitivity"]["pan"])
        self.slider_pan.pack(fill="x", pady=(0, 4))

        self.lbl_rot_spd = ttk.Label(self.frame_sens, text=self.tr("lbl_rotate_speed"), font=("Segoe UI", 9, "bold"))
        self.lbl_rot_spd.pack(anchor="w")
        self.slider_rotate = ttk.Scale(self.frame_sens, from_=2.0, to_=30.0, value=self.config_data["sensitivity"]["rotate"])
        self.slider_rotate.pack(fill="x", pady=(0, 4))

        self.lbl_zoom_spd = ttk.Label(self.frame_sens, text=self.tr("lbl_zoom_speed"), font=("Segoe UI", 9, "bold"))
        self.lbl_zoom_spd.pack(anchor="w")
        self.slider_zoom = ttk.Scale(self.frame_sens, from_=2.0, to_=30.0, value=self.config_data["sensitivity"]["zoom"])
        self.slider_zoom.pack(fill="x", pady=(0, 4))

        self.lbl_gyro_spd = ttk.Label(self.frame_sens, text=self.tr("lbl_gyro_speed"), font=("Segoe UI", 9, "bold"))
        self.lbl_gyro_spd.pack(anchor="w")
        self.slider_gyro = ttk.Scale(self.frame_sens, from_=2.0, to_=40.0, value=self.config_data["sensitivity"].get("gyro", 15.0))
        self.slider_gyro.pack(fill="x", pady=(0, 4))

        self.lbl_deadzone = ttk.Label(self.frame_sens, text=self.tr("lbl_deadzone"), font=("Segoe UI", 9, "bold"))
        self.lbl_deadzone.pack(anchor="w")
        self.slider_deadzone = ttk.Scale(self.frame_sens, from_=0.05, to_=0.35, value=self.config_data["deadzone"]["left_stick"])
        self.slider_deadzone.pack(fill="x", pady=(0, 4))

        self.lbl_curve = ttk.Label(self.frame_sens, text=self.tr("lbl_curve"), font=("Segoe UI", 9, "bold"))
        self.lbl_curve.pack(anchor="w")
        self.slider_curve = ttk.Scale(self.frame_sens, from_=1.0, to_=3.0, value=self.config_data["curve"]["exponent"])
        self.slider_curve.pack(fill="x", pady=(0, 4))

        btn_opt_frame = ttk.Frame(tab_options)
        btn_opt_frame.pack(fill="x", pady=8)

        self.btn_reset2 = ttk.Button(btn_opt_frame, text=self.tr("btn_reset_defaults"), command=self.reset_to_defaults)
        self.btn_reset2.pack(side="left")

        self.btn_save_opt = ttk.Button(btn_opt_frame, text=self.tr("btn_save_all"), command=self.save_config)
        self.btn_save_opt.pack(side="right")

        # Tab 3: About & User Guide
        tab_guide = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab_guide, text=self.tr("tab_guide"))

        self.txt_guide = tk.Text(tab_guide, height=18, font=("Consolas", 10), background="#181818", foreground="#38BDF8")
        self.txt_guide.pack(fill="both", expand=True)

        guide_content = GUIDE_TEXTS.get(self.lang_code, GUIDE_TEXTS["en"])
        self.txt_guide.insert(tk.END, guide_content)
        self.txt_guide.config(state="disabled")

        # Tab 4: Monitor
        tab_monitor = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab_monitor, text=self.tr("tab_monitor"))

        self.txt_monitor = tk.Text(tab_monitor, height=18, font=("Consolas", 10), background="#1E1E1E", foreground="#00FF66")
        self.txt_monitor.pack(fill="both", expand=True)

    def start_service(self):
        self.service_thread = threading.Thread(target=self.run_loop, daemon=True)
        self.service_thread.start()

    def run_loop(self):
        rate_hz = self.config_data.get("polling", {}).get("rate_hz", 120)
        sleep_time = 1.0 / rate_hz

        while self.running:
            title, proc_name = get_foreground_window_info()
            is_sw_active = self.navigator.is_solidworks_active()
            state = self.controller_mgr.poll()

            if state:
                dev_type = state.get("device_type", "xinput")
                dev_name = state.get("device_name", "Gamepad")

                if is_sw_active:
                    status_str = self.tr("status_connected").format(dev=dev_name, type=dev_type.upper())
                    status_clr = "#10B981"
                else:
                    status_str = self.tr("status_window_inactive").format(dev=dev_name, proc=proc_name)
                    status_clr = "#F59E0B"

                self.lbl_status.config(text=status_str, foreground=status_clr)
                self.navigator.process(state)

                active_pressed = [k for k, v in state["buttons"].items() if v]
                txt = (
                    f"--- UNIFIED MULTI-CONTROLLER DIAGNOSTICS ---\n"
                    f"Language            : {self.lang_code.upper()}\n"
                    f"Controller Profile  : {dev_name} ({dev_type.upper()})\n"
                    f"Foreground Window   : '{title}'\n"
                    f"Foreground Process  : '{proc_name}'\n"
                    f"SolidWorks Active   : {'YES (Controlling 3D Viewport)' if is_sw_active else 'NO (Control Suspended)'}\n"
                    f"Edge Border Wrap    : {'ENABLED (Seamless 3D Rotation)' if self.navigator.config.get('app_filter', {}).get('lock_cursor_center') else 'DISABLED'}\n"
                    f"Global Hotkey       : Ctrl+Alt+S (Toggle Show/Hide GUI)\n"
                    f"----------------------------------------------\n"
                    f"Left Stick (Pan)    : LX={state['lx']:+.3f}, LY={state['ly']:+.3f}\n"
                    f"Right Stick (Rotate): RX={state['rx']:+.3f}, RY={state['ry']:+.3f}\n"
                    f"Triggers (Zoom)     : LT={state['lt']:.3f}, RT={state['rt']:.3f}\n"
                    f"Gyroscope 6DoF      : Pitch={state.get('gyro_pitch', 0.0):+.3f}, Yaw={state.get('gyro_yaw', 0.0):+.3f}\n"
                    f"Active Buttons      : {active_pressed}\n"
                    f"Precision Mode      : {'ON (30% speed)' if self.navigator.precision_mode else 'OFF'}\n"
                    f"Control Status      : {'PAUSED (R3 to Resume)' if self.navigator.paused else 'ACTIVE'}\n"
                )
                self.txt_monitor.delete("1.0", tk.END)
                self.txt_monitor.insert(tk.END, txt)
            else:
                self.lbl_status.config(text=self.tr("status_no_device"), foreground="#EF4444")
                self.txt_monitor.delete("1.0", tk.END)
                self.txt_monitor.insert(tk.END, self.tr("no_device_msg"))

            time.sleep(sleep_time)

    def on_close(self):
        self.running = False
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.navigator._release_all()
        self.destroy()


if __name__ == "__main__":
    start_min = False
    for arg in sys.argv[1:]:
        if arg.lower() in ("--minimized", "--tray", "-m", "/minimized"):
            start_min = True
            break

    app = ApplicationGUI(start_minimized=start_min)
    app.mainloop()
