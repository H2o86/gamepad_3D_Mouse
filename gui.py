import json
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from inputs_manager import UnifiedControllerManager
from solidworks_mouse import SolidWorksNavigator, get_foreground_window_info


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

1. OVERVIEW & FEATURES
--------------------------------------------------
SolidMouse converts standard gamepads (Flydigi Dune Fox, Xbox, PS4/PS5) into a dedicated 3D SpaceMouse for SolidWorks.
- Native Low-Latency Control (~1ms XInput API response).
- Smooth Edge Border Wrapping: 100% continuous 3D rotation without cursor border collisions.
- SOLIDWORKS Window Focus Filtering: Automatically suspends control when switching to other apps.
- 6-Axis Gyroscope Navigation: Tilt your PS4/PS5 controller to rotate models physically in 3D space!

2. DEFAULT CONTROL MAPPING
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

3. HOW TO CONNECT CONTROLLERS
--------------------------------------------------
- Flydigi Dune Fox / Xbox: Connect via 2.4G USB Dongle or USB Cable (XInput Mode).
- PlayStation PS4 / PS5  : Connect via Bluetooth or USB Cable (DirectInput + Gyro Mode).

4. CUSTOM KEY MAPPER
--------------------------------------------------
Go to '🎮 Key Mapper' tab to rebind any of the 14 buttons to preset SolidWorks 2019 shortcuts or custom hotkeys (e.g., Ctrl+Alt+S, F5, Shift+E).
""",
    "vi": """=== SOLIDMOUSE - TRUNG TÂM ĐIỀU KHIỂN 3D SPACEMOUSE SOLIDWORKS ===

1. TỔNG QUAN & TÍNH NĂNG
--------------------------------------------------
SolidMouse biến các loại tay cầm chơi game (Flydigi Dune Fox, Xbox, PS4/PS5) thành thiết bị 3D SpaceMouse chuyên dụng cho SolidWorks.
- Phản hồi siêu mượt (~1ms XInput Native API).
- Chống văng viền chuột (Edge Wrapping): Xoay 3D mượt 100% không bị gián đoạn hay giật khựng.
- Tự động lọc cửa sổ SolidWorks: Chỉ kích hoạt khi mở SolidWorks, tự ngắt khi chuyển sang app khác.
- Gyroscope 6DoF: Nghiêng tay cầm PS4/PS5 thực tế để xoay mô hình 3D trực quan trong không gian!

2. SƠ ĐỒ ĐIỀU KHIỂN MẶC ĐỊNH
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

3. KẾT NỐI TAY CẦM
--------------------------------------------------
- Flydigi Dune Fox / Xbox: Cắm Dongle 2.4G USB hoặc Cáp USB (Chế độ XInput).
- PlayStation PS4 / PS5  : Kết nối Bluetooth hoặc Cáp USB (Chế độ DirectInput + Gyro).

4. GÁN PHÍM TÙY CHỈNH (KEY MAPPER)
--------------------------------------------------
Vào Tab '🎮 Gán Phím Chức Năng' để chọn nhanh phím tắt SolidWorks 2019 hoặc tự gõ tổ hợp phím bất kỳ (VD: Ctrl+Alt+S, F5, Shift+E) cho 14 nút bấm.
""",
    "ja": """=== SOLIDMOUSE - SOLIDWORKS用 3D SPACEMOUSE コントローラー ===

1. 概要と特徴
--------------------------------------------------
SolidMouseは、一般的なゲームパッド（Flydigi Dune Fox、Xbox、PS4/PS5）をSolidWorks専用の3D SpaceMouseに変換します。
- 超低遅延コントロール（~1ms XInput Native API）。
- 滑らかな画面端ラッピング（Edge Wrapping）：画面端に衝突することなく100%スムーズな3D回転。
- SOLIDWORKS ウィンドウフォーカス機能：他のアプリ操作時は自動的にコントロールを一時停止。
- 6軸ジャイロスコープナビゲーション：PS4/PS5コントローラーを傾けて、3Dモデルを直感的に回転！

2. デフォルトコントロール配置
--------------------------------------------------
- 左スティック     : パン移動 (Ctrl + 中央ドラッグ)
- 右スティック     : 3D回転 (中央ドラッグ)
- LT / RT (L2/R2)  : ズームアウト / ズームイン (Shift + 中央ドラッグ)
- LB / RB (L1/R1)  : ロール回転 左 / 右 (Alt + 中央ドラッグ)
- 方向キー 上      : 等角投影図 Isometric (Ctrl + 7)
- 方向キー 下      : 垂直面 Normal To (Ctrl + 8)
- 方向キー 左      : 全体表示 Zoom to Fit (Fキー)
- 方向キー 右      : 正面図 Front View (Ctrl + 1)
- A / ❌ ボタン    : キャンセル (ESCキー)
- B / ⭕ ボタン    : 再構築 Rebuild (Ctrl + B)
- X / 🟦 ボタン    : スマート寸法 (Dキー)
- Y / 🔺 ボタン    : 表示方向ダイアログ (スペースキー)
- L3スティック押し込: 精密モード切り替え (速度30%)
- R3スティック押し込: 一時停止 / 再開
""",
    "ko": """=== SOLIDMOUSE - SOLIDWORKS 3D SPACEMOUSE 컨트롤 센터 ===

1. 개요 및 주요 기능
--------------------------------------------------
SolidMouse는 일반 게임패드(Flydigi Dune Fox, Xbox, PS4/PS5)를 SolidWorks 전용 3D SpaceMouse로 전환해 줍니다.
- 초저지연 제어 (~1ms XInput Native API 응답).
- 부드러운 화면 가장자리 랩핑 (Edge Wrapping): 커서 멈춤 없이 100% 연속 3D 회전.
- SOLIDWORKS 창 감지 기능: 다른 프로그램 사용 시 3D 제어 자동 일시 정지.
- 6축 자이로스코프 제어: PS4/PS5 컨트롤러를 실제로 기울여 3D 모델을 회전!

2. 기본 컨트롤 매핑
--------------------------------------------------
- 왼쪽 스틱         : 평면 이동 Pan (Ctrl + 휠 드래그)
- 오른쪽 스틱       : 3D 회전 Rotate (휠 드래그)
- LT / RT (L2 / R2) : 축소 / 확대 Zoom (Shift + 휠 드래그)
- LB / RB (L1 / R1) : 롤 회전 Roll Left / Right (Alt + 휠 드래그)
- 방향키 위         : 등재 투영 Isometric (Ctrl + 7)
- 방향키 아래       : 수직 보기 Normal To (Ctrl + 8)
- 방향키 왼쪽       : 화면 맞춤 Zoom to Fit (F 키)
- 방향키 오른쪽     : 정면 보기 Front View (Ctrl + 1)
- A / ❌ 버튼       : 취소 (ESC 키)
- B / ⭕ 버튼       : 재생성 Rebuild (Ctrl + B)
- X / 🟦 버튼       : 지능형 치수 (D 키)
- Y / 🔺 버튼       : 방향 창 Orientation (스페이스바)
- L3 스틱 클릭      : 정밀 모드 토글 (30% 속도)
- R3 스틱 클릭      : 제어 일시 중지 / 재개
""",
    "zh": """=== SOLIDMOUSE - SOLIDWORKS 专用 3D SPACEMOUSE 控制中心 ===

1. 概述与核心功能
--------------------------------------------------
SolidMouse 将常规游戏手柄 (Flydigi Dune Fox、Xbox、PS4/PS5) 转换为 SolidWorks 专用 3D SpaceMouse。
- 超低延迟控制 (~1ms XInput Native API 响应)。
- 屏幕边缘平滑缠绕 (Edge Wrapping)：3D 旋转 100% 平滑，光标不会卡在屏幕边缘。
- SOLIDWORKS 窗口焦点过滤：切换到其他应用时自动暂停控制，防止干扰。
- 6 轴陀螺仪空间控制：倾斜 PS4/PS5 手柄即可在物理空间中直观旋转 3D 模型！

2. 默认控制映射
--------------------------------------------------
- 左摇杆            : 平移视图 Pan (Ctrl + 中键拖拽)
- 右摇杆            : 3D 旋转 Rotate (中键拖拽)
- LT / RT (L2 / R2) : 缩小 / 放大 Zoom (Shift + 中键拖拽)
- LB / RB (L1 / R1) : 倾斜旋转 Roll (Alt + 中键拖拽)
- 方向键 上         : 等轴测视图 Isometric (Ctrl + 7)
- 方向键 下         : 正视于 Normal To (Ctrl + 8)
- 方向键 左         : 整屏显示 Zoom to Fit (F 键)
- 方向键 右         : 前视图 Front View (Ctrl + 1)
- A / ❌ 键         : 退出 / 取消 (ESC 键)
- B / ⭕ 键         : 重建模型 Rebuild (Ctrl + B)
- X / 🟦 键         : 智能尺寸 (D 键)
- Y / 🔺 键         : 视图定向窗口 (空格键)
- 按下 L3 摇杆      : 切换精细模式 (30% 速度)
- 按下 R3 摇杆      : 暂停 / 恢复控制
""",
}


class ApplicationGUI(tk.Tk):
    """Unified Control Center for Flydigi Dune Fox, Xbox & PlayStation PS4/PS5 Controllers with i18n support."""

    def __init__(self):
        super().__init__()
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

        self.title(self.tr("title"))
        self.create_widgets()
        self.start_service()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

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

        # Update Guide Text
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
                    f"Edge Border Wrap    : {'ENABLED (Smooth rotation)' if self.navigator.config.get('app_filter', {}).get('lock_cursor_center') else 'DISABLED'}\n"
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
        self.navigator._release_all()
        self.destroy()


if __name__ == "__main__":
    app = ApplicationGUI()
    app.mainloop()
