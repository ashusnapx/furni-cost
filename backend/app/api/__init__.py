"""API routers."""

from fastapi import APIRouter

from app.api import catalog, estimates, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(catalog.router)
api_router.include_router(estimates.router)
