import subprocess
import shlex
import json
from typing import Optional

class IDBClient:
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id

    def _run_cmd(self, args: list[str]) -> str:
        cmd = ["idb"]
        if self.device_id:
            cmd.extend(["--udid", self.device_id])
        cmd.extend(args)

        result = subprocess.run(cmd, capture_output=True, text=True)
        result.check_returncode()
        return result.stdout

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
