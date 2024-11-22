from ...util.database import Base
from sqlalchemy import  Integer, String, ForeignKey, Uuid, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.sql import func


class Change(Base):
    __tablename__ = "change"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(32), nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(), nullable=False, default=func.now()
    )
    encoding_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("encoding.id"))
    encoding: Mapped["Encoding"] = relationship(back_populates="changes")  # type: ignore
