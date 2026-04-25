import sys
import json
import logging
from typing import Optional, Literal
from mcp.server.fastmcp import FastMCP

# Setup logging to stderr
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agentic_adb_mcp")

# Initialize MCP Server
mcp = FastMCP("AgenticADB", dependencies=["mcp>=1.0.0"])

def get_client(os_type: str, device_id: Optional[str] = None):
    if os_type == "android":
        from agentic_adb.adb_client import ADBClient
        return ADBClient(device_id=device_id)
    elif os_type == "ios":
        from agentic_adb.idb_client import IDBClient
        return IDBClient(device_id=device_id)
    else:
        raise ValueError(f"Unsupported OS type: {os_type}")

@mcp.tool()
def get_current_ui(os_type: Literal["android", "ios"], device_id: Optional[str] = None) -> str:
    """
    Retrieves the token-optimized, minified JSON representation of the current mobile screen.
    Call this first to understand the UI state.

    Args:
        os_type: "android" or "ios"
        device_id: Target device UDID/ID (optional)
    """
    try:
        logger.info(f"Getting current UI for {os_type} (device_id: {device_id})")
        client = get_client(os_type, device_id)
        raw_content = client.dump()

        if os_type == "android":
            from agentic_adb.parser import parse_xml
            ui_elements = parse_xml(raw_content)
        else:
            from agentic_adb.idb_parser import parse_idb_json
            ui_elements = parse_idb_json(raw_content)

        json_data = [element.to_dict() for element in ui_elements]
        return json.dumps(json_data, indent=2)
    except Exception as e:
        logger.error(f"Failed to get current UI: {e}")
        return f"Action failed: {str(e)}"

@mcp.tool()
def tap_coordinate(os_type: Literal["android", "ios"], x: int, y: int, device_id: Optional[str] = None) -> str:
    """
    Taps on the screen at the given (x, y) coordinates.

    Args:
        os_type: "android" or "ios"
        x: The center_x coordinate
        y: The center_y coordinate
        device_id: Target device UDID/ID (optional)
    """
    try:
        logger.info(f"Tapping coordinate ({x}, {y}) for {os_type} (device_id: {device_id})")
        client = get_client(os_type, device_id)
        client.tap(x, y)
        return f"Successfully tapped at ({x}, {y})"
    except Exception as e:
        logger.error(f"Failed to tap coordinate: {e}")
        return f"Action failed: {str(e)}"

@mcp.tool()
def swipe_screen(os_type: Literal["android", "ios"], x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500, device_id: Optional[str] = None) -> str:
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
        logger.info(f"Swiping from ({x1}, {y1}) to ({x2}, {y2}) for {os_type} (device_id: {device_id})")
        client = get_client(os_type, device_id)
        if os_type == "android":
            client.swipe(x1, y1, x2, y2, duration_ms)
        else:
            # iOS might not support duration in the cli tool currently based on the code,
            # but we pass it as it was requested or ignored internally.
            client.swipe(x1, y1, x2, y2, duration_ms)
        return f"Successfully swiped from ({x1}, {y1}) to ({x2}, {y2})"
    except Exception as e:
        logger.error(f"Failed to swipe screen: {e}")
        return f"Action failed: {str(e)}"

@mcp.tool()
def input_text_field(os_type: Literal["android", "ios"], text: str, device_id: Optional[str] = None) -> str:
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
        client = get_client(os_type, device_id)
        client.input_text(text)
        return f"Successfully input text: {text}"
    except Exception as e:
        logger.error(f"Failed to input text: {e}")
        return f"Action failed: {str(e)}"

if __name__ == "__main__":
    # The server uses stdio transport by default when run directly
    mcp.run()
