from abc import ABC, abstractmethod
import subprocess
import time
import logging
from typing import Optional, List

from agentic_adb.exceptions import CommandError

logger = logging.getLogger(__name__)

class BaseClient(ABC):
    """Abstract base client for interacting with mobile devices."""

    def __init__(self, device_id: Optional[str] = None):
        """Initializes the base client.

        Args:
            device_id: Optional identifier for the target device.
        """
        self.device_id = device_id

    def _run_command(self, cmd: list[str], *, retry: bool = False) -> str:
        """Executes a shell command with timeouts and controlled retries.

        Args:
            cmd: The list of arguments to execute.
            retry: Whether to retry the command on failure (hardcoded 2 retries, 15s timeout).

        Returns:
            The standard output string from the executed command.

        Raises:
            CommandError: If the command returns a non-zero exit code or times out.
        """
        timeout = 15
        retries = 2 if retry else 0
        attempt = 0

        while attempt <= retries:
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=timeout
                )
                result.check_returncode()
                return result.stdout
            except subprocess.TimeoutExpired as e:
                attempt += 1
                logger.warning(f"Command timed out. Attempt {attempt} of {retries + 1}. Command: {cmd}")
                if attempt > retries:
                    raise CommandError(f"Command timed out after {timeout} seconds: {e}")
            except subprocess.CalledProcessError as e:
                attempt += 1
                logger.warning(f"Command failed with exit code {e.returncode}. Attempt {attempt} of {retries + 1}. Error: {e.stderr}")
                if attempt > retries:
                    raise CommandError(f"Command failed with exit code {e.returncode}: {e.stderr or e.stdout}")
            if attempt <= retries:
                time.sleep(1)

        # This fallback is practically unreachable but satisfies return types
        raise CommandError(f"Command failed unexpectedly: {cmd}")

    @abstractmethod
    def dump_ui(self) -> str:
        """Dumps the current UI hierarchy from the device.

        Returns:
            The raw string output of the UI hierarchy (XML or JSON).
        """
        pass

    @abstractmethod
    def tap(self, x: int, y: int) -> None:
        """Taps at the specified physical screen coordinates.

        Args:
            x: The horizontal coordinate.
            y: The vertical coordinate.
        """
        pass

    @abstractmethod
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500) -> None:
        """Swipes from a starting coordinate to an ending coordinate.

        Args:
            x1: The starting horizontal coordinate.
            y1: The starting vertical coordinate.
            x2: The ending horizontal coordinate.
            y2: The ending vertical coordinate.
            duration_ms: The duration of the swipe in milliseconds.
        """
        pass

    @abstractmethod
    def input_text(self, text: str) -> None:
        """Inputs text into the currently focused UI element.

        Args:
            text: The text string to input.
        """
        pass

    @abstractmethod
    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Simulates a touch-and-hold interaction at the specified coordinates.

        Args:
            x: The horizontal coordinate.
            y: The vertical coordinate.
            duration_ms: Duration of the press in milliseconds.
        """
        pass

    @abstractmethod
    def press_keycode(self, keycode: str) -> None:
        """Simulates pressing hardware or system keys.

        Args:
            keycode: The abstract name of the system key.
        """
        pass

    @abstractmethod
    def launch_app(self, bundle_id: str) -> None:
        """Launches an application by its bundle identifier.

        Args:
            bundle_id: The bundle ID/package name of the application.
        """
        pass

    @abstractmethod
    def kill_app(self, bundle_id: str) -> None:
        """Force stops an application by its bundle identifier.

        Args:
            bundle_id: The bundle ID/package name of the application.
        """
        pass
