from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from . import tag_schema
from . import team_schema
from . import tag_schema
from datetime import date
from typing import Optional


class EncodingIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=32)
    description: str = Field(..., min_length=6, max_length=256)
    is_public: bool
    tags: list[tag_schema.TagIn] = []
    teams: list[team_schema.TeamIn] = []


class EncodingPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=32)
    description: Optional[str] = Field(None, min_length=6, max_length=256)
    is_public: Optional[bool] = None
    tags: list[tag_schema.TagIn] = []
    teams: list[team_schema.TeamIn] = []


class EncodingOut(BaseModel):
    name: str
    is_public: bool
    upload_date: date
    tags: list[tag_schema.TagOut] = []
    owner_username: str


class EncodingPublic(BaseModel):
    name: str
    description: str
    tags: list[tag_schema.TagOut] = []


class EncodingPublicDetail(EncodingOut):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    description: str
    user_encodings: list[team_schema.TeamPublic] = []
    file_url: str | None = None
    capability_token: str | None = None


class EncodingCount(BaseModel):
    count: list[tuple[int, int]]
