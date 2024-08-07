from typing import Annotated, List

from fastapi import Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.dependencies import get_session
from src.models.product import Product
from src.models.repository import get_product_by_id, get_product_list
from src.schema.response import GetGoodsDetailResponse, GetGoodsResponse


async def get_goods_list_handler(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> List[GetGoodsResponse]:
    goods_list: List[Product] = await get_product_list(session)

    return sorted(
        [
            GetGoodsResponse(
                id=goods.id,
                brand=goods.seller.corporate_name,
                product_name=goods.product_name,
                price=goods.price,
                discounted_price=goods.discounted_price,
            )
            for goods in goods_list
        ],
        key=lambda goods: -goods.id,
    )


async def get_goods_by_id_handler(
    goods_id: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> GetGoodsDetailResponse:
    goods: Product | None = await get_product_by_id(goods_id, session)

    if goods is None:
        raise HTTPException(status_code=404, detail="Goods Not Found")

    return GetGoodsDetailResponse(
        id=goods.id,
        category=goods.category.name,
        brand=goods.seller.corporate_name,
        product_name=goods.product_name,
        price=goods.price,
        discounted_price=goods.discounted_price,
        capacity=goods.capacity,
        key_specification=goods.key_specification,
        expiration_date=goods.expiration_date,
        how_to_use=goods.how_to_use,
        ingredient=goods.ingredient,
        caution=goods.caution,
        contact=goods.seller.contact_information,
    )
