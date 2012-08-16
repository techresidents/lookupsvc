from trpycore.datastruct.trie import MultiTrie
from trsvcscore.db.models import Tag
from trlookupsvc.gen.ttypes import LookupScope, LookupResult

from lookups.registry import LookupRegistry
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
                    "id": str(tag.id),
                    "conceptId": str(tag.concept_id),
                    "name": tag.name,
                }
                
                trie.insert(tag.name.lower(), tag_json)
                
                words = tag.name.lower().split()
                if len(words) > 1:
                    for word in words:
                        trie.insert(word, tag_json)

            self.trie = trie

        finally:
            if session:
                session.close()

    def lookup(self, value, category=None, max_results=None):
        result = []
        result_ids = {}
        for value, data in self.trie.find(value.lower(), max_results):
            tag_id = int(data["id"])
            lookup_result = LookupResult(
                    id=tag_id,
                    value=value,
                    data=data) 
            
            #prevent duplicates
            if tag_id not in result_ids:
                result.append(lookup_result)
                result_ids[tag_id] = True

        return result

LookupRegistry.register(TagLookup.__name__, LookupScope.TAG, TagLookup.create)
