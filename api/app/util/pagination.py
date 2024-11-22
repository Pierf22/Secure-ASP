from fastapi_pagination import add_pagination
from typing import TypeVar
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


def add(app):
    add_pagination(app)
    logger.info("Pagination added")
