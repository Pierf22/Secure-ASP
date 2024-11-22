from fastapi import APIRouter, Depends
import logging
from sqlalchemy.orm import Session
from typing import Annotated
from app.data.services.user_service import UserService
from app.schemas import (
    user_schemas,
    message_schema,
    user_encoding_schema,
)
from app.exceptions.bad_request_exceptions import ResourceNotFoundException
from app.data.services.public_profile_service import PublicProfileService
from app.util.database import get_db
from app import config
from fastapi_pagination import Page


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/public-profiles", tags=["public-profile"])


@router.get(
    "/{username}",
    response_model=user_schemas.UserPublic,
    description="get the public user info ",
    responses={
        404: {"description": "User not found", "model": message_schema.ErrorMessage}
    },
)
async def get_public_profile(username: str, db: Annotated[Session, Depends(get_db)]):
    _public_profile_service = PublicProfileService(db)
    _user_service = UserService(db)
    if not _user_service.is_not_only_admin_by_username(username):
        raise ResourceNotFoundException()
    user = _public_profile_service.get_public_profile(username)
    if user is None:
        raise ResourceNotFoundException()
    return user


@router.get(
    "/{username}/encodings",
    response_model=Page[user_encoding_schema.UserEncodingPublic],
    description="get the firs public encodings",
    responses={
        404: {
            "description": "encodings or user not found",
            "model": message_schema.ErrorMessage,
        }
    },
)
async def get_public_encodings(username: str, db: Annotated[Session, Depends(get_db)]):
    _public_profile_service = PublicProfileService(db)
    _user_service = UserService(db)
    if not _user_service.is_not_only_admin_by_username(username):
        raise ResourceNotFoundException()
    encodings = _public_profile_service.get_public_encodings(username)
    if encodings is None or encodings.items == []:
        raise ResourceNotFoundException()
    return encodings
