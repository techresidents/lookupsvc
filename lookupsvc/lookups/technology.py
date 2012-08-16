from trpycore.datastruct.trie import Trie
from trsvcscore.db.models import Technology
from trlookupsvc.gen.ttypes import LookupScope, LookupResult

from lookups.registry import LookupRegistry
from lookups.base import Lookup

class TechnologyLookup(Lookup):
    
    @staticmethod
    def create(handler):
        return TechnologyLookup(handler)
    
    def __init__(self, handler):
        super(TechnologyLookup, self).__init__(
                handler,
                TechnologyLookup.__name__,
                LookupScope.TECHNOLOGY)
        self.trie = Trie()

    def load(self):
        try:
            trie = Trie()
            session = self.handler.get_database_session()
            for technology in session.query(Technology):
                technology_json = {
                    "id": str(technology.id),
                    "name": technology.name or '',
                    "description": technology.description or '',
                    "type_id": str(technology.type_id)
                }
                trie.insert(technology.name.lower(), technology_json)
            self.trie = trie
        finally:
            if session:
                session.close()

    def lookup(self, value, category=None, max_results=None):
        result = []
        for value, data in self.trie.find(value.lower(), max_results):
            lookup_result = LookupResult(
                    id=int(data["id"]),
                    value=value,
                    data=data)
            result.append(lookup_result)
        return result

LookupRegistry.register(TechnologyLookup.__name__, LookupScope.TECHNOLOGY, TechnologyLookup.create)
