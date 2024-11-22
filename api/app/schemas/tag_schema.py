from pydantic import BaseModel, ConfigDict


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class TagIn(BaseModel):
    name: str
