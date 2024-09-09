from datetime import datetime
from core.log import LOG_INFO, LOG_ERROR
from modules.schema import WEEKDAY

def yyyymmdd_to_iso(yyyymmdd: str) -> str:
    """
    将 yyyymmdd 格式的日期转换为 ISO 8601 格式的日期字符串。

    :param yyyymmdd: 日期字符串，格式为 yyyymmdd
    :return: ISO 8601 格式的日期字符串
    """
    try:
        date = datetime.strptime(yyyymmdd, "%Y%m%d")
        return date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except Exception as e:
        LOG_ERROR(f"yyyymmdd_to_iso", e)


def get_weekday_by_iso_date(iso_date: str) -> str:
    """
    输入：iso格式（"%Y-%m-%dT%H:%M:%S.000Z"）
    """

    date_part = iso_date.split("T")[0]

    year, month, day = map(int, date_part.split("-"))

    if month == 1 or month == 2:
        month += 12
        year -= 1

    K = year % 100
    J = year // 100

    h = (day + (13 * (month + 1)) // 5 + K + K // 4 + J // 4 + 5 * J) % 7

    return WEEKDAY(h).value


def get_weekday_by_yyyymmdd(yyyymmdd: str) -> str:
    """
    :param yyyymmdd: 日期字符串，格式为 yyyymmdd
    :return: weekday
    """
    try:
        return get_weekday_by_iso_date(yyyymmdd_to_iso(yyyymmdd))
    except Exception as e:
        LOG_ERROR(f"get_weekday_by_yyyymmdd", e)
