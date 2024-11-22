from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ...util.database import Base


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    users: Mapped[set["User"]] = relationship(secondary="user_role", back_populates="roles")  # type: ignore
