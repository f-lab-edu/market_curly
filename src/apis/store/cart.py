from fastapi import Cookie, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.models.repository import CartRepository
from src.schema.request import AddToCartRequest
from src.service.auth import get_session_data
from src.service.session import SessionService


async def add_to_cart_handler(
    request: AddToCartRequest,
    cart_repo: CartRepository = Depends(CartRepository),
    session_id: str = Cookie(None),
    session_service: SessionService = Depends(),
):
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    session_data = await get_session_data(
        session_id=session_id, session_service=session_service
    )

    if "user_id" not in session_data:
        raise HTTPException(status_code=401, detail="User not authenticated")

    await cart_repo.add_product(
        user_id=session_data["user_id"],
        product_id=request.product_id,
        quantity=request.quantity,
    )

    response = JSONResponse(content={"message": "Goods added to cart successfully"})
    return response
