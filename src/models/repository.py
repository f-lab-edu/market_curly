from typing import List, Optional, TypeVar

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import SQLModel, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.dependencies import get_session
from src.elastic_client import get_elasticsearch_client
from src.models.product import (
    PrimaryCategory,
    Product,
    SecondaryCategory,
    StatusType,
    Stock,
    TertiaryCategory,
)
from src.models.user import Seller, User
from src.redis_client import get_redis_client

T = TypeVar("T", bound=SQLModel)


class ProductRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_product_list(self) -> List[Product]:
        result = await self.session.exec(
            select(Product)
            .where(Product.use_status == True)
            .options(joinedload(Product.seller))
        )
        return list(result.all())

    async def get_product_list_by_category(
        self, category_type: str, category_id: int
    ) -> Optional[List[Product]]:
        query = select(Product).options(
            selectinload(Product.seller).load_only(Seller.brand_name)
        )

        if category_type == "primary":
            query = (
                query.join(TertiaryCategory)
                .join(SecondaryCategory)
                .join(PrimaryCategory)
                .where(PrimaryCategory.id == category_id)
            )
        elif category_type == "secondary":
            query = (
                query.join(TertiaryCategory)
                .join(SecondaryCategory)
                .where(SecondaryCategory.id == category_id)
            )
        elif category_type == "tertiary":
            query = query.join(TertiaryCategory).where(
                TertiaryCategory.id == category_id
            )
        else:
            return None

        result = await self.session.exec(query)
        result = list(result.all())
        return result if result else None

    async def get_product_by_id(self, product_id: int) -> Product:
        result = await self.session.exec(
            select(Product)
            .where(Product.id == product_id, Product.use_status == True)
            .options(joinedload(Product.category), joinedload(Product.seller))
        )
        return result.one_or_none()

    async def create_product(self, product: Product) -> Product:
        self.session.add(instance=product)
        await self.session.commit()
        await self.session.refresh(instance=product)
        return product

    async def update_product(self, product: Product) -> Product:
        self.session.add(instance=product)
        await self.session.commit()
        await self.session.refresh(instance=product)
        return product

    async def delete_product(self, product: Product) -> None:
        product.use_status = False
        await self.session.commit()

    async def fetch_all_products(self) -> List[Product]:
        async with self.session as session:
            result = await session.exec(
                select(Product).options(
                    joinedload(Product.seller),
                    selectinload(Product.category)
                    .joinedload(TertiaryCategory.secondary_category)
                    .joinedload(SecondaryCategory.primary_category),
                )
            )
            return list(result.all())

    async def fetch_product(self, product_id: int) -> Product:
        result = await self.session.exec(
            select(Product)
            .where(Product.id == product_id)
            .options(
                joinedload(Product.seller),
                selectinload(Product.category)
                .joinedload(TertiaryCategory.secondary_category)
                .joinedload(SecondaryCategory.primary_category),
            )
        )
        return result.one_or_none()

    async def get_product_stock(self, product_id: int) -> Optional[int]:
        result = await self.session.exec(
            select(Product.inventory_quantity).where(
                Product.id == product_id, Product.use_status == True
            )
        )
        return result.one_or_none()


class StockRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def create_stocks(self, product_id: int, quantity: int):
        stock_list = [
            Stock(product_id=product_id, status=StatusType.AVAILABLE)
            for _ in range(quantity)
        ]
        self.session.add_all(stock_list)
        await self.session.commit()

    async def count_stocks_by_product_id(self, product_id: int):
        result = await self.session.exec(
            select(func.count(Stock.id)).where(
                Stock.product_id == product_id, Stock.status == StatusType.AVAILABLE
            )
        )
        return result.one_or_none()

    async def get_available_stock_by_quantity(self, product_id: int, quantity: int):
        result = await self.session.exec(
            select(Stock)
            .where(Stock.product_id == product_id, Stock.status == StatusType.AVAILABLE)
            .limit(quantity)
        )
        return result.all()


class UserRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_user_by_email(self, email: str) -> User:
        result = await self.session.exec(select(User).where(User.email == email))
        return result.one_or_none()

    async def get_user_by_id(self, user_id: int) -> User:
        result = await self.session.exec(select(User).where(User.id == user_id))
        return result.one_or_none()

    async def save_entity(self, instance: T) -> T:
        self.session.add(instance=instance)
        await self.session.commit()
        await self.session.refresh(instance=instance)
        return instance

    async def validate_seller_unique_data(
        self, registration_number: str, brand_name: str
    ) -> bool:
        result = await self.session.exec(
            select(Seller).where(
                (Seller.registration_number == registration_number)
                | (Seller.brand_name == brand_name)
            )
        )
        return result.first() is None


class ElasticsearchRepository:
    def __init__(self, es: AsyncElasticsearch = Depends(get_elasticsearch_client)):
        self.es = es

    async def search_products(self, keyword: str) -> List[dict]:
        def get_search_query(keyword: str) -> dict:
            return {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": keyword,
                                "fields": ["product_name", "brand_name", "ingredient"],
                                "fuzziness": "AUTO",
                            }
                        },
                        {"match_phrase_prefix": {"product_name": keyword}},
                        {"match_phrase_prefix": {"brand_name": keyword}},
                        {"match_phrase_prefix": {"ingredient": keyword}},
                    ]
                }
            }

        def get_filter_query() -> dict:
            return {"term": {"use_status": True}}

        query = {
            "query": {
                "bool": {
                    "must": [get_search_query(keyword)],
                    "filter": [get_filter_query()],
                }
            },
            "sort": [{"id": {"order": "desc"}}],
        }

        response = await self.es.search(index="products", body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    async def get_product_by_id(self, product_id: str) -> dict:
        response = await self.es.get(index="products", id=product_id)
        return response["_source"] if response["found"] else None

    async def get_product_list(self) -> List[dict]:
        response = await self.es.search(
            index="products",
            body={
                "query": {"bool": {"filter": [{"term": {"use_status": True}}]}},
                "sort": [{"id": {"order": "desc"}}],
            },
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]

    async def get_product_list_by_category(
        self, category_type: str, category_id: str
    ) -> List[dict]:
        # 카테고리별 필드 설정 (대분류, 중분류, 소분류)
        category_field = {
            "primary": "category_id_1",  # 대분류
            "secondary": "category_id_2",  # 중분류
            "tertiary": "category_id",  # 소분류
        }.get(category_type)

        if category_field is None:
            return None

        response = await self.es.search(
            index="products",
            body={
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {category_field: category_id}},  # 카테고리 필드로 필터링
                            {"term": {"use_status": True}},
                        ]
                    }
                },
                "sort": [{"id": {"order": "desc"}}],
            },
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]


class CartRepository:
    def __init__(self, redis: Redis = Depends(get_redis_client)):
        self.redis = redis

    @staticmethod
    def generate_cart_key(user_id: int) -> str:
        return f"cart:{user_id}"

    @staticmethod
    def generate_product_key_in_cart(user_id: int, product_id: int) -> str:
        return f"cart:{user_id}:{product_id}"

    @staticmethod
    def generate_reserve_key(user_id: int, product_id: int) -> str:
        return f"reserve:{product_id}:{user_id}"

    async def add_product(self, user_id: int, product_id: int, quantity: int):
        key = self.generate_product_key_in_cart(user_id=user_id, product_id=product_id)
        await self.redis.hset(key, mapping={"quantity": quantity})
        # await self.redis.expire(key, 86400)  # 상품별 TTL 설정 24시간
        await self.redis.expire(key, 60)  # 상품별 TTL 설정 2분

    async def get_cart_product_keys(self, user_id: int) -> list:
        cart_key = self.generate_cart_key(user_id=user_id) + ":*"
        keys = await self.redis.keys(cart_key)
        return keys

    async def delete_from_cart(self, user_id: int, product_id: int):
        key = self.generate_product_key_in_cart(user_id=user_id, product_id=product_id)
        await self.redis.delete(key)

    async def clear_cart(self, keys: list):
        await self.redis.delete(*keys)

    async def get_product_quantity_in_cart(self, user_id: int, product_id: int) -> int:
        key = self.generate_product_key_in_cart(user_id=user_id, product_id=product_id)
        quantity = await self.redis.hget(key, "quantity")
        return int(quantity or 0)

    async def total_stocks_in_cart(self, product_id: int) -> int:
        keys = await self.redis.keys(f"cart:*:{product_id}")
        quantities = 0

        for key in keys:
            quantity = await self.redis.hget(key, "quantity")
            quantities += int(quantity or 0)

        return quantities

    async def product_reservation(self, user_id: int, product_id: int, quantity: int):
        key = self.generate_reserve_key(user_id=user_id, product_id=product_id)
        await self.redis.hincrby(key, "quantity", quantity)
        await self.redis.expire(key, 60)

    async def get_reserved_quantity(self, user_id: int, product_id: int) -> int:
        key = self.generate_reserve_key(user_id=user_id, product_id=product_id)
        reserved_quantity = await self.redis.hget(key, "quantity")
        return int(reserved_quantity or 0)

    async def cancel_reservation(self, user_id: int, product_id: int, quantity: int):
        key = self.generate_reserve_key(user_id=user_id, product_id=product_id)
        reserved_quantity = int(await self.redis.hget(key, "quantity"))

        if reserved_quantity >= quantity:
            updated_quantity = reserved_quantity - quantity
            if updated_quantity > 0:
                await self.redis.hset(key, "quantity", updated_quantity)
                await self.redis.expire(key, 60)
            else:
                await self.redis.delete(key)
        else:
            raise ValueError("Cannot cancel more than the reserved quantity.")

    async def delete_reserve_key(self, user_id: int, product_id: int):
        key = self.generate_reserve_key(user_id=user_id, product_id=product_id)
        await self.redis.delete(key)

    async def reserve_key_exists(self, user_id: int, product_id: int) -> bool:
        key = self.generate_reserve_key(user_id=user_id, product_id=product_id)
        return await self.redis.exists(key) == 1
