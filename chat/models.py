import uuid

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auth import orm_utils as auth_orm_utils
from core import base, mixins, utils

from . import APP_NAME

chat_table_name: str = utils.get_db_table_name(APP_NAME, "chat")

m2m_user_chat_table: Table = Table(
    utils.get_db_table_name(APP_NAME, "m2m_user_chat", is_plural=False),
    base.Base.metadata,
    Column("user_id", ForeignKey(f"{auth_orm_utils.user_table_name}.id")),
    Column("chat_id", ForeignKey(f"{chat_table_name}.id")),
)


class Chat(mixins.TimeStampMixin, base.Base):
    __tablename__ = chat_table_name
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50))
    users: Mapped[list["User"]] = relationship(secondary=m2m_user_chat_table, back_populates="chats")  # noqa
