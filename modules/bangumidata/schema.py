from typing import List, Dict, Union
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
class OnairSite:
    site: str
    id: str
    begin: str
    regions: List[str]
    url: str = None
    broadcast: str = None
    end: str = None
    comment: str = None


@dataclass
class InfoSite:
    site: str
    id: str


@dataclass
class ResourceSite:
    site: str
    id: str


Site = Union[OnairSite, InfoSite, ResourceSite]


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


SiteList = str


@dataclass
class Data:
    siteMeta: Dict[SiteList, SiteMeta]
    items: List[Item]
