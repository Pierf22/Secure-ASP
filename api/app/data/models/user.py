from sqlalchemy import Boolean, Column, ForeignKey, Uuid, String, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from ...util.database import Base

user_role_table = Table(
    "user_role",
    Base.metadata,
    Column("user", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("role", ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(
        String(320), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    oauth2_user: Mapped[bool] = mapped_column(Boolean, default=False)
    hashed_password: Mapped[str] = mapped_column(String(72), nullable=False)
    public_key: Mapped[str] = mapped_column(String(512), nullable=True)
    roles: Mapped[set["Role"]] = relationship(secondary=user_role_table)  # type: ignore
    invalidated_tokens: Mapped[set["InvalidatedToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # type: ignore
    certification_request: Mapped["CertificationRequest"] = relationship(back_populates="user", cascade="all, delete-orphan")  # type: ignore
    user_encodings: Mapped[set["UserEncoding"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # type: ignore

    def roles_as_dict(self):
        return [role.name for role in self.roles]
