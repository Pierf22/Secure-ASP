from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import logging

templates = Jinja2Templates(directory="resources/templates")
logger = logging.getLogger(__name__)


def mount(app):
    app.mount(
        "/resources/static", StaticFiles(directory="resources/static"), name="static"
    )
    logger.info("Static files mounted")
