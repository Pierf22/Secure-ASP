from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class Token(BaseModel):
    token: str
    expires_at: datetime
    user_id: UUID


class TokenData(BaseModel):
    user_id: UUID
    expires_at: datetime
    roles: set[str] | None


class TokenEncodingOut(BaseModel):
    token: str
