import asyncore
import asynchat
import socket
import multiprocessing
import logging
import mimetypes
import os
import urllib
import argparse
from time import strftime, gmtime


class FileProducer(object):
    
    def __init__(self, file, chunk_size=4096):
        self.file = file
        self.chunk_size = chunk_size

    def more(self):
        if self.file:
            data = self.file.read(self.chunk_size)
            if data:
                return bytearray(data)
            self.file.close()
            self.file = None
        return ""


def url_normalize(path):
    if path.startswith("."):
        path = "/" + path
    while "../" in path:
        p1 = path.find("/..")
        p2 = path.rfind("/", 0, p1)
        if p2 != -1:
            path = path[:p2] + path[p1+3:]
        else:
            path = path.replace("/..", "", 1)
    path = path.replace("/./", "/")
    path = path.replace("/.", "")
    return path


class AsyncHTTPRequestHandler(asynchat.async_chat):

    def __init__(self, sock):
        super().__init__(sock)
        self.set_terminator(b"\r\n\r\n")
        self.reading_headers = True
        self.req_data = ""
        self.post_data = bytes()
        self.host = '127.0.0.1'
        self.port = 9002       


    def collect_incoming_data(self, data):
        if not self.reading_headers:
            self.post_data = data
        else:
            self.req_data += data.decode('utf-8')

    def found_terminator(self):
        self.parse_request()

    def parse_request(self):
        if self.reading_headers:
            method, path, headers = self.req_data.split(" ", 2)

            self.method = method
            self.uri = path

            self.reading_headers = False
            if not self.parse_headers(headers):
                self.send_error(400)
                self.handle_close()
                return

            if self.method == "POST":
                clen = self.query_params['Content-Length']
                if int(clen) > 0:
                    self.set_terminator(int(clen))
                else:
                    self.handle_request()
            else:
                self.set_terminator(None)
                self.handle_request()
        else:
            self.set_terminator(None)
            self.request_body = self.req_data
            self.handle_request()

    def parse_headers(self, headers):
        try:
            headers_list = headers.split("\r\n")

            protocol = headers_list[0]
            query_params = {}
            for header in headers_list[1:]:
                header = header.split(':', 1)
                if len(header) == 2:
                    query_params[header[0]] = header[1]
                    
            """parts = uri.split('?', 1)
            if len(parts) > 1:
                query_params = parse_qs(parts[1], keep_blank_values=True)
                print(query_params)"""


            self.http_protocol = protocol
            self.query_params = query_params
            self.request_body = ""
            return True
        except Exception as e:
            print(e)
            return False

    def handle_request(self):
        method_name = 'do_' + self.method
        if not hasattr(self, method_name):
            self.send_error(405)
            self.handle_close()
            return
        handler = getattr(self, method_name)
        handler()

    def send_error(self, code, message=None):
        try:
            short_msg, long_msg = self.responses[code]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg

        self.send_response(code, message)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Connection", "close")
        self.end_headers()

    def end_headers(self):
        self.push(bytearray('\r\n', 'utf8'))

    def send_response(self, code, message=None):
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        self.push(bytearray("{protocol} {code} {message}\r\n".format(
            protocol=self.http_protocol, code=code, message=message), 'utf8'))
        self.send_header("Server", "async-http-server")
        self.send_header("Date", self.date_time_string())

    def date_time_string(self):
        return strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())

    def send_header(self, keyword, value):
        self.push(bytearray('{}: {}\r\n'.format(keyword, value), 'utf8'))

    def send_head(self):
        path = self.translate_path(self.uri)

        if path == '' or os.path.isdir(path):
            path = os.path.join(path, "index.html")
            if not os.path.exists(path):
                self.send_response(403)
                self.handle_close()
                return None

        try:
            f = open(path, 'rb')
        except IOError:
            self.send_response(404)
            self.handle_close()
            return None

        _, ext = os.path.splitext(path)
        ctype = mimetypes.types_map[ext.lower()]

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", os.path.getsize(path))
        self.end_headers()
        return f

    def translate_path(self, path):
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        #path = url_normalize(urllib.unquote(path))
        if path[0] == '/':
            return path[1:]
        return path

    def do_GET(self):
        f = self.send_head()
        if f:
            self.push_with_producer(FileProducer(f))
            self.close_when_done()

    def do_HEAD(self):
        f = self.send_head()
        if f:
            f.close()
            self.handle_close()

    responses = {
        200: ('OK', 'Request fulfilled, document follows'),
        400: ('Bad Request',
            'Bad request syntax or unsupported method'),
        403: ('Forbidden',
            'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
            'Specified method is invalid for this resource.'),
    }


class AsyncServer(asyncore.dispatcher):
    def __init__(self, host="127.0.0.1", port=9002, handler=None):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.bind((host, port))
        self.address = self.socket.getsockname()
        self.listen(1)
        self.handler = handler
        return

    def handle_accept(self):
        client_info = self.accept()
        if self.handler is None:
            AsyncHTTPRequestHandler(sock=client_info[0])
        else:
            self.handler(sock=client_info[0])

    def serve_forever(self):
        asyncore.loop()
    
    def handle_close(self):
        self.close()


def parse_args():
    parser = argparse.ArgumentParser("Simple asynchronous web-server")
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9002)
    parser.add_argument("--log", dest="loglevel", default="info")
    parser.add_argument("--logfile", dest="logfile", default=None)
    parser.add_argument("-w", dest="nworkers", type=int, default=1)
    parser.add_argument("-r", dest="document_root", default=".")
    return parser.parse_args()

def run():
    server = AsyncServer(host=args.host, port=args.port)
    server.serve_forever()

if __name__ == "__main__":
    args = parse_args()

    logging.basicConfig(
        filename=args.logfile,
        level=getattr(logging, args.loglevel.upper()),
        format="%(name)s: %(process)d %(message)s")
    log = logging.getLogger(__name__)

    DOCUMENT_ROOT = args.document_root
    for _ in range(args.nworkers):
        p = multiprocessing.Process(target=run)
        p.start()
