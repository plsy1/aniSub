from modules.bangumidata.bangumidata import *



url = "https://unpkg.com/bangumi-data@0.3/dist/data.json"

directory: str = "data/cache"
filename: str = "bangumidata.json"
date='20240701'

items = BangumiData.getAnimeByQuarterAndYear('2024',QUARTER.WINTER)

for item in items:
    print(item.titleTranslate.get(LANGUAGE_ZH_HANS, item.title), item.begin)

