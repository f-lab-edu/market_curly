from typing import List

from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.product import Product


async def get_product_list(session: AsyncSession) -> List[Product]:
    result = await session.exec(
        select(Product)
        .where(Product.use_status == True)
        .options(joinedload(Product.seller))
    )
    return list(result.all())


async def get_product_by_id(product_id: int, session: AsyncSession) -> Product:
    result = await session.exec(
        select(Product)
        .where(Product.id == product_id, Product.use_status == True)
        .options(joinedload(Product.category), joinedload(Product.seller))
    )
    return result.one_or_none()


async def create_product(product: Product, session: AsyncSession) -> Product:
    session.add(instance=product)
    await session.commit()
    await session.refresh(instance=product)
    return product


async def update_product(product: Product, session: AsyncSession) -> Product:
    session.add(instance=product)
    await session.commit()
    await session.refresh(instance=product)
    return product


async def delete_product(product: Product, session: AsyncSession) -> None:
    # await session.execute(delete(Product).where(Product.id == product_id))
    product.use_status = False
    await session.commit()
