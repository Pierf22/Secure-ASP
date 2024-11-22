from sqlalchemy import Uuid, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ...util.database import Base
import uuid


class InvalidatedToken(Base):
    __tablename__ = "invalidated_token"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    token: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    expires_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship(back_populates="invalidated_tokens")  # type: ignore
