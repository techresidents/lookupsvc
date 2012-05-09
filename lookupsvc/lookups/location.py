from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from trpycore.datastruct.trie import Trie
from trlookupsvc.gen.ttypes import LookupScope, LookupResult

from registry import LookupRegistry
from lookups.base import Lookup

class Location(Base):
    __tablename__ = "location"

    id = Column(Integer, primary_key=True)
    country = Column(String(100))
    state = Column(String(100))
    city = Column(String(100))
    zip = Column(String(25))
    county = Column(String(100))


class LocationLookup(Lookup):
    
    @staticmethod
    def create(handler):
        return LocationLookup(handler)
    
    def __init__(self, handler):
        super(LocationLookup, self).__init__(
                handler,
                LocationLookup.__name__,
                LookupScope.LOCATION)
        self.trie = Trie()

    def load(self):
        try:
            trie = Trie()
            session = self.handler.get_database_session()
            for location in session.query(Location):
                location_json = {
                    "id": location.id,
                    "city": location.city,
                    "country": location.country,
                    "state": location.state,
                    "zip": location.zip,
                    "county": location.county,
                    "name": "%s, %s %s" % (location.city, location.state, location.zip)
                }

                trie.insert(location.city.lower(), location_json)
                trie.insert(location.zip.lower(), location_json)
                trie.insert(location.state.lower(), location_json)
                trie.insert(location_json["name"].lower(), location_json)
            self.trie = trie
        finally:
            if session:
                session.close()

    def lookup(self, value, category=None, max_results=None):
        result = []
        for value, data in self.trie.find(value.lower(), max_results):
            lookup_result = LookupResult(
                    id=data["id"],
                    value=value,
                    data=data)
            result.append(lookup_result)
        return result

LookupRegistry.register(LocationLookup.__name__, LookupScope.LOCATION, LocationLookup.create)
