from enum import Enum
from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String
from sqlmodel import Field, Relationship, SQLModel


class UserType(str, Enum):
    SELLER = "SELLER"
    BUYER = "BUYER"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(sa_column=Column(String(255), nullable=False, unique=True))
    password: str = Field(sa_column=Column(String(255), nullable=False))
    user_type: UserType = Field(sa_column=Column(SqlEnum(UserType), nullable=False))

    seller: Optional["Seller"] = Relationship(back_populates="user")
    buyer: Optional["Buyer"] = Relationship(back_populates="user")


class Seller(SQLModel, table=True):
    __tablename__ = "sellers"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    registration_number: str = Field(
        sa_column=Column(String(20), nullable=False, unique=True)
    )
    brand_name: str = Field(sa_column=Column(String(50), nullable=False, unique=True))
    contact_number: Optional[str] = Field(sa_column=Column(String(20), nullable=False))

    user: User = Relationship(back_populates="seller")
    products: List["Product"] = Relationship(back_populates="seller")


class Buyer(SQLModel, table=True):
    __tablename__ = "buyers"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    name: str = Field(sa_column=Column(String(50), nullable=False))
    phone_number: str = Field(sa_column=Column(String(20), nullable=False))
    address: str = Field(sa_column=Column(String(200), nullable=False))

    user: User = Relationship(back_populates="buyer")
