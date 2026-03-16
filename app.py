from flask import Flask, render_template, request, redirect, flash
import sqlite3
import os

DB_PATH = "shopping_list.db"


def get_all_items():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items ORDER BY id")
        items = cursor.fetchall()
    return items


def add_item(name: str, quantity: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, quantity) VALUES (?, ?)",
            (name, quantity),
        )
        conn.commit()


def toggle_item(item_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE items SET bought = NOT bought WHERE id = ?", (item_id,))
        conn.commit()


def delete_item(item_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()


app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-insecure-key-change-me")

# Home route: display shopping list
@app.route("/")
def home():
    shopping_list = get_all_items()
    return render_template("index.html", shopping_list=shopping_list)

# Add a new item
@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"].strip()
    quantity = request.form["quantity"]

    if not name:
        flash("Item name cannot be empty.", "error")
        return redirect("/")
    try:
        quantity = int(quantity)
        if quantity < 1:
            flash("Quantity must be at least 1.", "error")
            return redirect("/")
    except ValueError:
        flash("Quantity must be a number.", "error")
        return redirect("/")

    add_item(name, quantity)
    flash(f"Added {quantity} x {name}.", "success")
    return redirect("/")

#toggle bought status
@app.route("/toggle/<int:item_id>", methods=["POST"])
def toggle(item_id: int):
    toggle_item(item_id)
    return redirect("/")

# Delete and item
@app.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    delete_item(item_id)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=27016, debug=True)

