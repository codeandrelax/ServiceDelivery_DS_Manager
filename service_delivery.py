# service_delivery.py

from app import path_handlers, path_handler

from common_funcs import *

import os
import sys
import json
from datetime import datetime

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

def read_html_template(filename):
    """Reads an HTML file from the templates directory."""
    filepath = os.path.join(TEMPLATE_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "<h1>404 - Template Not Found</h1>"

def send_html_response(start_response, status, content, cors_headers):
    """Helper function to send HTML responses."""
    headers = [('Content-Type', 'text/html')] + cors_headers
    start_response(status, headers)
    return [content.encode()]  
        
@path_handler('/origin')
def handle_origin_request(environ, start_response, cors_headers):
    """Handles requests to the '/origin' endpoint by returning an HTML page."""
    html_content = read_html_template("origin.html")
    return send_html_response(start_response, '200 OK', html_content, cors_headers)
    
@path_handler('/register_device')
def handle_register_device_request(environ, start_response, cors_headers):
    """Handles requests to the '/register_device' endpoint by returning the register_device.html page."""
    html_content = read_html_template("register_device.html")
    return send_html_response(start_response, '200 OK', html_content, cors_headers)
    
@path_handler('/show_uuid')
def handle_show_uuid(environ, start_response, cors_headers):
    """Handles the '/show_uuid' request by returning the HTML template with the UUID information."""
    html_content = read_html_template("show_uuid.html")
    headers = [('Content-Type', 'text/html')] + cors_headers
    start_response('200 OK', headers)
    return [html_content.encode()]
    
def send_js_response(start_response, status, content, cors_headers):
    """Helper function to send JavaScript responses."""
    headers = [('Content-Type', 'application/javascript')] + cors_headers
    start_response(status, headers)
    return [content.encode('utf-8')]  # Return the JavaScript content encoded in UTF-8

def read_js_file(filename):
    """Reads a JavaScript file from the templates directory."""
    filepath = os.path.join(TEMPLATE_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "// 404 - JavaScript File Not Found"

@path_handler('/sw.js')
def handle_sw_js_request(environ, start_response, cors_headers):
    """Handles requests to the '/sw.js' endpoint by returning the sw.js file."""
    print("Handling /sw.js request")  # Debug print to confirm handler is triggered
    js_content = read_js_file("sw.js")
    return send_js_response(start_response, '200 OK', js_content, cors_headers)
    
@path_handler('/report_focus')
def handle_report_focus(environ, start_response, cors_headers):
    """Handles the '/report_focus' request by processing focus report data."""
    try:
        # Step 1: Read and parse the incoming JSON data
        length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(length).decode('utf-8')
        data = json.loads(body)

        uuid = data.get("uuid")
        date_str = data.get("date")
        is_in_focus = data.get("is_in_focus")
        
        try:
            # Convert the string '2025-02-12T15:00:00Z' to '2025-02-12 15:00:00'
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00")).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            headers = [('Content-Type', 'application/json')] + cors_headers
            start_response('400 Bad Request', headers)
            return [b'{"error": "Invalid date format"}']

        # Step 2: Validate the input data
        if not uuid or not date or is_in_focus is None:
            headers = [('Content-Type', 'application/json')] + cors_headers
            start_response('400 Bad Request', headers)
            return [b'{"error": "Missing required fields"}']

        # Step 3: Check if the display with the given UUID exists
        if not display_exists(uuid):
            headers = [('Content-Type', 'application/json')] + cors_headers
            start_response('404 Not Found', headers)
            return [b'{"error": "Display not found"}']

        # Step 4: Insert data into the display_focus table
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            query = """
                INSERT INTO display_focus (uuid, is_in_focus, focus_change_date)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (uuid, is_in_focus, date))
            connection.commit()
            cursor.close()
            connection.close()

            # Step 5: Respond with success message
            headers = [('Content-Type', 'application/json')] + cors_headers
            start_response('200 OK', headers)
            response_data = {"message": "Focus report successfully inserted"}
            return [json.dumps(response_data).encode()]

    except (ValueError, KeyError, json.JSONDecodeError) as e:
        # Catch errors related to the data and provide a response
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('400 Bad Request', headers)
        return [b'{"error": "Invalid JSON data"}']
    except Exception as e:
        # General error handling to catch unforeseen issues
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('500 Internal Server Error', headers)
        return [json.dumps({"error": f"Internal server error: {str(e)}"}).encode()]

@path_handler('/check_if_registered')
def handle_check_if_registered(environ, start_response, cors_headers):
    """Handles the '/check_if_registered' request by processing the UUID and returning a redirect or error response."""
    try:
        # Read the body of the request to get the UUID
        length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(length).decode('utf-8')
        data = json.loads(body)
        uuid = data.get("uuid")
    except (ValueError, KeyError):
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('400 Bad Request', headers)
        return [b'{"error": "Invalid JSON or missing UUID"}']

    # Check if the display exists using the display_exists function
    if display_exists(uuid):
        response_data = {
            "Redirect": "https://ds.manager.indigoingenium.ba/origin"
        }
    else:
        response_data = {
            "Non-redirect": "Device not registered"
        }

    headers = [('Content-Type', 'application/json')] + cors_headers
    start_response('200 OK', headers)
    response = json.dumps(response_data)
    return [response.encode()]
    