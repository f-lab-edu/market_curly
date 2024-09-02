import asyncio

from src.redis_client import get_task_redis_client

task_redis = get_task_redis_client()


async def process_tasks():
    while True:
        try:
            result = await task_redis.xreadgroup(
                groupname="task_group",
                consumername="worker_1",
                streams={"task_stream": ">"},
                count=1,
                block=1000,
            )

        except Exception as e:
            print(f"Error processing tasks: {e}")
        await asyncio.sleep(1)  # 잠시 대기 후 다음 메시지 확인
