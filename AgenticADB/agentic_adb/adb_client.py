import subprocess
import tempfile
import os
import shlex
import time
from typing import Optional


class ADBClient:
    """Client for interacting with Android devices via the Android Debug Bridge (ADB).

    This client implements the adapter pattern, providing a unified interface for
    device interactions that matches the IDBClient for iOS.
    """

    def __init__(self, device_id: Optional[str] = None):
        """Initializes the ADBClient.

        Args:
            device_id: Optional serial number of the target device to route commands to.
        """
        self.device_id = device_id

    def _run_cmd(self, args: list[str], timeout: int = 15, retries: int = 2) -> str:
        """Executes an ADB shell command with timeouts and retries.

        Args:
            args: The list of arguments to pass to the adb executable.
            timeout: Maximum execution time in seconds before raising a TimeoutExpired.
            retries: Number of retry attempts upon failure.

        Returns:
            The standard output string from the executed command.

        Raises:
            subprocess.TimeoutExpired: If the command execution exceeds the timeout duration.
            subprocess.CalledProcessError: If the command returns a non-zero exit code.
        """
        cmd = ["adb"]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
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
        """Dumps the current UI hierarchy from the device.

        Returns:
            The raw XML string representing the current UI state.
        """
        # Dump the hierarchy to a file on the device
        device_path = "/sdcard/window_dump.xml"
        self._run_cmd(["shell", "uiautomator", "dump", device_path])

        # Pull the file to a temporary file locally
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            local_path = tmp_file.name

        try:
            self._run_cmd(["pull", device_path, local_path])
            with open(local_path, "r", encoding="utf-8") as f:
                xml_content = f.read()
            return xml_content
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

    def tap(self, x: int, y: int) -> None:
        """Taps at the specified physical screen coordinates.

        Args:
            x: The horizontal coordinate.
            y: The vertical coordinate.
        """
        self._run_cmd(["shell", "input", "tap", str(x), str(y)])

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int) -> None:
        """Swipes from a starting coordinate to an ending coordinate.

        Args:
            x1: The starting horizontal coordinate.
            y1: The starting vertical coordinate.
            x2: The ending horizontal coordinate.
            y2: The ending vertical coordinate.
            duration: The duration of the swipe in milliseconds.
        """
        self._run_cmd(
            [
                "shell",
                "input",
                "swipe",
                str(x1),
                str(y1),
                str(x2),
                str(y2),
                str(duration),
            ]
        )

    def input_text(self, text: str) -> None:
        """Inputs text into the currently focused UI element.

        Automatically handles shell escaping and space conversion for ADB input.

        Args:
            text: The text string to input.
        """
        # Spaces in input text need to be replaced by %s for Android input command
        text_for_input = text.replace(" ", "%s")
        # Then properly escape the string for shell execution
        escaped_text = shlex.quote(text_for_input)
        self._run_cmd(["shell", "input", "text", escaped_text])

    def keyevent(self, keycode: int) -> None:
        """Sends a raw integer key event to the device.

        Args:
            keycode: The integer code representing the key event.
        """
        self._run_cmd(["shell", "input", "keyevent", str(keycode)])

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Simulates a touch-and-hold interaction at the specified coordinates.

        Args:
            x: The horizontal coordinate.
            y: The vertical coordinate.
            duration_ms: Duration of the press in milliseconds (defaults to 1000).
        """
        self._run_cmd(
            [
                "shell",
                "input",
                "swipe",
                str(x),
                str(y),
                str(x),
                str(y),
                str(duration_ms),
            ]
        )

    def press_keycode(self, keycode: str) -> None:
        """Simulates pressing hardware or system keys.

        Maps abstract key names (e.g., 'home', 'back') to OS-specific ADB key events.

        Args:
            keycode: The abstract name of the system key.
        """
        keycode_mapping = {
            "home": "KEYCODE_HOME",
            "back": "KEYCODE_BACK",
            "enter": "KEYCODE_ENTER",
        }
        mapped_keycode = keycode_mapping.get(keycode.lower(), keycode)
        self._run_cmd(["shell", "input", "keyevent", mapped_keycode])

    def launch_app(self, bundle_id: str) -> None:
        """Launches an application by its package name or bundle ID.

        Args:
            bundle_id: The package name of the Android application.
        """
        self._run_cmd(
            [
                "shell",
                "monkey",
                "-p",
                bundle_id,
                "-c",
                "android.intent.category.LAUNCHER",
                "1",
            ]
        )

    def kill_app(self, bundle_id: str) -> None:
        """Force stops an application by its package name or bundle ID.

        Args:
            bundle_id: The package name of the Android application.
        """
        self._run_cmd(["shell", "am", "force-stop", bundle_id])
