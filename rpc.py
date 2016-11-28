import functools
import logging
import socket
from struct import unpack, pack

from tornado import gen
from tornado.concurrent import is_future
from tornado.iostream import IOStream
from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
from json import dumps, loads

MESSAGE_BYTES = 4
METHOD_NOT_FOUND = 404
INTERNAL_ERROR = 500
FORBIDDEN_ERROR = 403
SUCCESS = 200
STATUS_DICT = {
    METHOD_NOT_FOUND: 'Method not found',
    INTERNAL_ERROR: 'Internal error',
    FORBIDDEN_ERROR: 'Token request'
}

logger = logging.getLogger(__name__)


class Connection(object):
    clients = set()

    def __init__(self, rpc_tcp_server, stream, address):
        Connection.clients.add(self)
        self._server = rpc_tcp_server
        self._stream = stream
        self._address = address
        self.read_message_bytes()

    def read_message_bytes(self):
        self._stream.read_bytes(MESSAGE_BYTES, self.read_message)

    def read_message(self, data):
        _bytes = unpack('!I', data)[0]
        self._stream.read_bytes(_bytes, self.handle_request)

    def _done_callback(self, f):
        res = dumps(f.result())
        _bytes = pack('!I', len(res))
        self.send_result(_bytes + res)

    def handle_request(self, data):
        content = loads(data)
        method = content['method']
        args = content['args']
        kwargs = content['kwargs']

        token = content['token'] if 'token' in content else None

        future = self._server.dispatch(token, method, args, kwargs)
        future.add_done_callback(self._done_callback)
        self.read_message_bytes()

    def send_result(self, data):
        self._stream.write(data)

    def set_on_close(self, f):
        if callable(f):
            self._stream.set_close_callback(f)


class RPCServer(TCPServer):
    def __init__(self, token=None):
        TCPServer.__init__(self)
        self.token = token

    def handle_stream(self, stream, address):
        logger.info('New connection created with %s:%s' % address)
        Connection(self, stream, address)

    @gen.coroutine
    def dispatch(self, token, method_name, args, kw):
        method = getattr(self, method_name, None)
        if self.token:
            if not token or token != self.token:

                raise gen.Return({'status': FORBIDDEN_ERROR})
        if not callable(method) or getattr(method, 'private', False):
            raise gen.Return({'status': METHOD_NOT_FOUND})
        try:
            response = method(*args, **kw)
        except Exception:
            raise gen.Return({'status': INTERNAL_ERROR})

        if is_future(response):
            response = yield response

        raise gen.Return({'status': SUCCESS, 'result': response})


class RPCClient(object):
    def __init__(self, io_loop=None, token=None):
        self._io_loop = self.io_loop = io_loop or IOLoop.current()
        self._sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._iostream = IOStream(self._sock_fd)
        self.token = token

    def check_iostream(self):
        if not self._iostream:
            return False
        try:
            self._iostream._check_closed()
        except Exception, e:
            self._iostream = None
            return False
        else:
            return True

    @gen.coroutine
    def connect(self, host, port):
        yield self._iostream.connect((host, port))

    @gen.coroutine
    def remote_call(self, method, *args, **kwargs):
        content = dict(method=method, args=args, kwargs=kwargs)
        if self.token:
            content['token'] = self.token
        req = dumps(content)
        bytes_num = pack('!I', len(req))

        if self.check_iostream():
            yield self._iostream.write(bytes_num + req)
            data = yield self._iostream.read_bytes(MESSAGE_BYTES)
            bytes_num = unpack('!I', data)[0]

            resp = yield self._iostream.read_bytes(bytes_num)
            resp_content = loads(resp)

            status = resp_content['status']
            if status in STATUS_DICT:
                raise Exception(STATUS_DICT[status])
            else:
                raise gen.Return(resp_content['result'])

        else:
            self.handle_iostream_close()

    def __getattr__(self, name):
        return functools.partial(self.remote_call, name)

    def handle_iostream_close(self):
        pass

