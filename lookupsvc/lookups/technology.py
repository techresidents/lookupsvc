from trpycore.datastruct.trie import Trie
from trlookupsvc.gen.ttypes import LookupScope, LookupResult

from registry import LookupRegistry
from lookups.base import Lookup

TECHNOLOGIES = [
    {"id": 1, "name": "Django", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus felis erat, laoreet sed aliquam ut, dictum ut elit. Proin posuere dapibus neque aliquam gravida.", "type_id": 1 },
    {"id": 2, "name": "Ruby on Rails", "description": "description", "type_id": 1 },
    {"id": 12, "name": "C", "description": "description", "type_id": 2 },
    {"id": 13, "name": "C++", "description": "", "type_id": 2 },
    {"id": 14, "name": "C#", "description": "description", "type_id": 2 },
    {"id": 42, "name": "Python", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus felis erat, laoreet sed aliquam ut, dictum ut elit. Proin posuere dapibus neque aliquam gravida. Ut risus nunc, suscipit at sollicitudin vel, fermentum at sem. Sed augue enim, pretium in posuere at, mattis eu leo. Duis purus est, porttitor quis mollis a, hendrerit in tellus. Nullam porta fringilla tellus, eu pulvinar mi tristique a. Etiam pharetra adipiscing accumsan.", "type_id": 2 },
    {"id": 29, "name": "Java", "description": "description", "type_id": 2 },
    {"id": 30, "name": "Javascript", "description": "", "type_id": 2 },
    {"id": 47, "name": "Scala", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type_id": 2 },
]


class TechnologyLookup(Lookup):
    
    @staticmethod
    def create():
        return TechnologyLookup()
    
    def __init__(self):
        super(TechnologyLookup, self).__init__(
                TechnologyLookup.__name__,
                LookupScope.TECHNOLOGY)
        self.trie = Trie()

    def load(self):
        for technology in TECHNOLOGIES:
            self.trie.insert(technology["name"].lower(), technology)

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
