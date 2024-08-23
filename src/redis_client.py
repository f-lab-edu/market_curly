from redis.asyncio import Redis

from src.config import redis as redis_config

redis_client = Redis(
    host=redis_config.host,
    port=redis_config.port,
    db=redis_config.db,
    encoding="UTF-8",
    decode_responses=True,
)


def get_redis_client() -> Redis:
    return redis_client
