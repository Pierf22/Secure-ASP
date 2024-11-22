from sqlalchemy.orm import Session
from ..models import certification_request as certification_request_model
from uuid import UUID
from ..models.enums.document_type import DocumentType


class CertificationRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_user_id(self, user_id: UUID):
        return (
            self.db.query(certification_request_model.CertificationRequest)
            .filter(certification_request_model.CertificationRequest.user_id == user_id)
            .first()
        )

    def save_certification_request(
        self,
        user_id: UUID,
        relative_front_path: str,
        relative_back_path: str,
        type: DocumentType,
        certification_request_uuid: UUID,
    ):
        db_certification_request = certification_request_model.CertificationRequest(
            user_id=user_id,
            type=type,
            document_front=relative_front_path,
            document_back=relative_back_path,
            id=certification_request_uuid,
        )
        self.db.add(db_certification_request)
        self.db.flush()

    def delete_certification_request(self, user_id: UUID):
        self.db.query(certification_request_model.CertificationRequest).filter(
            certification_request_model.CertificationRequest.user_id == user_id
        ).delete()
        self.db.flush()
        return

    def get_certification_request_count(self):
        return self.db.query(certification_request_model.CertificationRequest).count()

    def get_certification_request_count_by_status(self, status):
        return (
            self.db.query(certification_request_model.CertificationRequest)
            .filter(certification_request_model.CertificationRequest.status == status)
            .count()
        )

    def get_certification_request_by_id(self, request_id):
        return (
            self.db.query(certification_request_model.CertificationRequest)
            .filter(certification_request_model.CertificationRequest.id == request_id)
            .first()
        )

    def delete_certification_request_by_id(self, request_id):
        self.db.query(certification_request_model.CertificationRequest).filter(
            certification_request_model.CertificationRequest.id == request_id
        ).delete()
        self.db.flush()
        return

    def update_certification_request(self, request_id, denied_reason, status):
        certification_request = self.get_certification_request_by_id(request_id)
        certification_request.status = status
        certification_request.denied_reason = denied_reason
        self.db.flush()

    def find_by_id(self, request_id):
        return (
            self.db.query(certification_request_model.CertificationRequest)
            .filter(certification_request_model.CertificationRequest.id == request_id)
            .first()
        )
