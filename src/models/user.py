from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Seller(SQLModel, table=True):
    __tablename__ = "sellers"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(nullable=False, max_length=100, unique=True)
    password: str = Field(nullable=False, max_length=256)
    registration_number: str = Field(nullable=False, max_length=20, unique=True)
    corporate_name: str = Field(nullable=False, max_length=20, unique=True)
    contact_information: Optional[str] = Field(default=None, max_length=50)

    products: List["Product"] = Relationship(back_populates="seller")
