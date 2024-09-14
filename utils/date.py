from datetime import datetime, timedelta
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


def get_nearest_past_date():
    dates_str = [101, 401, 701, 1001]
    today = datetime.today().date()
    today_mmdd = today.month * 100 + today.day

    past_dates = []
    for date_int in dates_str:
        month = date_int // 100
        day = date_int % 100
        mmdd = month * 100 + day

        if mmdd < today_mmdd:
            date = datetime(today.year, month, day).date()
            days_diff = (today - date).days
            past_dates.append((date_int, days_diff))
        elif mmdd == today_mmdd:

            past_dates.append((date_int, 0))

    nearest_past_date_int = min(past_dates, key=lambda x: x[1])[0]
    nearest_past_date = datetime(
        today.year, nearest_past_date_int // 100, nearest_past_date_int % 100
    ).strftime("%Y%m%d")

    return nearest_past_date


def get_next_season() -> str:
    input_date = get_nearest_past_date()
    dates_str = ["0101", "0401", "0701", "1001"]
    input_year = int(input_date[:4])
    input_mmdd = int(input_date[4:])
    dates_str = [int(date) for date in dates_str]
    future_dates = [date for date in dates_str if date > input_mmdd]
    if not future_dates:
        next_date = min(dates_str)
    else:
        next_date = min(future_dates)
    if input_mmdd == 1001:
        input_year += 1

    next_date_str = f"{input_year}{next_date:04d}"

    return next_date_str
