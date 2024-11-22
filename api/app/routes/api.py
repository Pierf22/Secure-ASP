from .v1 import users, auth, certification_request, roles, encodings, public_profile
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)


def include_routes(app):
    app.include_router(users.router)
    app.include_router(auth.router)
    app.include_router(certification_request.router)
    app.include_router(roles.router)
    app.include_router(public_profile.router)
    app.include_router(encodings.router)
    logger.info("Routes included")


def include_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().origins,
        allow_credentials=True,
        expose_headers=["Authorization", "Refresh-Token", "Content-Disposition"],
        allow_methods=["*"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Refresh-Token",
            "Access-Control-Allow-Origin",
            "Content-Disposition",
        ],
    )
    logger.info("CORS included")
