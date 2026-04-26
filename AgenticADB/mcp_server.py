import sys
import json
import logging
from typing import Optional, Literal
from mcp.server.fastmcp import FastMCP

# Setup logging to stderr
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("agentic_adb_mcp")

# Initialize MCP Server
mcp = FastMCP("AgenticADB", dependencies=["mcp>=1.0.0"])


def get_services(os_type: str, device_id: Optional[str] = None):
    if os_type == "android":
        from agentic_adb.client import ADBClient
        from agentic_adb.parser import ADBParser
        from agentic_adb.service import UIQueryService, UIActionService

        client = ADBClient(device_id=device_id)
        parser = ADBParser()
        return UIQueryService(client, parser), UIActionService(client)
    elif os_type == "ios":
        from agentic_adb.client import IDBClient
        from agentic_adb.parser import IDBParser
        from agentic_adb.service import UIQueryService, UIActionService

        client = IDBClient(device_id=device_id)
        parser = IDBParser()
        return UIQueryService(client, parser), UIActionService(client)
    else:
        raise ValueError(f"Unsupported OS type: {os_type}")


@mcp.tool()
def get_current_ui(
    os_type: Literal["android", "ios"], device_id: Optional[str] = None
) -> str:
    """
    Retrieves the token-optimized, minified JSON representation of the current mobile screen.
    Call this first to understand the UI state.

    Args:
        os_type: "android" or "ios"
        device_id: Target device UDID/ID (optional)
    """
    try:
        logger.info(f"Getting current UI for {os_type} (device_id: {device_id})")
        query_service, _ = get_services(os_type, device_id)
        ui_elements = query_service.get_ui_elements()

        json_data = [element.to_dict() for element in ui_elements]
        return json.dumps(json_data, indent=2)
    except Exception as e:
        logger.error(f"Failed to get current UI: {e}")
        return f"Action failed: {str(e)}"


@mcp.tool()
def tap_coordinate(
    os_type: Literal["android", "ios"], x: int, y: int, device_id: Optional[str] = None
) -> str:
    """
    Taps on the screen at the given (x, y) coordinates.

    Args:
        os_type: "android" or "ios"
        x: The center_x coordinate
        y: The center_y coordinate
        device_id: Target device UDID/ID (optional)
    """
    try:
        logger.info(
            f"Tapping coordinate ({x}, {y}) for {os_type} (device_id: {device_id})"
        )
        _, action_service = get_services(os_type, device_id)
        action_service.tap(x, y)
        return f"Successfully tapped at ({x}, {y})"
    except Exception as e:
        logger.error(f"Failed to tap coordinate: {e}")
        return f"Action failed: {str(e)}"


@mcp.tool()
def swipe_screen(
    os_type: Literal["android", "ios"],
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    duration_ms: int = 500,
    device_id: Optional[str] = None,
) -> str:
    """
    Swipes from one coordinate to another.

    Args:
        os_type: "android" or "ios"
        x1: Starting x coordinate
        y1: Starting y coordinate
        x2: Ending x coordinate
        y2: Ending y coordinate
        duration_ms: Duration of the swipe in milliseconds (default: 500)
        device_id: Target device UDID/ID (optional)
    """
    try:
        logger.info(
            f"Swiping from ({x1}, {y1}) to ({x2}, {y2}) for {os_type} (device_id: {device_id})"
        )
        _, action_service = get_services(os_type, device_id)
        action_service.swipe(x1, y1, x2, y2, duration_ms)
        return f"Successfully swiped from ({x1}, {y1}) to ({x2}, {y2})"
    except Exception as e:
        logger.error(f"Failed to swipe screen: {e}")
        return f"Action failed: {str(e)}"


@mcp.tool()
def input_text_field(
    os_type: Literal["android", "ios"], text: str, device_id: Optional[str] = None
) -> str:
    """
    Inputs text into the currently focused field.
    Note: You should tap the text field first using tap_coordinate before calling this.

    Args:
        os_type: "android" or "ios"
        text: The text to type
        device_id: Target device UDID/ID (optional)
    """
    try:
        logger.info(f"Inputting text '{text}' for {os_type} (device_id: {device_id})")
        _, action_service = get_services(os_type, device_id)
        action_service.input_text(text)
        return f"Successfully input text: {text}"
    except Exception as e:
        logger.error(f"Failed to input text: {e}")
        return f"Action failed: {str(e)}"


@mcp.tool()
def long_press_coordinate(
    os_type: Literal["android", "ios"],
    x: int,
    y: int,
    duration_ms: int = 1000,
    device_id: Optional[str] = None,
) -> str:
    """
    Simulates a long press (touch-and-hold) on the screen at the given (x, y) coordinates.

    Args:
        os_type: "android" or "ios"
        x: The center_x coordinate
        y: The center_y coordinate
        duration_ms: Duration of the long press in milliseconds (default: 1000)
        device_id: Target device UDID/ID (optional)
    """
    try:
        logger.info(
            f"Long pressing coordinate ({x}, {y}) for {duration_ms}ms for {os_type} (device_id: {device_id})"
        )
        _, action_service = get_services(os_type, device_id)
        action_service.long_press(x, y, duration_ms)
        return f"Successfully long pressed at ({x}, {y}) for {duration_ms}ms"
    except Exception as e:
        logger.error(f"Failed to long press coordinate: {e}")
        return f"Action failed: {str(e)}"


@mcp.tool()
def press_system_key(
    os_type: Literal["android", "ios"], key_name: str, device_id: Optional[str] = None
) -> str:
    """
    Simulates pressing a hardware/system key (e.g., 'home', 'back', 'enter').

    Args:
        os_type: "android" or "ios"
        key_name: The abstract name of the key (e.g., "home", "back", "enter")
        device_id: Target device UDID/ID (optional)
    """
    try:
        logger.info(
            f"Pressing system key '{key_name}' for {os_type} (device_id: {device_id})"
        )
        _, action_service = get_services(os_type, device_id)
        result = action_service.press_keycode(key_name)
        if result:  # Used for the iOS 'back' button warning
            return result
        return f"Successfully pressed system key: {key_name}"
    except Exception as e:
        logger.error(f"Failed to press system key: {e}")
        return f"Action failed: {str(e)}"


@mcp.tool()
def launch_application(
    os_type: Literal["android", "ios"], bundle_id: str, device_id: Optional[str] = None
) -> str:
    """
    Launches an application by its bundle identifier.

    Args:
        os_type: "android" or "ios"
        bundle_id: The application's bundle ID/package name
        device_id: Target device UDID/ID (optional)
    """
    try:
        logger.info(
            f"Launching application '{bundle_id}' for {os_type} (device_id: {device_id})"
        )
        _, action_service = get_services(os_type, device_id)
        action_service.launch_app(bundle_id)
        return f"Successfully launched application: {bundle_id}"
    except Exception as e:
        logger.error(f"Failed to launch application: {e}")
        return f"Action failed: {str(e)}"


@mcp.tool()
def kill_application(
    os_type: Literal["android", "ios"], bundle_id: str, device_id: Optional[str] = None
) -> str:
    """
    Force stops/terminates an application by its bundle identifier.

    Args:
        os_type: "android" or "ios"
        bundle_id: The application's bundle ID/package name
        device_id: Target device UDID/ID (optional)
    """
    try:
        logger.info(
            f"Killing application '{bundle_id}' for {os_type} (device_id: {device_id})"
        )
        _, action_service = get_services(os_type, device_id)
        action_service.kill_app(bundle_id)
        return f"Successfully killed application: {bundle_id}"
    except Exception as e:
        logger.error(f"Failed to kill application: {e}")
        return f"Action failed: {str(e)}"


if __name__ == "__main__":
    # The server uses stdio transport by default when run directly
    mcp.run()
