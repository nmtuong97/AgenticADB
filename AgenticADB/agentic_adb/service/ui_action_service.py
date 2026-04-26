from agentic_adb.client.base_client import BaseClient

class UIActionService:
    """Service for handling write/interactive UI actions.

    Orchestrates operations that mutate the device state. Does not utilize parsers.
    """

    def __init__(self, client: BaseClient):
        """Initializes the UIActionService.

        Args:
            client: The mobile device client (IO) for dispatching actions.
        """
        self._client = client

    def tap(self, x: int, y: int) -> None:
        """Taps at the specified physical screen coordinates."""
        self._client.tap(x, y)

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500) -> None:
        """Swipes from a starting coordinate to an ending coordinate."""
        self._client.swipe(x1, y1, x2, y2, duration_ms)

    def input_text(self, text: str) -> None:
        """Inputs text into the currently focused UI element."""
        self._client.input_text(text)

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Simulates a touch-and-hold interaction at the specified coordinates."""
        self._client.long_press(x, y, duration_ms)

    def press_keycode(self, keycode: str) -> None:
        """Simulates pressing hardware or system keys."""
        self._client.press_keycode(keycode)

    def launch_app(self, bundle_id: str) -> None:
        """Launches an application by its bundle identifier."""
        self._client.launch_app(bundle_id)

    def kill_app(self, bundle_id: str) -> None:
        """Force stops an application by its bundle identifier."""
        self._client.kill_app(bundle_id)
