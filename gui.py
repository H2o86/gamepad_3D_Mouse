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


class ApplicationGUI(tk.Tk):
    """Unified Control Center for Flydigi Dune Fox, Xbox & PlayStation PS4/PS5 Controllers with i18n support."""

    def __init__(self):
        super().__init__()
        self.geometry("760x740")
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
        self.notebook.tab(2, text=self.tr("tab_monitor"))

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
            width=40,
        )

        curr_mode = self.config_data.get("device_mode", "auto")
        if curr_mode == "playstation":
            self.combo_dev_mode.set("PlayStation PS4 DualShock 4 / PS5 DualSense")
        elif curr_mode == "xinput":
            self.combo_dev_mode.set("Xbox / Flydigi Dune Fox (XInput)")
        else:
            self.combo_dev_mode.set("Auto Detect (Recommended)")

        self.combo_dev_mode.pack(side="left", padx=10)

        # Language Selector
        ttk.Label(dev_frame, text="🌐 Language:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(15, 5))
        self.combo_lang = ttk.Combobox(
            dev_frame,
            values=["English (EN)", "Tiếng Việt (VI)"],
            state="readonly",
            width=15,
        )
        self.combo_lang.set("English (EN)" if self.lang_code == "en" else "Tiếng Việt (VI)")
        self.combo_lang.pack(side="left")

        def on_lang_change(event):
            sel = self.combo_lang.get()
            new_lang = "en" if "English" in sel else "vi"
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

        # Tab 3: Monitor
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
