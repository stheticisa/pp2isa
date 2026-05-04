# connect.py — Returns a psycopg2 connection using config.py settings

import psycopg2
from config import DB_CONFIG


def get_connection():
    """Open and return a new database connection."""
    return psycopg2.connect(**DB_CONFIG)