from trpycore.datastruct.trie import Trie
from trlookupsvc.gen.ttypes import LookupScope, LookupResult

from registry import LookupRegistry
from lookups.base import Lookup

class TagLookup(Lookup):

    @staticmethod
    def create():
        return TagLookup()
    
    def __init__(self):
        super(TagLookup, self).__init__(TagLookup.__name__, LookupScope.TAG)
        self.trie = Trie()

    def load(self):
        for value in ["a", "abc", "at", "are", "attic", "and", "bat", "batter"]:
            self.trie.insert(value, {"id": value})

    def lookup(self, value, category=None):
        result = []
        for value, data in self.trie.find(value):
            lookup_result = LookupResult(id=0, value=value, data=data)
            result.append(lookup_result)
        return result

LookupRegistry.register(TagLookup.__name__, LookupScope.TAG, TagLookup.create)
