#!/usr/bin/env python

import argparse
import errno
import logging
import os
import signal
import sys
import time
import traceback

from trpycore.process.daemon import exec_daemon
from trpycore.process.pid import pid_exists


PROJECT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

SERVICE =  os.path.basename(PROJECT_DIRECTORY)
SERVICE_DIRECTORY = os.path.join(PROJECT_DIRECTORY, SERVICE)
SERVICE_PATH = os.path.join(SERVICE_DIRECTORY, "%s.py" % SERVICE)

#Add service directory path so we can import settings when needed
sys.path.insert(0, SERVICE_DIRECTORY)

class ManagerException(Exception):
    pass

#Operations

def start(env=None, user=None, group=None):
    #Set environment variable for forked daemon
    #This will not change os.environ for current process.
    if env:
        os.putenv("SERVICE_ENV", env)
    
    #If env directory exists, use that python.
    #Otherwise backoff to /usr/bin/env python.
    if os.path.exists(os.path.join(PROJECT_DIRECTORY, "env")):
        python = os.path.join(PROJECT_DIRECTORY, "env", "bin", "python")
        command = [python, SERVICE_PATH]
    else:
        command = ["/usr/bin/env", "python", SERVICE_PATH]

    pid = exec_daemon(
            command[0],
            command,
            umask=None,
            working_directory=PROJECT_DIRECTORY,
            username=user,
            groupname=group)

    #Sleep for a second and do quick sanity check to make sure process is running
    time.sleep(1)
    if not pid_exists(pid):
        raise ManagerException("Failed to start service")

def stop(env=None, block=False, timeout=None):
    #Modify process environment and import settings.
    #It's neccessary to modify environment prior to 
    #import so that the appropriate environment
    #settings are loaded.
    if env:
        os.environ["SERVICE_ENV"] = env
    import settings
    
    #Nothing to do if pid file does not exist
    if not os.path.exists(settings.SERVICE_PID_FILE):
        return
    
    #Open pidfile and send pid SIGTERM for graceful exit.
    with open(settings.SERVICE_PID_FILE, 'r') as pidfile:
        pid = int(pidfile.read())
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as error:
            if error.errno == errno.EPERM:
                raise ManagerException("Failed to stop service: permission denied.")
        else:
            #If blocking wait for service to exit or timeout to be exceeded
            start_time = time.time()
            while block and pid_exists(pid):
                running_time = time.time() - start_time
                if timeout and (running_time > timeout):
                    raise ManagerException("Failed to stop service: timeout.")
                time.sleep(1)
        

def restart(env=None, block=False, timeout=None, user=None, group=None):
    stop(env, block, timeout)
    start(env, user, group)


#Command handlers
def startCommandHandler(args):
    """Start service as daemon process"""
    start(args.env, args.user, args.group)

startCommandHandler.examples = """Examples:
    manager.py start             #Start service
    manager.py --env prod start  #Start prod service
"""


def stopCommandHandler(args):
    """Stop service"""
    stop(args.env, args.wait, args.timeout)

stopCommandHandler.examples = """Examples:
    manager.py stop                      #Stop service
    manager.py stop --wait               #Stop service (blocking)
    manager.py stop --wait --timeout 10  #Stop service (blocking w/ timeout)
"""


def restartCommandHandler(args):
    """Restart service"""
    restart(args.env, True, args.timeout, args.user, args.group)

restartCommandHandler.examples = """Examples:
    manager.py restart               #Restart service
    manager.py restart --timeout 10  #Restart service (w/ stop timeout)
"""



def main(argv):

    def parse_arguments():
        parser = argparse.ArgumentParser(description="manager.py controls Tech Residents services")
        parser.add_argument("-e", "--env", help="service environment")

        commandParsers = parser.add_subparsers()

        #start parser
        startCommandParser = commandParsers.add_parser(
                "start",
                help="start service",
                description=startCommandHandler.__doc__,
                epilog=startCommandHandler.examples,
                formatter_class=argparse.RawDescriptionHelpFormatter
                )
        startCommandParser.set_defaults(command="start", commandHandler=startCommandHandler)
        startCommandParser.add_argument("-u", "--user", help="Drop privileges to user (also requires --group)")
        startCommandParser.add_argument("-g", "--group", help="Drop privileges to group (also requires --user)")

        #stop parser
        stopCommandParser = commandParsers.add_parser(
                "stop",
                help="stop service",
                description=stopCommandHandler.__doc__,
                epilog=stopCommandHandler.examples,
                formatter_class=argparse.RawDescriptionHelpFormatter
                )
        stopCommandParser.set_defaults(command="stop", commandHandler=stopCommandHandler)
        stopCommandParser.add_argument("-w", "--wait", action="store_true", help="Wait for service to stop.")
        stopCommandParser.add_argument("-t", "--timeout", type=int, help="Wait timeout in seconds.")

        #restart parser
        restartCommandParser = commandParsers.add_parser(
                "restart",
                help="restart service",
                description=restartCommandHandler.__doc__,
                epilog=restartCommandHandler.examples,
                formatter_class=argparse.RawDescriptionHelpFormatter
                )
        restartCommandParser.set_defaults(command="restart", commandHandler=restartCommandHandler)
        restartCommandParser.add_argument("-t", "--timeout", default="15", type=int, help="Timeout in seconds for service to stop.")
        restartCommandParser.add_argument("-u", "--user", help="Drop privileges to user (also requires --group)")
        restartCommandParser.add_argument("-g", "--group", help="Drop privileges to group (also requires --user)")

        return parser.parse_args(argv[1:])


    #configure logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.INFO)
    logger.addHandler(consoleHandler)
    
    log = logging.getLogger("main")

    args = parse_arguments()

    try:
        #Invoke command handler
        args.commandHandler(args)

        return 0
    
    except ManagerException as error:
        log.error(str(error))
        return 1

    except KeyboardInterrupt:
        return 2 
    
    except Exception as error:
        log.error("Unhandled exception: %s" % str(error))
        log.error(traceback.format_exc())
        return 3 

if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
