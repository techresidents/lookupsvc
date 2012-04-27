from trlookupsvc.gen.ttypes import LookupScope

from registry import LookupRegistry
from lookups.base import Lookup

class LocationLookup(Lookup):
    
    @staticmethod
    def create():
        return LocationLookup()
    
    def __init__(self):
        super(LocationLookup, self).__init__(
                LocationLookup.__name__,
                LookupScope.LOCATION)

    def load(self):
        pass

    def lookup(self, value, category=None):
        return "Tag" 

LookupRegistry.register(LocationLookup.__name__, LookupScope.LOCATION, LocationLookup.create)
