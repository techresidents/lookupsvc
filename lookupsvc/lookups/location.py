from trpycore.datastruct.trie import Trie
from trlookupsvc.gen.ttypes import LookupScope, LookupResult

from registry import LookupRegistry
from lookups.base import Lookup

LOCATIONS = [
    {"id": 1, "country": "USA", "state": "RI", "city": "Cranston", "zip": "02921", "county": "Providence"},
    {"id": 2, "country": "USA", "state": "MA", "city": "Newton", "zip": "02465", "county": "Middlesex"},
    {"id": 3, "country": "USA", "state": "MA", "city": "Belmont", "zip": "02478", "county": "Middlesex"},
    {"id": 4, "country": "USA", "state": "MA", "city": "Boston", "zip": "02478", "county": "Suffolk"},
    {"id": 5, "country": "USA", "state": "VT", "city": "Williston", "zip": "05495", "county": "Chittenden"},
]


class LocationLookup(Lookup):
    
    @staticmethod
    def create():
        return LocationLookup()
    
    def __init__(self):
        super(LocationLookup, self).__init__(
                LocationLookup.__name__,
                LookupScope.LOCATION)
        self.trie = Trie()

    def load(self):
        for location in LOCATIONS:
            location["name"] = "%s, %s %s" % (location["city"], location["state"], location["zip"])
            self.trie.insert(location["city"].lower(), location)
            self.trie.insert(location["zip"].lower(), location)
            self.trie.insert(location["state"].lower(), location)

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
