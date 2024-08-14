from enum import Enum
from core.log import LOG_INFO, LOG_ERROR

DIRECTORY: str = "data/cache"
FILENAME: str = "bangumidata.json"
URL: str = "https://unpkg.com/bangumi-data@0.3/dist/data.json"



class QUARTER(Enum):
    WINTER = '01'
    SPRING = '04'
    SUMMER = '07'
    AUTUMN = '10'
    
      
def get_next_quarter(current_quarter: QUARTER) -> QUARTER:
    quarters = list(QUARTER)
    current_index = quarters.index(current_quarter)
    next_index = (current_index + 1) % len(quarters)
    return quarters[next_index]