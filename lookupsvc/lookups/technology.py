from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from trpycore.datastruct.trie import Trie
from trlookupsvc.gen.ttypes import LookupScope, LookupResult

from registry import LookupRegistry
from lookups.base import Lookup

class Technology(Base):
    __tablename__ = "technology"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(1024))
    type_id = Column(Integer)

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
                    "id": technology.id,
                    "name": technology.name,
                    "description": technology.description,
                    "type_id": technology.type_id
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
                    id=data["id"],
                    value=value,
                    data=data)
            result.append(lookup_result)
        return result

LookupRegistry.register(TechnologyLookup.__name__, LookupScope.TECHNOLOGY, TechnologyLookup.create)
