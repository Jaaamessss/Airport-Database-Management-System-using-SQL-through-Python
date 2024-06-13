import sqlite3
from p2app.events.regions import (Region, StartRegionSearchEvent, RegionSearchResultEvent,
                                  LoadRegionEvent, RegionLoadedEvent,
                                  SaveNewRegionEvent, RegionSavedEvent, SaveRegionEvent, SaveRegionFailedEvent)
from p2app.events.app import ErrorEvent

class RegionEventHandler:
    def __init__(self, connection):
        self.connection = connection

    def handle_event(self, event):
        if isinstance(event, StartRegionSearchEvent):
            return self.search_region(event)
        elif isinstance(event, LoadRegionEvent):
            return self.load_region(event)
        elif isinstance(event, SaveNewRegionEvent):
            return self.save_new_region(event)
        elif isinstance(event, SaveRegionEvent):
            return self.update_region(event)

    def search_region(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        search_results = []
        base_query = "SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region"
        params = []
        conditions = []

        if event.name():
            conditions.append("name = ?")
            params.append(event.name())
        if event.region_code():
            conditions.append("region_code = ?")
            params.append(event.region_code())
        if event.local_code():
            conditions.append("local_code = ?")
            params.append(event.local_code())

        if conditions:
            query = f"{base_query} WHERE {' AND '.join(conditions)}"
        else:
            return

        cursor.execute(query, params)
        for row in cursor.fetchall():
            region = Region(*row)
            search_results.append(RegionSearchResultEvent(region))

        return search_results
    def load_region(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        query = "SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE region_id = ?"
        region_id = event.region_id()
        try:
            cursor.execute(query, (region_id,))
            for row in cursor.fetchall():
                country = Region(*row)
                return RegionLoadedEvent(country)
        except Exception as e:
            return ErrorEvent(f'Unexpected Error{e}')

    def save_new_region(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        query = "INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        region = event.region()
        try:
            cursor.execute(query, (region.region_id, region.region_code, region.local_code, region.name,
                                   region.continent_id, region.country_id, region.wikipedia_link, region.keywords))
            conn.commit()
            return RegionSavedEvent(region)
        except sqlite3.Error as e:
            return SaveRegionFailedEvent(f"{str(e)}\n "
                                         f"Please check Region Code, Continent ID and Country ID")

    def update_region(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        region_code = event.region().region_code
        local_code = event.region().local_code
        region_name = event.region().name
        region_id = event.region().region_id
        continent_id = event.region().continent_id
        country_id = event.region().country_id
        wikipedia_link = event.region().wikipedia_link
        keywords = event.region().keywords
        try:
            query = "UPDATE region SET region_code = ?, local_code = ?, name = ?, continent_id = ?, country_id = ?, wikipedia_link = ?, keywords = ? WHERE region_id = ?"
            cursor.execute(query, (region_code, local_code, region_name, continent_id, country_id, wikipedia_link, keywords, region_id,))
            conn.commit()
            return RegionSavedEvent(event.region())
        except sqlite3.Error as e:
            return SaveRegionFailedEvent(f"{e}\n "
                                         f"Please check Region Code, Continent ID and Country ID")


