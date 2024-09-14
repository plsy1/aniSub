from fastapi import APIRouter,HTTPException # type: ignore
from modules.bangumidata.bangumidata import BangumiData
from modules.schema import QUARTER,WEEKDAY
from core.log import LOG_ERROR
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
        
@router.get("/getThisSeason", summary="返回本季新番")
async def func():
    try:
        return BangumiData.getThisSeason()
    except Exception as e:
        LOG_ERROR(f"Api getThisSeason", e)
        raise HTTPException(status_code=500, detail="Server internal error")
    
    
@router.get("/getAnimeByTitle", summary="根据title模糊匹配条目")
async def func(title: str):
    try:
        return BangumiData.getAnimeByTitle(title)
    except Exception as e:
        LOG_ERROR(f"Api getAnimeByTitle", e)
        raise HTTPException(status_code=500, detail="Server internal error")
    
    
@router.get("/getAnimeByAirDate", summary="date之后开始播出的，星期*放送的剧集")
async def func(date:str, weekday: WEEKDAY):
    try:
        return BangumiData.getAnimeByAirDateAndWeekday(date, weekday)
    except Exception as e:
        LOG_ERROR(f"Api getAnimeByAirDate", e)
        raise HTTPException(status_code=500, detail="Server internal error")
    
    
    
@router.get("/getImageLinkByBangumiID", summary="根据bangumi.tv的subjectID，返回对应的图片URL")
async def func(subjectID:str):
    try:
         response = await BangumiData.getImageByBangumiID(subjectID)
         if response is not None:
            return {"status": "true"}
         return {"status": "false"}
    except Exception as e:
        LOG_ERROR(f"Api getImageLinkByBangumiID", e)
        raise HTTPException(status_code=500, detail="Server internal error")
    