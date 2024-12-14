from enum import Enum


class UserRole(str, Enum):
    SUPERUSER = "superuser"
    NORMAL = "normal"


class TipType(str, Enum):
    PREPARATION = "preparation"  # 손질 팁
    COOKING = "cooking"  # 조리 팁
    FINISHING = "finishing"  # 마무리 팁


class ImageSize(str, Enum):
    X1 = "1x"
    X2 = "2x"
    X3 = "3x"


class TimerFeedbackType(str, Enum):
    GOOD = "good"
    SKIP = "skip"
    BAD = "bad"


class ColorTheme(str, Enum):
    BLACK = "black"
    WHITE = "white"
