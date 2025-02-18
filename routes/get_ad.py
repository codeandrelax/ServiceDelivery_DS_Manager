# get_ad.py

import sys
import json
 
from app import path_handlers, path_handler
from service_delivery import *
from common_funcs import *

# Implement your scheduler here

counter = 0  # Global counter

videos = [
    {"name": "Advertisement", "url": "https://indigoingenium.ba/Tuborg.mp4"},
    {"name": "Advertisement", "url": "https://indigoingenium.ba/Heineken.mp4"},
    {"name": "Advertisement", "url": "https://indigoingenium.ba/BudLight.mp4"},
]

@path_handler('/get_ad')
def handle_get_ad_request(environ, start_response, cors_headers):
    try:
        length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(length).decode('utf-8')
        data = json.loads(body)
        uuid = data.get("uuid")
    except (ValueError, KeyError):
        return send_response(start_response, '400 Bad Request', {"error": "Invalid JSON or missing UUID"})

    if display_exists(uuid):
        global counter
        counter = (counter % len(videos))  # Cycle through the list
        video = videos[counter]
        counter += 1
    else:
        video = {"name": "Redirection", "url": "https://ds.manager.indigoingenium.ba/register_device"}

    return send_response(start_response, '200 OK', video, cors_headers)

def send_response(start_response, status, data, cors_headers):
    """Helper function to send JSON responses."""
    headers = [('Content-Type', 'application/json')] + cors_headers
    start_response(status, headers)
    return [json.dumps(data).encode()]
    