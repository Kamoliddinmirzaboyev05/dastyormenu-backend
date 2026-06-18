#!/bin/bash
set -e

echo "Starting Dastyor Backend..."

# Wait for database to be ready
echo "Waiting for database..."
python << END
import sys
import time
import psycopg
from urllib.parse import urlparse
import os

max_tries = 30
tries = 0

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("DATABASE_URL not set, skipping database check")
    sys.exit(0)

# Parse DATABASE_URL
url = urlparse(DATABASE_URL)
conn_params = {
    'dbname': url.path[1:],
    'user': url.username,
    'password': url.password,
    'host': url.hostname,
    'port': url.port or 5432
}

while tries < max_tries:
    try:
        conn = psycopg.connect(**conn_params)
        conn.close()
        print("Database is ready!")
        break
    except Exception as e:
        tries += 1
        print(f"Database not ready yet (attempt {tries}/{max_tries}): {e}")
        if tries >= max_tries:
            print("Could not connect to database after maximum retries")
            sys.exit(1)
        time.sleep(2)
END

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating admin user..."
python manage.py create_admin

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application
