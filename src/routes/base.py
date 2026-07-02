from fastapi import FastAPI ,APIRouter, Depends
import os

from helper.config import Settings, get_settings
base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"]
)

@base_router.get("/")
async def read_root(settings: Settings = Depends(get_settings)):
    return {
        "message": "Hello World",
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION
    }