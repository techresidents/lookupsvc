import json
import logging

from trpycore import riak_gevent
from trpycore.riak_common.factory import RiakClientFactory
from trsvcscore.mongrel2.decorator import session_required
from trsvcscore.service_gevent.handler.service import GServiceHandler
from trsvcscore.service_gevent.handler.mongrel2 import GMongrel2Handler
from trsvcscore.session.riak import RiakSessionStorePool
from tridlcore.gen.ttypes import RequestContext
from trlookupsvc.gen import TLookupService
from trlookupsvc.gen.ttypes import LookupScope

import settings

from lookups.registry import LookupRegistry


class LookupServiceHandler(TLookupService.Iface, GServiceHandler):
    def __init__(self, service):
        super(LookupServiceHandler, self).__init__(
                service=service,
                zookeeper_hosts=settings.ZOOKEEPER_HOSTS,
                database_connection=settings.DATABASE_CONNECTION)
        
        self.log = logging.getLogger("%s.%s" % (__name__, LookupServiceHandler.__name__))

        self.lookups = self._create_lookups()

        self._load_lookups()
    
    def _create_lookups(self):
        lookups = {}
        for scope, registration in LookupRegistry.registry.items():
            try:
                lookups[scope] = registration.factory_method(self)
                self.log.info("%s created for scope %s." % (registration.name, scope))
            except Exception as error:
                self.log.error("unable to create %s for scope %s." % (registration.name, scope))
                self.log.exception(error)
        return lookups
    
    def _load_lookups(self):
        for scope, lookup in self.lookups.items():
            try:
                lookup.load()
                self.log.info("%s loaded." % lookup.name)
            except Exception as error:
                self.log.error("unable to load %s" % lookup.name)
                self.log.exception(error)


    def reinitialize(self, requestContext):
        self._load_lookups()

    def lookup(self, requestContext, scope, category, value, maxResults):
        if scope in self.lookups:
            result = self.lookups[scope].lookup(value, category, maxResults)
            return result
        else:
            return []


class LookupMongrel2Handler(GMongrel2Handler):

    URL_HANDLERS = [
        (r'^/lookup/(?P<scope>\w+)$', 'handle_lookup'),
    ]

    def __init__(self, service_handler):
        super(LookupMongrel2Handler, self).__init__(
                url_handlers=self.URL_HANDLERS)

        self.service_handler = service_handler
        
        self.log = logging.getLogger("%s.%s" % (__name__, LookupMongrel2Handler.__name__))

        self.riak_client_factory = RiakClientFactory(
                host=settings.RIAK_HOST,
                port=settings.RIAK_PORT,
                transport_class=riak_gevent.RiakPbcTransport)

        self.session_store_pool = RiakSessionStorePool(
                self.riak_client_factory,
                settings.RIAK_SESSION_BUCKET,
                settings.RIAK_SESSION_POOL_SIZE)
        
    def _handle_message(self, request, session):
        session_data = session.get_data()
        user_id = session_data["_auth_user_id"]
        request_context = RequestContext(userId = user_id, sessionId = session.get_key())
        return request_context

    def handle_disconnect(self, request):
        pass

    @session_required
    def handle_lookup(self, request, session=None, scope=None):
        request_context = self._handle_message(request, session)
        query = request.param("query") or ""
        max_results = request.param("maxResults") or 8

        results = self.service_handler.lookup(
                request_context,
                LookupScope._NAMES_TO_VALUES[scope.upper()],
                "",
                query,
                int(max_results))

        json_result = {
                "query": query,
                "matches": [],
        }

        for result in results:
            d = {}
            d.update(result.data)
            d.update({ "id": result.id, "value": result.value })
            json_result["matches"].append(d)
        
        response = self.JsonResponse(data=json.dumps(json_result))
        return response
