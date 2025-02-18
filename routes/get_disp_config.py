# get_display_config.py

from app import path_handlers, path_handler
from db import get_db_connection
import json

def get_display_config(uuid):
    """Fetch display configuration from the database based on uuid."""
    connection = get_db_connection()
    if connection is None:
        return False  # Avoid errors if the connection fails
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT brightness, contrast, saturation, hue, blur, grayscale, 
                       invert, sepia, opacity, uuid
                FROM display_config
                WHERE uuid = %s
            """, (uuid,))
            row = cursor.fetchone()
            if row:
                return {
                    "brightness": row[0],
                    "contrast": row[1],
                    "saturation": row[2],
                    "hue": row[3],
                    "blur": row[4],
                    "grayscale": row[5],
                    "invert": row[6],
                    "sepia": row[7],
                    "opacity": row[8],
                    "uuid": row[9]
                }
            else:
                return None  # No configuration found for the given uuid
    finally:
        connection.close()

@path_handler('/get_display_config')
def handle_get_display_config_request(environ, start_response, cors_headers):
    """Handles the '/get_display_config' request by retrieving display configuration for the given uuid."""
    try:
        # Read and parse the incoming JSON data
        length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(length).decode('utf-8')
        data = json.loads(body)
        uuid = data.get("uuid")  # Extract uuid from JSON
        if not uuid:
            raise ValueError("Missing uuid")
    except (ValueError, KeyError, json.JSONDecodeError):
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('400 Bad Request', headers)
        return [b'{"error": "Invalid JSON or missing uuid"}']

    # Retrieve display config for the given uuid
    display_config = get_display_config(uuid)

    # Check if display config was found and respond accordingly
    if display_config:
        response_data = json.dumps(display_config)
        print(f"Response data: {response_data}")  # Console log
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('200 OK', headers)
        return [response_data.encode()]
    else:
        response_data = json.dumps({"error": "Display config not found"})
        print(f"Response data: {response_data}")  # Console log
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('404 Not Found', headers)
        return [response_data.encode()]
