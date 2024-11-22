from fastapi import FastAPI
import uvicorn
import uvicorn.logging
from .routes import api
from .util import rate_limiter
from .util import database
from .util import pagination
from .util import resource_manager
from .handlers import exception_handler
from .data.models import *

app = FastAPI()

pagination.add(app)
resource_manager.mount(app)

api.include_routes(app)
api.include_cors(app)

rate_limiter.include_rate_limiter(app)

exception_handler.include_exception_handler(app)

database.database_start_up()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_certfile="resources/ssl_cert/cert.pem",
        ssl_keyfile="resources/ssl_cert/key.pem",
        log_config="./logging.yaml",
    )
