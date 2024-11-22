class AuthorizationException(Exception):
    def __init__(self, cause="Unauthorized"):
        self.cause = cause
        super().__init__(self.cause)


class UserDisabledException(AuthorizationException):
    def __init__(self):
        super().__init__("User is disabled")


class NotAdminException(AuthorizationException):
    def __init__(self):
        super().__init__("You must be an admin to perform this action")


class AuthenticationException(Exception):
    def __init__(self, cause="Incorrect username or password"):
        self.cause = cause
        super().__init__(self.cause)


class TokenException(AuthenticationException):
    def __init__(self):
        super().__init__("Invalid token")
