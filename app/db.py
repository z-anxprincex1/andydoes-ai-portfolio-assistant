import os
import psycopg
from contextlib import contextmanager

DB = os.environ["DATABASE_URL"]

@contextmanager
def get_conn():
    conn = psycopg.connect(DB, sslmode="require")
    try:
        yield conn
    finally:
        conn.close()
