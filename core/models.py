from __future__ import annotations

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import APP_NAME, utils
from .base import Base
from .mixins import TimeStampMixin

user_table_name: str = utils.get_db_table_name(APP_NAME, "user")
role_table_name: str = utils.get_db_table_name(APP_NAME, "role")

m2m_user_role_table: Table = Table(
    utils.get_db_table_name(APP_NAME, "m2m_user_role", is_plural=False),
    Base.metadata,
    Column("user_id", ForeignKey(f"{user_table_name}.id")),
    Column("role_id", ForeignKey(f"{role_table_name}.id")),
)


class User(TimeStampMixin, Base):
    __tablename__ = user_table_name
    first_name: Mapped[str] = mapped_column(String(20))
    last_name: Mapped[str] = mapped_column(String(40))
    nickname: Mapped[str] = mapped_column(String(20), unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    roles: Mapped[list[Role]] = relationship(secondary=m2m_user_role_table, back_populates="users")


class Role(TimeStampMixin, Base):
    __tablename__ = role_table_name
    name: Mapped[str] = mapped_column(String(20))
    users: Mapped[list[User]] = relationship(secondary=m2m_user_role_table, back_populates="roles")
