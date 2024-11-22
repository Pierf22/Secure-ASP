from ...util.database import Base
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    ForeignKey,
    Uuid,
    String,
    Boolean,
    Date,
    LargeBinary,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

encoding_tag_table = Table(
    "encoding_tag",
    Base.metadata,
    Column("encoding", ForeignKey("encoding.id"), primary_key=True),
    Column("tag", ForeignKey("tag.id"), primary_key=True),
)


class Encoding(Base):
    __tablename__ = "encoding"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    upload_date: Mapped[Date] = mapped_column(
        Date(), nullable=False, default=func.now()
    )
    file: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=False)
    capability_token: Mapped[str] = mapped_column(
        String(512), unique=True, nullable=True
    )
    owner_username: Mapped[str] = mapped_column(String(32), nullable=False)
    user_encodings: Mapped[set["UserEncoding"]] = relationship(back_populates="encoding", cascade="all, delete-orphan")  # type: ignore
    changes: Mapped[set["Change"]] = relationship(back_populates="encoding", cascade="all, delete-orphan")  # type: ignore
    tags: Mapped[set["Tag"]] = relationship(secondary=encoding_tag_table, back_populates="encodings")  # type: ignore
