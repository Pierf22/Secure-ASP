from enum import Enum


class UserEncodingSort(str, Enum):
    UPLOAD_DATE = "upload-date"
    NAME = "name"
    VISIBILITY = "visibility"
    ROLE = "role"
