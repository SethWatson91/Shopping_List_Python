# Shopping_List_Python

Simple Flask + SQLite shopping list application.

## Prerequisites

- Python 3.8+ installed

## Setup

1. (Optional but recommended) Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

2. Install dependencies:

   ```bash
   pip install flask
   ```

3. Initialize the database (this will create the `users` and `items` tables):

   ```bash
   python init_db.py
   ```

4. (Optional) Set a secure secret key for sessions:

   ```bash
   set FLASK_SECRET_KEY=some-long-random-value  # PowerShell: $env:FLASK_SECRET_KEY="..."
   ```

5. Run the app:

   ```bash
   python app.py
   ```

Then open `http://localhost:27016` in your browser.

## Users

- Go to `/register` to create an account.
- Log in via `/login`.
- Each user has their own shopping list; items are stored per-user.
