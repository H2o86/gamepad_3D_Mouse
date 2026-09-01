import json
import os
import sys
import time
import signal
from inputs_manager import UnifiedControllerManager
from solidworks_mouse import SolidWorksNavigator

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Warning] Failed to load config.json: {e}. Using defaults.")

    return {
        "device_mode": "auto",
        "sensitivity": {
            "pan": 12.0,
            "rotate": 10.0,
            "zoom": 15.0,
            "roll": 8.0,
            "gyro": 15.0,
            "precision_multiplier": 0.3,
        },
        "deadzone": {
            "left_stick": 0.15,
            "right_stick": 0.15,
            "trigger": 0.05,
        },
        "curve": {
            "exponent": 1.8,
        },
        "polling": {
            "rate_hz": 120,
        },
    }


def print_banner():
    print("=" * 70)
    print("  UNIFIED 3D SPACEMOUSE CONTROLLER FOR SOLIDWORKS")
    print("  Supports: Flydigi Dune Fox / Xbox (XInput) & PS4/PS5 (DirectInput)")
    print("=" * 70)
    print("  Controls Map:")
    print("    - Left Stick  : Pan View (Ctrl + MMB Drag)")
    print("    - Right Stick : Rotate View (MMB Drag)")
    print("    - LT / RT     : Zoom Out / Zoom In (Shift + MMB Drag)")
    print("    - LB / RB     : Roll Left / Roll Right (Alt + MMB Drag)")
    print("    - D-Pad Up    : Isometric View (Ctrl + 7)")
    print("    - D-Pad Down  : Normal To View (Ctrl + 8)")
    print("    - D-Pad Left  : Zoom to Fit (F)")
    print("    - D-Pad Right : Front View (Ctrl + 1)")
    print("    - Button A/X  : Escape (ESC)")
    print("    - Button B/O  : Rebuild (Ctrl + B)")
    print("    - Button Y/▲  : Orientation Dialog (Space)")
    print("    - Press L3    : Toggle Precision Mode (30% Speed)")
    print("    - Press R3    : Pause / Resume Control")
    print("=" * 70)


def main():
    print_banner()
    config = load_config()

    device_mode = config.get("device_mode", "auto")
    controller_mgr = UnifiedControllerManager(mode=device_mode)
    navigator = SolidWorksNavigator(config)

    rate_hz = config.get("polling", {}).get("rate_hz", 120)
    sleep_time = 1.0 / rate_hz

    running = True

    def signal_handler(sig, frame):
        nonlocal running
        print("\nShutting down SolidWorks 3D Mouse Service...")
        navigator._release_all()
        running = False
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print(f"\n[Status] Service running. Mode: [{device_mode.upper()}]. Polling: {rate_hz} Hz.")
    print("[Status] Auto-detecting gamepad (Flydigi Dune Fox / Xbox / PS4 / PS5)...")

    was_connected = False
    last_type = ""

    while running:
        t_start = time.perf_counter()
        state = controller_mgr.poll()

        if state:
            dev_type = state.get("device_type", "xinput")
            if not was_connected or dev_type != last_type:
                dev_name = state.get("device_name", "Gamepad")
                print(f"\n[Status] Connected to {dev_name} ({dev_type.upper()})! Ready for SolidWorks.")
                was_connected = True
                last_type = dev_type

            navigator.process(state)
        else:
            if was_connected:
                print("\n[Status] Gamepad disconnected! Waiting to reconnect...")
                navigator._release_all()
                was_connected = False

        t_elapsed = time.perf_counter() - t_start
        t_rem = sleep_time - t_elapsed
        if t_rem > 0:
            time.sleep(t_rem)


if __name__ == "__main__":
    main()
