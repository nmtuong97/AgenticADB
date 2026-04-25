import subprocess
import shlex
import json
import time
from typing import Optional

class IDBClient:
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id

    def _run_cmd(self, args: list[str], timeout: int = 15, retries: int = 2) -> str:
        cmd = ["idb"]
        if self.device_id:
            cmd.extend(["--udid", self.device_id])
        cmd.extend(args)

        attempt = 0
        while attempt <= retries:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                result.check_returncode()
                return result.stdout
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                attempt += 1
                if attempt > retries:
                    raise e
                time.sleep(1)

    def dump(self) -> str:
        """Dumps the UI hierarchy and returns the JSON string."""
        return self._run_cmd(["ui", "describe-all"])

    def tap(self, x: int, y: int) -> None:
        """Taps at the specified coordinates."""
        self._run_cmd(["ui", "tap", str(x), str(y)])

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = None) -> None:
        """Swipes from (x1, y1) to (x2, y2)."""
        self._run_cmd(["ui", "swipe", str(x1), str(y1), str(x2), str(y2)])

    def input_text(self, text: str) -> None:
        """Inputs text. Handles escaping for spaces and special characters."""
        # Subprocess run handles list escaping natively when shell=False
        self._run_cmd(["ui", "text", text])

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Simulates a touch-and-hold at the specified coordinates."""
        # idb swipe supports duration in ms according to original swipe, but we use duration parameter
        # Actually IDBClient swipe is just self._run_cmd(["ui", "swipe", str(x1), str(y1), str(x2), str(y2)])
        # wait let me just use swipe with duration argument. We didn't use duration flag before in IDBClient.swipe.
        # we will add duration to swipe.
        cmd = ["ui", "swipe", str(x), str(y), str(x), str(y), "--duration", str(duration_ms / 1000.0)]
        self._run_cmd(cmd)

    def press_keycode(self, keycode: str) -> str:
        """Simulates pressing hardware/system keys."""
        keycode_lower = keycode.lower()
        if keycode_lower == "home":
            self._run_cmd(["ui", "button", "HOME"])
        elif keycode_lower == "back":
            return "Warning: iOS does not support a hardware back button. Please use tap_coordinate to tap the back UI element on screen."
        elif keycode_lower == "enter":
            self._run_cmd(["ui", "text", "\n"])
        else:
            # Fallback
            self._run_cmd(["ui", "button", keycode])
        return ""

    def launch_app(self, bundle_id: str) -> None:
        """Opens the app using the bundle id."""
        self._run_cmd(["launch", bundle_id])

    def kill_app(self, bundle_id: str) -> None:
        """Force stops the app using the bundle id."""
        self._run_cmd(["terminate", bundle_id])
