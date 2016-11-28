#!/usr/bin/python
import argparse
import logging
import time

from tornado.ioloop import IOLoop
from rpclock.rpc import RPCServer
from rpclock.util import setup_logging

logger = logging.getLogger('rpc')


class Server(RPCServer):
    def __init__(self, host, port, token):
        RPCServer.__init__(self, token)
        self.host = host
        self.port = int(port)

    def listen(self, port=None, address=""):
        _port = port or self.port
        _address = address or self.host
        logger.info('Server listen on %s:%s' % (_address, _port))
        super(RPCServer, self).listen(_port, _address)


    def time(self):
        return time.time()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--host', help='server listen ip', required=True)
    parser.add_argument('-p', '--port', help='server listen port', required=True)
    parser.add_argument('-t', '--token', help='authentication token')

    args = parser.parse_args()

    setup_logging('rpc')

    server = Server(host=args.host, port=args.port, token=args.token)
    server.listen()
    IOLoop.instance().start()
