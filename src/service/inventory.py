from fastapi import Depends
from redis.asyncio import Redis

from src.redis_client import get_redis_client


class InventoryService:
    def __init__(self, redis: Redis = Depends(get_redis_client)):
        self.redis = redis

    def generate_reservation_key(self, product_id: int) -> str:
        return f"product:{product_id}:inventory"

    async def create_reservation_slots(self, product_id: int, stock: int):
        reservation_key = self.generate_reservation_key(product_id=product_id)

        try:
            for i in range(1, stock + 1):
                await self.redis.hset(
                    reservation_key, mapping={str(i): "" for i in range(1, stock + 1)}
                )
            return True
        except Exception as e:
            print(f"Redis error occurred: {e}")
            return False

    async def is_product_reserved(self, product_id: int) -> bool:
        reservation_key = self.generate_reservation_key(product_id=product_id)
        return await self.redis.exists(reservation_key)

    async def get_empty_reservation_slots(self, product_id: int) -> list:
        reservation_key = self.generate_reservation_key(product_id=product_id)
        all_slots = await self.redis.hgetall(reservation_key)
        empty_slots = [slot for slot, value in all_slots.items() if value == ""]
        return empty_slots

    async def reserve_product(
        self, user_id: int, product_id: int, quantity: int
    ) -> bool:
        empty_slots = await self.get_empty_reservation_slots(product_id=product_id)
        if len(empty_slots) < quantity:
            return False

        reservation_key = self.generate_reservation_key(product_id=product_id)
        for i in range(quantity):
            slot = empty_slots[i]
            await self.redis.hset(reservation_key, slot, user_id)

        return True

    async def release_product(self, user_id: int, product_id: int):
        if await self.is_product_reserved(product_id=product_id):
            reservation_key = self.generate_reservation_key(product_id=product_id)
            all_slots = await self.redis.hgetall(reservation_key)
            user_slots = [
                slot for slot, value in all_slots.items() if value == str(user_id)
            ]

            for slot_number in user_slots:
                await self.redis.hset(reservation_key, slot_number, "")

    async def release_partial_product(
        self, user_id: int, product_id: int, quantity_to_release: int
    ) -> bool:
        if await self.is_product_reserved(product_id=product_id):
            reservation_key = self.generate_reservation_key(product_id=product_id)
            all_slots = await self.redis.hgetall(reservation_key)
            user_slots = [
                slot for slot, value in all_slots.items() if value == str(user_id)
            ]

            if len(user_slots) < quantity_to_release:
                return False  # 해제하려는 수량이 예약된 수량보다 많으면 실패

            for slot in user_slots[:quantity_to_release]:
                await self.redis.hset(reservation_key, slot, "")

            return True

        return False
