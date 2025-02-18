# db.py
import mysql.connector
from mysql.connector import pooling

# DB Config
DB_CONFIG = {
    'host': 'neutron.global.ba',
    'user': 'indigoin_digital_signage_manager_admin',
    'password': 'jedan0:digital_signage_manager',
    'database': 'indigoin_digital_signage_manager'
}

# Create a connection pool
connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=10, **DB_CONFIG)

def get_db_connection():
    """Get a connection from the pool."""
    try:
        connection = connection_pool.get_connection()
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        return None
