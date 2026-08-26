#!/bin/sh
set -e

if [ -n "${DATABASE_URL:-}" ]; then
    python - <<'PY'
import os
import time

import psycopg2

database_url = os.environ["DATABASE_URL"]
deadline = time.time() + int(os.getenv("DATABASE_WAIT_TIMEOUT", "60"))

while True:
    try:
        connection = psycopg2.connect(database_url)
        connection.close()
        break
    except psycopg2.OperationalError:
        if time.time() >= deadline:
            raise
        print("Waiting for database...")
        time.sleep(2)
PY

    flask --app run.py db upgrade
    flask --app run.py cleanup-token-blocklist
fi

exec "$@"
