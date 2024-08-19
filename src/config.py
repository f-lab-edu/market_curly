import os

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    url: str = Field(default=os.getenv("DATABASE_URL"), alias="DATABASE_URL")
    echo: bool = Field(default=os.getenv("DATABASE_ECHO"), alias="DATABASE_ECHO")


class CORSConfig(BaseSettings):
    origins: str = Field(default=os.getenv("CORS_ORIGINS"), alias="CORS_ORIGINS")
    credentials: bool = Field(
        default=os.getenv("CORS_CREDENTIALS"), alias="CORS_CREDENTIALS"
    )
    methods: str = Field(default=os.getenv("CORS_METHODS"), alias="CORS_METHODS")
    headers: str = Field(default=os.getenv("CORS_HEADERS"), alias="CORS_HEADERS")


class WebConfig(BaseSettings):
    host: str = Field(default=os.getenv("WEB_HOST"), alias="WEB_HOST")
    port: int = Field(default=os.getenv("WEB_PORT"), alias="WEB_PORT")


class RedisConfig(BaseSettings):
    host: str = Field(default=os.getenv("REDIS_HOST"), alias="REDIS_HOST")
    port: str = Field(default=os.getenv("REDIS_PORT"), alias="REDIS_PORT")
    db: str = Field(default=os.getenv("REDIS_DB"), alias="REDIS_DB")


db = DatabaseConfig()
cors = CORSConfig()
web = WebConfig()
redis = RedisConfig()
