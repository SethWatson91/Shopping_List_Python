from flask import Flask, render_template, request, redirect, flash, session, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "shopping_list.db"


def get_all_items(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM items WHERE user_id = ? ORDER BY id",
            (user_id,),
        )
        items = cursor.fetchall()
    return items


def add_item(user_id: int, name: str, quantity: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, quantity, user_id) VALUES (?, ?, ?)",
            (name, quantity, user_id),
        )
        conn.commit()


def toggle_item(user_id: int, item_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE items SET bought = NOT bought WHERE id = ? AND user_id = ?",
            (item_id, user_id),
        )
        conn.commit()


def delete_item(user_id: int, item_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM items WHERE id = ? AND user_id = ?",
            (item_id, user_id),
        )
        conn.commit()


app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-insecure-key-change-me")


def login_required(view_func):
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    wrapped.__name__ = view_func.__name__
    return wrapped


def get_user_by_username(username: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()


def create_user(username: str, password: str):
    password_hash = generate_password_hash(password)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()


# Home route: display shopping list
@app.route("/")
@login_required
def home():
    shopping_list = get_all_items(session["user_id"])
    return render_template("index.html", shopping_list=shopping_list)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        if get_user_by_username(username) is not None:
            flash("Username is already taken.", "error")
            return redirect(url_for("register"))

        create_user(username, password)
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = get_user_by_username(username)
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash("Logged in successfully.", "success")
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# Add a new item
@app.route("/add", methods=["POST"])
@login_required
def add():
    user_id = session["user_id"]
    name = request.form["name"].strip()
    quantity = request.form["quantity"]

    if not name:
        flash("Item name cannot be empty.", "error")
        return redirect(url_for("home"))
    try:
        quantity = int(quantity)
        if quantity < 1:
            flash("Quantity must be at least 1.", "error")
            return redirect(url_for("home"))
    except ValueError:
        flash("Quantity must be a number.", "error")
        return redirect(url_for("home"))

    add_item(user_id, name, quantity)
    flash(f"Added {quantity} x {name}.", "success")
    return redirect(url_for("home"))


#toggle bought status
@app.route("/toggle/<int:item_id>", methods=["POST"])
@login_required
def toggle(item_id: int):
    toggle_item(session["user_id"], item_id)
    return redirect(url_for("home"))


# Delete an item
@app.route("/delete/<int:item_id>", methods=["POST"])
@login_required
def delete(item_id):
    delete_item(session["user_id"], item_id)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=27016, debug=True)
