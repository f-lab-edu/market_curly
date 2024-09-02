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
from src.service.background_task import process_tasks


async def create_consumer_group(stream_name: str, group_name: str):
    task_redis = get_task_redis_client()

    # consumer 그룹이 없을 경우 생성
    try:
        await task_redis.xgroup_create(stream_name, group_name, id="0", mkstream=True)
    except ResponseError as e:
        # consumer 그룹이 이미 존재할 경우 오류 무시
        if "BUSYGROUP Consumer Group name already exists" not in str(e):
            raise e


async def stop_background_tasks(app: FastAPI):
    # 비동기 작업 취소
    if app.state.stream_task:
        app.state.stream_task.cancel()
        try:
            await app.state.stream_task
        except asyncio.CancelledError:
            pass  # 작업이 취소되었음을 확인


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB 및 테이블 생성
    await create_db_and_tables()

    # Redis에서 consumer 그룹 생성
    await create_consumer_group(stream_name="task_stream", group_name="task_group")

    # 백그라운드 작업 실행
    loop = asyncio.get_event_loop()
    stream_task = loop.create_task(process_tasks())
    app.state.stream_task = stream_task

    yield

    # 백그라운드 작업 종료
    app.state.stream_task.cancel()  # 작업 취소
    try:
        await app.state.stream_task  # 작업 완료 대기
    except asyncio.CancelledError:
        pass  # 작업이 취소된 경우 예외 처리
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
