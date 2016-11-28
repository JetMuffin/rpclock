#!/usr/bin/python
import argparse
import os
import sys
import time
import platform
from tornado import gen
from tornado.ioloop import IOLoop

from rpc import RPCClient


def clear():
    if platform.system() in ['Darwin', 'Linux']:
        clear_cmd = 'clear'
    elif platform.system() in ['Windows']:
        clear_cmd = 'cls'
    else:
        raise Exception('Unsupported system.')

    os.system(clear_cmd)


@gen.coroutine
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--host', help='server listen ip', required=True)
    parser.add_argument('-p', '--port', help='server listen port', required=True)
    parser.add_argument('-t', '--token', help='authentication token')

    args = parser.parse_args()

    client = RPCClient(token=args.token)
    client.connect(args.host, int(args.port))

    try:
        while True:
            send_time = time.time()
            server_time = yield client.time()
            receive_time = time.time()

            print time.strftime('%Y-%m-%d %H:%M:%S',
                                time.localtime(server_time - (receive_time - send_time) / 2))
            time.sleep(1)
            clear()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    ioloop = IOLoop.current()
    ioloop.run_sync(main)
