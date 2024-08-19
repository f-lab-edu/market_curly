from typing import List, TypeVar

from fastapi import Depends
from sqlalchemy.orm import joinedload
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.dependencies import get_session
from src.models.product import Product
from src.models.user import Seller, User

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
