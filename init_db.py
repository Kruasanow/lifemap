import os
import psycopg2
from sensetive_data import username, password

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="flask_db",
        user=username,
        password=password
    )

conn = get_db_connection()
# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
# cur.execute('DROP TABLE IF EXISTS events;')
try:
        cur.execute('CREATE TABLE events (id SERIAL PRIMARY KEY,'
                        'coords TEXT NOT NULL,'
                        'title TEXT NOT NULL,'
                        'short_description TEXT NOT NULL,'
                        'full_description TEXT,'
                        'photo TEXT,'
                        'gallery_photos TEXT[],'
                        'rating INTEGER NOT NULL,'
                        'owner_name TEXT NOT NULL,'
                        'date_added date DEFAULT CURRENT_TIMESTAMP);'
                )
except Exception:
      pass
# cur.execute('DROP TABLE IF EXISTS users;')
try:
        cur.execute('CREATE TABLE users (id serial PRIMARY KEY,'
                                        'username TEXT NOT NULL,'
                                        'fname TEXT NOT NULL,'
                                        'sname TEXT NOT NULL,'
                                        'email TEXT NOT NULL,'
                                        'admin INTEGER NOT NULL,'
                                        'passwd TEXT NOT NULL,'
                                        'date_added date DEFAULT CURRENT_TIMESTAMP);'
                                        )
except Exception:
       pass
conn.commit()

cur.close()
conn.close()