# Season to taste - ESMOND_ROOT will need to be reset if it isn't
# /services/esmond or isn't set correctly in the Apache configuration.

import os
import site
import sys

from django.core.wsgi import get_wsgi_application

# ESMOND_ROOT should be defined via SetEnv in your Apache configuration.
# It needs to point to the directory esmond is installed in.

os.environ['DJANGO_SETTINGS_MODULE'] = 'esmond.settings'

print("path=", sys.path, file=sys.stderr)

# This fixes the hitch that mod_wsgi does not pass Apache SetEnv 
# directives into os.environ.

def application(environ, start_response):
    if 'ESMOND_ROOT' not in environ:
        print("Please define ESMOND_ROOT in your Apache configuration", file=sys.stderr)
        exit()
    esmond_root = environ['ESMOND_ROOT']
    os.environ['ESMOND_ROOT'] = esmond_root
    if 'ESMOND_CONF' in environ:
        os.environ['ESMOND_CONF'] = environ['ESMOND_CONF']
    return get_wsgi_application()(environ, start_response)

"""
Example apache httpd.conf directives:
Make sure that WSGIPassAuthorization is on when using the REST framework/django 
level auth or mod_wsgi will munch the auth headers.

WSGIScriptAlias / /services/esmond/esmond/wsgi.py
WSGIPythonPath /services/esmond/esmond:/services/esmond/venv/lib/python2.7/site-packages
WSGIPythonHome /services/esmond/venv
WSGIPassAuthorization On

WSGIDaemonProcess www python-path=/services/esmond/esmond:/services/esmond/venv/lib/python2.7/site-packages home=/services/esmond processes=3 threads=15
WSGIProcessGroup www

<Directory /services/esmond/esmond>
<Files wsgi.py>
SetEnv ESMOND_ROOT /services/esmond
AuthType None
Order deny,allow
Allow from all
</Files>
</Directory>
"""
