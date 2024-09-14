import requests, json, os  # type: ignore
from typing import Optional
from utils.date import yyyymmdd_to_iso
from modules.bangumidata import *
from fuzzywuzzy import fuzz
from core.database import Database as Database
from modules.schema.bangumidata import *
from concurrent.futures import ProcessPoolExecutor, as_completed
from fastapi.responses import FileResponse
import httpx
from config import conf
from utils.date import get_nearest_past_date, get_next_season

bangumi_config = conf.get_bangumi_config()


def match_title(title: str, row: tuple) -> bool:
    """
    模糊匹配
    """
    item_id = row[0]
    title_translate = Database._get_title_translate(item_id)
    return any(
        fuzz.partial_ratio(title.lower(), t.lower()) > 80
        for t in [title for titles in title_translate.values() for title in titles]
    )


class BangumiData:

    @staticmethod
    def getFromSource():
        """从 URL 下载 JSON 数据并保存到指定目录下的 JSON 文件中"""
        try:

            response = requests.get(URL)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            LOG_ERROR(f"BangumiData", e)

    @staticmethod
    def getThisSeason() -> List[Item]:
        """
        """
        try:
            date = get_nearest_past_date()
            begin_after = yyyymmdd_to_iso(date)
            query = "SELECT * FROM items WHERE begin > ?"
            rows = Database._query(query, (begin_after,))

            items = []
            for row in rows:
                item_id = row[0]
                title_translate = Database._get_title_translate(item_id)
                sites = Database._get_sites(item_id)

                item = Item(
                    title=row[1],
                    titleTranslate=title_translate,
                    type=row[2],
                    lang=row[3],
                    officialSite=row[4],
                    begin=row[5],
                    end=row[6],
                    sites=sites,
                    broadcast=row[7],
                    comment=row[8],
                )
                items.append(item)

            return items
        except Exception as e:
            LOG_ERROR(f"getThisSeason", e)

    @staticmethod
    def getAnimeByQuarterAndYear(year: str, quarter: QUARTER) -> List[Item]:
        """
        返回yyyy年第n季度的条目
        """
        try:
            begin_after = yyyymmdd_to_iso(f"{year}{quarter.value}01")
            next_quarter = get_next_quarter(quarter)
            year = str(int(year) + 1) if next_quarter == QUARTER.AUTUMN else year
            end_before = yyyymmdd_to_iso(f"{year}{next_quarter.value}01")

            query = """
            SELECT * FROM items WHERE (begin >= ? AND begin IS NOT NULL) AND (end < ? AND end IS NOT NULL)
            """
            rows = Database._query(query, (begin_after, end_before))
            items = []
            for row in rows:
                item_id = row[0]
                title_translate = Database._get_title_translate(item_id)
                sites = Database._get_sites(item_id)

                item = Item(
                    title=row[1],
                    titleTranslate=title_translate,
                    type=row[2],
                    lang=row[3],
                    officialSite=row[4],
                    begin=row[5],
                    end=row[6],
                    sites=sites,
                    broadcast=row[7],
                    comment=row[8],
                )
                items.append(item)

            return items

        except Exception as e:
            LOG_ERROR(f"getAnimeByQuarterAndYear", e)

    @staticmethod
    def getAnimeByTitle(title: str) -> List[Item]:
        """
        根据 title 匹配条目
        """
        try:
            items = []
            query = "SELECT * FROM items"
            rows = Database._query(query, ())
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(match_title, title, row) for row in rows]

                for future in as_completed(futures):
                    if future.result():
                        row = rows[futures.index(future)]
                        item_id = row[0]
                        title_translate = Database._get_title_translate(item_id)
                        sites = Database._get_sites(item_id)
                        item = Item(
                            title=row[1],
                            titleTranslate=title_translate,
                            type=row[2],
                            lang=row[3],
                            officialSite=row[4],
                            begin=row[5],
                            end=row[6],
                            sites=sites,
                            broadcast=row[7],
                            comment=row[8],
                        )
                        items.append(item)

            return items
        except Exception as e:
            LOG_ERROR(f"getAnimeByTitle", e)

    @staticmethod
    def getAnimeByAirDateAndWeekday(date: str, weekday: WEEKDAY):
        try:
            begin_after = yyyymmdd_to_iso(date)
            query = """
                    SELECT * FROM items 
                    WHERE weekday = ? AND begin > ?
                    """
            rows = Database._query(query, (str(weekday), begin_after))
            items = []
            for row in rows:
                item_id = row[0]
                title_translate = Database._get_title_translate(item_id)
                sites = Database._get_sites(item_id)

                item = Item(
                    title=row[1],
                    titleTranslate=title_translate,
                    type=row[2],
                    lang=row[3],
                    officialSite=row[4],
                    begin=row[5],
                    end=row[6],
                    sites=sites,
                    broadcast=row[7],
                    comment=row[8],
                )
                items.append(item)

            return items

        except Exception as e:
            LOG_ERROR(f"getAnimeByAirDateAndWeekday", e)

    @staticmethod
    async def getImageByBangumiID(subject_id: str) -> Optional[FileResponse]:
        img_directory = "data/img"
        file_path = None

        # 查找本地缓存的图片
        try:
            for filename in os.listdir(img_directory):
                if filename.startswith(f"{subject_id}."):
                    file_path = os.path.join(img_directory, filename)
                    if os.path.isfile(file_path):
                        img_url = f"/img/{filename}"
                        return True
        except FileNotFoundError:
            LOG_INFO("本地无对应封面缓存，尝试下载")
        except Exception as e:
            LOG_ERROR(f"Error while checking local cache: {e}")

        async with httpx.AsyncClient() as client:
            try:
                baseurl = "https://api.bgm.tv/"
                headers = {
                    "accept": "application/json",
                    "User-Agent": "plsy1/easybangumi (https://github.com/plsy1/easybangumi)",
                    "Authorization": f"Bearer {bangumi_config.get('token','')}",
                    'accept': 'application/json',
                }
                url = f"{baseurl}v0/subjects/{subject_id}"
                response = await client.get(url, headers=headers, timeout=30)

                if response.status_code == 200:
                    json_data = response.json()
                    img_url = (
                        json_data.get("images", {}).get("large")
                        or json_data.get("images", {}).get("medium")
                        or json_data.get("images", {}).get("small")
                    )
                    if img_url:
                        if not os.path.exists(img_directory):
                            os.makedirs(img_directory)

                        # Download image with streaming
                        async with client.stream("GET", img_url) as img_response:
                            if img_response.status_code == 200:
                                content_type = img_response.headers.get(
                                    "Content-Type", ""
                                )
                                file_extension = (
                                    content_type.split("/")[1]
                                    if "/" in content_type
                                    else "jpg"
                                )

                                file_name = f"{subject_id}.{file_extension}"
                                file_path = os.path.join(img_directory, file_name)

                                with open(file_path, "wb") as file:
                                    async for chunk in img_response.aiter_bytes(
                                        chunk_size=8192
                                    ):
                                        file.write(chunk)

                                LOG_INFO(f"Image saved as {file_name}")
                                return True
                            else:
                                LOG_ERROR("Failed to download image from URL")
                    else:
                        LOG_ERROR("No image URL found in the API response")
                else:
                    LOG_ERROR(
                        f"API request failed with status code {response.status_code}"
                    )
            except httpx.RequestError as e:
                LOG_ERROR(f"Error while downloading image: {e}")
            except Exception as e:
                LOG_ERROR(f"Unexpected error: {e}")

        return None
