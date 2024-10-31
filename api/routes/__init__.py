from fastapi import APIRouter
from .auth import router as auth_router
from .static import router as static_router
from .user import router as user_router
from .match import router as match_router
from .shop import  router as shop_router
from .tasks import router as tasks_router
from .rating import router as rating_router
from .referral import router as referral_router

router = APIRouter()

router.include_router(auth_router, prefix='/auth', tags=["Auth"])
router.include_router(static_router, prefix='/static', tags=["Static"])
router.include_router(user_router, prefix='/user', tags=["User"])
router.include_router(match_router, prefix='/match', tags=["Match"])
router.include_router(shop_router, prefix='/shop', tags=["Shop"])
router.include_router(tasks_router, prefix='/tasks', tags=["Tasks"])
router.include_router(rating_router, prefix='/rating', tags=["Rating"])
router.include_router(referral_router, prefix='/referral', tags=["Referral"])