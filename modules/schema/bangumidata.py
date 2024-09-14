from typing import List, Dict, Union, Optional
from dataclasses import dataclass


SiteType = str
Language = str
ItemType = str


SITE_TYPE_INFO = "info"
SITE_TYPE_ONAIR = "onair"
SITE_TYPE_RESOURCE = "resource"


LANGUAGE_JA = "ja"
LANGUAGE_EN = "en"
LANGUAGE_ZH_HANS = "zh-Hans"
LANGUAGE_ZH_HANT = "zh-Hant"


ITEM_TYPE_TV = "tv"
ITEM_TYPE_WEB = "web"
ITEM_TYPE_MOVIE = "movie"
ITEM_TYPE_OVA = "ova"


@dataclass
class SiteMeta:
    title: str
    urlTemplate: str
    type: SiteType
    regions: List[str] = None


@dataclass
class Site:
    site: str
    id: Optional[str] = None
    begin: Optional[str] = None
    regions: Optional[List[str]] = None
    url: Optional[str] = None
    broadcast: Optional[str] = None
    end: Optional[str] = None
    comment: Optional[str] = None



@dataclass
class Item:
    title: str
    titleTranslate: Dict[Language, List[str]]
    type: ItemType
    lang: Language
    officialSite: str
    begin: str
    end: str
    sites: List[Site]
    broadcast: str = None
    comment: str = None





