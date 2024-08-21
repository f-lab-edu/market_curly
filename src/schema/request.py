from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr

from src.models.user import UserType


class CreateProductRequest(BaseModel):
    # seller_id: int
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


class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=20)
    user_type: UserType

    # 판매자 정보
    registration_number: Optional[str] = Field(None, pattern=r"^\d{3}-\d{2}-\d{5}$")
    brand_name: Optional[str] = None
    contact_number: Optional[str] = Field(
        None, pattern=r"^(\d{2,3}-\d{3,4}-\d{4}|\d{4}-\d{4})$"
    )

    # 구매자 정보
    name: Optional[str] = None
    phone_number: Optional[str] = Field(None, pattern=r"^\d{3}-\d{3,4}-\d{4}$")
    address: Optional[str] = None


class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str
