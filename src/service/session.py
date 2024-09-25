import json
import secrets
from datetime import timedelta
from typing import Optional

from fastapi import Depends
from redis.asyncio import Redis

from src.redis_client import get_redis_client


class SessionService:
    def __init__(self, redis_client: Redis = Depends(get_redis_client)):
        self.redis_client = redis_client

    async def create_session(self, session_data: dict) -> str:
        session_id = secrets.token_hex(16)
        session_expires = timedelta(hours=1)
        await self.redis_client.setex(
            session_id, session_expires, value=json.dumps(session_data)
        )
        return session_id

    async def get_session(self, session_id: str) -> Optional[dict]:
        session_data = await self.redis_client.get(session_id)
        if session_data:
            return json.loads(session_data)
        return None

    async def delete_session(self, session_id: str):
        await self.redis_client.delete(session_id)

    async def extend_session(self, session_id: str, ttl: int = 3600):
        await self.redis_client.expire(session_id, ttl)
