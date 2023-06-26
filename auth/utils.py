import datetime
from typing import Any, Type

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from core.settings import SETTINGS

from . import exceptions, models, schemas


class PasswordHandler:
    _pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls._pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls._pwd_context.hash(password)


class Authenticator:
    password_handler: "Type[PasswordHandler]" = PasswordHandler

    def __init__(self, sql_session: AsyncSession) -> None:
        self._sql_session: AsyncSession = sql_session

    @staticmethod
    def _create_token(subject: str, expiry_delta: int, key: str) -> str:
        expiry_dt: datetime.datetime = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry_delta)
        return jwt.encode(
            {"sub": subject, "exp": expiry_dt},
            key,
            algorithm=SETTINGS.AUTH.JWT_ALGORITHM,
        )

    @staticmethod
    def _check_user_perms(user: models.User | None) -> None:
        if not user:
            raise exceptions.BaseAuthExceptionManager.no_user
        if user.disabled:
            raise exceptions.BaseAuthExceptionManager.blocked_user

    async def check_user(self, nickname: str) -> None:
        query: Select = (
            select(models.User)
            .options(
                load_only(
                    models.User.nickname,
                )
            )
            .where(models.User.nickname == nickname)
        )
        query_result: Result = await self._sql_session.execute(query)
        if query_result.scalar():
            raise exceptions.BaseAuthExceptionManager.signup_user_exists

    async def _get_user(self, nickname: str) -> models.User | None:
        query: Select = (
            select(models.User)
            .options(load_only(models.User.nickname, models.User.password_hash, models.User.disabled))
            .where(models.User.nickname == nickname)
        )
        query_result: Result = await self._sql_session.execute(query)
        return query_result.scalar()

    async def create_jwt_tokens(self, nickname: str, password: str) -> schemas.TokenGeneratedData:
        user: models.User | None = await self._get_user(nickname)
        self._check_user_perms(user)
        if not self.password_handler.verify_password(password, user.password_hash):
            raise exceptions.BaseAuthExceptionManager.authentication_error
        return schemas.TokenGeneratedData(
            access_token=self._create_token(
                nickname, SETTINGS.AUTH.JWT_ACCESS_TOKEN_EXPIRE_MIN, SETTINGS.AUTH.JWT_ACCESS_TOKEN_SECRET_KEY
            ),
            refresh_token=self._create_token(
                nickname, SETTINGS.AUTH.JWT_REFRESH_TOKEN_EXPIRE_MIN, SETTINGS.AUTH.JWT_REFRESH_TOKEN_SECRET_KEY
            ),
        )

    @staticmethod
    def get_user_nickname_from_token(token: str, key: str) -> str:
        try:
            payload: dict[str, Any] = jwt.decode(token, key, algorithms=[SETTINGS.AUTH.JWT_ALGORITHM])
            jwt_payload: schemas.JWTPayload = schemas.JWTPayload(**payload)
            if jwt_payload.expiry_date < datetime.datetime.now():
                raise exceptions.BaseAuthExceptionManager.token_expired
        except (JWTError, ValidationError):
            raise exceptions.BaseAuthExceptionManager.credentials_error
        return jwt_payload.nickname

    @classmethod
    def get_refreshed_access_token(cls, refresh_token: str) -> schemas.AccessToken:
        nickname: str = cls.get_user_nickname_from_token(refresh_token, SETTINGS.AUTH.JWT_REFRESH_TOKEN_SECRET_KEY)
        return schemas.AccessToken(
            access_token=cls._create_token(
                nickname, SETTINGS.AUTH.JWT_ACCESS_TOKEN_EXPIRE_MIN, SETTINGS.AUTH.JWT_ACCESS_TOKEN_SECRET_KEY
            )
        )
