from fastapi import APIRouter
from .router import bangumidata
api_router = APIRouter()

api_router.include_router(bangumidata.router, prefix="/bangumiData", tags=["bangumiData"])