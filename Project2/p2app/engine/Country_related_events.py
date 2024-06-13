import sqlite3
from p2app.events.countries import (Country, StartCountrySearchEvent, CountrySearchResultEvent,
                                   LoadCountryEvent, CountryLoadedEvent,
                                   SaveNewCountryEvent, SaveCountryFailedEvent,
                                   SaveCountryEvent, CountrySavedEvent)
from p2app.events.app import ErrorEvent

class CountryEventHandler:
    def __init__(self, connection):
        self.connection = connection

    def handle_event(self, event):
        if isinstance(event, StartCountrySearchEvent):
            return self.search_country(event)
        elif isinstance(event, LoadCountryEvent):
            return self.load_country(event)
        elif isinstance(event, SaveNewCountryEvent):
            return self.save_new_country(event)
        elif isinstance(event, SaveCountryEvent):
            return self.update_country(event)

    def search_country(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        search_results = []
        base_query = "SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country"
        params = []
        conditions = []

        if event.name():
            conditions.append("name = ?")
            params.append(event.name())
        if event.country_code():
            conditions.append("country_code = ?")
            params.append(event.country_code())

        if conditions:
            query = f"{base_query} WHERE {' AND '.join(conditions)}"
        else:
            return

        cursor.execute(query, params)
        for row in cursor.fetchall():
            country = Country(*row)
            search_results.append(CountrySearchResultEvent(country))

        return search_results

    def load_country(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        query = "SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country WHERE country_id = ?"
        country_id = event.country_id()
        try:
            cursor.execute(query, (country_id,))
            for row in cursor.fetchall():
                country = Country(*row)
                return CountryLoadedEvent(country)
        except Exception as e:
            return ErrorEvent(f'Unexpected Error{e}')

    def save_new_country(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        query = "INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords) VALUES (?, ?, ?, ?, ?, ?)"
        country = event.country()
        wikipedia_link = country.wikipedia_link if country.wikipedia_link is not None else ""
        try:
            cursor.execute(query, (country.country_id, country.country_code, country.name,
                                   country.continent_id, wikipedia_link, country.keywords))
            conn.commit()
            return CountrySavedEvent(country)
        except sqlite3.Error as e:
            return SaveCountryFailedEvent(f"{str(e)}\n "
                                          f"Please check Country Code and Continent ID")

    def update_country(self, event):
        conn = self.connection
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        country_code = event.country().country_code
        country_name = event.country().name
        country_id = event.country().country_id
        continent_id = event.country().continent_id
        wikipedia_link = event.country().wikipedia_link if event.country().wikipedia_link is not None else ""
        keywords = event.country().keywords
        try:
            query = "UPDATE country SET country_code = ?, name = ?, continent_id = ?, wikipedia_link = ?, keywords = ? WHERE country_id = ?"
            cursor.execute(query, (country_code, country_name, continent_id, wikipedia_link, keywords, country_id,))
            conn.commit()
            return CountrySavedEvent(event.country())
        except sqlite3.Error as e:
            return SaveCountryFailedEvent(f"{e}\n "
                                          f"Please check Country Code and Continent ID")

