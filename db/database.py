import sqlite3
from pathlib import Path

DB_PATH = Path("data/sportpartner.sqlite")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
