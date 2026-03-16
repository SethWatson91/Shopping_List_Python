from flask import Flask, render_template, request, redirect, flash, session, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.getenv("DB_PATH", "shopping_list.db")


def get_all_items(user_id: int, list_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM items WHERE user_id = ? AND list_id = ? ORDER BY id",
            (user_id, list_id),
        )
        items = cursor.fetchall()
    return items


def add_item(user_id: int, list_id: int, name: str, quantity: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, quantity, user_id, list_id) VALUES (?, ?, ?, ?)",
            (name, quantity, user_id, list_id),
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
        user_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO lists (name, user_id) VALUES (?, ?)",
            ("Default", user_id),
        )
        conn.commit()


def get_lists_for_user(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM lists WHERE user_id = ? ORDER BY id",
            (user_id,),
        )
        return cursor.fetchall()


def get_list_for_user(user_id: int, list_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM lists WHERE id = ? AND user_id = ?",
            (list_id, user_id),
        )
        return cursor.fetchone()


def get_or_create_default_list(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM lists WHERE user_id = ? ORDER BY id LIMIT 1",
            (user_id,),
        )
        existing = cursor.fetchone()
        if existing:
            return existing
        cursor.execute(
            "INSERT INTO lists (name, user_id) VALUES (?, ?)",
            ("Default", user_id),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute(
            "SELECT * FROM lists WHERE id = ?",
            (new_id,),
        )
        return cursor.fetchone()


# Home route: display shopping list
@app.route("/")
@login_required
def home():
    user_id = session["user_id"]

    # Determine current list (query param can switch lists)
    list_id_param = request.args.get("list_id", type=int)
    if list_id_param:
        if get_list_for_user(user_id, list_id_param):
            session["current_list_id"] = list_id_param

    current_list = None
    if "current_list_id" in session:
        current_list = get_list_for_user(user_id, session["current_list_id"])

    if current_list is None:
        current_list = get_or_create_default_list(user_id)
        session["current_list_id"] = current_list["id"]

    all_lists = get_lists_for_user(user_id)
    shopping_list = get_all_items(user_id, current_list["id"])

    return render_template(
        "index.html",
        shopping_list=shopping_list,
        lists=all_lists,
        current_list=current_list,
    )


@app.route("/lists/create", methods=["POST"])
@login_required
def create_list():
    user_id = session["user_id"]
    name = request.form["list_name"].strip()
    if not name:
        flash("List name cannot be empty.", "error")
        return redirect(url_for("home"))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO lists (name, user_id) VALUES (?, ?)",
            (name, user_id),
        )
        conn.commit()
        new_id = cursor.lastrowid

    session["current_list_id"] = new_id
    flash(f"Created list '{name}'.", "success")
    return redirect(url_for("home"))


@app.route("/lists/select", methods=["POST"])
@login_required
def select_list():
    user_id = session["user_id"]
    try:
        list_id = int(request.form["list_id"])
    except (KeyError, ValueError):
        flash("Invalid list selection.", "error")
        return redirect(url_for("home"))

    if not get_list_for_user(user_id, list_id):
        flash("List not found.", "error")
        return redirect(url_for("home"))

    session["current_list_id"] = list_id
    return redirect(url_for("home"))


@app.route("/lists", methods=["GET"])
@login_required
def manage_lists():
    user_id = session["user_id"]
    all_lists = get_lists_for_user(user_id)

    current_list = None
    if "current_list_id" in session:
        current_list = get_list_for_user(user_id, session["current_list_id"])

    return render_template(
        "lists.html",
        lists=all_lists,
        current_list=current_list,
    )


@app.route("/lists/delete/<int:list_id>", methods=["POST"])
@login_required
def delete_list(list_id: int):
    user_id = session["user_id"]

    # Ensure list belongs to user
    target = get_list_for_user(user_id, list_id)
    if target is None:
        flash("List not found.", "error")
        return redirect(url_for("manage_lists"))

    all_lists = get_lists_for_user(user_id)
    if len(all_lists) <= 1:
        flash("You must have at least one list.", "error")
        return redirect(url_for("manage_lists"))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Delete items first (SQLite FK constraints may not be enabled)
        cursor.execute(
            "DELETE FROM items WHERE user_id = ? AND list_id = ?",
            (user_id, list_id),
        )
        cursor.execute(
            "DELETE FROM lists WHERE id = ? AND user_id = ?",
            (list_id, user_id),
        )
        conn.commit()

    # If we deleted the current list, switch to another list
    if session.get("current_list_id") == list_id:
        remaining = get_lists_for_user(user_id)
        if remaining:
            session["current_list_id"] = remaining[0]["id"]
        else:
            session.pop("current_list_id", None)

    flash(f"Deleted list '{target['name']}'.", "success")
    return redirect(url_for("manage_lists"))


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

        default_list = get_or_create_default_list(user["id"])
        session["current_list_id"] = default_list["id"]
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
    current_list_id = session.get("current_list_id")
    if current_list_id is None:
        current_list = get_or_create_default_list(user_id)
        current_list_id = current_list["id"]
        session["current_list_id"] = current_list_id
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

    add_item(user_id, current_list_id, name, quantity)
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
