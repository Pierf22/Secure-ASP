from sqlalchemy import  Uuid, ForeignKey,  String,  Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ...util.database import Base
import uuid
from .enums.document_type import DocumentType
from .enums.request_status import RequestStatus


class CertificationRequest(Base):
    __tablename__ = "certification_request"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus), nullable=False, default=RequestStatus.PENDING
    )
    document_back: Mapped[str] = mapped_column(String(512), nullable=False)
    document_front: Mapped[str] = mapped_column(String(512), nullable=False)
    denied_reason: Mapped[str] = mapped_column(String(512), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("user.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship(back_populates="certification_request")  # type: ignore
