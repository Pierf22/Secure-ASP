import enum


class DocumentType(str, enum.Enum):
    PASSPORT = "Passport"
    IDENTITY_CARD = "Identity Card"
    DRIVER_LICENSE = "Driver's License"
