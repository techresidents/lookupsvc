from trpycore.datastruct.trie import Trie
from trsvcscore.models import Location
from trlookupsvc.gen.ttypes import LookupScope, LookupResult

from registry import LookupRegistry
from lookups.base import Lookup

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

            for location in session.query(Location).\
                filter(Location.state != None).\
                filter(Location.city == None):

                location_json = {
                    "id": location.id,
                    "city": location.city,
                    "country": location.country,
                    "state": location.state,
                    "zip": location.zip,
                    "county": location.county,
                    "name": "%s" % (location.state)
                }
                trie.insert(location.state.lower(), location_json)

            for location in session.query(Location).\
                filter(Location.city != None).\
                filter(Location.zip == None):
                location_json = {
                    "id": location.id,
                    "city": location.city,
                    "country": location.country,
                    "state": location.state,
                    "zip": location.zip,
                    "county": location.county,
                    "name": "%s, %s" % (location.city, location.state)
                }
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
