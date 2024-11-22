from pydantic import BaseModel
from ..data.models.enums.ownership import Ownership
from .encoding_schema import EncodingOut, EncodingPublic


class UserEncodingOut(BaseModel):
    ownership: Ownership
    encoding: EncodingOut


class UserEncodingPublic(BaseModel):
    encoding: EncodingPublic


class UserEncodingPublicDetail(BaseModel):
    ownership: Ownership
    encoding: EncodingPublic
