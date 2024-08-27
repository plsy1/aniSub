import requests, json, os # type: ignore
from typing import Optional
from modules.schema.bangumidata import *
from utils.date import yyyymmdd_to_iso
from modules.bangumidata import *
from fuzzywuzzy import fuzz

class BangumiData:

    @staticmethod
    def initData():
        """从 URL 下载 JSON 数据并保存到指定目录下的 JSON 文件中"""
        try:
            if not os.path.exists(DIRECTORY):
                os.makedirs(DIRECTORY)

            response = requests.get(URL)
            response.raise_for_status()

            data = response.json()

            filepath = os.path.join(DIRECTORY, FILENAME)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            LOG_ERROR(f"initData", e)

    @staticmethod
    def loadData() -> Data:
        """从文件中加载数据并返回 Data 实例"""
        try:
            filepath = os.path.join(DIRECTORY, FILENAME)
            with open(filepath, "r", encoding="utf-8") as f:
                data_dict = json.load(f)

            result = Data(
                siteMeta={
                    key: SiteMeta(**value)
                    for key, value in data_dict["siteMeta"].items()
                },
                items=[Item(**item) for item in data_dict["items"]],
            )

            return result

        except Exception as e:
            LOG_ERROR(f"loadData", e)

    def itemFilter(
        type: Optional[ItemType] = None,
        lang: Optional[Language] = None,
        begin_after: Optional[str] = None,
        end_before: Optional[str] = None,
    ) -> List[Item]:
        """
        根据指定的参数过滤 Item 列表。
        """
        try:

            data = BangumiData.loadData()

            filtered_items = data.items
            if type is not None:
                filtered_items = [
                    item for item in filtered_items if item.type and item.type == type
                ]

            if lang is not None:
                filtered_items = [
                    item for item in filtered_items if item.lang and item.lang == lang
                ]

            if begin_after is not None:
                filtered_items = [
                    item
                    for item in filtered_items
                    if item.begin and item.begin > begin_after
                ]

            if end_before is not None:
                filtered_items = [
                    item
                    for item in filtered_items
                    if item.end and item.end < end_before
                ]

            return filtered_items
        except Exception as e:
            LOG_ERROR(f"itemFilter", e)

    @staticmethod
    def getAnimeReleasedAfterGivenDate(date: str) -> List[Item]:
        """
        返回开播时间晚于date的条目，date格式yyyymmdd
        """
        try:
            begin_after = yyyymmdd_to_iso(date)
            return BangumiData.itemFilter(begin_after=begin_after)
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
            return BangumiData.itemFilter(
                begin_after=begin_after, end_before=end_before
            )
        except Exception as e:
            LOG_ERROR(f"getAnimeByQuarterAndYear", e)

    @staticmethod
    def getAnimeByTitle(title: str) -> Item:
        """
        根据title匹配条目
        """
        try:
            items = []
            for item in BangumiData.loadData().items:
                titles = [t for v in item.titleTranslate.values() for t in v]
                if any(fuzz.partial_ratio(title.lower(), t.lower()) > 80 for t in titles):
                    items.append(item)
            return items
        except Exception as e:
            LOG_ERROR(f"getAnimeByTitle", e)