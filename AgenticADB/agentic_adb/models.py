from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class UIElement:
    index: int
    class_name: str
    text: str
    id: str
    desc: str
    clickable: bool
    center_x: int
    center_y: int

    def to_dict(self) -> Dict[str, Any]:
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
