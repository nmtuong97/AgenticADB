import subprocess
import tempfile
import os
import shlex
from typing import Optional

class ADBClient:
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id

    def _run_cmd(self, args: list[str]) -> str:
        cmd = ["adb"]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        cmd.extend(args)

        result = subprocess.run(cmd, capture_output=True, text=True)
        result.check_returncode()
        return result.stdout

    def dump(self) -> str:
        """Dumps the UI hierarchy and returns the XML string."""
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
        """Taps at the specified coordinates."""
        self._run_cmd(["shell", "input", "tap", str(x), str(y)])

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int) -> None:
        """Swipes from (x1, y1) to (x2, y2) over the specified duration in ms."""
        self._run_cmd(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

    def input_text(self, text: str) -> None:
        """Inputs text. Handles escaping for spaces and special characters."""
        # Spaces in input text need to be replaced by %s for Android input command
        text_for_input = text.replace(" ", "%s")
        # Then properly escape the string for shell execution
        escaped_text = shlex.quote(text_for_input)
        self._run_cmd(["shell", "input", "text", escaped_text])

    def keyevent(self, keycode: int) -> None:
        """Sends a key event."""
        self._run_cmd(["shell", "input", "keyevent", str(keycode)])
