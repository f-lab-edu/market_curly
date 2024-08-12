from typing import List, Optional

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel


class Seller(SQLModel, table=True):
    __tablename__ = "sellers"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(sa_column=Column(String(255), nullable=False, unique=True))
    password: str = Field(sa_column=Column(String(255), nullable=False))
    registration_number: str = Field(
        sa_column=Column(String(20), nullable=False, unique=True)
    )
    corporate_name: str = Field(
        sa_column=Column(String(50), nullable=False, unique=True)
    )
    contact_information: Optional[str] = Field(
        sa_column=Column(String(20), nullable=False)
    )

    products: List["Product"] = Relationship(back_populates="seller")


class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(sa_column=Column(String(255), nullable=False, unique=True))
    password: str = Field(sa_column=Column(String(255), nullable=False))
    name: str = Field(sa_column=Column(String(50), nullable=False))
    phone_number: str = Field(sa_column=Column(String(20), nullable=False))
    address: str = Field(sa_column=Column(String(200), nullable=False))
