import enum


class Ownership(str, enum.Enum):
    OWNER = "Owner"
    SHARED = "Shared"
