
from db import get_db_connection

def display_exists(uuid):
    connection = get_db_connection()
    if connection is None:
        return False  # Avoid errors if the connection fails
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM displays WHERE uuid = %s LIMIT 1", (uuid,))
            return cursor.fetchone() is not None  # More readable
    finally:
        connection.close()
        