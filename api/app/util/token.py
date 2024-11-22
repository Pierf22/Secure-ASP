from datetime import datetime, timedelta, timezone
import jwt
import secrets
from ..schemas import token_schemas
from ..exceptions.security_exceptions import TokenException
import logging

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_HOURS = 24
SECRET_KEY = secrets.token_hex(32)

logger = logging.getLogger(__name__)


def create_access_token(
    id: str, roles: set[str], certificated: bool, username: str, public_key: str
):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": id}
    expire = datetime.now(timezone.utc) + access_token_expires
    to_encode.update({"exp": expire})
    to_encode.update({"roles": roles})
    to_encode.update({"username": username})
    to_encode.update({"certificated": certificated})
    to_encode.update({"have_a_signed_cert": public_key is not None})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        logger.error(f"Error creating token: {e}")
        raise e
    return encoded_jwt


def create_refresh_token(id: str):
    refresh_token_expires = timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    to_encode = {"sub": id}
    expire = datetime.now(timezone.utc) + refresh_token_expires
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        logger.error(f"Error creating token: {e}")
        raise e
    return encoded_jwt


def get_token_data(token: str):
    credentials_exception = TokenException()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expire_date = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        user_id: str = payload.get("sub")
        if user_id is None or expire_date < datetime.now(timezone.utc):
            raise credentials_exception
        token_data = token_schemas.TokenData(
            user_id=user_id, roles=payload.get("roles"), expires_at=expire_date
        )
    except Exception as e:
        logger.debug(f"Error decoding token: {e}")
        raise credentials_exception
    return token_data


def create_encoding_token(encoding_id: str):
    to_encode = {"sub": encoding_id}
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        logger.error(f"Error creating token: {e}")
        raise e
    return encoded_jwt


def get_encoding_if_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        encoding_id: str = payload.get("sub")
        if encoding_id is None:
            return None
    except Exception as e:
        logger.debug(f"Error decoding token: {e}")
        return None
    return encoding_id
