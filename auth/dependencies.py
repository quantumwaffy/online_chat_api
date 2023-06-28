from typing import Annotated, Type, Unpack

from fastapi import Depends
from fastapi.security import APIKeyHeader, APIKeyQuery
from sqlalchemy.ext.asyncio import AsyncSession

from core import dependencies as core_deps

from . import mixins, models, schemas, utils


class JWTAuthKeyHeader(mixins.JWTAuthMixin, APIKeyHeader):
    ...


class JWTAuthKeyQuery(mixins.JWTAuthMixin, APIKeyQuery):
    ...


class AuthenticatedUser:
    _schema_user: Type[schemas.UserDB] = schemas.UserDB

    def __init__(self, serializable: bool = False) -> None:
        self._serializable: bool = serializable
        self._user: models.User | None = None

    async def __call__(self, **kwargs: Unpack[dict[str, AsyncSession | str]]) -> models.User | schemas.UserDB:
        await self._set_user(**kwargs)
        return self._schema_user.from_orm(self._user) if self._serializable else self._user

    async def _set_user(self, sql_session: AsyncSession, nickname: str) -> None:
        self._user: models.User = await utils.Authenticator(sql_session).get_prefetched_user(nickname)


class AuthenticatedUserHeader(AuthenticatedUser):
    async def __call__(
        self,
        sql_session: core_deps.SqlSession,
        nickname: Annotated[str, Depends(JWTAuthKeyHeader())],
    ) -> models.User | schemas.UserDB:
        return await super().__call__(sql_session=sql_session, nickname=nickname)


class AuthenticatedUserQuery(AuthenticatedUser):
    async def __call__(
        self,
        sql_session: core_deps.SqlSession,
        nickname: Annotated[str, Depends(JWTAuthKeyQuery())],
    ) -> models.User | schemas.UserDB:
        return await super().__call__(sql_session=sql_session, nickname=nickname)


UserDBSchemaHeader = Annotated[schemas.UserDB, Depends(AuthenticatedUserHeader(serializable=True))]
UserHeader = Annotated[models.User, Depends(AuthenticatedUserHeader())]
UserDBSchemaQuery = Annotated[schemas.UserDB, Depends(AuthenticatedUserQuery(serializable=True))]
UserQuery = Annotated[models.User, Depends(AuthenticatedUserQuery())]
