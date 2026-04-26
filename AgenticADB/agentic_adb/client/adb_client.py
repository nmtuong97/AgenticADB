import tempfile
import os
import shlex
from typing import Optional

from .base_client import BaseClient

class ADBClient(BaseClient):
    """Client for interacting with Android devices via the Android Debug Bridge (ADB)."""

    def _build_cmd(self, args: list[str]) -> list[str]:
        cmd = ["adb"]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        cmd.extend(args)
        return cmd

    def dump_ui(self) -> str:
        """Dumps the current UI hierarchy from the device."""
        # Dump the hierarchy to a file on the device
        device_path = "/sdcard/window_dump.xml"
        # Safe/read operation, retry is allowed
        self._run_command(self._build_cmd(["shell", "uiautomator", "dump", device_path]), retry=True)

        # Pull the file to a temporary file locally
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            local_path = tmp_file.name

        try:
            self._run_command(self._build_cmd(["pull", device_path, local_path]), retry=True)
            with open(local_path, "r", encoding="utf-8") as f:
                xml_content = f.read()
            return xml_content
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

    def tap(self, x: int, y: int) -> None:
        """Taps at the specified physical screen coordinates."""
        # Action operations, zero retries
        self._run_command(self._build_cmd(["shell", "input", "tap", str(x), str(y)]))

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500) -> None:
        """Swipes from a starting coordinate to an ending coordinate."""
        self._run_command(
            self._build_cmd(
                [
                    "shell",
                    "input",
                    "swipe",
                    str(x1),
                    str(y1),
                    str(x2),
                    str(y2),
                    str(duration_ms),
                ]
            )
        )

    def input_text(self, text: str) -> None:
        """Inputs text into the currently focused UI element."""
        # Spaces in input text need to be replaced by %s for Android input command
        text_for_input = text.replace(" ", "%s")
        # Then properly escape the string for shell execution
        escaped_text = shlex.quote(text_for_input)
        self._run_command(self._build_cmd(["shell", "input", "text", escaped_text]))

    def keyevent(self, keycode: int) -> None:
        """Sends a raw integer key event to the device."""
        self._run_command(self._build_cmd(["shell", "input", "keyevent", str(keycode)]))

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Simulates a touch-and-hold interaction at the specified coordinates."""
        self._run_command(
            self._build_cmd(
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
        )

    def press_keycode(self, keycode: str) -> None:
        """Simulates pressing hardware or system keys."""
        keycode_mapping = {
            "home": "KEYCODE_HOME",
            "back": "KEYCODE_BACK",
            "enter": "KEYCODE_ENTER",
        }
        mapped_keycode = keycode_mapping.get(keycode.lower(), keycode)
        self._run_command(self._build_cmd(["shell", "input", "keyevent", mapped_keycode]))

    def launch_app(self, bundle_id: str) -> None:
        """Launches an application by its package name or bundle ID."""
        self._run_command(
            self._build_cmd(
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
        )

    def kill_app(self, bundle_id: str) -> None:
        """Force stops an application by its package name or bundle ID."""
        self._run_command(self._build_cmd(["shell", "am", "force-stop", bundle_id]))
