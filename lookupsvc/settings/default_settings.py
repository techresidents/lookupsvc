import os
import socket

ENV = os.getenv("SERVICE_ENV", "default")

#Service Settings
SERVICE = "lookupsvc"
SERVICE_PID_FILE = "%s.%s.pid" % (SERVICE, ENV)

#Server settings
SERVER_HOST = socket.gethostname()
SERVER_INTERFACE = "0.0.0.0"
SERVER_PORT = 9091

#Zookeeper settings
ZOOKEEPER_HOSTS = ["localdev:2181"]

#Mongrel settings
MONGREL_SENDER_ID = "lookupsvc_sender_id_default"
MONGREL_PUB_ADDR = "tcp://localdev:9998"
MONGREL_PULL_ADDR = "tcp://localdev:9999"

#Riak settings
RIAK_HOST = "localdev"
RIAK_PORT = 8087
RIAK_SESSION_BUCKET = "tr_sessions"
RIAK_SESSION_POOL_SIZE = 4

#Chat settings
CHAT_LONG_POLL_WAIT = 10

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
            "filename": "%s.%s.log" % (SERVICE, ENV),
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
