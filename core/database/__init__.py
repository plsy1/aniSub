import sqlite3, os
from modules.schema import *
from modules.schema.bangumidata import *
from utils.date import get_weekday_by_iso_date


def handle_empty_string(value):
    return None if value == "" else value


class Database:
    
    @staticmethod
    def init(data):
        Database.createDatabase()
        Database.updateDatabase(data)
        Database.calculateWeekday()

    @staticmethod
    def createDatabase():
        conn = sqlite3.connect("data/bangumidata.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                type TEXT,
                lang TEXT,
                officialSite TEXT,
                begin TEXT,
                end TEXT,
                broadcast TEXT,
                comment TEXT,
                weekday TEXT
                )
            """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS titleTranslate (
            item_id INTEGER,
            language TEXT,
            translation TEXT,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS sites (
            item_id INTEGER,
            site TEXT,
            id TEXT,
            begin TEXT,
            end TEXT,
            url TEXT,
            broadcast TEXT,
            comment TEXT,
            regions TEXT,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS siteMeta (
            siteList TEXT PRIMARY KEY,
            title TEXT,
            urlTemplate TEXT,
            type TEXT,
            regions TEXT
        )
        """
        )
        conn.commit()
        conn.close()

    @staticmethod
    def updateDatabase(data):
        conn = sqlite3.connect("data/bangumidata.db")
        cursor = conn.cursor()
        # 插入 SiteMeta 数据
        for site_list, meta in data.get("siteMeta", {}).items():
            cursor.execute(
                """
            INSERT OR REPLACE INTO siteMeta (siteList, title, urlTemplate, type, regions)
            VALUES (?, ?, ?, ?, ?)
            """,
                (
                    site_list,
                    handle_empty_string(meta.get("title", None)),
                    handle_empty_string(meta.get("urlTemplate", None)),
                    handle_empty_string(meta.get("type", None)),
                    ",".join(meta.get("regions", [])),
                ),
            )

        # 插入 Item 数据
        for item in data.get("items", []):
            cursor.execute(
                """
            INSERT INTO items (title, type, lang, officialSite, begin, end, broadcast, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    handle_empty_string(item.get("title", None)),
                    handle_empty_string(item.get("type", None)),
                    handle_empty_string(item.get("lang", None)),
                    handle_empty_string(item.get("officialSite", None)),
                    handle_empty_string(item.get("begin", None)),
                    handle_empty_string(item.get("end", None)),
                    handle_empty_string(item.get("broadcast", None)),
                    handle_empty_string(item.get("comment", None)),
                ),
            )
            item_id = cursor.lastrowid

            # 插入 titleTranslate 数据
            for lang, translations in item.get("titleTranslate", {}).items():
                for translation in translations:
                    cursor.execute(
                        """
                    INSERT INTO titleTranslate (item_id, language, translation)
                    VALUES (?, ?, ?)
                    """,
                        (item_id, lang, translation),
                    )

            # 插入 sites 数据
            for site in item.get("sites", []):
                cursor.execute(
                    """
                INSERT INTO sites (item_id, site, id, begin, end, url, broadcast, comment, regions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        item_id,
                        handle_empty_string(site.get("site", None)),
                        handle_empty_string(site.get("id", None)),
                        handle_empty_string(site.get("begin", None)),
                        handle_empty_string(site.get("end", None)),
                        handle_empty_string(site.get("url", None)),
                        handle_empty_string(site.get("broadcast", None)),
                        handle_empty_string(site.get("comment", None)),
                        ",".join(site.get("regions", [])),
                    ),
                )

        conn.commit()
        conn.close()

    @staticmethod
    def _query(query, params=()):
        """
        执行数据库查询并返回结果
        """
        conn = sqlite3.connect("data/bangumidata.db")
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    
    @staticmethod
    def _do(foo, params=()):
        """
        执行数据库操作
        """
        conn = sqlite3.connect("data/bangumidata.db")
        cursor = conn.cursor()
        cursor.execute(foo, params)
        conn.commit()
        conn.close()
    
 #
    @staticmethod
    def _get_title_translate(item_id: int) -> Dict[Language, List[str]]:
        query = "SELECT language, translation FROM titleTranslate WHERE item_id = ?"
        rows = Database._query(query, (item_id,))

        title_translate = {}
        for row in rows:
            lang, translation = row
            if lang not in title_translate:
                title_translate[lang] = []
            title_translate[lang].append(translation)

        return title_translate

    @staticmethod
    def _get_sites(item_id: int) -> List[Site]:
        query = "SELECT site, id, begin, end, url, broadcast, comment, regions FROM sites WHERE item_id = ?"
        rows = Database._query(query, (item_id,))

        sites = []
        for row in rows:
            site = Site(
                site=row[0],
                id=row[1],
                begin=row[2],
                end=row[3],
                url=row[4],
                broadcast=row[5],
                comment=row[6],
                regions=row[7].split(","),
            )

            sites.append(site)

        return sites

    @staticmethod
    def calculateWeekday():
        query = "SELECT begin FROM items WHERE weekday IS NULL"
        begins = Database._query(query, ())
        for begin in begins:
            weekday = str(get_weekday_by_iso_date(begin[0]))
            update = "UPDATE items SET weekday = ? WHERE begin = ?"
            Database._do(update,(weekday,begin[0]))