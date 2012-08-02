import unittest
import logging
import time
 
from trpycore.zookeeper.client import ZookeeperClient
from trsvcscore.proxy.zookeeper import ZookeeperServiceProxy

from tridlcore.gen.ttypes import RequestContext

from trlookupsvc.gen import TLookupService
from trlookupsvc.gen.ttypes import LookupScope, LookupResult

class BasicTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service_name = "lookupsvc"
        cls.service_class = TLookupService

        cls.zookeeper_client = ZookeeperClient(["localdev:2181"])
        cls.zookeeper_client.start()
        time.sleep(1)

        cls.service = ZookeeperServiceProxy(cls.zookeeper_client, cls.service_name, cls.service_class, keepalive=True)
        cls.request_context = RequestContext(userId=0, impersonatingUserId=0, sessionId="dummy_session_id", context="")

        logging.basicConfig(level=logging.DEBUG)

    @classmethod
    def tearDownClass(cls):
        cls.zookeeper_client.stop()
        cls.zookeeper_client.join()

    def test_getName(self):
        result = self.service.getName(self.request_context)
        self.assertEqual(result, self.service_name)
    
    def test_getVersion(self):
        result = self.service.getVersion(self.request_context)
        self.assertIsInstance(result, basestring)

    def test_getBuildNumber(self):
        result = self.service.getBuildNumber(self.request_context)
        self.assertIsInstance(result, basestring)
    
    def test_getStatus(self):
        result = self.service.getStatus(self.request_context)
        self.assertIsInstance(result, int)

    def test_getCounter(self):
        result = self.service.getCounter(self.request_context, "open_requests")
        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)

    def test_getCounters(self):
        result = self.service.getCounters(self.request_context)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["open_requests"], 1)

    def test_getOptions(self):
        result = self.service.getOptions(self.request_context)
        self.assertIsInstance(result, dict)

    def test_lookup_location(self):
        results = self.service.lookup(
                requestContext=self.request_context,
                scope=LookupScope.LOCATION,
                category="",
                value="boston",
                maxResults=10)

        for result in results:
            self.assertIsInstance(result, LookupResult)

    def test_lookup_tag(self):
        results = self.service.lookup(
                requestContext=self.request_context,
                scope=LookupScope.TAG,
                category="",
                value="aes",
                maxResults=10)

        for result in results:
            self.assertIsInstance(result, LookupResult)

    def test_lookup_technology(self):
        results = self.service.lookup(
                requestContext=self.request_context,
                scope=LookupScope.TECHNOLOGY,
                category="",
                value="django",
                maxResults=10)

        for result in results:
            self.assertIsInstance(result, LookupResult)

if __name__ == '__main__':
    unittest.main()
