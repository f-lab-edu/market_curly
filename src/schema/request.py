from typing import Optional

from pydantic import BaseModel


class CreateProductRequest(BaseModel):
    seller_id: int
    product_name: str
    category_id: int
    price: int
    discounted_price: Optional[int] = None
    capacity: Optional[str] = None
    key_specification: Optional[str] = None
    expiration_date: Optional[str] = None
    how_to_use: Optional[str] = None
    ingredient: Optional[str] = None
    caution: Optional[str] = None
    inventory_quantity: Optional[int] = None


class UpdateProductRequest(BaseModel):
    product_name: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[int] = None
    discounted_price: Optional[int] = None
    capacity: Optional[str] = None
    key_specification: Optional[str] = None
    expiration_date: Optional[str] = None
    how_to_use: Optional[str] = None
    ingredient: Optional[str] = None
    caution: Optional[str] = None
    inventory_quantity: Optional[int] = None
