import logging
import unittest
import os
import sys

import gevent

SERVICE_NAME = "lookupsvc"

#Add PROJECT_ROOT to python path, for version import.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, PROJECT_ROOT)

#Add SERVICE_ROOT to python path, for imports.
SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../", SERVICE_NAME))
sys.path.insert(0, SERVICE_ROOT)

from tridlcore.gen.ttypes import RequestContext
from trpycore.zookeeper_gevent.client import GZookeeperClient
from trsvcscore.proxy.zoo import ZookeeperServiceProxy
from trsvcscore.service_gevent.default import GDefaultService
from trsvcscore.service_gevent.server.default import GThriftServer
from trlookupsvc.gen import TLookupService

from handler import LookupServiceHandler

class LookupService(GDefaultService):
    def __init__(self, hostname, port):
        self.handler = LookupServiceHandler(self)

        self.server = GThriftServer(
                name="%s-thrift" % SERVICE_NAME,
                interface="0.0.0.0",
                port=port,
                handler=self.handler,
                processor=TLookupService.Processor(self.handler),
                address=hostname)

        super(LookupService, self).__init__(
                name=SERVICE_NAME,
                version="unittest-version",
                build="unittest-build",
                servers=[self.server],
                hostname=hostname,
                fqdn=hostname)
 

class IntegrationTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #logging.basicConfig(level=logging.DEBUG)

        cls.service = LookupService("localhost", 9091)
        cls.service.start()
        gevent.sleep(1)

        cls.service_name = SERVICE_NAME
        cls.service_class = TLookupService

        cls.zookeeper_client = GZookeeperClient(["localdev:2181"])
        cls.zookeeper_client.start()
        gevent.sleep(1)

        cls.service_proxy = ZookeeperServiceProxy(cls.zookeeper_client, cls.service_name, cls.service_class, keepalive=True)
        cls.request_context = RequestContext(userId=0, impersonatingUserId=0, sessionId="dummy_session_id", context="")


    @classmethod
    def tearDownClass(cls):
        cls.zookeeper_client.stop()
        cls.zookeeper_client.join()
        cls.service.stop()
        cls.service.join()
