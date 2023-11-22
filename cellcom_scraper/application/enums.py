from enum import Enum


class NavigatorWebDriverType(str, Enum):
    CHROME = "Chrome"
    FIREFOX = "Firefox"
    EDGE = "Edge"
