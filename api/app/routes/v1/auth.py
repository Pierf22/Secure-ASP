from fastapi import APIRouter, Depends, status, Response, Header, Request
from ...data.services.auth_service import AuthService, get_current_user
from fastapi.responses import RedirectResponse, HTMLResponse
from ...util import token
from typing import Annotated
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from ...schemas import user_schemas
import requests
from ... import config
from ...exceptions.security_exceptions import (
    AuthenticationException,
    UserDisabledException,
)
from ...exceptions.bad_request_exceptions import BadRequestException, ConflictException
from ...schemas.message_schema import ErrorMessage
from ...data.services.user_service import UserService
from ...data.services.invalidated_token_service import InvalidatedTokenService
from ...util.database import get_db
from sqlalchemy.orm import Session
import logging
from ...util.resource_manager import templates

logger = logging.getLogger(__name__)

security = HTTPBasic()

router = APIRouter(prefix="/v1/auth", tags=["auth"], dependencies=[])


@router.post(
    "/login",
    status_code=204,
    responses={
        401: {"description": "Incorrect username or password", "model": ErrorMessage}
    },
)
async def login(
    response: Response,
    form_data: Annotated[HTTPBasicCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    _auth_service = AuthService(db)
    _user_service = UserService(db)
    logging.debug(f"user {form_data.username} is trying to login")
    user = _auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise AuthenticationException("Incorrect username or password")
    logger.debug(f"User '{form_data.username}' successfully authenticated.")
    response.headers["Authorization"] = (
        f"Bearer {token.create_access_token(str(user.id), user.roles_as_dict(), _user_service.is_certificated(user), user.username, user.public_key)}"
    )
    response.headers["Refresh-Token"] = f"{token.create_refresh_token(str(user.id))}"
    logger.debug(f"token created for user '{form_data.username}'")
    response.status_code = status.HTTP_204_NO_CONTENT


@router.post(
    "/logout",
    status_code=204,
    responses={
        401: {"description": "Incorrect username or password", "model": ErrorMessage}
    },
)
async def logout(
    response: Response,
    authorization: Annotated[str | None, Header()],
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[user_schemas.User, Depends(get_current_user)],
):
    _user_service = UserService(db)
    _invalidated_token_service = InvalidatedTokenService(db)
    access_token = authorization[7:]
    token_data = token.get_token_data(access_token)
    logger.debug(f"User '{auth.username}' is trying to logout")
    user = _user_service.find_by_id(token_data.user_id)
    _invalidated_token_service.save_invalidated_token(
        access_token, token_data.expires_at, token_data.user_id
    )
    logger.debug(f"User '{auth.username}' successfully logged out.")
    response.status_code = status.HTTP_204_NO_CONTENT


@router.post("/refresh-token", status_code=204)
async def refresh_token(
    response: Response,
    refresh_token: Annotated[str | None, Header()],
    db: Annotated[Session, Depends(get_db)],
):
    _user_service = UserService(db)
    _invalidated_token_service = InvalidatedTokenService(db)
    if refresh_token is None:
        logger.debug("Refresh token is missing")
        raise BadRequestException("Refresh token is missing")
    if _invalidated_token_service.is_token_invalid(refresh_token):
        logger.debug("Refresh token is invalid")
        raise AuthenticationException("Refresh token is invalid")
    token_data = token.get_token_data(refresh_token)
    user = _user_service.find_by_id(token_data.user_id)
    logger.debug(f"User '{token_data.user_id}' is trying to refresh token")
    if not user:
        logger.debug(f"User '{token_data.user_id}' not found in the system.")
        raise AuthenticationException("Incorrect username or password")

    _invalidated_token_service.save_invalidated_token(
        refresh_token, token_data.expires_at, user.id
    )

    response.headers["Authorization"] = (
        f"Bearer {token.create_access_token(str(user.id), user.roles_as_dict(),_user_service.is_certificated(user), user.username, user.public_key)}"
    )
    response.headers["Refresh-Token"] = f"{token.create_refresh_token(str(user.id))}"
    logger.debug(f"token refreshed for user '{user.username}'")

    response.status_code = status.HTTP_204_NO_CONTENT


@router.post(
    "/sign-up",
    status_code=201,
    responses={
        409: {"description": "Username already registered", "model": ErrorMessage},
        201: {"description": "User created"},
    },
)
async def sign_up(
    response: Response,
    user: user_schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    _user_service = UserService(db)

    db_user = _user_service.find_user_by_email_or_username(user.email, user.username)
    if db_user:
        logger.debug(
            f"A username '{user.username}' or email '{user.email}' already registered."
        )
        raise ConflictException("Username or email already registered")
    _user_service.create_user(user)
    logger.debug(f"New user '{user.username}' registered.")
    response.status_code = status.HTTP_201_CREATED





@router.get("/oauth2/callback", response_class=HTMLResponse)
async def oauth2_callback(
    settings: Annotated[config.Settings, Depends(config.get_settings)],
    request: Request,
    response: Response,
    code: str,
    db: Annotated[Session, Depends(get_db)],
):
    _user_service = UserService(db)
    try:
        url = "https://github.com/login/oauth/access_token"
        client_id = settings.github_client_id
        client_secret = settings.github_client_secret
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
        }
        headers = {"Accept": "application/json"}
        response_access_token = requests.post(url, headers=headers, data=payload)
        access_token = response_access_token.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        response_user_data = requests.get(
            "https://api.github.com/user", headers=headers
        )
        saved_user = _user_service.find_user_by_username(
            response_user_data.json()["login"]
        )
        if saved_user and saved_user.oauth2_user:
            logger.debug(
                f"User '{response_user_data.json()['login']}' already registered via oauth2."
            )
            if saved_user.disabled:
                logger.debug(f"User '{saved_user.username}' is disabled.")
                raise UserDisabledException()
            access_token = token.create_access_token(
                str(saved_user.id),
                saved_user.roles_as_dict(),
                _user_service.is_certificated(saved_user),
                saved_user.username,
                saved_user.public_key,
            )
            refresh_token = token.create_refresh_token(str(saved_user.id))
            logger.debug(
                f"User '{saved_user.username}' successfully authenticated via oauth2."
            )
            return templates.TemplateResponse(
                "oauth-login-successful.html",
                {
                    "front_ends": ",".join(map(str, settings.origins)),
                    "request": request,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                request=request,
            )

        if saved_user:
            logger.debug(
                f"A user '{response_user_data.json()['login']}' already registered with the same username."
            )
            raise ConflictException("Username already registered")
        saved_user = _user_service.find_user_by_email(
            response_user_data.json()["email"]
        )
        if saved_user:
            logger.debug(
                f"A user '{response_user_data.json()['login']}' already registered with the same email."
            )
            raise ConflictException("Email already registered")
        new_user = user_schemas.UserCreate(
            email=response_user_data.json()["email"],
            username=response_user_data.json()["login"],
            full_name=response_user_data.json()["name"],
            password="Oauth2User123!",
        )
        saved_user = _user_service.create_user(new_user, True)
        logger.debug(
            f"New user '{response_user_data.json()['login']}' registered via oauth2."
        )
        access_token = token.create_access_token(
            str(saved_user.id),
            saved_user.roles_as_dict(),
            _user_service.is_certificated(saved_user),
            saved_user.username,
            saved_user.public_key,
        )
        refresh_token = token.create_refresh_token(str(saved_user.id))
        logger.debug(
            f"New user with username: '{saved_user.username}' successfully authenticated via oauth2."
        )
        return templates.TemplateResponse(
            "oauth-login-successful.html",
            {
                "front_ends": ",".join(map(str, settings.origins)),
                "request": request,
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            request=request,
        )
    except Exception as e:
        logger.error(f"Error during oauth2 login: {e}")
        return templates.TemplateResponse(
            "oauth-login-failed.html", {"request": request}, request=request
        )
