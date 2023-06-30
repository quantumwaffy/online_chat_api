from typing import Type
from uuid import UUID

from beanie.odm.enums import SortDirection
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import models as auth_models

from . import exceptions, models, schemas


class ChatGetter:
    def __init__(self, user: auth_models.User, chat_id: str, sql_session: AsyncSession) -> None:
        self._user: auth_models.User = user
        self._chat_id: str = chat_id
        self._sql_session: AsyncSession = sql_session

    async def get(self) -> models.Chat:
        if self._chat_id not in (user_chat.id for user_chat in self._user.chats):
            raise exceptions.BaseChatExceptionManager.not_subscribed

        query: Select = select(models.Chat).where(models.Chat.id == self._chat_id)
        chat: models.Chat | None = (await self._sql_session.execute(query)).scalar()

        if not chat:
            raise exceptions.BaseChatExceptionManager.no_chat
        return chat


class ChatHistoryMaker:
    _chat_getter_class: Type[ChatGetter] = ChatGetter

    def __init__(
        self,
        user: auth_models.User,
        chat_id: str,
        sql_session: AsyncSession,
        skip: int,
        limit: int,
    ) -> None:
        self._chat_getter: ChatGetter = self._chat_getter_class(user, chat_id, sql_session)
        self._skip: int = skip
        self._limit: int = limit

    async def get(self) -> schemas.ChatHistory:
        chat: models.Chat = await self._chat_getter.get()
        messages: list[schemas.Message] = await schemas.Message.find_many(
            schemas.Message.chat_id == UUID(chat.id),
            sort=[("sent_at", SortDirection.DESCENDING)],
            skip=self._skip,
            limit=self._limit,
        ).to_list()
        return schemas.ChatHistory(
            id=chat.id,
            name=chat.name,
            messages=messages,
        )
