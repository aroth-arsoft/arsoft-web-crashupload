#!env python3
# -*- coding: utf-8 -*-
#

import os
import sys

def get_bytes_from_wsgi(environ, key, default):
    """
    Get a value from the WSGI environ dictionary as bytes.

    key and default should be strings.
    """
    value = environ.get(key, default)
    # Non-ASCII values in the WSGI environ are arbitrarily decoded with
    # ISO-8859-1. This is wrong for Django websites where UTF-8 is the default.
    # Re-encode to recover the original bytestring.
    return value.encode("iso-8859-1")

http_base_path = os.environ.get('BASE_PATH', '')

def gunicorn_dispatch_request(environ, start_response):

    base_path = get_bytes_from_wsgi(environ, "HTTP_BASE_PATH", http_base_path)
    if base_path:
        #len_base_path = len(base_path)
        path_info = get_bytes_from_wsgi(environ, 'PATH_INFO', '')
        if path_info.startswith(base_path):
            split_path = path_info.split(b'/')
        
            environ['SCRIPT_NAME'] = b'/'.join(split_path[:2])
            environ['PATH_INFO'] = b'/'+b'/'.join(split_path[2:])

            environ['SCRIPT_NAME'] = environ['SCRIPT_NAME'].decode("iso-8859-1")
            environ['PATH_INFO'] = environ['PATH_INFO'].decode("iso-8859-1")

    verbose = False
    if 'GUNICORN_DEBUG' in environ:
        verbose = True

    if verbose:
        for f in ['SCRIPT_URL', 'SCRIPT_NAME', 'BASE_PATH', 'PATH_INFO', 'HTTP_SCRIPT_URL', 'HTTP_BASE_PATH', 'HTTP_PATH_INFO']:
            print('%s=%s' % (f, environ.get(f, 'N/A')) )

    # set script prefix from BASE_PATH/HTTP_BASE_PATH passed along by
    # the HTTP server (e.g. nginx).
    # Possible nginx config:
    #   proxy_set_header BASE_PATH "<%= @uri %>";
    #   proxy_set_header FORCE_SCRIPT_NAME "<%= @uri %>";
    #   proxy_set_header SCRIPT_URL $request_uri;
    from arsoft.web.crashupload.wsgi import application as wsgi_application, django_settings
    from whitenoise import WhiteNoise
    wsgi_application = WhiteNoise(wsgi_application, root=django_settings.STATIC_ROOT, prefix='static')
    for d in django_settings.STATICFILES_DIRS:
        wsgi_application.add_files(d, prefix='static')    
    return wsgi_application(environ, start_response)

application = gunicorn_dispatch_request

if __name__ == "__main__":
    gunicorn_dispatch_request(os.environ, None)
