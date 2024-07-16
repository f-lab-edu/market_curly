from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    url: str = Field(default="sqlite+aiosqlite:///./db.sqlite3", alias="DATABASE_URL")
    echo: bool = Field(default=True, alias="DATABASE_ECHO")


class CORSConfig(BaseSettings):
    origins: str = Field(default="*", alias="CORS_ORIGINS")
    credentials: bool = Field(default=True, alias="CORS_CREDENTIALS")
    methods: str = Field(default="*", alias="CORS_METHODS")
    headers: str = Field(default="*", alias="CORS_HEADERS")


class WebConfig(BaseSettings):
    host: str = Field(default="0.0.0.0", alias="WEB_HOST")
    port: int = Field(default=8000, alias="WEB_PORT")


db = DatabaseConfig()
cors = CORSConfig()
web = WebConfig()
