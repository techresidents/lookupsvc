from trpycore.datastruct.trie import Trie
from trlookupsvc.gen.ttypes import LookupScope, LookupResult

from registry import LookupRegistry
from lookups.base import Lookup

TAGS = {
    "a":      {"id": 0},
    "abc":    {"id": 1},
    "attic":  {"id": 2},
    "at":     {"id": 3},
    "are":    {"id": 4},
    "and":    {"id": 5},
    "bat":    {"id": 6},
    "batter": {"id": 7},
}

class TagLookup(Lookup):

    @staticmethod
    def create():
        return TagLookup()
    
    def __init__(self):
        super(TagLookup, self).__init__(TagLookup.__name__, LookupScope.TAG)
        self.trie = Trie()

    def load(self):
        for key, value in TAGS.items():
            self.trie.insert(key.lower(), value)

    def lookup(self, value, category=None, max_results=None):
        result = []
        for value, data in self.trie.find(value.lower(), max_results):
            lookup_result = LookupResult(
                    id=data["id"],
                    value=value,
                    data=data) 

            result.append(lookup_result)
        return result

LookupRegistry.register(TagLookup.__name__, LookupScope.TAG, TagLookup.create)
