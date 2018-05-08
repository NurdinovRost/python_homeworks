import argparse
import sys
import os
import async_webserver


class AsyncWSGIServer(async_webserver.AsyncServer):

    def set_app(self, application):
        self.application = application

    def get_app(self):
        return self.application


class AsyncWSGIRequestHandler(async_webserver.AsyncHTTPRequestHandler):

    def get_environ(self):
        
        env = {}
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = 'http'
        env['wsgi.input']        = sys.stdin
        env['wsgi.errors']       = sys.stderr
        env['wsgi.multithread']  = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once']     = False
        env['REQUEST_METHOD']    = self.request_method
        env['PATH_INFO']         = self.path
        env['SERVER_NAME']       = self.server_name
        env['SERVER_PORT']       = str(self.server_port)

        return env

    def start_response(self, status, response_headers, exc_info=None):
        self.code, self.msg = status.split(" ", 1)
        self.send_response(self.code, self.msg)
        
        for key, value in response_headers:
            send_response(key, value)
        self.headers_end()          

    def handle_request(self):
        app = server.get_app()
        result = app(self.get_environ, self.start_response)
        self.finish_response(result)

    def finish_response(self, result):
        [body] = result
        self.send(body)
        self.close()
        

def parse_args():
    parser = argparse.ArgumentParser("Simple asynchronous web-server")
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9002)
    parser.add_argument("--log", dest="loglevel", default="info")
    parser.add_argument("--logfile", dest="logfile", default=None)
    parser.add_argument("-w", dest="nworkers", type=int, default=1)
    parser.add_argument("-r", dest="document_root", default="/")
    parser.add_argument("-app", dest="application", help="application:module")
    return parser.parse_args()

       
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app = sys.argv[1]
    module, application = app.split(':')
    module = __import__(module)
    application = getattr(module, application)
    server = AsyncWSGIServer(handler=AsyncWSGIRequestHandler)
    server.set_app(application)
    server.serve_forever()        