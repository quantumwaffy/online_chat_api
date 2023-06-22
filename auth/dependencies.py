from typing import Type

from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload
from starlette.requests import Request

from core import dependencies as core_deps
from core.settings import SETTINGS

from . import models, schemas, utils


class JWTAuthSecurity(APIKeyHeader):
    def __init__(
        self,
        *,
        name: str = SETTINGS.AUTH.JWT_TOKEN_NAME,
        description: str = "JWT authentication token",
        scheme_name: str = "JWT",
        auto_error: bool = True,
    ) -> None:
        super().__init__(name=name, description=description, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(
        self, request: Request, sql_session: AsyncSession = Depends(core_deps.get_sql_db_session)  # noqa
    ) -> str:
        token: str = await super().__call__(request)
        user_nickname: str = utils.Authenticator(sql_session).get_user_nickname_from_token(
            token, SETTINGS.AUTH.JWT_ACCESS_TOKEN_SECRET_KEY
        )
        return user_nickname


class AuthenticatedUser:
    _schema_user: Type[schemas.UserDB] = schemas.UserDB

    def __init__(self, serializable: bool = True):
        self._serializable: bool = serializable
        self._user: models.User | None = None

    async def __call__(
        self,
        nickname: str = Depends(JWTAuthSecurity()),  # noqa
        sql_session: AsyncSession = Depends(core_deps.get_sql_db_session),  # noqa
    ) -> models.User | schemas.UserDB:
        await self._set_user(nickname, sql_session)

        return self._schema_user.from_orm(self._user) if self._serializable else self._user

    async def _set_user(self, nickname: str, sql_session: AsyncSession) -> None:
        query: Select = (
            select(models.User)
            .options(subqueryload(models.User.chats), subqueryload(models.User.roles))
            .where(models.User.nickname == nickname)
        )
        self._user: models.User = (await sql_session.execute(query)).scalar()
