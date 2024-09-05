import re
from typing import List

from fastapi import Depends, HTTPException, Query

from src.models.product import Product
from src.models.repository import ElasticsearchRepository, ProductRepository
from src.schema.response import GetGoodsDetailResponse, GetGoodsResponse


async def get_goods_list_handler(
    category: str = Query(default=None, max_length=15),
    product_repo: ProductRepository = Depends(ProductRepository),
) -> List[GetGoodsResponse]:
    if not category:
        goods_list: List[Product] = await product_repo.get_product_list()
    else:
        match = re.match(r"(\D+)(\d+)", category)
        if not match:
            raise HTTPException(status_code=400, detail="Invalid query format.")

        category_type, category_id = match.groups()
        category_id = int(category_id)

        goods_list = await product_repo.get_product_list_by_category(
            category_type, category_id
        )

    if goods_list is None:
        goods_list = []

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
    goods_id: int, es_repo: ElasticsearchRepository = Depends(ElasticsearchRepository)
) -> GetGoodsDetailResponse:
    goods: dict | None = await es_repo.get_product_by_id(product_id=goods_id)

    if goods is None:
        raise HTTPException(status_code=404, detail="Goods Not Found")

    return GetGoodsDetailResponse(
        category=f"{goods['category_1']} > {goods['category_2']} > {goods['category_3']}",
        **goods,
    )


async def search_goods_handler(
    keyword: str, es_repo: ElasticsearchRepository = Depends(ElasticsearchRepository)
) -> List[GetGoodsResponse]:
    if not keyword:
        raise HTTPException(
            status_code=422, detail="Keyword is required and cannot be empty."
        )

    products = await es_repo.search_products(keyword)

    response = [
        GetGoodsResponse(
            id=product["id"],
            brand_name=product["brand_name"],
            product_name=product["product_name"],
            price=product["price"],
            discounted_price=product["discounted_price"],
        )
        for product in products
    ]

    return response
