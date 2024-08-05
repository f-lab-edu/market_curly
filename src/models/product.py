from typing import List, Optional

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
    name: str = Field(nullable=False, max_length=20, unique=True)
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
    name: str = Field(nullable=False, max_length=20, unique=True)
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
    capacity: Optional[str] = Field(default=None, max_length=20)
    key_specification: Optional[str] = Field(default=None, max_length=50)
    expiration_date: Optional[str] = Field(default=None, max_length=50)
    how_to_use: Optional[str] = Field(default=None)
    ingredient: Optional[str] = Field(default=None)
    caution: Optional[str] = Field(default=None)
    inventory_quantity: Optional[int] = Field(default=0, nullable=False)
    use_status: bool = Field(default=True, nullable=False)

    category: "TertiaryCategory" = Relationship(back_populates="products")
    seller: "Seller" = Relationship(back_populates="products")
