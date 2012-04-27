import sys
import time

from trpycore.zookeeper.client import ZookeeperClient
from trsvcscore.proxy.zookeeper import ZookeeperServiceProxy
from tridlcore.gen.ttypes import RequestContext
from trlookupsvc.gen import TLookupService
from trlookupsvc.gen.ttypes import LookupScope

def main(argv):
    try:
        zookeeper_client = ZookeeperClient(["localdev:2181"])
        zookeeper_client.start()
        time.sleep(1)
        lookupsvc = ZookeeperServiceProxy(zookeeper_client, "lookupsvc", TLookupService)

        context = RequestContext(userId=0, impersonatingUserId=0, sessionId="sessionid", context="")
        print lookupsvc.getVersion(context)
        for result in lookupsvc.lookup(context, LookupScope.TAG, "", "b"):
            print result
            print result.value
    
    except Exception as error:
        print str(error)
    finally:
        zookeeper_client.stop()            
        zookeeper_client.join()
     
if __name__ == '__main__':
    sys.exit(main(sys.argv))
