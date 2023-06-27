from typing import Annotated

from asyncpg import IntegrityConstraintViolationError
from fastapi import Depends
from motor import motor_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from .db import SessionLocal
from .settings import SETTINGS


async def get_sql_db_session() -> AsyncSession:
    try:
        async with SessionLocal() as session:
            yield session
    except IntegrityConstraintViolationError as e:
        await session.rollback()
        raise e


async def get_no_sql_client() -> motor_asyncio.AsyncIOMotorDatabase:
    client: motor_asyncio.AsyncIOMotorClient = SETTINGS.MONGO.client
    try:
        yield client[SETTINGS.MONGO.MONGO_INITDB_DATABASE]
    finally:
        client.close()


SqlSession = Annotated[AsyncSession, Depends(get_sql_db_session)]
NoSqlSession = Annotated[motor_asyncio.AsyncIOMotorDatabase, Depends(get_no_sql_client)]
