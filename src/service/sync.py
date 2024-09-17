from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import engine
from src.elastic_client import get_elasticsearch_client
from src.models.repository import ProductRepository

es = get_elasticsearch_client()


async def sync_all_products():
    async with AsyncSession(engine) as session:
        product_repo = ProductRepository(session)
        try:
            products = await product_repo.fetch_all_products()  # 기존 상품 전체 가져오기

            for product in products:
                product_info = product.model_dump()

                ##### 필요한 추가 정보 입력 #####
                # 1. 판매자 정보 : 브랜드명, 전화번호
                product_info["brand_name"] = product.seller.brand_name
                product_info["contact_number"] = product.seller.contact_number
                # 2. 카테고리 정보 : 종류별(대/중/소) 카테고리 ID, 카테고리명
                # 소분류 (id는 상품 정보에 category_id 필드로 이미 포함되어 있음)
                product_info["category_3"] = product.category.name
                # 중분류
                product_info["category_id_2"] = product.category.secondary_category.id
                product_info["category_2"] = product.category.secondary_category.name
                # 대분류
                product_info[
                    "category_id_1"
                ] = product.category.secondary_category.primary_category.id
                product_info[
                    "category_1"
                ] = product.category.secondary_category.primary_category.name

                await es.index(
                    index="products",
                    id=product_info["id"],
                    body=product_info,
                    refresh="wait_for",
                )
        except Exception as e:
            print(f"Error syncing all products: {e}")
