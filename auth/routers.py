from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core import dependencies as core_deps
from core import schemas as core_schemas

from . import consts, dependencies, exceptions, models, schemas, utils

auth_router: APIRouter = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={401: {"model": core_schemas.ResponseDetail}},
)

register_router: APIRouter = APIRouter(
    prefix="/register",
    tags=["Register"],
)


@register_router.get("/check-nickname/{nickname}")
async def check_nickname(
    nickname: str, sql_session: AsyncSession = Depends(core_deps.get_sql_db_session)  # noqa
) -> schemas.CheckStatus:
    if await utils.Authenticator(sql_session).get_user(nickname, check=True):
        raise exceptions.BaseAuthExceptionManager.signup_user_exists
    return schemas.CheckStatus(status=consts.CheckStatus.OK)


@register_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(
    user_data: schemas.NewUser, sql_session: AsyncSession = Depends(core_deps.get_sql_db_session)  # noqa
) -> schemas.CreatedUser:
    auth_handler: utils.Authenticator = utils.Authenticator(sql_session)
    if await auth_handler.get_user(user_data.nickname, check=True):
        raise exceptions.BaseAuthExceptionManager.signup_user_exists
    user_data.password_hash = auth_handler.password_handler.get_password_hash(user_data.confirm_password)
    user: models.User = await models.User(**user_data.dict(exclude={"confirm_password"})).create(sql_session)
    return schemas.CreatedUser.from_orm(user)


@auth_router.post("/login")
async def login(
    user_login_data: schemas.LoginUser, sql_session: AsyncSession = Depends(core_deps.get_sql_db_session)  # noqa
) -> schemas.TokenGeneratedData:
    return await utils.Authenticator(sql_session).create_jwt_tokens(**user_login_data.dict())


@auth_router.get("/me")
async def get_me(user: schemas.UserDB = Depends(dependencies.AuthenticatedUser())) -> schemas.UserDB:  # noqa
    return user


@auth_router.post("/refresh-token")
async def refresh_access_token(token: schemas.RefreshToken) -> schemas.AccessToken:
    return utils.Authenticator.get_refreshed_access_token(token.refresh_token)
