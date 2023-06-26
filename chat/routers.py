from fastapi import APIRouter, status

from auth import dependencies as auth_deps
from core import dependencies as core_deps
from core import schemas as core_schemas

from . import models, schemas

chat_router: APIRouter = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={401: {"model": core_schemas.ResponseDetail}},
)


@chat_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: schemas.ChatInput,
    sql_session: core_deps.SqlSession,
    user: auth_deps.User,
) -> schemas.ChatDB:
    chat: models.Chat = await models.Chat(**chat_data.dict()).create(sql_session)
    user.chats.append(chat)
    await sql_session.commit()
    return schemas.ChatDB.from_orm(chat)
