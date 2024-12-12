from fastapi import APIRouter

from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.categories import router as categories_router
from api.v1.endpoints.cooking_methods import router as cooking_methods_router
from api.v1.endpoints.cooking_settings import router as cooking_settings_router
from api.v1.endpoints.cooking_tools import router as cooking_tools_router
from api.v1.endpoints.feedback import router as feedback_router
from api.v1.endpoints.heating_methods import router as heating_methods_router
from api.v1.endpoints.ingredients import router as ingredients_router
from api.v1.endpoints.timers import router as timers_router
from api.v1.endpoints.users import router as users_router
from core.config import settings

api_router = APIRouter(prefix=settings.API_V1_STR)

api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_router.include_router(cooking_methods_router, prefix="/cooking-methods", tags=["cooking-methods"])
api_router.include_router(cooking_tools_router, prefix="/cooking-tools", tags=["cooking-tools"])
api_router.include_router(ingredients_router, prefix="/ingredients", tags=["ingredients"])
api_router.include_router(feedback_router, prefix="/feedback", tags=["feedback"])
api_router.include_router(heating_methods_router, prefix="/heating-methods", tags=["heating-methods"])
api_router.include_router(timers_router, prefix="/timers", tags=["timers"])
api_router.include_router(cooking_settings_router, prefix="/cooking-settings", tags=["cooking-settings"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
