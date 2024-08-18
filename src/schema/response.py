from typing import Optional

from pydantic import BaseModel


class GetGoodsResponse(BaseModel):
    id: int
    brand_name: str
    product_name: str
    price: int
    discounted_price: int


class GetGoodsDetailResponse(BaseModel):
    id: int
    category: str
    brand_name: str
    product_name: str
    price: int
    discounted_price: int
    capacity: Optional[str] = None
    key_specification: Optional[str] = None
    expiration_date: Optional[str] = None
    how_to_use: Optional[str] = None
    ingredient: Optional[str] = None
    caution: Optional[str] = None
    contact_number: str


class GetProductResponse(BaseModel):
    id: int
    product_name: str
    price: int
    discounted_price: int


class GetProductDetailResponse(BaseModel):
    id: int
    category: str
    product_name: str
    price: int
    discounted_price: int
    capacity: Optional[str] = None
    key_specification: Optional[str] = None
    expiration_date: Optional[str] = None
    how_to_use: Optional[str] = None
    ingredient: Optional[str] = None
    caution: Optional[str] = None
    inventory_quantity: int
    use_status: bool
