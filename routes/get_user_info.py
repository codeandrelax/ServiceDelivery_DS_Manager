# get_user_info.py

from app import path_handlers, path_handler
from db import get_db_connection
import json

def get_user_info(email):
    """Fetch user information from the database based on email."""
    connection = get_db_connection()
    if connection is None:
        return False  # Avoid errors if the connection fails
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, email, username, status, verified, resettable, roles_mask, 
                       registered, last_login, force_logout, phone_number 
                FROM users 
                WHERE email = %s
            """, (email,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "username": row[2],
                    "status": row[3],
                    "verified": row[4],
                    "resettable": row[5],
                    "roles_mask": row[6],
                    "registered": row[7],
                    "last_login": row[8],
                    "force_logout": row[9],
                    "phone_number": row[10]
                }
            else:
                return None  # User not found
    finally:
        connection.close()

@path_handler('/get_user_info')
def handle_get_user_info(environ, start_response, cors_headers):
    """Handles the '/get_user_info' request by retrieving user details for the given email."""
    try:
        # Read and parse the incoming JSON data
        length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(length).decode('utf-8')
        data = json.loads(body)
        email = data.get("email")  # Extract email from JSON
        if not email:
            raise ValueError("Missing email")
    except (ValueError, KeyError, json.JSONDecodeError):
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('400 Bad Request', headers)
        return [b'{"error": "Invalid JSON or missing email"}']

    # Retrieve user info for the given email
    user_info = get_user_info(email)

    # Check if user info was found and respond accordingly
    if user_info:
        response_data = json.dumps(user_info)
        print(f"Response data: {response_data}")  # Console log
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('200 OK', headers)
        return [response_data.encode()]
    else:
        response_data = json.dumps({"error": "User not found"})
        print(f"Response data: {response_data}")  # Console log
        headers = [('Content-Type', 'application/json')] + cors_headers
        start_response('404 Not Found', headers)
        return [response_data.encode()]
