from fastapi import APIRouter, status

from src.apis.user import user

user_router = APIRouter(tags=["user"])

user_router.add_api_route(
    methods=["POST"],
    path="/register",
    endpoint=user.register_user_handler,
    response_model=user.GetRegisterInfoResponse,
    status_code=status.HTTP_201_CREATED,
)

user_router.add_api_route(
    methods=["POST"],
    path="/login",
    endpoint=user.login_user_handler,
    status_code=status.HTTP_200_OK,
)

user_router.add_api_route(
    methods=["POST"],
    path="/logout",
    endpoint=user.logout_user_handler,
    status_code=status.HTTP_200_OK,
)

user_router.add_api_route(
    methods=["GET"],
    path="/me",
    endpoint=user.get_user_info_handler,
    response_model=user.GetSellerInfoResponse | user.GetBuyerInfoResponse,
    status_code=status.HTTP_200_OK,
)
