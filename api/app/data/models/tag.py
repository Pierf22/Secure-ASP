from ...util.database import Base
from sqlalchemy import  Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from ..models.encoding import encoding_tag_table
from sqlalchemy.orm import relationship


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    encodings: Mapped[set["Encoding"]] = relationship(secondary=encoding_tag_table, back_populates="tags")  # type: ignore
