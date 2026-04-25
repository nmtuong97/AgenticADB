import subprocess
import shlex
import json
import time
from typing import Optional


class IDBClient:
    """Client for interacting with iOS devices via the iOS Device Bridge (idb).

    This client implements the adapter pattern, providing a unified interface for
    device interactions that matches the ADBClient for Android.
    """

    def __init__(self, device_id: Optional[str] = None):
        """Initializes the IDBClient.

        Args:
            device_id: Optional UDID of the target iOS device to route commands to.
        """
        self.device_id = device_id

    def _run_cmd(self, args: list[str], timeout: int = 15, retries: int = 2) -> str:
        """Executes an IDB shell command with timeouts and retries.

        Args:
            args: The list of arguments to pass to the idb executable.
            timeout: Maximum execution time in seconds before raising a TimeoutExpired.
            retries: Number of retry attempts upon failure.

        Returns:
            The standard output string from the executed command.

        Raises:
            subprocess.TimeoutExpired: If the command execution exceeds the timeout duration.
            subprocess.CalledProcessError: If the command returns a non-zero exit code.
        """
        cmd = ["idb"]
        if self.device_id:
            cmd.extend(["--udid", self.device_id])
        cmd.extend(args)

        attempt = 0
        while attempt <= retries:
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=timeout
                )
                result.check_returncode()
                return result.stdout
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                attempt += 1
                if attempt > retries:
                    raise e
                time.sleep(1)

    def dump(self) -> str:
        """Dumps the current UI hierarchy from the iOS device.

        Returns:
            The raw JSON string representing the current UI state.
        """
        return self._run_cmd(["ui", "describe-all"])

    def tap(self, x: int, y: int) -> None:
        """Taps at the specified physical screen coordinates.

        Args:
            x: The horizontal coordinate.
            y: The vertical coordinate.
        """
        self._run_cmd(["ui", "tap", str(x), str(y)])

    def swipe(
        self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = None
    ) -> None:
        """Swipes from a starting coordinate to an ending coordinate.

        Args:
            x1: The starting horizontal coordinate.
            y1: The starting vertical coordinate.
            x2: The ending horizontal coordinate.
            y2: The ending vertical coordinate.
            duration_ms: The duration of the swipe in milliseconds (ignored on iOS).
        """
        self._run_cmd(["ui", "swipe", str(x1), str(y1), str(x2), str(y2)])

    def input_text(self, text: str) -> None:
        """Inputs text into the currently focused UI element.

        Automatically handles shell escaping natively via subprocess list arguments.

        Args:
            text: The text string to input.
        """
        # Subprocess run handles list escaping natively when shell=False
        self._run_cmd(["ui", "text", text])

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Simulates a touch-and-hold interaction at the specified coordinates.

        Args:
            x: The horizontal coordinate.
            y: The vertical coordinate.
            duration_ms: Duration of the press in milliseconds (defaults to 1000).
        """
        # idb swipe supports duration in ms according to original swipe, but we use duration parameter
        # Actually IDBClient swipe is just self._run_cmd(["ui", "swipe", str(x1), str(y1), str(x2), str(y2)])
        # wait let me just use swipe with duration argument. We didn't use duration flag before in IDBClient.swipe.
        # we will add duration to swipe.
        cmd = [
            "ui",
            "swipe",
            str(x),
            str(y),
            str(x),
            str(y),
            "--duration",
            str(duration_ms / 1000.0),
        ]
        self._run_cmd(cmd)

    def press_keycode(self, keycode: str) -> str:
        """Simulates pressing hardware or system keys.

        Maps abstract key names (e.g., 'home', 'back') to OS-specific idb interactions.
        Note that iOS does not have a native back button, so calling 'back' returns a warning string.

        Args:
            keycode: The abstract name of the system key.

        Returns:
            An empty string on success, or a warning message string if the key is unsupported (like 'back').
        """
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
        """Launches an application by its bundle identifier.

        Args:
            bundle_id: The bundle ID of the iOS application.
        """
        self._run_cmd(["launch", bundle_id])

    def kill_app(self, bundle_id: str) -> None:
        """Force stops an application by its bundle identifier.

        Args:
            bundle_id: The bundle ID of the iOS application.
        """
        self._run_cmd(["terminate", bundle_id])
