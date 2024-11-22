from ...util.database import Base
from sqlalchemy import ForeignKey, Uuid, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .enums.ownership import Ownership
import uuid


class UserEncoding(Base):
    __tablename__ = "user_encoding"
    ownership: Mapped[Ownership] = mapped_column(Enum(Ownership), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("user.id"), primary_key=True
    )

    user: Mapped["User"] = relationship(back_populates="user_encodings")  # type: ignore
    encoding_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("encoding.id"), primary_key=True
    )
    encoding: Mapped["Encoding"] = relationship(back_populates="user_encodings")  # type: ignore
