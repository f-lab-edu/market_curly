import datetime

from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(max_length=500)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
