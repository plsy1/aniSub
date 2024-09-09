from fastapi import APIRouter,HTTPException # type: ignore
from modules.bangumidata.bangumidata import *
import re
router = APIRouter()


@router.get("/getAnimeByQuarterAndYear", summary="返回yyyy年第n季度的条目", description="""
""")
async def func(year: str, quarter: QUARTER):
    try:
        if not re.fullmatch(r"\d{4}", year):
            raise HTTPException(status_code=400, detail="Invalid field: year")
        if quarter not in QUARTER:
            raise HTTPException(status_code=400, detail="Invalid field: quarter")
        return BangumiData.getAnimeByQuarterAndYear(year,quarter)
    except Exception as e:
        LOG_ERROR(f"Api getAnimeByQuarterAndYear", e)
        raise HTTPException(status_code=500, detail="Server internal error")
        
@router.get("/getAnimeReleasedAfterGivenDate", summary="返回开播时间晚于date的条目，date格式yyyymmdd")
async def func(date: str):
    if not re.fullmatch(r"\d{8}", date):
        raise HTTPException(status_code=400, detail="Invalid field: date")
    try:
        return BangumiData.getAnimeReleasedAfterGivenDate(date)
    except Exception as e:
        LOG_ERROR(f"Api getAnimeReleasedAfterGivenDate", e)
        raise HTTPException(status_code=500, detail="Server internal error")
    
    
@router.get("/getAnimeByTitle", summary="根据title模糊匹配条目")
async def func(title: str):
    try:
        return BangumiData.getAnimeByTitle(title)
    except Exception as e:
        LOG_ERROR(f"Api getAnimeByTitle", e)
        raise HTTPException(status_code=500, detail="Server internal error")