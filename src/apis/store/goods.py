from typing import List

from fastapi import Depends, HTTPException

from src.models.product import Product
from src.models.repository import ProductRepository
from src.schema.response import GetGoodsDetailResponse, GetGoodsResponse


async def get_goods_list_handler(
    # session: Annotated[AsyncSession, Depends(get_session)]
    product_repo: ProductRepository = Depends(ProductRepository),
) -> List[GetGoodsResponse]:
    goods_list: List[Product] = await product_repo.get_product_list()

    return sorted(
        [
            GetGoodsResponse(
                id=goods.id,
                brand_name=goods.seller.brand_name,
                product_name=goods.product_name,
                price=goods.price,
                discounted_price=goods.discounted_price,
            )
            for goods in goods_list
        ],
        key=lambda goods: -goods.id,
    )


async def get_goods_by_id_handler(
    goods_id: int, product_repo: ProductRepository = Depends(ProductRepository)
) -> GetGoodsDetailResponse:
    goods: Product | None = await product_repo.get_product_by_id(goods_id)

    if goods is None:
        raise HTTPException(status_code=404, detail="Goods Not Found")

    return GetGoodsDetailResponse(
        id=goods.id,
        category=goods.category.name,
        brand_name=goods.seller.brand_name,
        product_name=goods.product_name,
        price=goods.price,
        discounted_price=goods.discounted_price,
        capacity=goods.capacity,
        key_specification=goods.key_specification,
        expiration_date=goods.expiration_date,
        how_to_use=goods.how_to_use,
        ingredient=goods.ingredient,
        caution=goods.caution,
        contact_number=goods.seller.contact_number,
    )
