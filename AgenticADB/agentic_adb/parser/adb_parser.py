import xml.etree.ElementTree as ET
import re
from agentic_adb.models import UIElement
from agentic_adb.exceptions import ParseError
from .base_parser import BaseParser

class ADBParser(BaseParser[UIElement]):
    """Parses an Android UI XML string and returns a filtered list of UI elements."""

    def parse(self, raw: str) -> list[UIElement]:
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            raise ParseError(f"Failed to parse Android XML: {e}")

        elements = []
        filtered_index = 1

        for node in root.iter("node"):
            text = node.attrib.get("text", "")
            desc = node.attrib.get("content-desc", "")
            resource_id = node.attrib.get("resource-id", "")
            clickable_str = node.attrib.get("clickable", "false")
            clickable = clickable_str.lower() == "true"

            if not text and not desc and not resource_id and not clickable:
                continue

            class_name_full = node.attrib.get("class", "")
            class_name = class_name_full.split(".")[-1] if class_name_full else ""

            id_str = resource_id
            if "/" in id_str:
                id_str = id_str.split("/", 1)[-1]

            bounds_str = node.attrib.get("bounds", "")
            center_x, center_y = 0, 0
            if bounds_str:
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
