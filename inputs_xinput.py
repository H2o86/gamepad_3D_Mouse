import ctypes
from ctypes import Structure, c_ushort, c_byte, c_short, c_ulong, POINTER, byref
import time

# XInput Constants
ERROR_SUCCESS = 0
ERROR_DEVICE_NOT_CONNECTED = 1167

# Button Bitmasks
XINPUT_GAMEPAD_DPAD_UP = 0x0001
XINPUT_GAMEPAD_DPAD_DOWN = 0x0002
XINPUT_GAMEPAD_DPAD_LEFT = 0x0004
XINPUT_GAMEPAD_DPAD_RIGHT = 0x0008
XINPUT_GAMEPAD_START = 0x0010
XINPUT_GAMEPAD_BACK = 0x0020
XINPUT_GAMEPAD_LEFT_THUMB = 0x0040
XINPUT_GAMEPAD_RIGHT_THUMB = 0x0080
XINPUT_GAMEPAD_LEFT_SHOULDER = 0x0100
XINPUT_GAMEPAD_RIGHT_SHOULDER = 0x0200
XINPUT_GAMEPAD_A = 0x1000
XINPUT_GAMEPAD_B = 0x2000
XINPUT_GAMEPAD_X = 0x4000
XINPUT_GAMEPAD_Y = 0x8000


class XINPUT_GAMEPAD(Structure):
    _fields_ = [
        ("wButtons", c_ushort),
        ("bLeftTrigger", c_byte),
        ("bRightTrigger", c_byte),
        ("sThumbLX", c_short),
        ("sThumbLY", c_short),
        ("sThumbRX", c_short),
        ("sThumbRY", c_short),
    ]


class XINPUT_STATE(Structure):
    _fields_ = [
        ("dwPacketNumber", c_ulong),
        ("Gamepad", XINPUT_GAMEPAD),
    ]


class XInputController:
    """XInput controller reader for Flydigi Dune Fox & Xbox compatible gamepads."""

    def __init__(self, controller_index=0):
        self.controller_index = controller_index
        self.xinput_dll = None
        self._load_xinput_dll()

        self.is_connected = False
        self.last_state = None
        self.last_buttons = 0

    def _load_xinput_dll(self):
        for dll_name in ["xinput1_4.dll", "xinput1_3.dll", "xinput9_1_0.dll"]:
            try:
                self.xinput_dll = ctypes.windll.LoadLibrary(dll_name)
                self._XInputGetState = self.xinput_dll.XInputGetState
                self._XInputGetState.argtypes = [c_ulong, POINTER(XINPUT_STATE)]
                self._XInputGetState.restype = c_ulong
                return
            except OSError:
                continue
        raise RuntimeError("Could not load any XInput DLL (xinput1_4.dll, xinput1_3.dll, xinput9_1_0.dll)")

    def poll(self):
        """Polls current state of the controller. Returns state dict or None if disconnected."""
        state = XINPUT_STATE()
        res = self._XInputGetState(self.controller_index, byref(state))

        if res != ERROR_SUCCESS:
            if self.is_connected:
                self.is_connected = False
            return None

        self.is_connected = True
        gp = state.Gamepad

        # Normalize thumbsticks (-1.0 to 1.0)
        lx = gp.sThumbLX / 32768.0 if gp.sThumbLX < 0 else gp.sThumbLX / 32767.0
        ly = gp.sThumbLY / 32768.0 if gp.sThumbLY < 0 else gp.sThumbLY / 32767.0
        rx = gp.sThumbRX / 32768.0 if gp.sThumbRX < 0 else gp.sThumbRX / 32767.0
        ry = gp.sThumbRY / 32768.0 if gp.sThumbRY < 0 else gp.sThumbRY / 32767.0

        # Normalize triggers (0.0 to 1.0)
        lt = (gp.bLeftTrigger & 0xFF) / 255.0
        rt = (gp.bRightTrigger & 0xFF) / 255.0

        buttons = gp.wButtons
        prev_buttons = self.last_buttons
        self.last_buttons = buttons

        button_states = {
            "dpad_up": bool(buttons & XINPUT_GAMEPAD_DPAD_UP),
            "dpad_down": bool(buttons & XINPUT_GAMEPAD_DPAD_DOWN),
            "dpad_left": bool(buttons & XINPUT_GAMEPAD_DPAD_LEFT),
            "dpad_right": bool(buttons & XINPUT_GAMEPAD_DPAD_RIGHT),
            "start": bool(buttons & XINPUT_GAMEPAD_START),
            "back": bool(buttons & XINPUT_GAMEPAD_BACK),
            "l3": bool(buttons & XINPUT_GAMEPAD_LEFT_THUMB),
            "r3": bool(buttons & XINPUT_GAMEPAD_RIGHT_THUMB),
            "lb": bool(buttons & XINPUT_GAMEPAD_LEFT_SHOULDER),
            "rb": bool(buttons & XINPUT_GAMEPAD_RIGHT_SHOULDER),
            "a": bool(buttons & XINPUT_GAMEPAD_A),
            "b": bool(buttons & XINPUT_GAMEPAD_B),
            "x": bool(buttons & XINPUT_GAMEPAD_X),
            "y": bool(buttons & XINPUT_GAMEPAD_Y),
        }

        # Button click triggers (just pressed)
        just_pressed = {
            k: button_states[k] and not bool(prev_buttons & getattr(self, f"_mask_{k}", 0))
            for k in button_states
        }

        self.last_state = {
            "lx": lx,
            "ly": ly,
            "rx": rx,
            "ry": ry,
            "lt": lt,
            "rt": rt,
            "buttons": button_states,
            "packet_number": state.dwPacketNumber,
        }

        return self.last_state


# Button masks helper
for name, val in [
    ("dpad_up", XINPUT_GAMEPAD_DPAD_UP),
    ("dpad_down", XINPUT_GAMEPAD_DPAD_DOWN),
    ("dpad_left", XINPUT_GAMEPAD_DPAD_LEFT),
    ("dpad_right", XINPUT_GAMEPAD_DPAD_RIGHT),
    ("start", XINPUT_GAMEPAD_START),
    ("back", XINPUT_GAMEPAD_BACK),
    ("l3", XINPUT_GAMEPAD_LEFT_THUMB),
    ("r3", XINPUT_GAMEPAD_RIGHT_THUMB),
    ("lb", XINPUT_GAMEPAD_LEFT_SHOULDER),
    ("rb", XINPUT_GAMEPAD_RIGHT_SHOULDER),
    ("a", XINPUT_GAMEPAD_A),
    ("b", XINPUT_GAMEPAD_B),
    ("x", XINPUT_GAMEPAD_X),
    ("y", XINPUT_GAMEPAD_Y),
]:
    setattr(XInputController, f"_mask_{name}", val)


if __name__ == "__main__":
    print("Testing XInput Controller Reader...")
    controller = XInputController()
    print("Polling controller status...")
    for _ in range(50):
        data = controller.poll()
        if data:
            print(f"\rLX: {data['lx']:+.2f} LY: {data['ly']:+.2f} | RX: {data['rx']:+.2f} RY: {data['ry']:+.2f} | LT: {data['lt']:.2f} RT: {data['rt']:.2f}", end="")
        else:
            print("\rController not connected. Plug in Flydigi Dune Fox (2.4G/Dây)...", end="")
        time.sleep(0.05)
    print("\nTest completed.")
