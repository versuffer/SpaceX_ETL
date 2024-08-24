from fastapi import APIRouter

from app.api.v1.data_mart.data_mart_router import data_mart_router

v1_router = APIRouter()
v1_router.include_router(data_mart_router)
