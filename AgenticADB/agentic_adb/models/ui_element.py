from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class UIElement:
    """Represents a unified, abstract mobile UI element parsed from an XML or JSON hierarchy.

    Attributes:
        index: The chronological sequence index of the element in the traversal.
        class_name: The underlying component class name.
        text: The text content or value displayed in the UI element.
        id: The resource identifier or bundle identifier for the element.
        desc: The content description or accessibility label.
        clickable: Indicates whether the element can be tapped or interacted with.
        center_x: The horizontal center coordinate of the element.
        center_y: The vertical center coordinate of the element.
    """

    index: int
    class_name: str
    text: str
    id: str
    desc: str
    clickable: bool
    center_x: int
    center_y: int

    def __post_init__(self):
        if self.center_x < 0 or self.center_y < 0:
            raise ValueError("Coordinates must be non-negative")

    def to_dict(self) -> Dict[str, Any]:
        """Converts the UIElement instance into a dictionary suitable for JSON serialization.

        Returns:
            A dictionary representation of the UI element mapping explicitly to snake_case keys.
        """
        return {
            "index": self.index,
            "class": self.class_name,
            "text": self.text,
            "id": self.id,
            "desc": self.desc,
            "clickable": self.clickable,
            "center_x": self.center_x,
            "center_y": self.center_y,
        }
