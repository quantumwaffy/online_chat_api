from asyncpg import IntegrityConstraintViolationError
from sqlalchemy.ext.asyncio import AsyncSession

from .db import SessionLocal


async def get_db_session() -> AsyncSession:
    try:
        async with SessionLocal() as session:
            yield session
    except IntegrityConstraintViolationError as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
