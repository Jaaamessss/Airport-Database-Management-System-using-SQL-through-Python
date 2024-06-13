# p2app/engine/main.py
#
# ICS 33 Winter 2024
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.
import sqlite3

from p2app.events.database import (OpenDatabaseEvent, CloseDatabaseEvent,
                                   DatabaseOpenedEvent, DatabaseClosedEvent, DatabaseOpenFailedEvent)
from p2app.engine.Application_level_events import DatabaseEventHandler
from p2app.events.app import ErrorEvent, EndApplicationEvent, QuitInitiatedEvent
from p2app.events.continents import (Continent, StartContinentSearchEvent, ContinentSearchResultEvent,
                                     LoadContinentEvent, ContinentLoadedEvent,
                                     SaveNewContinentEvent, ContinentSavedEvent, SaveContinentFailedEvent, SaveContinentEvent)
from p2app.engine.Continent_related_events import ContinentEventHandler
from p2app.views.countries import (StartCountrySearchEvent, CountrySearchResultEvent,
                                   LoadCountryEvent, CountryLoadedEvent,
                                   SaveNewCountryEvent, CountrySavedEvent, SaveCountryFailedEvent,
                                   SaveCountryEvent, CountrySavedEvent)
from p2app.engine.Country_related_events import CountryEventHandler
from p2app.events.regions import (StartRegionSearchEvent, RegionSearchResultEvent,
                                  LoadRegionEvent, RegionLoadedEvent,
                                  SaveNewRegionEvent, RegionSavedEvent, SaveRegionEvent, SaveRegionFailedEvent)
from p2app.engine.Region_related_events import RegionEventHandler

class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self.connection = None
        self.db_event_handler = DatabaseEventHandler()
        self.continent_event_handler = None
        self.country_event_handler = None
        self.region_event_handler = None


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""
        if isinstance(event, OpenDatabaseEvent):
            yield self.db_event_handler.handle_event(event)
            self.connection = sqlite3.connect(event.path())
            self.connection.execute("PRAGMA foreign_keys = ON;")
        elif isinstance(event, CloseDatabaseEvent):
            yield DatabaseClosedEvent()
        elif isinstance(event, QuitInitiatedEvent):
            yield EndApplicationEvent()

        if isinstance(event, StartContinentSearchEvent):
            self.continent_event_handler = ContinentEventHandler(self.connection)
            yield from self.continent_event_handler.handle_event(event)

        if isinstance(event,
                      (LoadContinentEvent, SaveNewContinentEvent, SaveContinentEvent)):
            self.continent_event_handler = ContinentEventHandler(self.connection)
            yield self.continent_event_handler.handle_event(event)

        if isinstance(event, StartCountrySearchEvent):
            self.country_event_handler = CountryEventHandler(self.connection)
            yield from self.country_event_handler.handle_event(event)

        if isinstance(event,
                      (LoadCountryEvent, SaveNewCountryEvent, SaveCountryEvent)):
            self.country_event_handler = CountryEventHandler(self.connection)
            yield self.country_event_handler.handle_event(event)

        if isinstance(event, StartRegionSearchEvent):
            self.region_event_handler = RegionEventHandler(self.connection)
            yield from self.region_event_handler.handle_event(event)

        if isinstance(event,
                      (LoadRegionEvent, SaveNewRegionEvent, SaveRegionEvent)):
            self.region_event_handler = RegionEventHandler(self.connection)
            yield self.region_event_handler.handle_event(event)


















