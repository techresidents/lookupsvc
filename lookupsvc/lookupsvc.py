#!/usr/bin/env python

import logging
import logging.config
import os
import signal
import sys
import gevent

#Add PROJECT_ROOT to syspath for version import
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, PROJECT_ROOT)

import settings
import version

from trpycore.process.pid import pidfile, PidFileException
from trsvcscore.service_gevent.default import GDefaultService
from trsvcscore.service_gevent.server.default import GThriftServer
from trsvcscore.service_gevent.server.mongrel2 import GMongrel2Server
from trlookupsvc.gen import TLookupService

from handler import LookupServiceHandler, LookupMongrel2Handler


class LookupService(GDefaultService):
    def __init__(self):

        handler = LookupServiceHandler(self)
        server = GThriftServer(
                name="%s-thrift" % settings.SERVICE,
                interface=settings.THRIFT_SERVER_INTERFACE,
                port=settings.THRIFT_SERVER_PORT,
                handler=handler,
                processor=TLookupService.Processor(handler),
                address=settings.THRIFT_SERVER_ADDRESS)

        mongrel2_handler = LookupMongrel2Handler(handler)
        mongrel2_server = GMongrel2Server(
                name="%s-mongrel" % settings.SERVICE,
                mongrel2_sender_id=settings.MONGREL_SENDER_ID,
                mongrel2_pull_addr=settings.MONGREL_PULL_ADDR,
                mongrel2_pub_addr=settings.MONGREL_PUB_ADDR,
                handler=mongrel2_handler)

        super(LookupService, self).__init__(
                name=settings.SERVICE,
                version=version.VERSION,
                build=version.BUILD,
                servers=[server, mongrel2_server],
                hostname=settings.SERVICE_HOSTNAME,
                fqdn=settings.SERVICE_FQDN)
 
def main(argv):
    try:
        #Configure logger
        logging.config.dictConfig(settings.LOGGING)

        with pidfile(settings.SERVICE_PID_FILE, create_directory=True):

            
            #Create service
            service = LookupService()
            
            def sigterm_handler():
                service.stop()

            gevent.signal(signal.SIGTERM, sigterm_handler);

            service.start()
            service.join()
    
    except PidFileException as error:
        logging.error("Service is already running: %s" % str(error))

    except KeyboardInterrupt:
        service.stop()
        service.join()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
