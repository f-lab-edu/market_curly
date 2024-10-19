from fastapi import Depends

from src.models.order import Order, OrderItem, OrderStatusType
from src.models.repository import OrderRepository, StockRepository


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository = Depends(OrderRepository),
        stock_repo: StockRepository = Depends(StockRepository),
    ):
        self.order_repo = order_repo
        self.stock_repo = stock_repo

    async def create_order(self, user_id: int, items: list) -> Order:
        total_price = sum(
            (item.discounted_price if item.discounted_price else item.price)
            * item.quantity
            for item in items
        )
        order = Order(
            user_id=user_id, total_price=total_price, status=OrderStatusType.PENDING
        )
        created_order = await self.order_repo.create_order(order=order)
        return created_order

    async def created_order_items(self, order_id: int, items: list):
        order_items = [
            OrderItem(
                order_id=order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.discounted_price if item.discounted_price else item.price,
            )
            for item in items
        ]
        await self.order_repo.create_order_items(order_items=order_items)

    async def change_to_sold(self, items: list):
        for item in items:
            stocks: list = await self.stock_repo.get_available_stock_by_quantity(
                product_id=item.product_id, quantity=item.quantity
            )
            await self.stock_repo.update_stock_status_to_sold(stocks=stocks)
