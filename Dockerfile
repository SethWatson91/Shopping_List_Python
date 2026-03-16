FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

ENV DB_PATH=/data/shopping_list.db

RUN mkdir -p /data

EXPOSE 8000

CMD ["sh", "-c", "python init_db.py && gunicorn -b 0.0.0.0:8000 wsgi:app"]

