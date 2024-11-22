from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
import uuid
from typing import Optional, List
import re
from ..data.models.enums.request_status import RequestStatus
from . import role_schema


class UserBase(BaseModel):
    email: str
    username: str
    full_name: str
    oauth2_user: bool


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str

    @field_validator("username")
    @classmethod
    def check_username(cls, username: str) -> str:
        return Validators.check_username(cls, username)

    @field_validator("full_name")
    @classmethod
    def check_full_name(cls, full_name: str) -> str:
        return Validators.check_full_name(cls, full_name)

    password: str

    @field_validator("password")
    @classmethod
    def check_password(cls, password: str) -> str:
        return Validators.check_password(cls, password)


class User(BaseModel):
    id: uuid.UUID
    disabled: bool
    roles: list[role_schema.RoleBase]


class UserInDB(User):
    hashed_password: str


class UserEdit(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None
    roles: Optional[List[str]] = None

    @field_validator("username")
    @classmethod
    def check_username(cls, username: Optional[str]) -> Optional[str]:
        if username is None:
            return username
        return Validators.check_username(cls, username)

    @field_validator("full_name")
    @classmethod
    def check_full_name(cls, full_name: Optional[str]) -> Optional[str]:
        if full_name is None:
            return full_name
        return Validators.check_full_name(cls, full_name)

    @field_validator("password")
    @classmethod
    def check_password(cls, password: Optional[str]) -> Optional[str]:
        if password is None:
            return password
        return Validators.check_password(cls, password)


class Validators:
    @staticmethod
    def check_username(cls, username: str) -> str:
        pattern = r"^[a-zA-Z0-9-]{6,32}$"
        if not re.match(pattern, username):
            raise ValueError(
                "Invalid username. It must be 6-32 characters long and can contain only letters, numbers, and dashes."
            )
        return username

    @staticmethod
    def check_full_name(cls, full_name: str) -> str:
        pattern = r"^(?=.*[a-zA-Z])[a-zA-Z ]{2,64}$"
        if not re.match(pattern, full_name):
            raise ValueError(
                "Invalid full name. It must be 2-64 characters long and can contain only letters and spaces, and ha has to begin with a letter."
            )
        return full_name

    @staticmethod
    def check_password(cls, password: str) -> str:
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_])[A-Za-z\d\W_]{8,64}$"
        if not re.match(pattern, password):
            raise ValueError(
                "Invalid password. It must be 8-64 characters long and contain one uppercase letter, one lowercase letter, one number, and one special character."
            )
        return password


class UserCount(BaseModel):
    total: int
    disabled: int
    active: int
    oauth2: int
    username_password: int


class UserOut(UserBase):
    model_config = ConfigDict(strict=True)
    id: uuid.UUID
    disabled: bool
    roles: list[str]
    certification_status: Optional[RequestStatus] = None

    @field_validator("roles", mode="before")
    @classmethod
    def split_roles(cls, value) -> list[str]:
        # Split the roles string by dot and return as a list
        if isinstance(value, str):
            return value.split(",")
        return value


class UserKeys(BaseModel):
    private_key: str
    public_key: str
    certificate: str


class UserUsername(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str


class UserPublic(BaseModel):
    username: str
    full_name: str
