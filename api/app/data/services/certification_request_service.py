from ..repository.certification_request_repository import CertificationRequestRepository
from sqlalchemy.orm import Session
import os
from uuid import uuid4
from pathlib import Path
from fastapi import UploadFile
from ..models.enums.request_status import RequestStatus
from ...util import  storage
from ..repository.user_repository import UserRepository
from ..models.enums.document_type import DocumentType
from ...schemas.certification_request_schemas import (
    CertificationRequestResponse,
    CertificationRequestEdit,
    CertificationRequestCount,
)
import logging
from ...data.repository.encoding_repository import EncodingRepository

logger = logging.getLogger(__name__)


class CertificationRequestService:
    def __init__(self, db: Session):
        self.db = db
        self.certification_request_repository = CertificationRequestRepository(db)
        self.user_repository = UserRepository(db)
        self.encoding_repository = EncodingRepository(db)

    def find_by_user_id(self, user_id):
        certification = self.certification_request_repository.find_by_user_id(user_id)
        if certification is None:
            return None
        certification_model = CertificationRequestResponse.model_validate(certification)
        certification_model.front_url = storage.get_user_document_url(
            certification.document_front, "/v1/certification-requests/"
        )
        certification_model.back_url = storage.get_user_document_url(
            certification.document_back, "/v1/certification-requests/"
        )
        return certification_model

    def save_certification_request(
        self,
        user_id,
        type: DocumentType,
        document_front: UploadFile,
        document_back: UploadFile,
    ):
        front_content = document_front.file.read()
        back_content = document_back.file.read()
        front_id = uuid4()
        back_id = uuid4()
        certification_request_id = uuid4()
        base_directory = os.path.join(os.getcwd(), "resources")
        base_directory = os.path.join(base_directory, "certifications_files")
        new_directory = os.path.join(base_directory, str(certification_request_id))
        front_path = os.path.join(
            new_directory, str(front_id) + Path(document_front.filename).suffix
        )
        back_path = os.path.join(
            new_directory, str(back_id) + Path(document_back.filename).suffix
        )

        relative_front_path = os.path.relpath(front_path, start=base_directory)
        relative_back_path = os.path.relpath(back_path, start=base_directory)

        self.certification_request_repository.save_certification_request(
            user_id,
            relative_front_path,
            relative_back_path,
            type,
            certification_request_id,
        )
        storage.save_user_documents(
            front_content, back_content, front_path, back_path, new_directory
        )

        self.db.commit()

    def delete_certification_request(self, request_id):
        self.certification_request_repository.delete_certification_request_by_id(
            request_id
        )
        storage.delete_directory_user_documents(str(request_id))

        self.db.commit()

    def get_certification_request_count(self):
        approved_count = self.certification_request_repository.get_certification_request_count_by_status(
            RequestStatus.APPROVED
        )
        denied_count = self.certification_request_repository.get_certification_request_count_by_status(
            RequestStatus.REJECTED
        )
        pending_count = self.certification_request_repository.get_certification_request_count_by_status(
            RequestStatus.PENDING
        )
        return CertificationRequestCount(
            approved=approved_count, denied=denied_count, pending=pending_count
        )

    def get_certification_request_count_by_status(self, status):
        return self.certification_request_repository.get_certification_request_count_by_status(
            status
        )

    def get_certification_request_by_id(self, request_id):
        return self.certification_request_repository.get_certification_request_by_id(
            request_id
        )

    def update_certification_request(
        self, certification_id, request: CertificationRequestEdit
    ):
        certification = self.certification_request_repository.find_by_id(
            certification_id
        )
        user = self.user_repository.find_by_id(certification.user_id)
        if certification is None:
            return None
        if (
            request.status == RequestStatus.REJECTED
            or request.status == RequestStatus.PENDING
        ):
            user.public_key = None
            self.encoding_repository.delete_encodings_by_user_id_owner(user.id)
            self.user_repository.update_user(user)
        self.certification_request_repository.update_certification_request(
            certification.id, request.denied_reason, request.status
        )
        logger.debug("Certification request updated")
        logger.debug("new status: " + request.status.value)

        self.db.commit()
