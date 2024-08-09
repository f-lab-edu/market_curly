from typing import List

from fastapi import Depends
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.dependencies import get_session
from src.models.product import Product


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
