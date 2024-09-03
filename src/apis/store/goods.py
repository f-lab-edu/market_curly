import re
from typing import List

from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException, Query

from src.elastic_client import get_elasticsearch_client
from src.models.product import Product
from src.models.repository import ProductRepository
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


async def search_goods_handler(
    keyword: str, es_client: AsyncElasticsearch = Depends(get_elasticsearch_client)
) -> List[GetGoodsResponse]:
    try:
        response = await es_client.search(
            index="products",
            body={
                "query": {
                    "multi_match": {
                        "query": keyword,
                        "fields": ["product_name", "brand_name", "ingredient"],
                        "fuzziness": "AUTO",
                    }
                }
            },
        )

        products = [
            GetGoodsResponse(
                id=hit["_source"]["id"],
                brand_name=hit["_source"]["brand_name"],
                product_name=hit["_source"]["product_name"],
                price=hit["_source"]["price"],
                discounted_price=hit["_source"]["discounted_price"],
            )
            for hit in response["hits"]["hits"]
        ]

        return products

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
