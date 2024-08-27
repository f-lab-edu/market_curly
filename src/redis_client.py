from redis.asyncio import Redis

from src.config import redis as redis_config

# 세션 관리용 Redis 클라이언트
redis_client = Redis(
    host=redis_config.host,
    port=redis_config.port,
    db=redis_config.session_db,
    encoding="UTF-8",
    decode_responses=True,
)

# 작업 관리용 Redis 클라이언트
task_redis_client = Redis(
    host=redis_config.host,
    port=redis_config.port,
    db=redis_config.task_db,
    encoding="UTF-8",
    decode_responses=True,
)


def get_redis_client() -> Redis:
    """세션 관리용 Redis 클라이언트를 반환합니다."""
    return redis_client


def get_task_redis_client() -> Redis:
    """작업 관리용 Redis 클라이언트를 반환합니다."""
    return task_redis_client
