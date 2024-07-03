from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api import router
from src.config import limiter, settings

app = FastAPI(
    title=settings.title,
    version=settings.version,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.include_router(router)
