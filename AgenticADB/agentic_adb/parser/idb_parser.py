import json
from typing import Any
from agentic_adb.models import UIElement
from agentic_adb.exceptions import ParseError
from .base_parser import BaseParser

class IDBParser(BaseParser[UIElement]):
    """Parses an iOS IDB UI JSON string and returns a filtered list of UI elements."""

    def parse(self, raw: str) -> list[UIElement]:
        if not raw.strip():
            return []

        try:
            root_node = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ParseError(f"Failed to parse iOS JSON: {e}")

        elements = []
        filtered_index = [1]

        def traverse(node: dict[str, Any]):
            node_type = node.get("type", "")
            if node_type.startswith("XCUIElementType"):
                class_name = node_type[len("XCUIElementType") :]
            else:
                class_name = node_type

            identifier = node.get("AXIdentifier", "")
            desc = node.get("AXLabel", "")

            text = node.get("AXValue", "")
            if not text:
                text = node.get("title", "")

            traits = node.get("traits", [])
            clickable = (
                "button" in traits
                or "link" in traits
                or "plays_sound" in traits
                or "keyboard_key" in traits
            )

            if not text and not desc and not identifier and not clickable:
                pass
            else:
                frame = node.get("frame", {})
                center_x = None
                center_y = None
                if frame:
                    x = frame.get("x", 0.0)
                    y = frame.get("y", 0.0)
                    width = frame.get("width", 0.0)
                    height = frame.get("height", 0.0)
                    cx = int(x + (width / 2))
                    cy = int(y + (height / 2))
                    # Basic validation for out-of-bounds or zero-size coordinates
                    if cx > 0 and cy > 0 and cx < 10000 and cy < 10000:
                        center_x = cx
                        center_y = cy

                element = UIElement(
                    index=filtered_index[0],
                    class_name=class_name,
                    text=str(text),
                    id=identifier,
                    desc=desc,
                    clickable=clickable,
                    center_x=center_x,
                    center_y=center_y,
                )
                elements.append(element)
                filtered_index[0] += 1

            for child in node.get("children", []):
                traverse(child)

        if isinstance(root_node, list):
            for item in root_node:
                traverse(item)
        elif isinstance(root_node, dict):
            traverse(root_node)

        return elements
