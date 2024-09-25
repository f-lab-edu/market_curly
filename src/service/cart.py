from fastapi import Depends

from src.models.repository import (
    CartRepository,
    ElasticsearchRepository,
    ProductRepository,
)
from src.schema.response import CartResponse
from src.service.inventory import InventoryService


class CartService:
    def __init__(
        self,
        cart_repo: CartRepository = Depends(CartRepository),
        es_repo: ElasticsearchRepository = Depends(ElasticsearchRepository),
        product_repo: ProductRepository = Depends(ProductRepository),
        inventory_service: InventoryService = Depends(InventoryService),
    ):
        self.cart_repo = cart_repo
        self.es_repo = es_repo
        self.product_repo = product_repo
        self.inventory_service = inventory_service

    async def add_to_cart(self, user_id: int, product_id: int, quantity: int) -> dict:
        # 1. 예약 관리 여부 확인
        if await self.inventory_service.is_product_reserved(product_id=product_id):
            # 2. 예약 관리 중일 때 예약 슬롯 확인
            empty_slots: list = (
                await self.inventory_service.get_empty_reservation_slots(
                    product_id=product_id
                )
            )
            available_quantity: int = len(empty_slots)

            if available_quantity == 0:
                return {
                    "is_success": False,
                    "status_code": 400,
                    "message": "Insufficient stock",
                }
            elif available_quantity < quantity:
                return {
                    "is_success": False,
                    "status_code": 400,
                    "message": "Quantity requested is more than available",
                }
        else:
            # 3. 비예약 관리 상품인 경우 MySQL에서 재고 확인
            stock: int | None = await self.product_repo.get_product_stock(
                product_id=product_id
            )

            if stock is None:
                return {
                    "is_success": False,
                    "status_code": 404,
                    "message": "Product not found or unavailable",
                }
            elif stock < quantity:
                return {
                    "is_success": False,
                    "status_code": 400,
                    "message": "Insufficient stock",
                }

            # 4. 재고가 10개 이하일 때 Redis에서 예약 관리하도록 슬롯 생성
            if stock <= 10:
                is_created_slots: bool = (
                    await self.inventory_service.create_reservation_slots(
                        product_id=product_id, stock=stock
                    )
                )
                if not is_created_slots:
                    return {
                        "is_success": False,
                        "status_code": 503,
                        "message": "Service temporarily unavailable. Please try again later.",
                    }

        # 5. 장바구니에 상품 추가 또는 수량 업데이트
        current_quantity: int = await self.cart_repo.get_product_quantity_in_cart(
            user_id=user_id, product_id=product_id
        )
        if current_quantity:
            total_quantity = current_quantity + quantity
            await self.cart_repo.add_product(
                user_id=user_id, product_id=product_id, quantity=total_quantity
            )
        else:
            await self.cart_repo.add_product(
                user_id=user_id, product_id=product_id, quantity=quantity
            )

        # 6. 예약 관리 중인 상품일 때 예약 슬롯 업데이트
        if await self.inventory_service.is_product_reserved(product_id=product_id):
            is_reservation_result = await self.inventory_service.reserve_product(
                user_id=user_id, product_id=product_id, quantity=quantity
            )
            if not is_reservation_result:
                return {
                    "is_success": False,
                    "status_code": 503,
                    "message": "Reservation failed. Please try again later.",
                }

        return {"is_success": True, "message": "Goods added to cart successfully"}

    async def get_cart(self, user_id: int) -> list[CartResponse]:
        cart_data = await self.cart_repo.get_cart(user_id=user_id)

        cart_response = []
        for product_id, quantity in cart_data.items():
            product_info = await self.es_repo.get_product_by_id(product_id=product_id)
            cart_response.append(
                CartResponse(product_id=product_id, quantity=quantity, **product_info)
            )

        return cart_response

    async def delete_from_cart(self, user_id: int, product_id: int):
        await self.cart_repo.delete_from_cart(user_id=user_id, product_id=product_id)
        await self.inventory_service.release_product(
            user_id=user_id, product_id=product_id
        )

    async def clear_cart(self, user_id: int):
        cart_data = await self.cart_repo.get_cart(user_id=user_id)
        for product_id, quantity in cart_data.items():
            if await self.inventory_service.is_product_reserved(product_id=product_id):
                await self.inventory_service.release_product(
                    user_id=user_id, product_id=product_id
                )

        await self.cart_repo.clear_cart(user_id=user_id)

    async def update_cart_quantity(
        self, user_id: int, product_id: int, quantity: int
    ) -> dict:
        if quantity == 0:
            await self.cart_repo.delete_from_cart(
                user_id=user_id, product_id=product_id
            )
            if await self.inventory_service.is_product_reserved(product_id=product_id):
                await self.inventory_service.release_product(
                    user_id=user_id, product_id=product_id
                )
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

        if quantity < current_quantity:
            quantity_to_release = current_quantity - quantity

            if await self.inventory_service.is_product_reserved(product_id=product_id):
                is_release_result = (
                    await self.inventory_service.release_partial_product(
                        user_id=user_id,
                        product_id=product_id,
                        quantity_to_release=quantity_to_release,
                    )
                )

                if not is_release_result:
                    return {
                        "is_success": False,
                        "status_code": 503,
                        "message": "Slot release failed. Please try again later.",
                    }

            await self.cart_repo.add_product(
                user_id=user_id, product_id=product_id, quantity=quantity
            )

        elif quantity > current_quantity:
            additional_quantity = quantity - current_quantity
            return await self.add_to_cart(
                user_id=user_id, product_id=product_id, quantity=additional_quantity
            )

        return {"is_success": True, "message": "Cart updated successfully"}
