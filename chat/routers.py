from fastapi import APIRouter, status

from auth import dependencies as auth_deps
from auth import models as auth_models
from auth import schemas as auth_schemas
from auth import utils as auth_utils
from core import dependencies as core_deps
from core import schemas as core_schemas

from . import models, schemas, utils

chat_router: APIRouter = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={401: {"model": core_schemas.ResponseDetail}},
)


@chat_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: schemas.ChatInput,
    sql_session: core_deps.SqlSession,
    user: auth_deps.UserHeader,
) -> schemas.ChatDB:
    chat: models.Chat = await models.Chat(**chat_data.dict()).create(sql_session)
    user.chats.append(chat)
    await sql_session.commit()
    return schemas.ChatDB.from_orm(chat)


@chat_router.get("/{chat_id}")
async def get_chat_history(
    chat_id: str,
    sql_session: core_deps.SqlSession,
    no_sql_session: core_deps.NoSqlSession,
    user: auth_deps.UserHeader,
    skip: int,
    limit: int = 50,
) -> schemas.ChatHistory:
    return await utils.ChatHistoryMaker(user, chat_id, sql_session, no_sql_session, skip, limit).get()


@chat_router.post("/add-user-to-chat")
async def add_user_to_chat(
    data: schemas.UserToChat,
    sql_session: core_deps.SqlSession,
    user: auth_deps.UserHeader,
) -> auth_schemas.UserDB:
    chat: models.Chat = await utils.ChatGetter(user, data.chat_id, sql_session).get()
    user_for_chat: auth_models.User = await auth_utils.Authenticator(sql_session).get_prefetched_user(
        data.user_nickname
    )
    user_for_chat.chats.append(chat)
    await sql_session.commit()
    await sql_session.refresh(user_for_chat, attribute_names=("chats",))
    return auth_schemas.UserDB.from_orm(user_for_chat)
