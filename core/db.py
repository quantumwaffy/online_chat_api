from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.settings import SETTINGS

engine: AsyncEngine = create_async_engine(
    SETTINGS.get_psql_url(),
    echo=True,
    future=True,
)

SessionLocal: sessionmaker = sessionmaker(
    bind=engine, autocommit=False, expire_on_commit=False, autoflush=False, class_=AsyncSession
)
