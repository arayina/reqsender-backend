from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.proxies import router as proxies_router
from app.api.v1.urls import router as urls_router
from app.api.v1.request import router as request_router
from app.api.v1.url_settings import router as url_settings_router


router = APIRouter()

router.include_router(health_router)
router.include_router(proxies_router)
router.include_router(url_settings_router)
router.include_router(urls_router)
router.include_router(request_router)