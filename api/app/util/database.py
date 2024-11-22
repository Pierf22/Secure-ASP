from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from ..config import get_settings
import logging

logger = logging.getLogger(__name__)

engine = create_engine(get_settings().sqlalchemy_database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    logger.debug(f"Creating a new database session {db}")
    try:
        yield db
    finally:
        logger.debug(f"Closing database session {db}")
        db.close()


class Base(DeclarativeBase):
    pass


def database_start_up():

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
