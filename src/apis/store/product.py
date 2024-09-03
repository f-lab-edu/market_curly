import asyncio

from fastapi import Cookie, Depends, HTTPException

from src.models.product import Product
from src.models.repository import ProductRepository, UserRepository
from src.models.user import User
from src.schema.request import CreateProductRequest, UpdateProductRequest
from src.schema.response import GetProductDetailResponse, GetProductResponse
from src.service.auth import verify_seller, verify_user_can_access_product
from src.service.background_task import add_product_to_stream
from src.service.session import SessionService


async def create_product_handler(
    request: CreateProductRequest,
    product_repo: ProductRepository = Depends(ProductRepository),
    user_repo: UserRepository = Depends(UserRepository),
    session_id: str = Cookie(None),
    session_service: SessionService = Depends(),
) -> GetProductResponse:
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    user_id: int = await verify_seller(
        session_id=session_id, session_service=session_service
    )
    user: User = await user_repo.get_user_by_id(user_id=user_id)

    request_data = request.model_dump(exclude_unset=True)
    product: Product = Product(seller_id=user.seller.id, **request_data)
    created_product: Product = await product_repo.create_product(product)

    product_info = created_product.model_dump()
    product_info["brand_name"] = created_product.seller.brand_name
    await asyncio.create_task(add_product_to_stream(product_info=product_info))

    return GetProductResponse(
        id=created_product.id,
        product_name=created_product.product_name,
        price=created_product.price,
        discounted_price=created_product.discounted_price,
    )


async def get_product_by_id_handler(
    product_id: int,
    product_repo: ProductRepository = Depends(ProductRepository),
    user_repo: UserRepository = Depends(UserRepository),
    session_id: str = Cookie(None),
    session_service: SessionService = Depends(),
) -> GetProductDetailResponse:
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    user_id: int = await verify_seller(
        session_id=session_id, session_service=session_service
    )
    user: User = await user_repo.get_user_by_id(user_id=user_id)

    product: Product | None = await product_repo.get_product_by_id(product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product Not Found")

    await verify_user_can_access_product(
        seller_id=user.seller.id, product_seller_id=product.seller_id
    )

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
    product_repo: ProductRepository = Depends(ProductRepository),
    user_repo: UserRepository = Depends(UserRepository),
    session_id: str = Cookie(None),
    session_service: SessionService = Depends(),
):
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    user_id: int = await verify_seller(
        session_id=session_id, session_service=session_service
    )
    user: User = await user_repo.get_user_by_id(user_id=user_id)

    product: Product | None = await product_repo.get_product_by_id(product_id)

    if product:
        await verify_user_can_access_product(
            seller_id=user.seller.id, product_seller_id=product.seller_id
        )

        request_data = request.model_dump(exclude_unset=True)
        for key, value in request_data.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)

        updated_product: Product = await product_repo.update_product(product)
        return GetProductResponse(
            id=updated_product.id,
            product_name=updated_product.product_name,
            price=updated_product.price,
            discounted_price=updated_product.discounted_price,
        )

    raise HTTPException(status_code=404, detail="Product Not Found")


async def delete_product_handler(
    product_id: int,
    product_repo: ProductRepository = Depends(ProductRepository),
    user_repo: UserRepository = Depends(UserRepository),
    session_id: str = Cookie(None),
    session_service: SessionService = Depends(),
):
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing Session ID")

    user_id: int = await verify_seller(
        session_id=session_id, session_service=session_service
    )
    user: User = await user_repo.get_user_by_id(user_id=user_id)

    product: Product | None = await product_repo.get_product_by_id(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")

    await verify_user_can_access_product(
        seller_id=user.seller.id, product_seller_id=product.seller_id
    )

    await product_repo.delete_product(product)
