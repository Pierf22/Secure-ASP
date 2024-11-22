from pydantic import BaseModel, ConfigDict
from ..data.models.enums.document_type import DocumentType
from ..data.models.enums.request_status import RequestStatus
import uuid
from typing import Optional



class CertificationRequest(BaseModel):
    document_type: DocumentType


class CertificationRequestResponse(BaseModel):
    id: uuid.UUID
    type: DocumentType
    status: RequestStatus
    denied_reason: Optional[str]
    front_url: str = "url"
    back_url: str = "url"
    model_config = ConfigDict(from_attributes=True)


class CertificationRequestCount(BaseModel):
    approved: int
    denied: int
    pending: int


class CertificationRequestEdit(BaseModel):
    status: RequestStatus
    denied_reason: Optional[str] = None
