import datetime
import uuid

from beanie import Document, Indexed
from pydantic import BaseModel, Field

from core import mixins as core_mixins


class ChatInput(core_mixins.ORMBaseModelMixin):
    name: str


class ChatDB(ChatInput):
    id: str


class Message(Document):
    chat_id: Indexed(uuid.UUID)
    sent_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    content: str

    class Settings:
        name = "messages"


class HistoryMessage(BaseModel):
    sent_at: datetime.datetime
    content: str


class ChatHistory(ChatDB):
    messages: list[HistoryMessage]


class UserToChat(BaseModel):
    user_nickname: str
    chat_id: str
