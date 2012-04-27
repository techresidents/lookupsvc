import json
import logging
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, PROJECT_ROOT)

from trpycore import riak_gevent
from trpycore.riak_common.factory import RiakClientFactory
from trsvcscore.mongrel2.decorator import session_required
from trsvcscore.service_gevent.handler import GMongrel2Handler
from trsvcscore.session.riak import RiakSessionStorePool
from tridlcore.gen.ttypes import RequestContext
from trlookupsvc.gen import TLookupService

import version
import settings

from lookups.registry import LookupRegistry

URL_HANDLERS = [
    (r'^/lookup/(?P<scope>\w+)$', 'handle_lookup'),
]


class LookupServiceHandler(TLookupService.Iface, GMongrel2Handler):
    def __init__(self):
        super(LookupServiceHandler, self).__init__(
                url_handlers = URL_HANDLERS,
                name=settings.SERVICE,
                interface=settings.SERVER_INTERFACE,
                port=settings.SERVER_PORT,
                version=version.VERSION,
                build=version.BUILD,
                zookeeper_hosts=settings.ZOOKEEPER_HOSTS)
        
        self.log = logging.getLogger("%s.%s" % (__name__, LookupServiceHandler.__name__))

        self.riak_client_factory = RiakClientFactory(
                host=settings.RIAK_HOST,
                port=settings.RIAK_PORT,
                transport_class=riak_gevent.RiakPbcTransport)

        self.session_store_pool = RiakSessionStorePool(
                self.riak_client_factory,
                settings.RIAK_SESSION_BUCKET,
                settings.RIAK_SESSION_POOL_SIZE)
        
        self.lookups = self._create_lookups()

        self._load_lookups()
    
    def _create_lookups(self):
        lookups = {}
        for scope, registration in LookupRegistry.registry.items():
            try:
                lookups[scope] = registration.factory_method()
                self.log.info("%s created." % registration.name)
            except Exception as error:
                self.log.error("unable to create %s." % registration.name)
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
        results = self.lookup(request_context, 2, "", query)
        json_result = {
                "query": query,
                "matches": [],
        }
        for result in results:
            d = {"id": result.id,
                 "value": result.value,
                 "data": result.data
            }
            json_result["matches"].append(d)

        return json.dumps(json_result)

    def lookup(self, requestContext, scope, category, value):
        if scope in self.lookups:
            result = self.lookups[scope].lookup(value, category)
            return result
        else:
            return []

