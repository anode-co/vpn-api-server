from http.server import HTTPServer, BaseHTTPRequestHandler
from functools import partial
import json
import urllib.parse


class ApiHttpServer:
    """Simple CGI-python web server."""

    server = None
    router = None
    request_handler = None
    in_verbose_mode = False

    def __init__(self, bind_address='localhost', port=8000):
        """Initialize the server."""
        self.bind_address = bind_address
        self.port = port
        self.router = Router()

    def add_route(self, route):
        """Add route."""
        self.router.add_route(route)

    def add_routes(self, routes):
        """Add several routes."""
        for route in routes:
            self.add_route(route)

    def run(self):
        """Run."""
        self.request_handler = partial(self.RequestHandler, self.router)
        self.server = HTTPServer((self.bind_address, self.port), self.request_handler)
        self.server.serve_forever()

    class RequestHandler(BaseHTTPRequestHandler):
        """Default Handler."""

        router = None
        in_verbose_mode = False

        def __init__(self, router, request, client_address, server, *args, **kwargs):
            """Initialize the Request Handler."""
            self.router = router
            BaseHTTPRequestHandler.__init__(self, request, client_address, server)
            # self.router = Router()

        def do_OPTIONS(self):
            """Return OPTIONS headers.""" 
            print("OPTIONS!")  
            #  self.send_response(200, "ok")
            self.write_status(Response.STATUS_200_OK)
            self.send_header('Access-Control-Allow-Credentials', 'true')
            self.send_header('Access-Control-Allow-Origin', 'http://localhost:8888')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
            self.write_body("Hello")
            '''
            headers = {
                'Content-Type': 'application/json; encoding=utf-8',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            }
            self.write_status(Response.STATUS_200_OK)
            self.write_headers(headers)
            self.write_body("")
            '''

        def do_HEAD(self):
            """Send headers."""
            route = self.router.get_route(self.path)
            if route is None:
                response = Response("<html><head><title>404 not found</title></head><body><h1>404 Not found</h1></body></html>", status=Response.STATUS_404_NOT_FOUND)
            else:
                response = route.get(self)
            self.write_status(response.status)
            self.write_headers(response.headers)
            # self.write_body(response.body)

        def do_GET(self):
            """Handle GET."""
            route = self.router.get_route(self.path)
            response = None
            if route is None:
                response = Response("<html><head><title>404 not found</title></head><body><h1>404 Not found</h1></body></html>", status=Response.STATUS_404_NOT_FOUND)
            else:
                self.say("printing body")
                request = Request(self)
                response = route.get(request)
            self.say("printing body")
            self.say("==============================")
            self.write_status(response.status)
            self.write_headers(response.headers)
            self.write_body(response.body)
            self.say("==============================")

        def do_POST(self):
            """Handle POST."""
            route = self.router.get_route(self.path)
            response = None
            if route is None:
                response = Response("<html><head><title>404 not found</title></head><body><h1>404 Not found</h1></body></html>", status=Response.STATUS_404_NOT_FOUND)
            else:
                self.say("printing body")
                request = Request(self)
                response = route.post(request)
            self.say("printing body")
            self.say("==============================")
            self.write_status(response.status)
            self.write_headers(response.headers)
            self.write_body(response.body)
            self.say("==============================")

        def do_DELETE(self):
            """Handle POST."""
            route = self.router.get_route(self.path)
            response = None
            if route is None:
                response = Response("<html><head><title>404 not found</title></head><body><h1>404 Not found</h1></body></html>", status=Response.STATUS_404_NOT_FOUND)
            else:
                self.say("printing body")
                request = Request(self)
                response = route.delete(request)
            self.say("printing body")
            self.say("==============================")
            self.write_status(response.status)
            self.write_headers(response.headers)
            self.write_body(response.body)
            self.say("==============================")

        def write_status(self, status):
            """Write the HTTP Status."""
            self.send_response(status)

        def write_headers(self, headers):
            """Output headers."""
            for key, value in headers.items():
                self.send_header(key, value)
                self.say("{}: {}".format(key, value))
            self.end_headers()
            self.say("")

        def write_body(self, body):
            """Write the output body."""
            output = body
            if isinstance(body, dict) or isinstance(body, list):
                output = json.dumps(body, indent=4)
            output = output.encode('utf-8')
            # self.wfile.write("hello".encode('utf-8'))
            self.wfile.write(output)
            self.say(output)

        def say(self, message):
            """Print debugging messages."""
            if self.in_verbose_mode is True:
                print("[{}] {}".format(self.__class__.__name__, message))


class Route:
    """URL Route."""

    path = None
    view = None

    def __init__(self, path, view):
        """Initialize Route."""
        self.path = path
        self.view = view

    def get(self, request):
        """Get request."""
        return self.view.get(request)

    def post(self, request):
        """Get request."""
        return self.view.post(request)

    def put(self, request):
        """Get request."""
        return self.view.put(request)

    def delete(self, request):
        """Get request."""
        return self.view.delete(request)


class Router:
    """URL Router."""

    routes = {}

    def __init__(self):
        """Initialize."""
        pass

    def add_route(self, route):
        """Add a route."""
        self.routes[route.path] = route

    def get_route(self, path):
        """Get a route from the path."""
        print("PATH: {}".format(path))
        if path in self.routes:
            print("    found path: {}".format(self.routes[path]))
            return self.routes[path]
        print("    no path found")
        return None

    def route(self, path):
        """Find a route."""
        if path in self.routes:
            return self.routes[path]
        return None


class Request:
    """HTTP Request."""

    METHOD_GET = 'GET'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_PATCH = 'PATCH'
    METHOD_DELETE = 'DELETE'
    METHOD_OPTIONS = 'OPTIONS'
    METHOD_HEAD = 'HEAD'
    METHOD_CONNECT = 'CONNECT'
    METHOD_TRACE = 'TRACE'
    DEFAULT_CHARSET = 'utf-8'
    content_type = 'text/plain'
    charset = DEFAULT_CHARSET
    content_length = 0
    headers = {}
    body = None
    method = METHOD_GET

    def __init__(self, handler):
        """Initialize from a BaseHTTPRequestHandler object."""
        for key, value in handler.headers.items():
            header = "-".join([key_part.capitalize() for key_part in key.split('-')])
            if header == 'Content-Type':
                if "; encoding" in value:
                    self.charset = value[value.index('=') + 1:]
                    self.content_type = value[:value.index(';')].lower()
                else:
                    self.content_type = value.lower()
            if header == 'Content-Length':
                self.content_length = int(value)
            self.headers[header] = value
            self.body = handler.rfile.read(self.content_length).decode(self.charset)

    @property
    def body_json(self):
        """Convert respnose body into JSON."""
        if self.content_type == "application/json" or self.content_type == 'text/json':
            return json.loads(self.body)
        elif self.content_type == 'application/x-www-form-urlencoded':
            return urllib.parse.parse_qs(self.body)
        elif self.content_type == 'multipart/form-data':
            print("THIS FEATURE NOT YET SUPPORTED")
        else:
            raise Exception("Unable to process text into JSON")


class Response:
    """HTTP Response."""

    status = None
    headers = {}
    body = None

    DEFAULT_HEADERS = {
        'Content-Type': 'text/html',
    }
    DEFAULT_JSON_HEADERS = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
    }

    STATUS_200_OK = 200
    STATUS_201_CREATED = 201

    STATUS_400_BAD_REQUEST = 400
    STATUS_403_DENIED = 403
    STATUS_404_NOT_FOUND = 404

    def __init__(self, body, status=STATUS_200_OK, headers=None):
        """Initialize the Response."""
        self.body = body
        self.status = status
        if headers is None:
            if isinstance(body, dict) or isinstance(body, list):
                self.headers = self.DEFAULT_JSON_HEADERS
            else:
                self.headers = self.DEFAULT_HEADERS
        else:
            self.headers = headers
