from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from ...data.services.auth_service import get_current_user, is_admin
from ...data.models.enums.document_type import DocumentType
from ...data.models.enums.request_status import RequestStatus
from ...schemas import message_schema
from sqlalchemy.orm import Session
from ...util.database import get_db
from ...util import storage
from typing import Annotated
from ...schemas import user_schemas
from ...schemas.certification_request_schemas import CertificationRequestCount
from ...data.services.certification_request_service import CertificationRequestService
from ...exceptions.bad_request_exceptions import (
    ResourceNotFoundException,
    BadRequestException,
)
from ...exceptions.security_exceptions import AuthorizationException
import logging
import uuid
import os
from ...schemas import certification_request_schemas

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1/certification-requests",
    tags=["certification-requests"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/document-types",
    response_model=list[str],
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        }
    },
)
async def get_document_types():
    logger.debug("Retrieving document types")
    return [doc_type.value for doc_type in DocumentType]


@router.get(
    "/status",
    response_model=list[str],
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        }
    },
)
async def get_request_status():
    logger.debug("Retrieving request status")
    return [status.value for status in RequestStatus]


@router.get(
    "/count",
    response_model=CertificationRequestCount,
    description="Retrieve the count of certification requests for each status.",
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
async def get_certification_request_count(
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[user_schemas.User, Depends(is_admin)],
):
    _certification_request_service = CertificationRequestService(db)
    return _certification_request_service.get_certification_request_count()


@router.delete(
    "/{request_id}",
    status_code=204,
    description="Delete a certification request with status Pending by id",
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        }
    },
)
async def delete_certification_request(
    request_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
):
    _certification_request_service = CertificationRequestService(db)
    certification_request = (
        _certification_request_service.get_certification_request_by_id(request_id)
    )
    if not certification_request:
        return
    if certification_request.user_id != auth.id:
        raise AuthorizationException("You can only delete your own requests")
    if certification_request.status == RequestStatus.APPROVED:
        raise AuthorizationException("You can only delete pending or rejected requests")
    _certification_request_service.delete_certification_request(request_id)


@router.get(
    "/{certification_id}/{document}",
    response_class=FileResponse,
    description="Retrieve a document from a certification request by id",
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
        403: {
            "description": "Unauthorized, you should be a admin",
            "model": message_schema.ErrorMessage,
        },
        404: {
            "description": "Certification request or file not found",
            "model": message_schema.ErrorMessage,
        },
        200: {
            "description": "Document retrieved successfully",
            "content": {"application/octet-stream": {}},
        },
    },
)
async def get_certification_document(
    certification_id: uuid.UUID,
    document: str,
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[user_schemas.User, Depends(is_admin)],
):
    _certification_request_service = CertificationRequestService(db)
    certification_request = (
        _certification_request_service.get_certification_request_by_id(certification_id)
    )
    file_path = os.path.join(certification_id.__str__(), document)
    logger.debug(f"Retrieving document {file_path} ")
    if not certification_request:
        raise ResourceNotFoundException("Certification request not found")
    if (
        certification_request.document_front == file_path
        or certification_request.document_back == file_path
    ):

        path = storage.get_path(file_path)
        logger.debug(f"Document {path} found")
        if not path:
            raise ResourceNotFoundException("File not found")
        return FileResponse(path)
    else:
        raise ResourceNotFoundException("File not found")


@router.put(
    "/{certification_id}",
    status_code=204,
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": message_schema.ErrorMessage,
        },
        403: {"description": "Unauthorized", "model": message_schema.ErrorMessage},
        400: {
            "description": "Denied reason can only be set if status is Rejected",
            "model": message_schema.ErrorMessage,
        },
    },
)
async def update_certification_request(
    certification_id: uuid.UUID,
    request: certification_request_schemas.CertificationRequestEdit,
    auth: Annotated[user_schemas.User, Depends(is_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    _certification_request_service = CertificationRequestService(db)
    if request.denied_reason is not None and request.status != RequestStatus.REJECTED:
        raise BadRequestException("Denied reason can only be set if status is Rejected")
    _certification_request_service.update_certification_request(
        certification_id, request
    )
