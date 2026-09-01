import ctypes
from ctypes import Structure, c_long, c_ulong, c_short, c_ushort, sizeof, Union, POINTER, byref, create_unicode_buffer
import math
import os
import time

# Windows Input Constants
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800

KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002

# Virtual Keycode Lookup Table
VK_MAP = {
    "CTRL": 0x11,
    "CONTROL": 0x11,
    "SHIFT": 0x10,
    "ALT": 0x12,
    "MENU": 0x12,
    "ESC": 0x1B,
    "ESCAPE": 0x1B,
    "SPACE": 0x20,
    "SPACEBAR": 0x20,
    "TAB": 0x09,
    "ENTER": 0x0D,
    "RETURN": 0x0D,
    "DELETE": 0x2E,
    "DEL": 0x2E,
    "BACKSPACE": 0x08,
    "CAPSLOCK": 0x14,
}

# Add F1-F12
for i in range(1, 13):
    VK_MAP[f"F{i}"] = 0x6F + i

# Add A-Z and 0-9
for c in range(ord("A"), ord("Z") + 1):
    VK_MAP[chr(c)] = c
for c in range(ord("0"), ord("9") + 1):
    VK_MAP[chr(c)] = c


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


class MOUSEINPUT(Structure):
    _fields_ = [
        ("dx", c_long),
        ("dy", c_long),
        ("mouseData", c_ulong),
        ("dwFlags", c_ulong),
        ("time", c_ulong),
        ("dwExtraInfo", POINTER(c_ulong)),
    ]


class KEYBDINPUT(Structure):
    _fields_ = [
        ("wVk", c_ushort),
        ("wScan", c_ushort),
        ("dwFlags", c_ulong),
        ("time", c_ulong),
        ("dwExtraInfo", POINTER(c_ulong)),
    ]


class HARDWAREINPUT(Structure):
    _fields_ = [
        ("uMsg", c_ulong),
        ("wParamL", c_short),
        ("wParamH", c_ushort),
    ]


class _INPUT_UNION(Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(Structure):
    _fields_ = [
        ("type", c_ulong),
        ("union", _INPUT_UNION),
    ]


# Windows API Handles
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

SendInput = user32.SendInput
SendInput.argtypes = [c_ulong, POINTER(INPUT), ctypes.c_int]
SendInput.restype = c_ulong


def get_foreground_window_info():
    """Returns (title, process_name) of current active foreground window."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return "", ""

    length = user32.GetWindowTextLengthW(hwnd)
    buff = create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    title = buff.value

    pid = c_ulong()
    user32.GetWindowThreadProcessId(hwnd, byref(pid))

    process_name = ""
    h_process = kernel32.OpenProcess(0x1000, False, pid)
    if h_process:
        proc_buff = create_unicode_buffer(512)
        size = c_ulong(512)
        if kernel32.QueryFullProcessImageNameW(h_process, 0, proc_buff, byref(size)):
            process_name = os.path.basename(proc_buff.value)
        kernel32.CloseHandle(h_process)

    return title, process_name


def get_screen_size():
    """Returns (width, height) of primary monitor."""
    sw = user32.GetSystemMetrics(0)
    sh = user32.GetSystemMetrics(1)
    return sw, sh


def get_cursor_pos():
    """Returns current cursor position (x, y)."""
    pt = POINT()
    user32.GetCursorPos(byref(pt))
    return pt.x, pt.y


def set_cursor_pos(x, y):
    """Sets cursor position to (x, y)."""
    user32.SetCursorPos(int(x), int(y))


def send_mouse_event(flags, dx=0, dy=0, data=0):
    """Sends a mouse event to Windows using SendInput."""
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.union.mi.dx = int(dx)
    inp.union.mi.dy = int(dy)
    inp.union.mi.mouseData = int(data)
    inp.union.mi.dwFlags = flags
    inp.union.mi.time = 0
    inp.union.mi.dwExtraInfo = None
    SendInput(1, byref(inp), sizeof(INPUT))


def send_key_event(vk_code, key_up=False):
    """Sends a keyboard event to Windows using SendInput."""
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk_code
    inp.union.ki.wScan = 0
    inp.union.ki.dwFlags = KEYEVENTF_KEYUP if key_up else KEYEVENTF_KEYDOWN
    inp.union.ki.time = 0
    inp.union.ki.dwExtraInfo = None
    SendInput(1, byref(inp), sizeof(INPUT))


def execute_shortcut(shortcut_str):
    """Parses and executes a shortcut string like 'Ctrl+7', 'Ctrl+Shift+B', 'F', 'Space', 'TAB'."""
    if not shortcut_str:
        return

    parts = [p.strip().upper() for p in shortcut_str.split("+") if p.strip()]
    if not parts:
        return

    modifiers = []
    keys = []

    for p in parts:
        if p in ("CTRL", "CONTROL", "SHIFT", "ALT", "MENU"):
            modifiers.append(VK_MAP[p])
        else:
            if p in VK_MAP:
                keys.append(VK_MAP[p])

    for mod in modifiers:
        send_key_event(mod, key_up=False)
    time.sleep(0.008)

    for k in keys:
        send_key_event(k, key_up=False)
        time.sleep(0.008)
        send_key_event(k, key_up=True)
        time.sleep(0.008)

    for mod in reversed(modifiers):
        send_key_event(mod, key_up=True)


def apply_deadzone_and_curve(val, deadzone=0.15, exponent=1.8):
    """Filters stick deadzone and applies a non-linear sensitivity curve."""
    abs_val = abs(val)
    if abs_val < deadzone:
        return 0.0

    scaled = (abs_val - deadzone) / (1.0 - deadzone)
    curved = math.pow(scaled, exponent)
    return math.copysign(curved, val)


class SolidWorksNavigator:
    """Translates controller state to SolidWorks 3D viewport navigation, Gyroscope 6DoF, and window filtering."""

    def __init__(self, config):
        self.config = config
        self.precision_mode = False
        self.paused = False

        self.mmb_down = False
        self.ctrl_down = False
        self.shift_down = False
        self.alt_down = False

        self.acc_x = 0.0
        self.acc_y = 0.0

        self.start_cursor_pos = (0, 0)
        self.prev_buttons = {}

    def update_config(self, new_config):
        self.config = new_config

    def is_solidworks_active(self):
        """Checks if current active foreground window matches SolidWorks filters."""
        app_filter = self.config.get("app_filter", {})
        if not app_filter.get("target_app_only", True):
            return True

        title, proc_name = get_foreground_window_info()
        title_upper = title.upper()
        proc_upper = proc_name.upper()

        keywords = app_filter.get("target_keywords", ["SOLIDWORKS", "SLDWORKS.EXE"])
        for kw in keywords:
            kw_u = kw.upper()
            if kw_u in title_upper or kw_u in proc_upper:
                return True

        return False

    def process(self, state):
        """Process controller state and dispatch SolidWorks navigation events."""
        if not state:
            self._release_all()
            return

        if not self.is_solidworks_active():
            if self.mmb_down:
                self._release_all()
            return

        buttons = state["buttons"]
        just_pressed = {
            k: buttons[k] and not self.prev_buttons.get(k, False)
            for k in buttons
        }
        self.prev_buttons = buttons.copy()

        keymap = self.config.get("keymap", {})

        for btn_key, is_just_pressed in just_pressed.items():
            if not is_just_pressed:
                continue

            config_key = f"button_{btn_key}"
            action = keymap.get(config_key, "")

            if action == "precision_toggle":
                self.precision_mode = not self.precision_mode
                print(f"[SolidWorks 3D Mouse] Precision Mode: {'ON (30% speed)' if self.precision_mode else 'OFF (100% speed)'}")
            elif action == "pause_toggle":
                self.paused = not self.paused
                print(f"[SolidWorks 3D Mouse] Status: {'PAUSED' if self.paused else 'ACTIVE'}")
                if self.paused:
                    self._release_all()
            elif action and action not in ("roll_left", "roll_right") and not self.paused:
                execute_shortcut(action)

        if self.paused:
            return

        dz_stick = self.config["deadzone"]["left_stick"]
        dz_trig = self.config["deadzone"]["trigger"]
        exp = self.config["curve"]["exponent"]

        lx = apply_deadzone_and_curve(state["lx"], dz_stick, exp)
        ly = apply_deadzone_and_curve(state["ly"], dz_stick, exp)
        rx = apply_deadzone_and_curve(state["rx"], dz_stick, exp)
        ry = apply_deadzone_and_curve(state["ry"], dz_stick, exp)

        lt = apply_deadzone_and_curve(state["lt"], dz_trig, exp)
        rt = apply_deadzone_and_curve(state["rt"], dz_trig, exp)

        mult = self.config["sensitivity"]["precision_multiplier"] if self.precision_mode else 1.0

        pan_x = lx * self.config["sensitivity"]["pan"] * mult
        pan_y = -ly * self.config["sensitivity"]["pan"] * mult

        rot_x = rx * self.config["sensitivity"]["rotate"] * mult
        rot_y = -ry * self.config["sensitivity"]["rotate"] * mult

        # PlayStation Gyro Navigation support
        gyro_pitch = state.get("gyro_pitch", 0.0)
        gyro_yaw = state.get("gyro_yaw", 0.0)
        gyro_mult = self.config.get("sensitivity", {}).get("gyro", 15.0)

        if abs(gyro_pitch) > 0.05 or abs(gyro_yaw) > 0.05:
            rot_x += gyro_yaw * gyro_mult * mult
            rot_y += gyro_pitch * gyro_mult * mult

        zoom_val = (rt - lt) * self.config["sensitivity"]["zoom"] * mult

        roll_val = 0.0
        if keymap.get("button_lb") == "roll_left" and buttons.get("lb", False):
            roll_val -= self.config["sensitivity"]["roll"] * mult
        if keymap.get("button_rb") == "roll_right" and buttons.get("rb", False):
            roll_val += self.config["sensitivity"]["roll"] * mult

        is_panning = abs(pan_x) > 0.01 or abs(pan_y) > 0.01
        is_rotating = abs(rot_x) > 0.01 or abs(rot_y) > 0.01
        is_zooming = abs(zoom_val) > 0.01
        is_rolling = abs(roll_val) > 0.01

        target_dx = 0.0
        target_dy = 0.0
        target_ctrl = False
        target_shift = False
        target_alt = False

        if is_panning:
            target_dx = pan_x
            target_dy = pan_y
            target_ctrl = True
        elif is_zooming:
            target_dx = 0.0
            target_dy = -zoom_val
            target_shift = True
        elif is_rolling:
            target_dx = roll_val
            target_dy = 0.0
            target_alt = True
        elif is_rotating:
            target_dx = rot_x
            target_dy = rot_y

        if target_ctrl != self.ctrl_down:
            send_key_event(VK_MAP["CTRL"], key_up=not target_ctrl)
            self.ctrl_down = target_ctrl

        if target_shift != self.shift_down:
            send_key_event(VK_MAP["SHIFT"], key_up=not target_shift)
            self.shift_down = target_shift

        if target_alt != self.alt_down:
            send_key_event(VK_MAP["ALT"], key_up=not target_alt)
            self.alt_down = target_alt

        is_moving = is_panning or is_rotating or is_zooming or is_rolling
        lock_mode = self.config.get("app_filter", {}).get("lock_cursor_center", True)

        sw, sh = get_screen_size()
        center_x, center_y = sw // 2, sh // 2

        if is_moving and not self.mmb_down:
            self.start_cursor_pos = get_cursor_pos()
            send_mouse_event(MOUSEEVENTF_MIDDLEDOWN)
            self.mmb_down = True
            time.sleep(0.005)

        elif not is_moving and self.mmb_down:
            send_mouse_event(MOUSEEVENTF_MIDDLEUP)
            self.mmb_down = False
            self._release_modifiers()

            if lock_mode:
                set_cursor_pos(self.start_cursor_pos[0], self.start_cursor_pos[1])

        if is_moving:
            self.acc_x += target_dx
            self.acc_y += target_dy

            move_x = int(self.acc_x)
            move_y = int(self.acc_y)

            if move_x != 0 or move_y != 0:
                send_mouse_event(MOUSEEVENTF_MOVE, dx=move_x, dy=move_y)
                self.acc_x -= move_x
                self.acc_y -= move_y

            if lock_mode:
                cur_x, cur_y = get_cursor_pos()
                margin = 100
                if cur_x < margin or cur_x > sw - margin or cur_y < margin or cur_y > sh - margin:
                    set_cursor_pos(center_x, center_y)

    def _release_modifiers(self):
        if self.ctrl_down:
            send_key_event(VK_MAP["CTRL"], key_up=True)
            self.ctrl_down = False
        if self.shift_down:
            send_key_event(VK_MAP["SHIFT"], key_up=True)
            self.shift_down = False
        if self.alt_down:
            send_key_event(VK_MAP["ALT"], key_up=True)
            self.alt_down = False

    def _release_all(self):
        if self.mmb_down:
            send_mouse_event(MOUSEEVENTF_MIDDLEUP)
            self.mmb_down = False
        self._release_modifiers()
        self.acc_x = 0.0
        self.acc_y = 0.0
