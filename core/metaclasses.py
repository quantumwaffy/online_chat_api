from typing import Any

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import MappedColumn

from . import APP_NAME, utils


class ModelMeta(DeclarativeMeta):
    def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict) -> Any:
        if bases:
            if "__tablename__" not in attrs:
                attrs |= {
                    "__tablename__": utils.get_db_table_name(APP_NAME, name.lower()),
                }
            if not any(
                field.column.primary_key if isinstance(field, MappedColumn) else field.primary_key
                for field in attrs.values()
                if isinstance(field, MappedColumn | Column)
            ):
                attrs |= {"id": Column(Integer, primary_key=True)}
        return super().__new__(mcs, name, bases, attrs)
