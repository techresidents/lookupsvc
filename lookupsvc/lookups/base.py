import abc

class Lookup(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, handler, name, scope):
        self.handler = handler
        self.name = name
        self.scope = scope
    
    @abc.abstractmethod
    def load(self):
        return
    
    @abc.abstractmethod
    def lookup(self, value, category=None, max_results=None):
        return
