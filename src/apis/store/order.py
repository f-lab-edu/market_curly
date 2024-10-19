from fastapi import Cookie, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.service.auth import get_session_data
from src.service.cart import CartService
from src.service.order import OrderService
from src.service.session import SessionService


async def create_order_handler(
    session_id: str = Cookie(None),
    session_service: SessionService = Depends(SessionService),
    cart_service: CartService = Depends(CartService),
    order_service: OrderService = Depends(OrderService),
):
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    session_data = await get_session_data(
        session_id=session_id, session_service=session_service
    )

    if "user_id" not in session_data:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = session_data["user_id"]
    cart_items = await cart_service.get_cart(user_id=user_id)

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    created_order = await order_service.create_order(user_id=user_id, items=cart_items)
    await order_service.created_order_items(order_id=created_order.id, items=cart_items)
    await order_service.change_to_sold(items=cart_items)
    await cart_service.clear_cart(user_id=user_id)

    return JSONResponse(content={"message": "Your order has been completed"})
