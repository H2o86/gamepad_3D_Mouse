import time
from inputs_xinput import XInputController
from inputs_playstation import PlayStationController


class UnifiedControllerManager:
    """Unified Controller Manager: auto-detects and switches between XInput (Flydigi/Xbox) and PlayStation (PS4/PS5)."""

    def __init__(self, mode="auto"):
        self.mode = mode.lower()
        self.xinput = XInputController(controller_index=0)
        self.playstation = PlayStationController(device_index=0)

        self.active_type = "none"

    def set_mode(self, mode):
        self.mode = mode.lower()

    def poll(self):
        """Polls active controller based on mode and auto-detection."""
        if self.mode == "xinput":
            state = self.xinput.poll()
            if state:
                state["device_type"] = "xinput"
                state["device_name"] = "Flydigi Dune Fox / Xbox Controller"
                self.active_type = "xinput"
                return state
            self.active_type = "none"
            return None

        if self.mode == "playstation":
            state = self.playstation.poll()
            if state:
                self.active_type = "playstation"
                return state
            self.active_type = "none"
            return None

        # Mode == 'auto': Try XInput first, fallback to PlayStation
        state = self.xinput.poll()
        if state:
            state["device_type"] = "xinput"
            state["device_name"] = "Flydigi Dune Fox / Xbox Controller"
            self.active_type = "xinput"
            return state

        state = self.playstation.poll()
        if state:
            self.active_type = "playstation"
            return state

        self.active_type = "none"
        return None


if __name__ == "__main__":
    print("Testing Unified Controller Manager...")
    mgr = UnifiedControllerManager(mode="auto")
    for _ in range(30):
        data = mgr.poll()
        if data:
            print(f"\r[Active: {data['device_type'].upper()} - {data.get('device_name', '')}] LX:{data['lx']:+.2f} LY:{data['ly']:+.2f} RX:{data['rx']:+.2f} RY:{data['ry']:+.2f}", end="")
        else:
            print("\rNo controller detected (Auto-Detecting XInput / PlayStation)...", end="")
        time.sleep(0.05)
    print("\nTest completed.")
