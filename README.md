# Shopping_List_Python

Simple Flask + SQLite shopping list application.

## Prerequisites

- Python 3.8+ installed (for non-Docker run)
- Docker Desktop (recommended)

## Run with Docker (recommended for resume/demo)

1. Install Docker Desktop.
2. From the project root, run:

   ```bash
   docker compose up --build
   ```

3. Open `http://localhost:8000`

Notes:
- The SQLite database is persisted in a Docker volume (`shopping_data`).
- Change `FLASK_SECRET_KEY` in `docker-compose.yml` for anything beyond local testing.
- Stop containers with `Ctrl+C`, or in another terminal: `docker compose down`.

## Run without Docker (local Python)

1. (Optional but recommended) Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database (this will create the `users`, `lists`, and `items` tables):

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

## Multiple lists

- Each user can have multiple named lists (for example: "Default", "Monthly", "Party").
- Use the list dropdown on the main page to switch between lists.
- Use the "Create List" form to add a new list; items you add will go into the currently selected list.
- Manage and delete lists at `/lists`.
