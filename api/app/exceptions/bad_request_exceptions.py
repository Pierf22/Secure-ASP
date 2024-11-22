class BadRequestException(Exception):
    def __init__(self, cause: str):
        self.cause = cause
        super().__init__(self.cause)


class InvalidFileTypeException(BadRequestException):
    def __init__(self, allowed_extension: list[str]):
        self.allowed_extension = allowed_extension
        self.cause = f"Invalid file type. Allowed file types: {', '.join(self.allowed_extension)}"
        super().__init__(self.cause)


class FileSizeExceededException(BadRequestException):
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.cause = f"File is too large. Max file size: {self.max_size} bytes"
        super().__init__(self.cause)


class ConflictException(BadRequestException):
    def __init__(self, cause: str):
        self.cause = cause
        super().__init__(self.cause)


class ResourceNotFoundException(BadRequestException):
    def __init__(self, cause: str = "Resource not found"):
        self.cause = cause
        super().__init__(self.cause)


class InvalidDataException(BadRequestException):
    def __init__(self, cause: str):
        self.cause = cause
        super().__init__(self.cause)
