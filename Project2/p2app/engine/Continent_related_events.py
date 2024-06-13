import sqlite3
from p2app.events.continents import (Continent, StartContinentSearchEvent, ContinentSearchResultEvent,
                                     LoadContinentEvent, ContinentLoadedEvent,
                                     SaveNewContinentEvent, ContinentSavedEvent, SaveContinentFailedEvent, SaveContinentEvent)
from p2app.events.app import ErrorEvent

class ContinentEventHandler:
    def __init__(self, connection):
        self.connection = connection

    def handle_event(self, event):
        if isinstance(event, StartContinentSearchEvent):
            return self.search_continent(event)
        elif isinstance(event, LoadContinentEvent):
            return self.load_continent(event)
        elif isinstance(event, SaveNewContinentEvent):
            return self.save_new_continent(event)
        elif isinstance(event, SaveContinentEvent):
            return self.update_continent(event)

    def search_continent(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        search_results = []
        base_query = "SELECT continent_id, continent_code, name FROM continent"
        params = []
        conditions = []

        if event.name():
            conditions.append("name = ?")
            params.append(event.name())
        if event.continent_code():
            conditions.append("continent_code = ?")
            params.append(event.continent_code())

        if conditions:
            query = f"{base_query} WHERE {' AND '.join(conditions)}"
        else:
            return

        cursor.execute(query, params)

        for row in cursor.fetchall():
            continent = Continent(*row)
            search_results.append(ContinentSearchResultEvent(continent))

        return search_results

    def load_continent(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        query = "SELECT continent_id, continent_code, name FROM continent WHERE continent_id = ?"
        continent_id = event.continent_id()
        try:
            cursor.execute(query, (continent_id,))
            for row in cursor.fetchall():
                continent = Continent(*row)
                return ContinentLoadedEvent(continent)
        except Exception as e:
            return ErrorEvent(f'Unexpected Error{e}')

    def save_new_continent(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        query = "INSERT INTO continent (continent_id, continent_code, name) VALUES (?, ?, ?)"
        continent = event.continent()
        try:
            cursor.execute(query, (continent.continent_id, continent.continent_code, continent.name))
            conn.commit()
            return ContinentSavedEvent(continent)
        except sqlite3.Error as e:
            return SaveContinentFailedEvent(f"{str(e)}\n "
                                            f"Please check Continent Code")

    def update_continent(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        continent_code = event.continent().continent_code
        continent_name = event.continent().name
        continent_id = event.continent().continent_id
        try:
            query = "UPDATE continent SET continent_code = ?, name = ? WHERE continent_id = ?"
            cursor.execute(query, (continent_code, continent_name, continent_id,))
            conn.commit()
            return ContinentSavedEvent(event.continent())
        except sqlite3.Error as e:
            return SaveContinentFailedEvent(f"{e}\n "
                                            f"Please check Continent Code")
