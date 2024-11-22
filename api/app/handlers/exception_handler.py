from fastapi.responses import JSONResponse
from fastapi.requests import Request
from ..exceptions import bad_request_exceptions, security_exceptions
from datetime import datetime, UTC
from ..schemas.message_schema import ErrorMessage
from slowapi.errors import RateLimitExceeded


def include_exception_handler(app):

    @app.exception_handler(Exception)
    async def catch_all_exception_handler(request: Request, exc: Exception):
        return create_json_response(500, request.url.path, "Internal server error")

    @app.exception_handler(security_exceptions.AuthenticationException)
    async def catch_authentication_exception_handler(
        request: Request, exc: security_exceptions.AuthenticationException
    ):
        return create_json_response(401, request.url.path, exc.cause)

    @app.exception_handler(
        RateLimitExceeded
    )  # slowapi doesn't support async exception handlers
    def catch_rate_limit_exceeded_exception_handler(
        request: Request, exc: RateLimitExceeded
    ):
        return create_json_response(429, request.url.path, "Rate limit exceeded")

    @app.exception_handler(bad_request_exceptions.BadRequestException)
    async def catch_bad_request_exception_handler(
        request: Request, exc: bad_request_exceptions
    ):
        return create_json_response(400, request.url.path, exc.cause)

    @app.exception_handler(bad_request_exceptions.ConflictException)
    async def catch_conflict_exception_handler(
        request: Request, exc: bad_request_exceptions.ConflictException
    ):
        return create_json_response(409, request.url.path, exc.cause)

    @app.exception_handler(security_exceptions.AuthorizationException)
    async def catch_authorization_exception_handler(
        request: Request, exc: security_exceptions.AuthorizationException
    ):
        return create_json_response(403, request.url.path, exc.cause)

    @app.exception_handler(bad_request_exceptions.InvalidFileTypeException)
    async def catch_invalid_file_type_exception_handler(
        request: Request, exc: bad_request_exceptions.InvalidFileTypeException
    ):
        return create_json_response(422, request.url.path, exc.cause)

    @app.exception_handler(bad_request_exceptions.FileSizeExceededException)
    async def catch_file_size_exceeded_exception_handler(
        request: Request, exc: bad_request_exceptions.FileSizeExceededException
    ):
        return create_json_response(413, request.url.path, exc.cause)

    @app.exception_handler(bad_request_exceptions.ResourceNotFoundException)
    async def catch_resource_not_found_exception_handler(
        request: Request, exc: bad_request_exceptions.ResourceNotFoundException
    ):
        return create_json_response(404, request.url.path, exc.cause)

    @app.exception_handler(bad_request_exceptions.InvalidDataException)
    async def catch_invalid_data_exception_handler(
        request: Request, exc: bad_request_exceptions.InvalidDataException
    ):
        return create_json_response(422, request.url.path, exc.cause)


def create_json_response(status_code: int, path: str, message: str) -> JSONResponse:
    current_time = datetime.now(UTC).isoformat()

    error_message = ErrorMessage(
        status_code=status_code, message=message, timestamp=current_time, path=path
    )

    return JSONResponse(
        status_code=status_code,
        content=error_message.model_dump(),
    )
