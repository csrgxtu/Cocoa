from wsgiref.simple_server import make_server
import re


class Cocoa(object):
    ''' Cocoa, the class '''
    def __init__(self):
        self.routes = []

    @staticmethod
    def build_route_pattern(route):
        ''' build re pattern through registered url '''
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
        return re.compile("^{}$".format(route_regex))

    def route(self, route_str):
        ''' the route decorator '''
        def decorator(f):
            ''' just set the route map '''
            route_pattern = self.build_route_pattern(route_str)
            self.routes.append((route_pattern, f))

            return f

        return decorator

    def get_route_match(self, path):
        ''' get the matching route and view '''
        for route_pattern, view_function in self.routes:
            m = route_pattern.match(path)
            if m:
                return m.groupdict(), view_function

        return None

    def application(self, environ, start_response):
        ''' implement the wsgi '''
        path = environ['PATH_INFO']
        route_match = self.get_route_match(path)
        if route_match:
            kwargs, view_function = route_match
            start_response('200 OK', [('Content-Type', 'text/html')])
            return view_function(**kwargs)
        else:
            start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
            return 'Route "{}" has not been registered'.format(path)
    
    def __call__(self, environ, start_response):
        """Shortcut for :attr:`wsgi_app`"""
        return self.application(environ, start_response)

    def run(self, host, port):
        ''' start a embed wsgi compatible http web server '''
        httpd = make_server(host, port, self.application)
        print 'Serving at {}:{}'.format(host, port)
        httpd.serve_forever()
