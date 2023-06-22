import datetime
import string

from pydantic import BaseModel, Field, root_validator, validator

from chat import schemas as chat_schemas
from core import mixins as core_mixins

from . import consts


class CreatedUser(core_mixins.ORMBaseModelMixin):
    id: int
    nickname: str
    first_name: str
    last_name: str


class RoleDB(core_mixins.ORMBaseModelMixin):
    id: int
    name: str


class UserDB(CreatedUser):
    roles: list[RoleDB]
    chats: list[chat_schemas.ChatDB]


class NewUser(BaseModel):
    nickname: str = Field(max_length=20, regex=consts.NICKNAME_REGEX)
    first_name: str = Field(max_length=20, regex=consts.NAME_REGEX)
    last_name: str = Field(max_length=40, regex=consts.NAME_REGEX)
    password_hash: str = Field(min_length=8, max_length=20, regex=consts.PASSWORD_REGEX, alias="password")
    confirm_password: str

    @root_validator()
    def verify_password_match(cls, values: dict[str, str]) -> dict[str, str]:
        password = values.get("password_hash")
        confirm_password = values.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValueError("The two passwords did not match.")
        return values

    @validator("password_hash")
    def validate_nickname(cls, nickname: str) -> str:
        if nickname.startswith("."):
            raise ValueError("Must not start with '.'")
        return nickname

    @validator("password_hash")
    def validate_password_security(cls, password: str) -> str:
        if not any(char in consts.PASSWORD_REGEX for char in password):
            raise ValueError("Password must contain at least one specific character")
        if not any(char in string.digits for char in password):
            raise ValueError("Password must contain at least one numeric character")
        if not any(char in string.ascii_letters for char in password):
            raise ValueError("Password must contain at least one ascii character")
        if not any(char in string.ascii_lowercase for char in password):
            raise ValueError("Password must contain at least one ascii character in lowercase")
        if not any(char in string.ascii_uppercase for char in password):
            raise ValueError("Password must contain at least one ascii character in uppercase")
        return password


class LoginUser(BaseModel):
    nickname: str
    password: str


class TokenGeneratedData(BaseModel):
    access_token: str
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str


class RefreshToken(BaseModel):
    refresh_token: str


class JWTPayload(BaseModel):
    expiry_date: int | datetime.datetime = Field(alias="exp")
    nickname: str = Field(alias="sub")

    @validator("expiry_date")
    def validate_expiry_date(cls, exp_timestamp: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(exp_timestamp)


class CheckStatus(BaseModel):
    status: consts.CheckStatus
