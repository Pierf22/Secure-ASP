from fastapi import APIRouter, Depends, UploadFile, Form, Response, File
from typing import Annotated, Tuple
from ...data.models.enums.ownership import Ownership
from ...schemas import user_schemas
from ...data.services.auth_service import get_current_user, is_admin, is_admin_
import uuid
from datetime import date
from ...util import cryptography
from ...data.models.enums.user_encoding_sort import UserEncodingSort
from ...schemas import certification_request_schemas
from ...data.models.enums.document_type import DocumentType
from ...data.models.enums.request_status import RequestStatus
from ...schemas import message_schema
from fastapi.responses import StreamingResponse
from ...util.database import get_db
from sqlalchemy.orm import Session
from fastapi import Query
from fastapi_pagination import Page
from ...data.services.user_service import UserService
from ...data.models.enums.sort_type import Sort
from ...data.models.enums.user_sort import UserSort
from ...data.services.certification_request_service import CertificationRequestService
from ...schemas import encoding_schema
from ...schemas import user_encoding_schema
from ...exceptions.security_exceptions import AuthorizationException, NotAdminException
from ...exceptions.bad_request_exceptions import (
    InvalidFileTypeException,
    FileSizeExceededException,
    ConflictException,
    ResourceNotFoundException,
    InvalidDataException,
)
import logging
from ...data.services.auth_service import get_current_user_without_exceptions
from ...data.services.public_profile_service import PublicProfileService
from ... import config
from ...config import (
    allowed_types,
    max_file_size,
    allowed_encoding_types,
    allowed_signature_types,
    max_encoding_size,
    max_signature_size,
    allowed_mime_type_csr,
    max_file_size_csr,
)
from ...schemas import team_schema, tag_schema
from ...data.services.encoding_service import EncodingService

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/v1/users", tags=["users"])


@router.get(
    "/usernames",
    description="Method for a user to search another user by username",
    response_model=Page[user_schemas.UserUsername],
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        }
    },
)
async def get_usernames(
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
    value: Annotated[str | None, Query(...)] = None,
):
    _user_service = UserService(db)
    logger.debug(f"Searching for users with username '{value}'")
    return _user_service.get_usernames(value, auth.id)


@router.post(
    "/{user_id}/certification-request",
    status_code=201,
    responses={
        422: {"description": "Invalid file type", "model": message_schema.ErrorMessage},
        413: {"description": "File is too large", "model": message_schema.ErrorMessage},
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
        409: {
            "description": "Certificated request already exists",
            "model": message_schema.ErrorMessage,
        },
        403: {"description": "Unauthorized", "model": message_schema.ErrorMessage},
        201: {"description": "Certification request created successfully."},
    },
)
async def create_certification_request(
    response: Response,
    user_id: uuid.UUID,
    front: Annotated[UploadFile, File()],
    back: Annotated[UploadFile, File()],
    type: Annotated[DocumentType, Form()],
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    _certification_request_service = CertificationRequestService(db)
    if auth.id != user_id:
        raise AuthorizationException()
    if (
        front.content_type not in allowed_types
        or back.content_type not in allowed_types
    ):
        raise InvalidFileTypeException(allowed_types)
    if front.size > max_file_size or back.size > max_file_size:
        raise FileSizeExceededException(max_file_size)
    if _certification_request_service.find_by_user_id(user_id):
        raise ConflictException("Certificated request already exists")
    _certification_request_service.save_certification_request(
        user_id, type, front, back
    )
    logger.debug(f"Certification request created for user '{auth.username}'")
    response.status_code = 201


@router.get(
    "/{user_id}/certification-request",
    response_model=certification_request_schemas.CertificationRequestResponse,
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
        403: {"description": "Unauthorized", "model": message_schema.ErrorMessage},
        404: {
            "description": "Certification request not found",
            "model": message_schema.ErrorMessage,
        },
    },
)
async def get_certification_request(
    user_id: uuid.UUID,
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    _certification_request_service = CertificationRequestService(db)
    if auth.id != user_id and not is_admin_(auth):
        raise AuthorizationException()
    certification_request = _certification_request_service.find_by_user_id(user_id)
    if not certification_request:
        logger.debug(f"Certification request not found for user '{auth.username}'")
        raise ResourceNotFoundException()
    return certification_request


@router.get(
    "/count",
    description="A method that returns the count of users by status (disabled, active) and authentication method (OAuth2, username/password).",
    response_model=user_schemas.UserCount,
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
        403: {
            "description": "Unauthorized, you must be a admin",
            "model": message_schema.ErrorMessage,
        },
    },
)
async def get_user_count(
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[user_schemas.User, Depends(is_admin)],
):
    _user_service = UserService(db)
    return _user_service.get_user_count()


@router.get(
    "/{user_id}",
    response_model=user_schemas.UserBase,
    responses={
        403: {"description": "Unauthorized", "model": message_schema.ErrorMessage},
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
    },
)
async def get_user(
    user_id: uuid.UUID,
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    _user_service = UserService(db)
    if auth.id != user_id:
        raise AuthorizationException()

    return _user_service.find_by_id(user_id)


@router.delete(
    "/{user_id}",
    status_code=204,
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
        404: {"description": "User not found", "model": message_schema.ErrorMessage},
        403: {"description": "Unauthorized", "model": message_schema.ErrorMessage},
    },
)
async def delete_user(
    user_id: uuid.UUID,
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    _user_service = UserService(db)
    if auth.id != user_id:
        raise AuthorizationException()
    _user_service.delete_user(user_id)


@router.patch(
    "/{user_id}",
    status_code=204,
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
        403: {"description": "Unauthorized", "model": message_schema.ErrorMessage},
        409: {
            "description": "User already exists",
            "model": message_schema.ErrorMessage,
        },
    },
)
async def update_user(
    user_id: uuid.UUID,
    user: user_schemas.UserEdit,
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    _user_service = UserService(db)
    conflict_exception = ConflictException("User already exists")
    if auth.id != user_id and not is_admin_(auth):
        raise AuthorizationException()
    if not is_admin_(auth) and (user.disabled is not None or user.roles is not None):
        raise NotAdminException()
    if user.email is not None and _user_service.find_user_by_email(user.email):
        raise conflict_exception

    if user.username is not None and _user_service.find_user_by_username(user.username):
        raise conflict_exception
    db_user = _user_service.find_by_id(user_id)
    if db_user.oauth2_user:
        raise AuthorizationException("OAuth2 users cannot be updated")
    _user_service.update_user(user_id, user)


@router.get(
    "",
    response_model=Page[user_schemas.UserOut],
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
        403: {
            "description": "Unauthorized, you should be a admin",
            "model": message_schema.ErrorMessage,
        },
    },
)
async def get_users(
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[user_schemas.User, Depends(is_admin)],
    order: Annotated[Sort | None, Query(...)] = None,
    sort: Annotated[UserSort | None, Query(...)] = None,
    username: Annotated[str | None, Query(...)] = None,
    email: Annotated[str | None, Query(...)] = None,
    full_name: Annotated[str | None, Query(alias="full-name")] = None,
):
    if sort is not None and order is None:
        order = Sort.ASC
    _user_service = UserService(db)
    filters = {}
    if username is not None:
        filters["username"] = username
    if email is not None:
        filters["email"] = email
    if full_name is not None:
        filters["full_name"] = full_name
    return _user_service.get_users(order, sort, filters)


@router.post(
    "/{user_id}/encodings",
    status_code=201,
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
async def create_encoding(
    user_id: uuid.UUID,
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    encoding_file: Annotated[UploadFile, File()],
    signature_file: Annotated[UploadFile, File()],
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    is_public: Annotated[bool, Form()],
    tags: Annotated[list[str], Form()] = [],
    teams: Annotated[list[str], Form()] = [],
    ownerships: Annotated[list[str], Form()] = [],
):
    _encoding_service = EncodingService(db)
    if _encoding_service.exists_by_name_and_user_id(name, user_id):
        raise ConflictException("Encoding already exists")
    if auth.id != user_id:
        raise AuthorizationException()
    if encoding_file.content_type not in allowed_encoding_types:
        raise InvalidFileTypeException(allowed_encoding_types)
    if signature_file.content_type not in allowed_signature_types:
        raise InvalidFileTypeException(allowed_signature_types)
    if encoding_file.size > max_encoding_size:
        raise FileSizeExceededException(max_encoding_size)
    if signature_file.size > max_signature_size:
        raise FileSizeExceededException(max_signature_size)
    team_list: list[team_schema.TeamIn] = []
    tag_list: list[tag_schema.TagIn] = []
    if len(teams) != len(ownerships):
        raise InvalidDataException(
            "The number of teams and ownerships must be the same"
        )
    try:
        for team, ownership in zip(teams, ownerships):
            ownership_enum = Ownership[ownership]
            team_list.append(team_schema.TeamIn(name=team, ownership=ownership_enum))
        for tag in tags:
            tag_list.append(tag_schema.TagIn(name=tag))
    except Exception as e:
        raise InvalidDataException("Invalid ownership or team")
    encoding = encoding_schema.EncodingIn(
        name=name,
        description=description,
        is_public=is_public,
        tags=tag_list,
        teams=team_list,
    )
    logger.debug(f"Creating encoding : {encoding}")
    logger.debug(f"Creating encoding for user '{auth.username}'")
    if not _encoding_service.check_encoding_signature(
        encoding_file, signature_file, user_id
    ):
        raise AuthorizationException("Invalid signature")
    await _encoding_service.save_encoding(
        user_id, encoding, signature_file, encoding_file
    )


@router.get(
    "/{user_id}/encodings",
    response_model=Page[user_encoding_schema.UserEncodingOut],
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
        403: {"description": "Unauthorized", "model": message_schema.ErrorMessage},
    },
)
async def get_user_encodings(
    user_id: uuid.UUID,
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    order: Annotated[Sort | None, Query(...)] = None,
    sort: Annotated[UserEncodingSort | None, Query(...)] = None,
    name: Annotated[str | None, Query(...)] = None,
    tags: Annotated[list[str] | None, Query(...)] = None,
    start_upload_date: Annotated[
        date | None, Query(..., alias="start-upload-date")
    ] = None,
    end_upload_date: Annotated[date | None, Query(..., alias="end-upload-date")] = None,
):
    _encoding_service = EncodingService(db)
    if auth.id != user_id:
        raise AuthorizationException()

    if sort is not None and order is None:
        order = Sort.ASC
    filters = {}
    if name is not None:
        filters["name"] = name
    if start_upload_date is not None:
        filters["start_upload_date"] = start_upload_date
    if end_upload_date is not None:
        filters["end_upload_date"] = end_upload_date
    if tags is not None:
        filters["tags"] = tags
    return _encoding_service.get_user_encodings(user_id, order, sort, filters)


@router.get(
    "/{username}/{encoding_name}",
    response_model=encoding_schema.EncodingPublicDetail,
    description="get the public encoding or private if user is allowed info",
    responses={
        404: {
            "description": "encoding or user not found",
            "model": message_schema.ErrorMessage,
        }
    },
)
async def get_public_encoding(
    username: str,
    encoding_name: str,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[config.Settings, Depends(config.get_settings)],
    auth: Annotated[
        None | user_schemas.User, Depends(get_current_user_without_exceptions)
    ],
):
    _public_profile_service = PublicProfileService(db)
    _encoding_service = EncodingService(db)
    _user_service = UserService(db)

    if auth is None:
        encoding = _public_profile_service.get_public_encoding(
            username, encoding_name, settings.base_url
        )
        if encoding is None:
            raise ResourceNotFoundException()
    else:
        logger.debug(
            f"User '{auth.username}' is trying to get encoding '{encoding_name}'"
        )
        encoding = _encoding_service.get_encoding_by_user_id_and_name(
            auth.id, encoding_name, settings.base_url, username
        )
        if encoding is None:
            raise ResourceNotFoundException()
    return encoding


@router.post(
    "/{user_id}/csr-request",
    status_code=200,
    response_class=StreamingResponse,
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
        403: {"description": "Unauthorized", "model": message_schema.ErrorMessage},
    },
)
async def create_csr_request(
    user_id: uuid.UUID,
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile,
):
    _user_service = UserService(db)
    _certification_service = CertificationRequestService(db)
    if auth.id != user_id:
        raise AuthorizationException()
    current_user = _user_service.find_by_id(user_id)
    certification_request = _certification_service.find_by_user_id(user_id)
    if (
        not certification_request
        or certification_request.status != RequestStatus.APPROVED
    ):
        raise ResourceNotFoundException(
            "Certification request not found or not approved"
        )
    logger.debug(f"file content type: {file.content_type}")
    if file.content_type != allowed_mime_type_csr:
        raise InvalidFileTypeException(".pem file required")

    if file.size > max_file_size_csr:
        raise FileSizeExceededException("File size exceeds the 10MB limit")
    cert, key = cryptography.generate_certificate(user_id, file.file.read().decode())
    _user_service.update_public_key(user_id, key)
    return StreamingResponse(
        content=cert,
        media_type="application/x-pem-file",
        headers={
            "Content-Disposition": f"attachment; filename={current_user.username}.pem"
        },
    )
