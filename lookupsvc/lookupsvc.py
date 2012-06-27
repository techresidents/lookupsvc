#!/usr/bin/env python

import logging
import logging.config
import signal
import sys
import gevent

import settings

from trpycore.process.pid import pidfile, PidFileException
from trsvcscore.service_gevent.base import GMongrel2Service
from trlookupsvc.gen import TLookupService

from handler import LookupServiceHandler


class LookupService(GMongrel2Service):
    def __init__(self):

        handler = LookupServiceHandler()

        super(LookupService, self).__init__(
                name=settings.SERVICE,
                interface=settings.SERVER_INTERFACE,
                port=settings.SERVER_PORT,
                handler=handler,
                processor=TLookupService.Processor(handler),
                mongrel2_sender_id=settings.MONGREL_SENDER_ID,
                mongrel2_pull_addr=settings.MONGREL_PULL_ADDR,
                mongrel2_pub_addr=settings.MONGREL_PUB_ADDR)
 
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
