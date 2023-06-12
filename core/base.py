import functools
from typing import Any, Callable, Concatenate, ParamSpec, Self, TypeVar, Unpack

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, as_declarative, declared_attr, mapped_column

from . import APP_NAME
from .utils import get_db_table_name

ModelMethodParam = ParamSpec("ModelMethodParam")
ModelMethodResult = TypeVar("ModelMethodResult")


@as_declarative()
class Base:
    id: Mapped[int] = mapped_column(primary_key=True)

    @declared_attr
    def __tablename__(self) -> str:
        return get_db_table_name(APP_NAME, self.__name__.lower())

    @staticmethod
    def model_error_handler(
        func: Callable[Concatenate[Self, ModelMethodParam], ModelMethodResult]
    ) -> Callable[[Self, ModelMethodParam], ModelMethodResult]:
        @functools.wraps(func)
        async def wrapper(
            self: Self, *args: ModelMethodParam.args, **kwargs: ModelMethodParam.kwargs
        ) -> ModelMethodResult:
            try:
                return await func(self, *args, **kwargs)
            except SQLAlchemyError as ex:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))

        return wrapper

    @model_error_handler
    async def create(self, db_session: AsyncSession) -> Self:
        db_session.add(self)
        await db_session.commit()
        return self

    @model_error_handler
    async def delete(self, db_session: AsyncSession) -> bool:
        await db_session.delete(self)
        await db_session.commit()
        return True

    @model_error_handler
    async def update(self, db_session: AsyncSession, **upd_obj_attrs: Unpack[dict[str, Any]]) -> Self:
        for attr_name, attr_value in upd_obj_attrs.items():
            setattr(self, attr_name, attr_value)
        await db_session.commit()
        return self
