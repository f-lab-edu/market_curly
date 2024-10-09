import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.exceptions import ResponseError

from src import config
from src.apis.common import common_router
from src.apis.store import store_router
from src.apis.user import user_router
from src.database import close_db, create_db_and_tables
from src.redis_client import get_task_redis_client
from src.service.background_task import (  # , process_expired_cart_messages
    listen_to_expired_keys,
    process_tasks,
)


async def create_consumer_group(stream_name: str, group_name: str):
    task_redis = get_task_redis_client()

    try:
        await task_redis.xgroup_create(stream_name, group_name, id="0", mkstream=True)
    except ResponseError as e:
        if "BUSYGROUP Consumer Group name already exists" not in str(e):
            raise e


async def stop_background_tasks(app: FastAPI):
    tasks = [app.state.stream_task, app.state.notify_task]  # , app.state.cart_task]
    for task in tasks:
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Error occurred while canceling task: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB 및 테이블 생성
    await create_db_and_tables()

    # 상품 정보 동기화
    # await sync_all_products()

    # Redis에서 consumer 그룹 생성
    await create_consumer_group(stream_name="task_stream", group_name="task_group")

    # 백그라운드 작업 실행
    loop = asyncio.get_event_loop()
    app.state.stream_task = loop.create_task(process_tasks())
    # app.state.cart_task = loop.create_task(process_expired_cart_messages())
    app.state.notify_task = loop.create_task(listen_to_expired_keys())

    yield

    await stop_background_tasks(app)

    await close_db()


app = FastAPI(lifespan=lifespan)
app.include_router(common_router)
app.include_router(store_router)
app.include_router(user_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.origins.split(","),
    allow_credentials=True,
    allow_methods=config.cors.methods.split(","),
    allow_headers=config.cors.headers.split(","),
)


if __name__ == "__main__":
    uvicorn.run(app, host=config.web.host, port=config.web.port)
