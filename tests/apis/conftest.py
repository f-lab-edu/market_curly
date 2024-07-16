import pytest_asyncio
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import close_db, create_db_and_tables, engine
from src.main import app


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        await create_db_and_tables()
        yield client
        await close_db()


@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
