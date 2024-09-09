import requests, json, os  # type: ignore
from typing import Optional
from utils.date import yyyymmdd_to_iso
from modules.bangumidata import *
from fuzzywuzzy import fuzz
from core.database import Database as Database
from modules.schema.bangumidata import *
from concurrent.futures import ProcessPoolExecutor, as_completed


class BangumiData:

    @staticmethod
    def get():
        """从 URL 下载 JSON 数据并保存到指定目录下的 JSON 文件中"""
        try:

            response = requests.get(URL)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            LOG_ERROR(f"BangumiData", e)

    @staticmethod
    def getAnimeReleasedAfterGivenDate(date: str) -> List[Item]:
        """
        返回开播时间晚于date的条目，date格式yyyymmdd
        """
        try:
            begin_after = yyyymmdd_to_iso(date)
            query = "SELECT * FROM items WHERE begin > ?"
            rows = Database._query_items(query, (begin_after,))

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
            LOG_ERROR(f"getAnimeByAirDate", e)

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
            rows = Database._query_items(query, (begin_after, end_before))
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
            rows = Database._query_items(query, ())
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
                            comment=row[8]
                        )
                        items.append(item)

            return items
        except Exception as e:
            LOG_ERROR(f"getAnimeByTitle", e)


def match_title(title: str, row: tuple) -> bool:
    """
    模糊匹配
    """
    item_id = row[0]
    title_translate = Database._get_title_translate(item_id)
    return any(fuzz.partial_ratio(title.lower(), t.lower()) > 80 for t in [title for titles in title_translate.values() for title in titles])