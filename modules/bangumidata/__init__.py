from modules.schema import QUARTER,WEEKDAY
from core.log import LOG_INFO, LOG_ERROR

DIRECTORY: str = "data"
FILENAME: str = "bangumidata.json"
URL: str = "https://unpkg.com/bangumi-data@0.3/dist/data.json"
      
def get_next_quarter(current_quarter: QUARTER) -> QUARTER:
    quarters = list(QUARTER)
    current_index = quarters.index(current_quarter)
    next_index = (current_index + 1) % len(quarters)
    return quarters[next_index]