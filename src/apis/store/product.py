from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.dependencies import get_session
from src.models.product import Product
from src.models.repository import (
    create_product,
    delete_product,
    get_product_by_id,
    update_product,
)
from src.schema.request import CreateProductRequest, UpdateProductRequest
from src.schema.response import GetProductDetailResponse, GetProductResponse


async def create_product_handler(
    request: CreateProductRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetProductResponse:
    request_data = request.dict(exclude_unset=True)

    product: Product = Product(**request_data)
    created_product: Product = await create_product(product, session)

    return GetProductResponse(
        id=created_product.id,
        product_name=created_product.product_name,
        price=created_product.price,
        discounted_price=created_product.discounted_price,
    )


async def get_product_by_id_handler(
    product_id: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> GetProductDetailResponse:
    product: Product | None = await get_product_by_id(product_id, session)

    if product is None:
        raise HTTPException(status_code=404, detail="Product Not Found")

    return GetProductDetailResponse(
        id=product.id,
        category=f"{product.category.name}({product.category_id})",
        product_name=product.product_name,
        price=product.price,
        discounted_price=product.discounted_price,
        capacity=product.capacity,
        key_specification=product.key_specification,
        expiration_date=product.expiration_date,
        how_to_use=product.how_to_use,
        ingredient=product.ingredient,
        caution=product.caution,
        inventory_quantity=product.inventory_quantity,
        use_status=product.use_status,
    )


async def update_product_handler(
    product_id: int,
    request: UpdateProductRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    product: Product | None = await get_product_by_id(product_id, session)

    if product:
        request_data = request.dict(exclude_unset=True)
        for key, value in request_data.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)

        updated_product: Product = await update_product(product, session)
        return GetProductResponse(
            id=updated_product.id,
            product_name=updated_product.product_name,
            price=updated_product.price,
            discounted_price=updated_product.discounted_price,
        )

    raise HTTPException(status_code=404, detail="Product Not Found")


async def delete_product_handler(
    product_id: int, session: Annotated[AsyncSession, Depends(get_session)]
):
    product: Product | None = await get_product_by_id(product_id, session)

    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")

    await delete_product(product_id, session)
