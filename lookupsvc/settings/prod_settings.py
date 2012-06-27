import hashlib
import socket

from default_settings import *

ENV = "prod"

#Service Settings
SERVICE_PID_FILE = "/opt/30and30/data/%s/pid/%s.%s.pid" % (SERVICE, SERVICE, ENV)

#Server settings
SERVER_HOST = socket.gethostname()
SERVER_INTERFACE = "0.0.0.0"
SERVER_PORT = 9091

#Database settings
DATABASE_HOST = "localhost"
DATABASE_NAME = "techresidents"
DATABASE_USERNAME = "techresidents"
DATABASE_PASSWORD = "t3chResident$"
DATABASE_CONNECTION = "postgresql+psycopg2://%s:%s@/%s?host=%s" % (DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME, DATABASE_HOST)

#Zookeeper settings
ZOOKEEPER_HOSTS = ["localhost:2181"]

#Mongrel settings
MONGREL_SENDER_ID = "lookupsvc_" + hashlib.sha1(SERVER_HOST+str(SERVER_PORT)).hexdigest()
MONGREL_PUB_ADDR = "tcp://localhost:9998"
MONGREL_PULL_ADDR = "tcp://localhost:9999"

#Riak settings
RIAK_HOST = "localhost"
RIAK_PORT = 8087
RIAK_SESSION_BUCKET = "tr_sessions"
RIAK_SESSION_POOL_SIZE = 4

#Logging settings
LOGGING = {
    "version": 1,

    "formatters": {
        "brief_formatter": {
            "format": "%(levelname)s: %(message)s"
        },

        "long_formatter": {
            "format": "%(asctime)s %(levelname)s: %(name)s %(message)s"
        }
    },

    "handlers": {

        "console_handler": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
            "formatter": "brief_formatter",
            "stream": "ext://sys.stdout"
        },

        "file_handler": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "long_formatter",
            "filename": "/opt/30and30/data/%s/logs/%s.%s.log" % (SERVICE, SERVICE, ENV),
            "when": "midnight",
            "interval": 1,
            "backupCount": 7
        }
    },
    
    "root": {
        "level": "DEBUG",
        "handlers": ["console_handler", "file_handler"]
    }
}
