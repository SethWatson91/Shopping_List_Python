import sqlite3
import os
from pathlib import Path


DB_PATH = os.getenv("DB_PATH", "shopping_list.db")

db_file = Path(DB_PATH)
if db_file.parent and str(db_file.parent) not in (".", ""):
    db_file.parent.mkdir(parents=True, exist_ok=True)

# Connect to the database (creates file if it doesn't exist)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create the users table if it doesn't exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
    """
)

# Create the lists table if it doesn't exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS lists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """
)

# Create the items table if it doesn't exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        bought BOOLEAN NOT NULL DEFAULT 0,
        user_id INTEGER NOT NULL,
        list_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (list_id) REFERENCES lists (id)
    )
    """
)

conn.commit()
conn.close()

print("Database initialized!")