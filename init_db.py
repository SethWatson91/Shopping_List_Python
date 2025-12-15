import sqlite3

# Connect to the database (creates file if it doesn't exist)
conn = sqlite3.connect("shopping_list.db")
cursor = conn.cursor()

# Create the items table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    bought BOOLEAN NOT NULL DEFAULT 0
)
""")

conn.commit()
conn.close()

print("Database initialized!")