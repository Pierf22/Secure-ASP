from ...schemas import user_schemas
from fastapi import Depends
from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordBearer
from ...util import token
from ..repository.user_repository import UserRepository
from ..repository.invalidated_token_repository import InvalidatedTokenRepository
from sqlalchemy.orm import Session
from ...util.database import get_db
from ...util import bcrypt
from ...exceptions.security_exceptions import (
    TokenException,
    NotAdminException,
    AuthenticationException,
    UserDisabledException,
)
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login", auto_error=False)


class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.invalidated_token_repository = InvalidatedTokenRepository(db)

    def authenticate_user(self, username: str, password: str):
        user = self.user_repository.find_user_by_username(username)
        if not user or user.oauth2_user:
            raise AuthenticationException()
        if user.disabled:
            raise UserDisabledException()
        if not bcrypt.verify_password(password, user.hashed_password):
            raise AuthenticationException()
        return user


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token_val: Annotated[str, Depends(oauth2_scheme)],
):
    _invalidated_token_repository = InvalidatedTokenRepository(db)
    _user_repository = UserRepository(db)
    if _invalidated_token_repository.is_token_invalid(token_val):
        logger.debug(f"A user tried to access with an invalidated token")
        raise TokenException()
    token_data = token.get_token_data(token_val)
    user_db = _user_repository.get_user_from_id_and_roles(
        user_id=token_data.user_id, roles=token_data.roles
    )
    if not user_db:
        logger.debug(f"User with id {token_data.user_id} not found in the system")
        raise AuthenticationException()
    if user_db.disabled:
        logger.debug(f"User '{user_db.username}' is disabled")
        raise UserDisabledException()
    return user_db


def get_current_user_without_exceptions(
    db: Annotated[Session, Depends(get_db)],
    token_val: Annotated[Optional[str], Depends(oauth2_scheme)],
):
    _invalidated_token_repository = InvalidatedTokenRepository(db)
    _user_repository = UserRepository(db)
    if not token_val:
        return None
    if _invalidated_token_repository.is_token_invalid(token_val):
        logger.debug(f"A user tried to access with an invalidated token")
        return None
    token_data = token.get_token_data(token_val)
    user_db = _user_repository.get_user_from_id_and_roles(
        user_id=token_data.user_id, roles=token_data.roles
    )
    if not user_db:
        logger.debug(f"User with id {token_data.user_id} not found in the system")
        return None
    if user_db.disabled:
        logger.debug(f"User '{user_db.username}' is disabled")
        return None
    return user_db


def is_admin(current_user: user_schemas.User = Depends(get_current_user)):
    for role in current_user.roles:
        if role.name == "ROLE_ADMIN":
            logger.debug(f"User '{current_user.username}' is a admin")
            return current_user

    raise NotAdminException()


def is_admin_(user: user_schemas.User):
    for role in user.roles:
        if role.name == "ROLE_ADMIN":
            logger.debug(f"User '{user.username}' is a admin")
            return True

    return False
