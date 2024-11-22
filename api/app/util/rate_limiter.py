from slowapi.extension import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
import logging

logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address, default_limits=["100/second"], headers_enabled=True
)


def include_rate_limiter(app):
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    logger.info("Rate limiter included")
