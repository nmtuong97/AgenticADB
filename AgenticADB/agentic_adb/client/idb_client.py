from typing import Optional

from .base_client import BaseClient


class IDBClient(BaseClient):
    """Client for interacting with iOS devices via the iOS Device Bridge (idb)."""

    def _build_cmd(self, args: list[str]) -> list[str]:
        cmd = ["idb"]
        if self.device_id:
            cmd.extend(["--udid", self.device_id])
        cmd.extend(args)
        return cmd

    def dump_ui(self) -> str:
        """Dumps the current UI hierarchy from the iOS device."""
        # Safe/read operation, allow retries
        return self._run_command(self._build_cmd(["ui", "describe-all"]), retries=2)

    def tap(self, x: int, y: int) -> None:
        """Taps at the specified physical screen coordinates."""
        # Action operations, zero retries
        self._run_command(self._build_cmd(["ui", "tap", str(x), str(y)]))

    def swipe(
        self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500
    ) -> None:
        """Swipes from a starting coordinate to an ending coordinate."""
        self._run_command(self._build_cmd(["ui", "swipe", str(x1), str(y1), str(x2), str(y2)]))

    def input_text(self, text: str) -> None:
        """Inputs text into the currently focused UI element."""
        # Subprocess run handles list escaping natively when shell=False
        self._run_command(self._build_cmd(["ui", "text", text]))

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Simulates a touch-and-hold interaction at the specified coordinates."""
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
        self._run_command(self._build_cmd(cmd))

    def press_keycode(self, keycode: str) -> str:
        """Simulates pressing hardware or system keys.

        Returns:
            An empty string on success, or a warning message string if the key is unsupported (like 'back').
        """
        keycode_lower = keycode.lower()
        if keycode_lower == "home":
            self._run_command(self._build_cmd(["ui", "button", "HOME"]))
        elif keycode_lower == "back":
            return "Warning: iOS does not support a hardware back button. Please use tap_coordinate to tap the back UI element on screen."
        elif keycode_lower == "enter":
            self._run_command(self._build_cmd(["ui", "text", "\n"]))
        else:
            # Fallback
            self._run_command(self._build_cmd(["ui", "button", keycode]))
        return ""

    def launch_app(self, bundle_id: str) -> None:
        """Launches an application by its bundle identifier."""
        self._run_command(self._build_cmd(["launch", bundle_id]))

    def kill_app(self, bundle_id: str) -> None:
        """Force stops an application by its bundle identifier."""
        self._run_command(self._build_cmd(["terminate", bundle_id]))
