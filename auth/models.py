from __future__ import annotations

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core import base as core_base
from core import mixins as core_mixins
from core import utils as core_utils

from . import APP_NAME, orm_utils

m2m_user_role_table: Table = Table(
    core_utils.get_db_table_name(APP_NAME, "m2m_user_role", is_plural=False),
    core_base.Base.metadata,
    Column("user_id", ForeignKey(f"{orm_utils.user_table_name}.id")),
    Column("role_id", ForeignKey(f"{orm_utils.role_table_name}.id")),
)


class User(core_mixins.TimeStampMixin, core_base.Base):
    __tablename__ = orm_utils.user_table_name
    first_name: Mapped[str] = mapped_column(String(20))
    last_name: Mapped[str] = mapped_column(String(40))
    nickname: Mapped[str] = mapped_column(String(20), unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    roles: Mapped[list[Role]] = relationship(secondary=m2m_user_role_table, back_populates="users")
    chats: Mapped[list[Chat]] = relationship(secondary="m2m_user_chat_table", back_populates="users")  # noqa


class Role(core_mixins.TimeStampMixin, core_base.Base):
    __tablename__ = orm_utils.role_table_name
    name: Mapped[str] = mapped_column(String(20))
    users: Mapped[list[User]] = relationship(secondary=m2m_user_role_table, back_populates="roles")
