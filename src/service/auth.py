from fastapi import HTTPException

from src.models.user import UserType
from src.service.session import SessionService


async def get_session_data(session_id: str, session_service: SessionService) -> dict:
    session_data = await session_service.get_session(session_id=session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session Not Found")

    return session_data


async def verify_seller(session_id: str, session_service: SessionService) -> int:
    session_data = await get_session_data(
        session_id=session_id, session_service=session_service
    )

    user_type = session_data["user_type"]
    if user_type != UserType.SELLER:
        raise HTTPException(status_code=403, detail="Not Authorized")

    return session_data["user_id"]


async def verify_user_can_access_product(
    seller_id: int, product_seller_id: int
) -> None:
    if seller_id != product_seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
