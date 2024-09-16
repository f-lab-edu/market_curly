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

    async def reserve_product(
        self, user_id: int, product_id: int, quantity: int, stock: int
    ) -> bool:
        reservation_key = self.generate_reservation_key(product_id=product_id)

        if not await self.redis.exists(reservation_key):
            if not await self.create_reservation_slots(
                product_id=product_id, stock=stock
            ):
                return False

        reserved_items = []
        for i in range(1, quantity + 1):
            item_key = await self.redis.hget(reservation_key, str(i))
            if item_key == "":  # 예약 가능
                await self.redis.hset(reservation_key, str(i), user_id)
                reserved_items.append(i)
            else:
                return False
        return True

    async def release_product(self, user_id: int, product_id: int):
        reservation_key = self.generate_reservation_key(product_id=product_id)

        if await self.redis.exists(reservation_key):
            all_slots = await self.redis.hgetall(reservation_key)
            user_slots = [
                slot for slot, value in all_slots.items() if value == str(user_id)
            ]

            for slot_number in user_slots:
                await self.redis.hset(reservation_key, slot_number, "")
