import sqlite3
from pathlib import Path
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def initialize_db(db_name):
    already_initialized = False
    db_path = Path(db_name)
    if db_path.is_file():
        already_initialized = True
    else:
        conn, cursor = get_db_connection(db_name)
        with open(os.path.join(BASE_DIR, 'sql_migrations.sql')) as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)
            conn.commit()

    return already_initialized


def get_db_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()