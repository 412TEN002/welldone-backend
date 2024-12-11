from enum import Enum


class UserRole(str, Enum):
    SUPERUSER = "superuser"
    NORMAL = "normal"
