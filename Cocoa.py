from wsgiref.simple_server import make_server


class Cocoa(object):
    ''' Cocoa, the class '''
    def __init__(self):
        self.routes = {}

    def route(self, route_str):
        ''' the route decorator '''
        def decorator(f):
            ''' just set the route map '''
            self.routes[route_str] = f
            return f
        return decorator

    def serve(self, path):
        ''' server a request '''
        view_function = self.routes[path]
        if view_function:
            return view_function
        else:
            raise ValueError('Route "{}" has not been registered'.format(path))

    def application(self, environ, start_response):
        ''' implement the wsgi '''
        path = environ['PATH_INFO']
        view_function = self.routes[path] if self.routes.has_key(path) else None
        if view_function:
            start_response('200 OK', [('Content-Type', 'text/html')])
            return view_function()
        else:
            start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
            return 'Route "{}" has not been registered'.format(path)
            # raise ValueError('Route "{}" has not been registered'.format(path))

    def run(self, host, port):
        ''' start a embed wsgi compatible http web server '''
        httpd = make_server(host, port, self.application)
        print 'Serving at {}:{}'.format(host, port)
        httpd.serve_forever()
