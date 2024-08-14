from datetime import datetime

def yyyymmdd_to_iso(yyyymmdd: str) -> str:
    """
    将 yyyymmdd 格式的日期转换为 ISO 8601 格式的日期字符串。
    
    :param yyyymmdd: 日期字符串，格式为 yyyymmdd
    :return: ISO 8601 格式的日期字符串
    """
    try:
        date = datetime.strptime(yyyymmdd, "%Y%m%d")
        return date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except ValueError:
        raise ValueError("日期格式错误，必须为 yyyymmdd 格式")