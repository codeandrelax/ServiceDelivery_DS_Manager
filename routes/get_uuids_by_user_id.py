# get_uuids_by_user_id.py

from app import path_handlers, path_handler
from db import get_db_connection
import json

def get_uuids_by_user_id(user_id):
    connection = get_db_connection()
    if connection is None:
        return False  # Avoid errors if the connection fails
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT uuid 
                FROM display_user 
                WHERE user_id = %s
            """, (user_id,))
            return [row[0] for row in cursor.fetchall()]
    finally:
        connection.close() 

@path_handler('/get_uuids_by_user_id')
def handle_get_uuids_by_user_id(environ, start_response, cors_headers):
    """Handles the '/get_uuids_by_user_id' request by retrieving UUIDs for the given user_id."""
    try:
        # Read and parse the incoming JSON data
        length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(length).decode('utf-8')
        data = json.loads(body)
        user_id = int(data.get("user_id"))  # Ensure user_id is an integer
    except (ValueError, KeyError):
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('400 Bad Request', headers)
        print("Error: Invalid JSON or missing user_id")
        return [b'{"error": "Invalid JSON or missing user_id"}']

    # Retrieve UUIDs for the given user_id
    uuids = get_uuids_by_user_id(user_id)

    # Check if UUIDs were found and respond accordingly
    if uuids:
        response_data = {"uuids": uuids}
        print(f"Response data: {json.dumps(response_data)}")  # Console log
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('200 OK', headers)
        return [json.dumps(response_data).encode()]
    else:
        response_data = {"error": "No UUIDs found for the given user_id"}
        print(f"Response data: {json.dumps(response_data)}")  # Console log
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('404 Not Found', headers)
        return [json.dumps(response_data).encode()]
        