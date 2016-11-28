#!/usr/bin/python
import argparse
import time

from tornado.ioloop import IOLoop
from rpc import RPCServer
from util import setup_logging


class Server(RPCServer):
    def __init__(self, host, port, token):
        RPCServer.__init__(self, token)
        self.host = host
        self.port = int(port)

    def listen(self, port=None, address=""):
        _port = port or self.port
        _address = address or self.host
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
