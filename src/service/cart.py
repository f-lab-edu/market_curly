from fastapi import Depends

from src.models.repository import (
    CartRepository,
    ElasticsearchRepository,
    ProductRepository,
    StockRepository,
)
from src.schema.response import CartResponse
from src.service.inventory import InventoryService


class CartService:
    def __init__(
        self,
        cart_repo: CartRepository = Depends(CartRepository),
        es_repo: ElasticsearchRepository = Depends(ElasticsearchRepository),
        product_repo: ProductRepository = Depends(ProductRepository),
        stock_repo: StockRepository = Depends(StockRepository),
        inventory_service: InventoryService = Depends(InventoryService),
    ):
        self.cart_repo = cart_repo
        self.es_repo = es_repo
        self.product_repo = product_repo
        self.stock_repo = stock_repo
        self.inventory_service = inventory_service

    async def add_to_cart(self, user_id: int, product_id: int, quantity: int) -> dict:
        available_stock = None

        try:
            stocks_count: int = await self.stock_repo.count_stocks_by_product_id(
                product_id=product_id
            )
            total_in_cart: int = await self.cart_repo.total_stocks_in_cart(
                product_id=product_id
            )
            available_stock = stocks_count - total_in_cart

            current_quantity: int = await self.cart_repo.get_product_quantity_in_cart(
                user_id=user_id, product_id=product_id
            )
            total_quantity = current_quantity + quantity

            if available_stock <= 10:  # 임계값 이하일 경우 Redis에서 별도 예약 관리
                reserved_quantity: int = await self.cart_repo.get_reserved_quantity(
                    user_id=user_id, product_id=product_id
                )
                total_reserved_quantity: int = reserved_quantity + quantity

                await self.cart_repo.product_reservation(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=total_reserved_quantity,
                )

            if available_stock >= quantity:
                await self.cart_repo.add_product(
                    user_id=user_id, product_id=product_id, quantity=total_quantity
                )

                return {
                    "is_success": True,
                    "message": "Goods added to cart successfully",
                }
            else:
                if available_stock <= 10:
                    await self.cart_repo.cancel_reservation(
                        user_id=user_id, product_id=product_id, quantity=quantity
                    )

                return {
                    "is_success": False,
                    "status_code": 400,
                    "message": f"Quantity requested ({quantity}) exceeds available stock ({available_stock}).",
                }

        except Exception as e:
            if available_stock is not None and available_stock <= 10:
                await self.cart_repo.cancel_reservation(
                    user_id=user_id, product_id=product_id, quantity=quantity
                )

            return {
                "is_success": False,
                "status_code": 500,
                "message": f"An error occurred: {str(e)}",
            }

    async def get_cart(self, user_id: int) -> list[CartResponse]:
        cart_response = []
        product_keys = await self.cart_repo.get_cart_product_keys(user_id=user_id)
        for key in product_keys:
            product_id = key.split(":")[2]
            quantity = await self.cart_repo.get_product_quantity_in_cart(
                user_id=user_id, product_id=product_id
            )
            info = await self.es_repo.get_product_by_id(product_id=product_id)
            cart_response.append(
                CartResponse(product_id=product_id, quantity=quantity, **info)
            )
        return cart_response

    async def delete_from_cart(self, user_id: int, product_id: int):
        await self.cart_repo.delete_from_cart(user_id=user_id, product_id=product_id)

        if await self.cart_repo.reserve_key_exists(
            user_id=user_id, product_id=product_id
        ):
            await self.cart_repo.delete_reserve_key(
                user_id=user_id, product_id=product_id
            )

    async def clear_cart(self, user_id: int):
        product_keys = await self.cart_repo.get_cart_product_keys(user_id=user_id)
        for key in product_keys:
            product_id = key.split(":")[-1]
            if await self.cart_repo.reserve_key_exists(
                user_id=user_id, product_id=product_id
            ):
                await self.cart_repo.delete_reserve_key(
                    user_id=user_id, product_id=product_id
                )

        await self.cart_repo.clear_cart(keys=product_keys)

    async def update_cart_quantity(
        self, user_id: int, product_id: int, quantity: int
    ) -> dict:
        if quantity == 0:
            await self.delete_from_cart(user_id=user_id, product_id=product_id)
            return {"is_success": True, "message": "Product removed from cart"}

        current_quantity: int = await self.cart_repo.get_product_quantity_in_cart(
            user_id=user_id, product_id=product_id
        )
        if current_quantity == 0:
            return {
                "is_success": False,
                "status_code": 400,
                "message": "Product not in cart",
            }

        if quantity == current_quantity:
            return {"is_success": True, "message": "Quantity remains the same"}
        elif quantity < current_quantity:
            if await self.cart_repo.reserve_key_exists(
                user_id=user_id, product_id=product_id
            ):
                await self.cart_repo.cancel_reservation(
                    user_id=user_id, product_id=product_id, quantity=quantity
                )
        else:
            if await self.cart_repo.reserve_key_exists(
                user_id=user_id, product_id=product_id
            ):
                await self.cart_repo.product_reservation(
                    user_id=user_id, product_id=product_id, quantity=quantity
                )

        await self.cart_repo.add_product(
            user_id=user_id, product_id=product_id, quantity=quantity
        )
        return {"is_success": True, "message": "Cart updated successfully"}
