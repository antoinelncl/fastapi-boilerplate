from fastapi import APIRouter

from src.api.auth.router import router as login_router
from src.api.users.router import router as user_router

router = APIRouter()

router.include_router(login_router)
router.include_router(user_router)
