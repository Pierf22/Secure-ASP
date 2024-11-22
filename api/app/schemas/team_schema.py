from pydantic import BaseModel, Field, ConfigDict
from ..data.models.enums.ownership import Ownership
from .user_schemas import UserUsername


class TeamIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=32)
    ownership: Ownership


class TeamOut(BaseModel):
    ownership: Ownership


class TeamPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ownership: Ownership
    user: UserUsername
