from enum import Enum
from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Text
from sqlmodel import Field, Relationship, SQLModel

from src.models.user import Seller


class PrimaryCategory(SQLModel, table=True):
    __tablename__ = "primary_categories"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(nullable=False, max_length=20, unique=True)

    secondary_categories: List["SecondaryCategory"] = Relationship(
        back_populates="primary_category"
    )


class SecondaryCategory(SQLModel, table=True):
    __tablename__ = "secondary_categories"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(nullable=False, max_length=20)
    primary_category_id: int = Field(
        foreign_key="primary_categories.id", nullable=False
    )

    primary_category: "PrimaryCategory" = Relationship(
        back_populates="secondary_categories"
    )
    tertiary_categories: List["TertiaryCategory"] = Relationship(
        back_populates="secondary_category"
    )


class TertiaryCategory(SQLModel, table=True):
    __tablename__ = "tertiary_categories"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(nullable=False, max_length=20)
    secondary_category_id: int = Field(
        foreign_key="secondary_categories.id", nullable=False
    )

    secondary_category: "SecondaryCategory" = Relationship(
        back_populates="tertiary_categories"
    )
    products: List["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    seller_id: int = Field(foreign_key="sellers.id", nullable=False)
    product_name: str = Field(nullable=False, max_length=100)
    category_id: int = Field(foreign_key="tertiary_categories.id", nullable=False)
    price: int = Field(nullable=False)
    discounted_price: Optional[int] = Field(default=0, nullable=False)
    capacity: Optional[str] = Field(default=None, max_length=20, nullable=True)
    key_specification: Optional[str] = Field(default=None, max_length=50, nullable=True)
    expiration_date: Optional[str] = Field(default=None, max_length=50, nullable=True)
    how_to_use: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    ingredient: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    caution: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    inventory_quantity: Optional[int] = Field(default=0, nullable=False)
    use_status: bool = Field(default=True, nullable=False)

    category: "TertiaryCategory" = Relationship(back_populates="products")
    seller: "Seller" = Relationship(back_populates="products")
    stocks: List["Stock"] = Relationship(back_populates="product")


class StatusType(str, Enum):
    AVAILABLE = "AVAILABLE"
    SOLD = "SOLD"


class Stock(SQLModel, table=True):
    __tablename__ = "stocks"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    status: StatusType = Field(sa_column=Column(SqlEnum(StatusType), nullable=False))

    product: "Product" = Relationship(back_populates="stocks")
