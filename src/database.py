from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import DATABASE_URL

engine = create_async_engine(url=DATABASE_URL)
Base = declarative_base()
async_session = sessionmaker(engine, expire_on_commit=False,
                             class_=AsyncSession)


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
