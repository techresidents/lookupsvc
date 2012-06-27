from trpycore.datastruct.trie import MultiTrie
from trsvcscore.models import Tag
from trlookupsvc.gen.ttypes import LookupScope, LookupResult

from registry import LookupRegistry
from lookups.base import Lookup

class TagLookup(Lookup):

    @staticmethod
    def create(handler):
        return TagLookup(handler)
    
    def __init__(self, handler):
        super(TagLookup, self).__init__(
                handler,
                TagLookup.__name__,
                LookupScope.TAG)
        self.trie = MultiTrie()

    def load(self):
        try:
            trie = MultiTrie()
            session = self.handler.get_database_session()
            for tag in session.query(Tag):
                tag_json = {
                    "id": tag.id,
                    "conceptId": tag.concept_id,
                    "name": tag.name,
                }

                for word in tag.name.lower().split():
                    trie.insert(word, tag_json)

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

LookupRegistry.register(TagLookup.__name__, LookupScope.TAG, TagLookup.create)
