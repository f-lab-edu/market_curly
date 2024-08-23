from fastapi import Cookie, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.models.repository import UserRepository
from src.models.user import Buyer, Seller, User, UserType
from src.schema.request import LoginUserRequest, RegisterUserRequest
from src.schema.response import (
    GetBuyerInfoResponse,
    GetRegisterInfoResponse,
    GetSellerInfoResponse,
)
from src.service.session import SessionService
from src.service.user import UserService


async def register_user_handler(
    request: RegisterUserRequest,
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
):
    email = request.email
    existing_user = await user_repo.get_user_by_email(email=email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered.")

    user_type = request.user_type
    if user_type == UserType.SELLER:
        is_valid_seller_data = await user_repo.validate_seller_unique_data(
            request.registration_number, request.brand_name
        )
        if not is_valid_seller_data:
            raise HTTPException(
                status_code=400, detail="Seller data validation failed."
            )

    hashed_password = user_service.hash_password(request.password)

    user: User = User(email=email, password=hashed_password, user_type=user_type)
    created_user: User = await user_repo.save_entity(instance=user)

    if user_type == UserType.SELLER:
        seller: Seller = Seller(
            user_id=created_user.id,
            registration_number=request.registration_number,
            brand_name=request.brand_name,
            contact_number=request.contact_number,
        )
        created_seller = await user_repo.save_entity(instance=seller)

        return GetRegisterInfoResponse(
            user_type=created_seller.user.user_type,
            email=created_seller.user.email,
            name=created_seller.brand_name,
        )

    elif user_type == UserType.BUYER:
        buyer: Buyer = Buyer(
            user_id=created_user.id,
            name=request.name,
            phone_number=request.phone_number,
            address=request.address,
        )
        created_buyer = await user_repo.save_entity(instance=buyer)

        return GetRegisterInfoResponse(
            user_type=created_buyer.user.user_type,
            email=created_buyer.user.email,
            name=created_buyer.name,
        )


async def login_user_handler(
    request: LoginUserRequest,
    user_service: UserService = Depends(),
    session_service: SessionService = Depends(),
    user_repo: UserRepository = Depends(),
) -> JSONResponse:
    user: User = await user_repo.get_user_by_email(email=request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found.")

    is_verified: bool = user_service.verify_password(
        plain_password=request.password, hashed_password=user.password
    )
    if not is_verified:
        raise HTTPException(status_code=401, detail="Not Authorized")

    session_data = {"user_id": user.id, "user_type": user.user_type}
    session_id = await session_service.create_session(session_data=session_data)

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True)
    return response


async def logout_user_handler(
    session_id: str = Cookie(None), session_service: SessionService = Depends()
) -> JSONResponse:
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    session_data = await session_service.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session Not Found")

    await session_service.delete_session(session_id)

    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie(key="session_id")
    return response


async def get_user_info_handler(
    session_id: str = Cookie(None),
    session_service: SessionService = Depends(),
    user_repo: UserRepository = Depends(),
) -> GetSellerInfoResponse | GetBuyerInfoResponse:
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    session_data = await session_service.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session Not Found")

    user_id = session_data["user_id"]
    user: User = await user_repo.get_user_by_id(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    if user.user_type == UserType.SELLER:
        return GetSellerInfoResponse(
            email=user.email,
            registration_number=user.seller.registration_number,
            brand_name=user.seller.brand_name,
            contact_number=user.seller.contact_number,
        )

    return GetBuyerInfoResponse(
        email=user.email,
        name=user.buyer.name,
        phone_number=user.buyer.phone_number,
        address=user.buyer.address,
    )
