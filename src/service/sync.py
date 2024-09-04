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
                await es.index(
                    index="products",
                    id=product_info["id"],
                    body=product_info,
                    refresh="wait_for",
                )
        except Exception as e:
            print(f"Error syncing all products: {e}")
