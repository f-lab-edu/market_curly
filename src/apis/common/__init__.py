from fastapi import APIRouter, status

from src.apis.common import health

common_router = APIRouter(tags=["common"])

common_router.add_api_route(
    methods=["GET"],
    path="/health",
    endpoint=health.handler,
    status_code=status.HTTP_200_OK,
)
