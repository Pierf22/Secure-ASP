from pydantic import BaseModel
from datetime import datetime


class ChangeOut(BaseModel):
    description: str
    updated_by: str
    timestamp: datetime
