from wsgiref.simple_server import make_server
from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase
from werkzeug.local import LocalStack, LocalProxy
import re
import logging as log
import json


_request_context_stack = LocalStack()
request = LocalProxy(lambda: _request_context_stack.top.request)


class Request(RequestBase):
    def __init__(self, environ):
        RequestBase.__init__(self, environ)


class Response(ResponseBase):
    default_mimetype = 'text/html'


class RequestContext(object):
    def __init__(self, environ):
        self.request = Request(environ)
        self.response = Response()

    def __enter__(self):
        _request_context_stack.push(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        _request_context_stack.pop()


class Cocoa(object):
    """ Cocoa, the class """
    def __init__(self):
        self.routes = []

    @staticmethod
    def build_route_pattern(route):
        """ build re pattern through registered url """
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
        return re.compile("^{}$".format(route_regex))

    def route(self, route_str):
        """ the route decorator """
        def decorator(f):
            """ just set the route map """
            route_pattern = self.build_route_pattern(route_str)
            self.routes.append((route_pattern, f))

            return f

        return decorator

    def get_route_match(self, path):
        """ get the matching route and view """
        for route_pattern, view_function in self.routes:
            m = route_pattern.match(path)
            if m:
                return m.groupdict(), view_function

        return None

    def application(self, environ, start_response):
        """ implement the wsgi """
        with RequestContext(environ):
            path = environ['PATH_INFO']
            route_match = self.get_route_match(path)
            if route_match:
                kwargs, view_function = route_match
                ret = view_function(**kwargs)
                body, content_type = self.__set_content_type_and_body(
                    view_ret=ret,
                    resource_extension=self.__get_request_resource_extension(path)
                )
                start_response('200 OK', [('Content-Type', content_type)])
                return body
            else:
                start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
                return 'Route "{}" has not been registered'.format(path)
    
    def __call__(self, environ, start_response):
        """Shortcut for :attr:`wsgi_app`"""
        return self.application(environ, start_response)

    def run(self, host, port):
        """ start a embed wsgi compatible http web server """
        httpd = make_server(host, port, self.application)
        log.info('Cocoa start at {}:{}'.format(host, port))
        httpd.serve_forever()

    def __get_request_resource_extension(self, path_str):
        """ get extension from path_str """
        import os
        _, file_extension = os.path.splitext(path_str)
        return file_extension

    def __set_content_type_and_body(self, view_ret, resource_extension):
        """ """
        body = view_ret
        if resource_extension == '.css':
            content_type = 'text/css'
        elif resource_extension == '.js':
            content_type = 'application/javascript'
        elif resource_extension in ['.html', '.hml']:
            content_type = 'text/html'
        elif resource_extension in ['.jpeg', '.jpg']:
            content_type = 'image/jpeg'
        elif resource_extension == '.png':
            content_type = 'image/png'
        else:
            if type(view_ret) is dict:
                content_type = 'application/json'
                body = json.dumps(view_ret, indent=2)
            else:
                content_type = 'text/html'

        return body, content_type
