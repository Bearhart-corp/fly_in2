from enum import Enum
from typing import Tuple


class Color(Enum):
    GREEN = (0, 128, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    PURPLE = (128, 0, 128)
    VIOLET = (238, 130, 238)
    CYAN = (0, 255, 255)
    CRIMSON = (220, 20, 60)
    BLACK = (0, 0, 0)
    BROWN = (165, 42, 42)
    ORANGE = (255, 165, 0)
    MAROON = (128, 0, 0)
    GOLD = (255, 215, 0)
    DARKRED = (139, 0, 0)
    RAINBOW = (255, 0, 255)
    LIME = (0, 255, 0)
    MAGENTA = (255, 0, 255)

    @staticmethod
    def get(s: str) -> Tuple[int, int, int]:
        return {
            "green": (0, 128, 0),
            "white": (255, 255, 255),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "red": (255, 0, 0),
            "purple": (128, 0, 128),
            "violet": (238, 130, 238),
            "cyan": (0, 255, 255),
            "crimson": (220, 20, 60),
            "black": (0, 0, 0),
            "brown": (165, 42, 42),
            "orange": (255, 165, 0),
            "maroon": (128, 0, 0),
            "gold": (255, 215, 0),
            "darkred": (139, 0, 0),
            "rainbow": (255, 0, 255),
            "lime": (0, 255, 0),
            "magenta": (255, 0, 255)
        }[s]


class ZoneType():
    zone = {
        "normal": 1,
        "blocked": 999,
        "restricted": 2,
        "priority": 1
    }


class MetaType(Enum):
    COLOR = "color"
    ZONE = "zone"
    MAX_LINK_CAPACITY = "max_link_capacity"
    MAX_DRONES = "max_drones"
