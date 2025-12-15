import sqlite3

conn = sqlite3.connect("shopping_list.db")
cursor = conn.cursor()

#insert and item
cursor.execute("INSERT INTO items (name, quantity) VALUES (?, ?)", ("Milk", 2))
conn.commit()

#query all items
cursor.execute("SELECT * FROM items")
items = cursor.fetchall()
print("Items in DB:", items)

#toggle bought status
item_id = items[0][0]
cursor.execute("UPDATE items SET bought = NOT bought WHERE id = ?", (item_id,))
conn.commit()

#query again to see change
cursor.execute("SELECT * FROM items")
print("After toggle:", cursor.fetchall())

# Delete the item
cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
conn.commit()

# Final query
cursor.execute("SELECT * FROM items")
print("After delete:", cursor.fetchall())

conn.close()