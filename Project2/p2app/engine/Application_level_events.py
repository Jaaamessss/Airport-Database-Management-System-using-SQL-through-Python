import sqlite3
from p2app.events.database import (OpenDatabaseEvent, CloseDatabaseEvent,
                                   DatabaseOpenedEvent, DatabaseClosedEvent, DatabaseOpenFailedEvent)

class DatabaseEventHandler:
    def __init__(self):
        self.connection = None

    def handle_event(self, event):
        if isinstance(event, OpenDatabaseEvent):
            return self.open_database(event)

    def open_database(self, event):
        try:
            self.connection = sqlite3.connect(event.path())
            self.connection.execute("PRAGMA foreign_keys = ON;")
            cursor = self.connection.cursor()
            query = "SELECT name FROM continent WHERE continent_id = 0"
            cursor.execute(query)
            return DatabaseOpenedEvent(event.path())
        except Exception as e:
            return DatabaseOpenFailedEvent(str(e))
