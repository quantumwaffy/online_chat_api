import datetime
import uuid

from beanie import Document, Indexed
from pydantic import BaseModel, Field

from core import mixins as core_mixins


class ChatInput(core_mixins.ORMBaseModelMixin):
    name: str


class ChatDB(ChatInput):
    id: str


class MessageEvent(BaseModel):
    sent_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    content: str
    nickname: str


class Message(MessageEvent, Document):
    chat_id: Indexed(uuid.UUID)

    class Settings:
        name = "messages"


class ChatHistory(ChatDB):
    messages: list[MessageEvent]


class UserToChat(BaseModel):
    user_nickname: str
    chat_id: str
