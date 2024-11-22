import logging
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from ...data.services.auth_service import get_current_user
from ...schemas.message_schema import ErrorMessage
from ...schemas import tag_schema
from ...util.database import get_db
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse, StreamingResponse
from typing import Annotated, Optional
from ...data.services.tag_service import TagService
from fastapi_pagination import Page
from ...data.services.encoding_service import EncodingService
from ...exceptions.security_exceptions import (
    AuthenticationException,
    AuthorizationException,
)
from ...exceptions.bad_request_exceptions import ResourceNotFoundException
from uuid import UUID
from ...schemas import encoding_schema, message_schema
from ...data.services.user_service import UserService
from ...data.services.auth_service import get_current_user_without_exceptions
from ...data.services.public_profile_service import PublicProfileService
from ... import config
from fastapi_pagination import Page
from ...schemas import user_schemas
from ...exceptions.bad_request_exceptions import (
    InvalidDataException,
    InvalidFileTypeException,
    FileSizeExceededException,
)
from ...data.models.enums.ownership import Ownership
from ...schemas import change_schemas
from ...schemas import token_schemas
from ...data.services.auth_service import is_admin
from ...config import (
    allowed_encoding_types,
    allowed_signature_types,
    max_encoding_size,
    max_signature_size,
)
from ...schemas import team_schema
from ...util import cryptography
from datetime import datetime


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1/encodings",
    tags=["encodings"],
)


@router.get(
    "/tags",
    response_model=Page[tag_schema.TagOut],
    description="Get all tags",
    responses={
        200: {"description": "Tags retrieved", "model": tag_schema.TagOut},
        401: {"description": "Unauthorized", "model": ErrorMessage},
        404: {"description": "No tags found", "model": ErrorMessage},
    },
)
async def get_tags(
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[None, Depends(get_current_user)],
    name: Annotated[str | None, Query(...)] = None,
):
    _tag_service = TagService(db)
    logger.info("Getting tags")
    return _tag_service.get_tags(name)


@router.get(
    "/{encoding_id}/file",
    response_class=StreamingResponse,
    description="Get a encoding file",
    responses={
        401: {"description": "Unauthorized", "model": ErrorMessage},
        403: {"description": "Forbidden", "model": ErrorMessage},
        404: {"description": "Encoding not found", "model": ErrorMessage},
        404: {"description": "File not found", "model": ErrorMessage},
    },
)
async def get_encoding_file(
    encoding_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[
        None | user_schemas.User, Depends(get_current_user_without_exceptions)
    ],
):
    _encoding_service = EncodingService(db)
    encoding = _encoding_service.find_by_id(encoding_id)
    if encoding is None or encoding.file is None:
        raise ResourceNotFoundException()
    if not encoding.is_public and auth is None:
        raise AuthenticationException()
    if not encoding.is_public:
        for user_encoding in encoding.user_encodings:
            if user_encoding.user_id == auth.id:
                headers = {
                "Content-Disposition": f'attachment; filename="{encoding.name.strip()+"_encrypted.asp"}"'
                 }
                logger.info(f"Getting encoding file for user '{encoding.file}'")
                return StreamingResponse(
                    file_generator(encoding_file=encoding.file), media_type="text/plain", headers=headers
                )
        raise AuthorizationException()
# set the file name to the original file name
    headers = {
        "Content-Disposition": f'attachment; filename="{encoding.name.strip()+"_encrypted.asp"}"'
    }
    logger.info(f"Getting encoding file for user '{auth.username}'")

# return the file as a streaming response
    return StreamingResponse(
        file_generator(encoding_file=encoding.file), media_type="text/plain", headers=headers
    )


@router.get(
    "/{encoding_id}/changes",
    response_model=Page[change_schemas.ChangeOut],
    description="Get all changes for an encoding",
    responses={
        401: {"description": "Unauthorized", "model": ErrorMessage},
        403: {"description": "Forbidden", "model": ErrorMessage},
        404: {"description": "Encoding not found", "model": ErrorMessage},
    },
)
async def get_changes(
    encoding_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[
        None | user_schemas.User, Depends(get_current_user_without_exceptions)
    ],
):
    _encoding_service = EncodingService(db)
    encoding = _encoding_service.find_by_id(encoding_id)
    if encoding is None:
        raise ResourceNotFoundException()
    if encoding.is_public:
        return _encoding_service.get_changes(encoding_id)
    if auth is None:
        raise AuthenticationException()
    for user_encoding in encoding.user_encodings:  # one of authorized users
        if user_encoding.user_id == auth.id:
            return _encoding_service.get_changes(encoding_id)
    raise AuthorizationException()


@router.put(
    "/{encoding_id}/token",
    response_model=token_schemas.TokenEncodingOut,
    description="Create a token for an encoding",
    responses={
        401: {"description": "Unauthorized", "model": ErrorMessage},
        403: {"description": "Forbidden", "model": ErrorMessage},
        404: {"description": "Encoding not found", "model": ErrorMessage},
    },
)
async def create_token(
    encoding_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
):
    _encoding_service = EncodingService(db)
    encoding = _encoding_service.find_by_id(encoding_id)
    if encoding is None:
        raise ResourceNotFoundException()
    for user_encoding in encoding.user_encodings:
        if (
            user_encoding.user_id == auth.id
            and user_encoding.ownership == Ownership.OWNER
        ):
            return _encoding_service.create_token(encoding_id, auth.username)
    raise AuthorizationException()


@router.get(
    "/count",
    response_model=encoding_schema.EncodingCount,
    description="Get the number of encodings in the last year",
    responses={
        401: {"description": "Unauthorized", "model": ErrorMessage},
        403: {"description": "You must be a admin", "model": ErrorMessage},
    },
)
async def get_encoding_count(
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[user_schemas.User, Depends(is_admin)],
):
    _encoding_service = EncodingService(db)
    logger.info("Getting encoding count")
    return _encoding_service.get_encoding_count()


@router.get(
    "/{token}",
    response_model=encoding_schema.EncodingPublicDetail,
    description="get a encoding by token",
    responses={
        404: {
            "description": "encoding or user not found",
            "model": message_schema.ErrorMessage,
        }
    },
)
async def get_public_encoding(
    token: str,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[config.Settings, Depends(config.get_settings)],
):
    _encoding_service = EncodingService(db)
    logger.info(f"Getting encoding by token {token}")
    encoding = _encoding_service.get_encoding_by_token(token)
    if not encoding:
        raise ResourceNotFoundException()

    encoding = _encoding_service.get_encoding_by_encoding_id(
        encoding.id, settings.base_url
    )
    if encoding is None:
        raise ResourceNotFoundException()
    return encoding


@router.get(
    "/token/{token}/changes",
    response_model=Page[change_schemas.ChangeOut],
    description="Get all changes for an encoding",
    responses={
        401: {"description": "Unauthorized", "model": ErrorMessage},
        403: {"description": "Forbidden", "model": ErrorMessage},
        404: {"description": "Encoding not found", "model": ErrorMessage},
    },
)
async def get_changes(token: str, db: Annotated[Session, Depends(get_db)]):
    _encoding_service = EncodingService(db)
    logger.info(f"Getting encoding by token {token}")
    encoding = _encoding_service.get_encoding_by_token(token)
    if not encoding:
        raise ResourceNotFoundException()

    return _encoding_service.get_changes(encoding_id=encoding.id)


@router.delete(
    "/{encoding_id}/token",
    status_code=204,
    description="Delete an encoding sharing url",
    responses={
        401: {"description": "Unauthorized", "model": ErrorMessage},
        403: {"description": "Forbidden", "model": ErrorMessage},
        404: {"description": "Encoding not found", "model": ErrorMessage},
    },
)
async def delete_token(
    encoding_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
):
    _encoding_service = EncodingService(db)
    encoding = _encoding_service.find_by_id(encoding_id)
    if encoding is None:
        raise ResourceNotFoundException()
    for user_encoding in encoding.user_encodings:
        if (
            user_encoding.user_id == auth.id
            and user_encoding.ownership == Ownership.OWNER
        ):
            _encoding_service.delete_token(encoding_id, auth.username)
            return
    raise AuthorizationException()


@router.delete(
    "/{encoding_id}",
    status_code=204,
    description="Delete an encoding",
    responses={
        401: {"description": "Unauthorized", "model": ErrorMessage},
        403: {"description": "Forbidden", "model": ErrorMessage},
        404: {"description": "Encoding not found", "model": ErrorMessage},
    },
)
async def delete_encoding(
    encoding_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
):
    _encoding_service = EncodingService(db)
    encoding = _encoding_service.find_by_id(encoding_id)
    if encoding is None:
        raise ResourceNotFoundException()
    for user_encoding in encoding.user_encodings:
        if (
            user_encoding.user_id == auth.id
            and user_encoding.ownership == Ownership.OWNER
        ):
            _encoding_service.delete_encoding(encoding_id)
            return
    raise AuthorizationException()


@router.patch(
    "/{encoding_id}",
    status_code=204,
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
        403: {"description": "Invalid signature", "model": message_schema.ErrorMessage},
        422: {
            "description": "Invalid file type, or data",
            "model": message_schema.ErrorMessage,
        },
        413: {"description": "File is too large", "model": message_schema.ErrorMessage},
        409: {"description": "Conflict", "model": message_schema.ErrorMessage},
    },
)
async def update_encoding(
    encoding_id: UUID,
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    encoding_file: Annotated[Optional[UploadFile], File()] = None,
    signature_file: Annotated[UploadFile, File()] = None,
    name: Annotated[str, Form()] = None,
    description: Annotated[str, Form()] = None,
    is_public: Annotated[bool, Form()] = None,
    tags: Annotated[list[str], Form()] = [],
    teams: Annotated[list[str], Form()] = [],
    ownerships: Annotated[list[str], Form()] = [],
):
    _encoding_service = EncodingService(db)
    encoding = _encoding_service.find_by_id(encoding_id)
    if encoding is None:
        raise ResourceNotFoundException()
    if (encoding_file is not None and signature_file is None) or (
        encoding_file is None and signature_file is not None
    ):
        raise InvalidDataException()
    if (
        encoding_file is not None
        and encoding_file.content_type not in allowed_encoding_types
    ):
        raise InvalidFileTypeException(allowed_encoding_types)
    if (
        signature_file is not None
        and signature_file.content_type not in allowed_signature_types
    ):
        raise InvalidFileTypeException(allowed_signature_types)
    if encoding_file is not None and encoding_file.size > max_encoding_size:
        raise FileSizeExceededException(max_encoding_size)
    if signature_file is not None and signature_file.size > max_signature_size:
        raise FileSizeExceededException(max_signature_size)
    team_list: list[team_schema.TeamIn] = []
    tag_list: list[tag_schema.TagIn] = []
    if teams is not None and ownerships is not None:
        if len(teams) != len(ownerships):
            raise InvalidDataException(
                "The number of teams and ownerships must be the same"
            )
        try:
            for team, ownership in zip(teams, ownerships):
                ownership_enum = Ownership[ownership]
                team_list.append(
                    team_schema.TeamIn(name=team, ownership=ownership_enum)
                )
            for tag in tags:
                tag_list.append(tag_schema.TagIn(name=tag))
        except Exception as e:
            raise InvalidDataException("Invalid ownership or team")
    for user_encoding in encoding.user_encodings:
        if (
            user_encoding.user_id == auth.id
            and user_encoding.ownership == Ownership.OWNER
        ):
            encoding = encoding_schema.EncodingPatch(
                name=name,
                description=description,
                is_public=is_public,
                tags=tag_list,
                teams=team_list,
            )
            logger.debug(f"Updating encoding : {encoding}")
            logger.debug(f"Updating encoding for user '{auth.username}'")
            if encoding_file is not None and signature_file is not None:
                if not _encoding_service.check_encoding_signature(
                    encoding_file, signature_file, auth.id
                ):
                    raise AuthorizationException("Invalid signature")
            await _encoding_service.update_encoding(
                auth.id, encoding_id, encoding, signature_file, encoding_file
            )
            return
    raise AuthorizationException()


@router.post(
    "/verify",
    response_class=StreamingResponse,
    description="Verify an encoding signature and return the unencrypted file",
    responses={
        400: {"description": "Bad Request - Invalid Signature", "model": ErrorMessage},
        422: {
            "description": "Unprocessable Entity - Invalid Certificate",
            "model": ErrorMessage,
        },
        404: {"description": "Encoding or User not found", "model": ErrorMessage},
    },
)
async def verify_signature(
    encoding_file: UploadFile,
    certificate_file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
):
    _encoding_service = EncodingService(db)
    _user_service = UserService(db)
    user_id = cryptography.verify_certificate(certificate_file.file.read())
    logger.info(f"Verifying signature for user {user_id}")
    if user_id is None:
        raise InvalidDataException("Invalid certificate")
    user = _user_service.find_by_id(user_id)
    if user is None:
        raise ResourceNotFoundException("User not found")
    encoding = _encoding_service.find_by_user_id_and_encoding_file(
        user_id, encoding_file.file.read()
    )
    if encoding is None:
        raise ResourceNotFoundException("Encoding not found")
    user_owner_encoding = _encoding_service.get_user_owner(encoding.encoding_id)
    user_owner = _user_service.find_by_id(user_owner_encoding.user_id)
    unencrypted_file = _encoding_service.decrypt_encoding_file(
        encoding.encoding.file, user_owner.public_key
    )
    if unencrypted_file is None:
        raise InvalidDataException("Invalid signature")


# set the file name to the original file name
    headers = {
        "Content-Disposition": f'attachment; filename="{encoding.encoding.name+"_unencrypted.asp"}"'
    }

# return the file as a streaming response
    return StreamingResponse(
        file_generator(encoding_file=unencrypted_file),
        headers=headers,
        media_type="text/plain"
)

def file_generator(encoding_file):
    chunk_size = 1024 * 1024  # 1MB chunks
    for i in range(0, len(encoding_file), chunk_size):
        yield encoding_file[i : i + chunk_size]
