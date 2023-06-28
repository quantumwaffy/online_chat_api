from typing import Annotated, Type

from fastapi import Depends, Request
from fastapi.security import APIKeyHeader

from core import dependencies as core_deps
from core.settings import SETTINGS

from . import models, schemas, utils


class JWTAuthKeyHeader(APIKeyHeader):
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
        self,
        request: Request,
    ) -> str:
        token: str = await super().__call__(request)
        user_nickname: str = utils.Authenticator.get_user_nickname_from_token(
            token, SETTINGS.AUTH.JWT_ACCESS_TOKEN_SECRET_KEY
        )
        return user_nickname


class AuthenticatedUserHeader:
    _schema_user: Type[schemas.UserDB] = schemas.UserDB

    def __init__(self, serializable: bool = False) -> None:
        self._serializable: bool = serializable
        self._user: models.User | None = None

    async def __call__(
        self,
        sql_session: core_deps.SqlSession,
        nickname: Annotated[str, Depends(JWTAuthKeyHeader())],
    ) -> models.User | schemas.UserDB:
        self._user: models.User = await utils.Authenticator(sql_session).get_prefetched_user(nickname)
        return self._schema_user.from_orm(self._user) if self._serializable else self._user


UserDBSchemaHeader = Annotated[schemas.UserDB, Depends(AuthenticatedUserHeader(serializable=True))]
UserHeader = Annotated[models.User, Depends(AuthenticatedUserHeader())]
