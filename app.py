#!env python3
# -*- coding: utf-8 -*-
#

import os
import sys

def gunicorn_dispatch_request(environ, start_response):
    environ['BASE_PATH'] = environ.get('HTTP_BASE_PATH', '')
    script_url = environ.get('HTTP_SCRIPT_URL', '')
    path_info = environ.get('PATH_INFO', '/')
    if path_info == '/' and script_url and script_url[-1] != '/':
        script_url += '/'
    environ['SCRIPT_URL'] = script_url
    environ['SCRIPT_NAME'] = ''

    verbose = False
    if 'GUNICORN_DEBUG' in environ:
        verbose = True

    if verbose:
        for f in ['SCRIPT_URL', 'SCRIPT_NAME', 'BASE_PATH', 'PATH_INFO', 'HTTP_SCRIPT_URL', 'HTTP_BASE_PATH', 'HTTP_PATH_INFO']:
            print('%s=%s' % (f, environ.get(f, 'N/A')) )

    from django.urls import set_script_prefix
    # set script prefix from BASE_PATH/HTTP_BASE_PATH passed along by
    # the HTTP server (e.g. nginx).
    # Possible nginx config:
    #   proxy_set_header SCRIPT_URL $request_uri;
    print('base=%s' % environ['BASE_PATH'])
    set_script_prefix(environ['BASE_PATH'])
    os.environ['BASE_PATH'] = environ['BASE_PATH']
    from arsoft.web.crashupload.wsgi import application as wsgi_application
    return wsgi_application(environ, start_response)

application = gunicorn_dispatch_request

if __name__ == "__main__":
    gunicorn_dispatch_request(os.environ, None)
