import os
import sys
import time

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class PlayStationController:
    """PlayStation DualShock 4 (PS4) & DualSense (PS5) Controller Reader."""

    def __init__(self, device_index=0):
        self.device_index = device_index
        self.is_connected = False
        self.joystick = None
        self.last_buttons = {}

        if PYGAME_AVAILABLE:
            if not pygame.get_init():
                pygame.init()
            if not pygame.joystick.get_init():
                pygame.joystick.init()

    def _init_joystick(self):
        if not PYGAME_AVAILABLE:
            return False

        count = pygame.joystick.get_count()
        if count <= self.device_index:
            self.is_connected = False
            self.joystick = None
            return False

        try:
            self.joystick = pygame.joystick.Joystick(self.device_index)
            self.joystick.init()
            self.is_connected = True
            return True
        except Exception:
            self.is_connected = False
            self.joystick = None
            return False

    def poll(self):
        """Polls current state of PlayStation controller. Returns normalized state dict or None."""
        if not PYGAME_AVAILABLE:
            return None

        pygame.event.pump()

        if not self.joystick or not self.is_connected:
            if not self._init_joystick():
                return None

        try:
            num_axes = self.joystick.get_numaxes()
            num_buttons = self.joystick.get_numbuttons()
            num_hats = self.joystick.get_numhats()

            # Axis Mapping
            lx = self.joystick.get_axis(0) if num_axes > 0 else 0.0
            ly = -self.joystick.get_axis(1) if num_axes > 1 else 0.0  # Invert Y to match XInput

            # RX, RY depends on DS4/DualSense mapping in Pygame
            rx = self.joystick.get_axis(2) if num_axes > 2 else 0.0
            ry = -self.joystick.get_axis(3) if num_axes > 3 else 0.0

            if num_axes >= 6:
                # Triggers on 6-axis layout
                lt_raw = self.joystick.get_axis(4)  # Range -1.0 -> 1.0
                rt_raw = self.joystick.get_axis(5)
                lt = (lt_raw + 1.0) / 2.0
                rt = (rt_raw + 1.0) / 2.0
            else:
                lt = 0.0
                rt = 0.0

            # Buttons mapping (Standard DualShock4 / DualSense layout)
            # 0: Cross (X), 1: Circle (O), 2: Square ([]), 3: Triangle (/\)
            btn_cross = self.joystick.get_button(0) if num_buttons > 0 else 0
            btn_circle = self.joystick.get_button(1) if num_buttons > 1 else 0
            btn_square = self.joystick.get_button(2) if num_buttons > 2 else 0
            btn_triangle = self.joystick.get_button(3) if num_buttons > 3 else 0

            btn_share = self.joystick.get_button(4) if num_buttons > 4 else 0
            btn_options = self.joystick.get_button(6) if num_buttons > 6 else 0
            btn_l3 = self.joystick.get_button(7) if num_buttons > 7 else 0
            btn_r3 = self.joystick.get_button(8) if num_buttons > 8 else 0
            btn_l1 = self.joystick.get_button(9) if num_buttons > 9 else 0
            btn_r1 = self.joystick.get_button(10) if num_buttons > 10 else 0

            # D-Pad (Hat 0)
            dpad_up, dpad_down, dpad_left, dpad_right = False, False, False, False
            if num_hats > 0:
                hat_x, hat_y = self.joystick.get_hat(0)
                dpad_up = hat_y == 1
                dpad_down = hat_y == -1
                dpad_left = hat_x == -1
                dpad_right = hat_x == 1

            button_states = {
                "dpad_up": bool(dpad_up),
                "dpad_down": bool(dpad_down),
                "dpad_left": bool(dpad_left),
                "dpad_right": bool(dpad_right),
                "start": bool(btn_options),
                "back": bool(btn_share),
                "l3": bool(btn_l3),
                "r3": bool(btn_r3),
                "lb": bool(btn_l1),
                "rb": bool(btn_r1),
                "a": bool(btn_cross),     # Mapped to 'a' position for unified solidworks navigator
                "b": bool(btn_circle),    # Mapped to 'b' position
                "x": bool(btn_square),    # Mapped to 'x' position
                "y": bool(btn_triangle),  # Mapped to 'y' position
            }

            # Gyro simulation / reading from extended axes if available
            gyro_pitch = 0.0
            gyro_yaw = 0.0
            if num_axes >= 8:
                gyro_pitch = self.joystick.get_axis(6)
                gyro_yaw = self.joystick.get_axis(7)

            return {
                "lx": lx,
                "ly": ly,
                "rx": rx,
                "ry": ry,
                "lt": lt,
                "rt": rt,
                "buttons": button_states,
                "gyro_pitch": gyro_pitch,
                "gyro_yaw": gyro_yaw,
                "device_name": self.joystick.get_name(),
                "device_type": "playstation",
            }
        except Exception:
            self.is_connected = False
            return None


if __name__ == "__main__":
    print("Testing PlayStation Controller Reader...")
    ps = PlayStationController()
    print("Polling controller status...")
    for _ in range(50):
        data = ps.poll()
        if data:
            print(f"\r[{data['device_name']}] LX:{data['lx']:+.2f} LY:{data['ly']:+.2f} | RX:{data['rx']:+.2f} RY:{data['ry']:+.2f} | LT:{data['lt']:.2f} RT:{data['rt']:.2f}", end="")
        else:
            print("\rNo PlayStation controller connected...", end="")
        time.sleep(0.05)
    print("\nTest completed.")
