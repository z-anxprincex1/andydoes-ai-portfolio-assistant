import os
import psycopg

DB = os.environ["DATABASE_URL"]

def get_conn():
    return psycopg.connect(DB)