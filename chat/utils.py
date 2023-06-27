from uuid import UUID

from beanie.odm.enums import SortDirection
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import models as auth_models

from . import exceptions, models, schemas


class ChatHistoryMaker:
    def __init__(
        self,
        user: auth_models.User,
        chat_id: str,
        sql_session: AsyncSession,
        no_sql_session: AsyncIOMotorDatabase,
        skip: int,
        limit: int,
    ) -> None:
        self._user: auth_models.User = user
        self._sql_session: AsyncSession = sql_session
        self._no_sql_session: AsyncSession = no_sql_session
        self._chat_id: str = chat_id
        self._skip: int = skip
        self._limit: int = limit

    async def _get_chat(self) -> models.Chat:
        if self._chat_id not in (user_chat.id for user_chat in self._user.chats):
            raise exceptions.BaseChatExceptionManager.not_subscribed

        query: Select = select(models.Chat).where(models.Chat.id == self._chat_id)
        chat: models.Chat | None = (await self._sql_session.execute(query)).scalar()

        if not chat:
            raise exceptions.BaseChatExceptionManager.no_chat
        return chat

    async def get(self) -> schemas.ChatHistory:
        chat: models.Chat = await self._get_chat()
        messages: list[schemas.Message] = await schemas.Message.find_many(
            schemas.Message.chat_id == UUID(self._chat_id),
            sort=[("sent_at", SortDirection.DESCENDING)],
            skip=self._skip,
            limit=self._limit,
        ).to_list()
        return schemas.ChatHistory(
            id=self._chat_id,
            name=chat.name,
            messages=[schemas.HistoryMessage(sent_at=message.sent_at, content=message.content) for message in messages],
        )
