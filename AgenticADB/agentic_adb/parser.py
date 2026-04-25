import xml.etree.ElementTree as ET
import re
from typing import List
from agentic_adb.models import UIElement


def parse_xml(xml_content: str) -> List[UIElement]:
    """Parses an Android UI XML string and returns a filtered list of UI elements.

    It strips out non-interactable noise and computes integer center coordinates
    for bounds to optimize token usage.

    Args:
        xml_content: The raw XML string extracted via uiautomator.

    Returns:
        A list of parsed, filtered `UIElement` instances.
    """
    root = ET.fromstring(xml_content)
    elements = []

    # We will traverse all nodes, but filtering is needed.
    # To use sequential index
    filtered_index = 1

    # Extract all node elements
    for node in root.iter("node"):
        text = node.attrib.get("text", "")
        desc = node.attrib.get("content-desc", "")
        resource_id = node.attrib.get("resource-id", "")
        clickable_str = node.attrib.get("clickable", "false")
        clickable = clickable_str.lower() == "true"

        # Filter out "useless noise"
        # Discard the node entirely if ALL of the following are true:
        # text is empty, desc is empty, id is empty, clickable is false
        if not text and not desc and not resource_id and not clickable:
            continue

        # Process class name: extract short class name
        class_name_full = node.attrib.get("class", "")
        class_name = class_name_full.split(".")[-1] if class_name_full else ""

        # Strip package prefix from resource-id
        # e.g. "com.example:id/login_btn" -> "login_btn"
        id_str = resource_id
        if "/" in id_str:
            id_str = id_str.split("/", 1)[-1]

        # Calculate center coordinates from bounds "[x1,y1][x2,y2]"
        bounds_str = node.attrib.get("bounds", "")
        center_x, center_y = 0, 0
        if bounds_str:
            # Parse [x1,y1][x2,y2]
            match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
            if match:
                x1, y1, x2, y2 = map(int, match.groups())
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

        element = UIElement(
            index=filtered_index,
            class_name=class_name,
            text=text,
            id=id_str,
            desc=desc,
            clickable=clickable,
            center_x=center_x,
            center_y=center_y,
        )
        elements.append(element)
        filtered_index += 1

    return elements
