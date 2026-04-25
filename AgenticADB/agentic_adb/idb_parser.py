import json
from typing import List, Dict, Any
from agentic_adb.models import UIElement

def parse_idb_json(json_content: str) -> List[UIElement]:
    """Parses iOS IDB UI JSON string and returns a filtered list of UI Elements."""
    try:
        root_node = json.loads(json_content)
    except json.JSONDecodeError:
        return []

    elements = []
    # Use a list to pass by reference for a mutable integer index
    filtered_index = [1]

    def traverse(node: Dict[str, Any]):
        node_type = node.get("type", "")
        # Strip prefix
        if node_type.startswith("XCUIElementType"):
            class_name = node_type[len("XCUIElementType"):]
        else:
            class_name = node_type

        identifier = node.get("AXIdentifier", "")
        desc = node.get("AXLabel", "")

        # Check text: AXValue or title
        text = node.get("AXValue", "")
        if not text:
            text = node.get("title", "")

        traits = node.get("traits", [])
        clickable = "button" in traits or "link" in traits or "plays_sound" in traits or "keyboard_key" in traits

        # Filter logic: if empty text, empty desc, empty id, AND not clickable -> skip
        if not text and not desc and not identifier and not clickable:
            pass # skip creating an element
        else:
            frame = node.get("frame", {})
            center_x, center_y = 0, 0
            if frame:
                x = frame.get("x", 0.0)
                y = frame.get("y", 0.0)
                width = frame.get("width", 0.0)
                height = frame.get("height", 0.0)
                center_x = int(x + (width / 2))
                center_y = int(y + (height / 2))

            element = UIElement(
                index=filtered_index[0],
                class_name=class_name,
                text=str(text),
                id=identifier,
                desc=desc,
                clickable=clickable,
                center_x=center_x,
                center_y=center_y
            )
            elements.append(element)
            filtered_index[0] += 1

        for child in node.get("children", []):
            traverse(child)

    # idb ui describe-all usually returns a single root object or a list of objects.
    # We should handle both cases just in case.
    if isinstance(root_node, list):
        for item in root_node:
            traverse(item)
    elif isinstance(root_node, dict):
        traverse(root_node)

    return elements
