from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import engine


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
