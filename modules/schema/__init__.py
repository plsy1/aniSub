from enum import Enum,IntEnum

class QUARTER(Enum):
    WINTER = '01'
    SPRING = '04'
    SUMMER = '07'
    AUTUMN = '10'
    
class WEEKDAY(IntEnum):
    SATURDAY = 0
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6