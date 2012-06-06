import logging

class LookupRegistration(object):
    def __init__(self, name, scope, factory_method):
        self.name = name
        self.scope = scope
        self.factory_method = factory_method

class LookupRegistry(object):
    registry = {}
    
    @classmethod 
    def register(cls, name, scope, factory_method):
        if scope not in LookupRegistry.registry:
            logging.info("Registering %s." % name) 
            registration = LookupRegistration(name, scope, factory_method)
            cls.registry[scope] = registration
        else:
            logging.error("Unable to register %s - lookup already registered for scope %s." % (name, scope))
