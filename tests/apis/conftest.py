import asyncio

import pytest_asyncio
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import close_db, create_db_and_tables, engine
from src.main import app
from src.redis_client import get_redis_client


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


@pytest_asyncio.fixture(scope="function")
async def redis_client() -> Redis:
    client = get_redis_client()
    yield client
    await client.close()


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
