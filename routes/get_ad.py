# get_ad.py

import os
import sys
import json
import time
import hmac
import hashlib

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

##################################

videos_for_signature = [
    {"name": "Advertisement", "filename": "BudLight.mp4"},
    {"name": "Advertisement", "filename": "BudLight.mp4"},
    {"name": "Advertisement", "filename": "BudLight.mp4"},
]

SECRET_KEY = "123"
VIDEO_DIR = "/home/indigoin/advertisement_storage/"

def generate_signed_url(filename, expiry=300):
    expires = int(time.time()) + expiry
    payload = f"{filename}|{expires}"
    signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"https://ds.manager.indigoingenium.ba/video?filename={filename}&expires={expires}&signature={signature}"


def verify_signature(filename, expires, signature):
    try:
        expires = int(expires)
    except ValueError:
        return False

    if time.time() > expires:
        return False  # Link expired

    payload = f"{filename}|{expires}"
    expected_signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return expected_signature == signature

@path_handler('/get_signed_ad')
def handle_get_signed_ad_request(environ, start_response, cors_headers):
    try:
        length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(length).decode('utf-8')
        data = json.loads(body)
        uuid = data.get("uuid")
    except (ValueError, KeyError):
        return send_response(start_response, '400 Bad Request', {"error": "Invalid JSON or missing UUID"})

    if display_exists(uuid):
        global counter
        counter = counter % len(videos)  # Cycle through videos
        video_info = videos_for_signature[counter]
        counter += 1

        # Generate a signed URL for secure access
        signed_url = generate_signed_url(video_info["filename"])
        video = {"name": video_info["name"], "url": signed_url}
    else:
        video = {"name": "Redirection", "url": "https://ds.manager.indigoingenium.ba/register_device"}

    return send_response(start_response, '200 OK', video, cors_headers)

# Register a new handler for video delivery
@path_handler('/video')
def handle_video_request(environ, start_response, cors_headers):
    query_string = environ.get('QUERY_STRING', '')

    # Extract parameters from the URL query string
    params = dict(param.split("=") for param in query_string.split("&") if "=" in param)
    filename = params.get("filename", "")
    expires = params.get("expires", "")
    signature = params.get("signature", "")

    # Validate parameters
    if not filename or not expires or not signature:
        return send_response(start_response, '400 Bad Request', {"error": "Missing parameters"}, cors_headers)

    # Verify signature and expiration
    if not verify_signature(filename, expires, signature):
        return send_response(start_response, '403 Forbidden', {"error": "Invalid or expired signature"}, cors_headers)

    # Full path to the requested video file
    filepath = os.path.join(VIDEO_DIR, filename)
    if not os.path.exists(filepath):
        return send_response(start_response, '404 Not Found', {"error": "Video not found"}, cors_headers)

    # Serve the video file using WSGI file wrapper
    file_size = os.path.getsize(filepath)
    headers = [
        ('Content-Type', 'video/mp4'),
        ('Content-Length', str(file_size)),
    ] + cors_headers

    start_response('200 OK', headers)
    
    return environ.get('wsgi.file_wrapper', open)(filepath, 'rb')

# Debug route
@path_handler('/list_videos')
def handle_list_videos(environ, start_response, cors_headers):
    """Logs and returns a list of available video files in VIDEO_DIR."""
    try:
        video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')]
        print(f"[LOG] Available videos: {video_files}")  # Log to console
    except Exception as e:
        print(f"[ERROR] Failed to list videos: {str(e)}")
        return send_response(start_response, '500 Internal Server Error', {"error": str(e)}, cors_headers)

    return send_response(start_response, '200 OK', {"videos": video_files}, cors_headers)

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
    