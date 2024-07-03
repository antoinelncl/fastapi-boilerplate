import os

from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address

load_dotenv()

t = os.environ.get("DATABASE_URL")


class GlobalConfig:
    def __init__(self):
        pass

    title: str = "fastapi-boilerplate"
    version: str = "0.1.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"


@property
def sync_db_url(self) -> str | None:
    return os.environ.get("DATABASE_URL")


settings = GlobalConfig()

limiter = Limiter(key_func=get_remote_address)
