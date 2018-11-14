import os
import sys

sys.path.append(os.getcwd() + '\\plrc_project')

from waitress import serve
from plrc.app import wsgi_app, cfg

WSGI_PORT = 80
if "api_port" in cfg:
    WSGI_PORT = int(cfg["api_port"])

serve(wsgi_app, host='0.0.0.0', port='%d' % WSGI_PORT)
