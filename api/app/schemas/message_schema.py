from pydantic import BaseModel
from ..data.models.enums.sort_type import Sort


class ErrorMessage(BaseModel):
    status_code: int
    message: str
    timestamp: str
    path: str


class SortType(BaseModel):
    sort: Sort


class Message(BaseModel):
    message: str
    timestamp: str
