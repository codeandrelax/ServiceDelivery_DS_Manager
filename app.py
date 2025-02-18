# app.py

import os
os.chdir(os.path.dirname(__file__))

import sys
import json
import mysql.connector
from mysql.connector import pooling
from mysql.connector import Error
from datetime import datetime

from functools import wraps

# A dictionary to store path handlers
path_handlers = {}
    
def path_handler(path):
    """Decorator to register functions as path handlers."""
    def decorator(func):
        print(f"Registering handler for path: {path}")
        path_handlers[path] = func
        return func
    return decorator
    
sys.path.insert(0, os.path.dirname(__file__))

from db import get_db_connection

from common_funcs import *

# Import handles here
# from service_delivery import handle_origin_request
# from service_delivery import handle_register_device_request
# from service_delivery import handle_show_uuid
# from service_delivery import handle_sw_js_request
# from service_delivery import handle_report_focus
# from service_delivery import handle_check_if_registered
from service_delivery import *

from routes.get_ad import handle_get_ad_request
from routes.get_uuids_by_user_id import handle_get_uuids_by_user_id
from routes.get_user_info import handle_get_user_info
from routes.get_disp_config import handle_get_display_config_request
    
def handle_not_found(environ, start_response):
    """Handles 404 Not Found response."""
    headers = [('Content-Type', 'text/plain')]
    start_response('404 Not Found', headers)
    return [b'404 Not Found']

def application(environ, start_response):
    path = environ.get('PATH_INFO', '').strip()
    method = environ.get('REQUEST_METHOD', '')

    # Common CORS headers
    cors_headers = [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type'),
    ]

    # Handle CORS preflight (OPTIONS request)
    if method == 'OPTIONS':
        start_response('200 OK', cors_headers)
        return [b""]

    # Look up the handler for the path, if it exists
    handler = path_handlers.get(path)

    if handler:
        return handler(environ, start_response, cors_headers)
    else:
        return handle_not_found(environ, start_response)

