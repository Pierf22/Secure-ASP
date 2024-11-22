from enum import Enum


class UserSort(str, Enum):
    USERNAME = "username"
    EMAIL = "email"
    FULL_NAME = ("full-name",)
    DISABLED = ("disabled",)
    OAUTH2_USER = ("oauth2-user",)
    ROLES = ("roles",)
    CERTIFICATION_STATUS = ("certification-status",)
