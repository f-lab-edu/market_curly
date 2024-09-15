from fastapi import Cookie, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.schema.request import AddToCartRequest
from src.service.auth import get_session_data
from src.service.cart import CartService
from src.service.session import SessionService


async def add_to_cart_handler(
    request: AddToCartRequest,
    session_id: str = Cookie(None),
    session_service: SessionService = Depends(),
    cart_service: CartService = Depends(CartService),
):
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    session_data = await get_session_data(
        session_id=session_id, session_service=session_service
    )

    if "user_id" not in session_data:
        raise HTTPException(status_code=401, detail="User not authenticated")

    await cart_service.add_to_cart(
        user_id=session_data["user_id"],
        product_id=request.product_id,
        quantity=request.quantity,
    )

    await session_service.extend_session(session_id=session_id)

    response = JSONResponse(content={"message": "Goods added to cart successfully"})
    return response


async def get_cart_handler(
    session_id: str = Cookie(None),
    session_service: SessionService = Depends(),
    cart_service: CartService = Depends(CartService),
):
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    session_data = await get_session_data(
        session_id=session_id, session_service=session_service
    )

    if "user_id" not in session_data:
        raise HTTPException(status_code=401, detail="User not authenticated")

    return await cart_service.get_cart(user_id=session_data["user_id"])


async def delete_from_cart_handler(
    product_id: int,
    session_id: str = Cookie(None),
    session_service: SessionService = Depends(),
    cart_service: CartService = Depends(CartService),
):
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    session_data = await get_session_data(
        session_id=session_id, session_service=session_service
    )

    if "user_id" not in session_data:
        raise HTTPException(status_code=401, detail="User not authenticated")

    await cart_service.delete_from_cart(
        user_id=session_data["user_id"], product_id=product_id
    )


async def clear_cart_handler(
    session_id: str = Cookie(None),
    session_service: SessionService = Depends(),
    cart_service: CartService = Depends(CartService),
):
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    session_data = await get_session_data(
        session_id=session_id, session_service=session_service
    )

    if "user_id" not in session_data:
        raise HTTPException(status_code=401, detail="User not authenticated")

    await cart_service.clear_cart(user_id=session_data["user_id"])
