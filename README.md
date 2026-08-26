# Flask Template

Flask API starter with PostgreSQL, SQLAlchemy, Alembic migrations, JWT auth,
password hashing, refresh token support, logout token revocation, CORS, Docker,
and role-based admin protection.

## Stack

- Python 3.14.7
- Flask 3
- PostgreSQL 18.6
- SQLAlchemy and Flask-Migrate
- Flask-JWT-Extended
- Flask-Limiter
- Gunicorn
- uv
- Ruff

## Requirements

- Python 3.14+ (the container currently uses 3.14.7)
- uv
- PostgreSQL for local development, or Docker Compose for the full stack

## Local Setup

Install the locked dependencies:

```bash
uv sync --locked
```

Create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:<database-password>@localhost:5432/flask_template
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<database-password>
POSTGRES_PORT=5432
SECRET_KEY=<long-random-secret>
JWT_SECRET_KEY=<long-random-secret>
FLASK_DEBUG=false
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
RATELIMIT_STORAGE_URI=memory://
MAX_CONTENT_LENGTH=1048576
```

You can start from the checked-in example with `cp .env.example .env`.

Generate suitable local secrets:

```bash
openssl rand -hex 32
```

`DATABASE_URL` and a `SECRET_KEY` of at least 32 bytes are required outside
debug mode. Invalid boolean and integer configuration values stop startup with
a clear error instead of silently selecting a potentially unsafe default.
`JWT_SECRET_KEY`, when set, must also be at least 32 bytes; otherwise the app
uses `SECRET_KEY` for JWT signing. In debug mode only, the app can fall back to
development secrets.

## Database

Start the persistent PostgreSQL database on localhost:

```bash
docker compose up -d database --wait
```

The default host port is `127.0.0.1:5432`. If that port is occupied, set
`POSTGRES_PORT` in `.env` and use the same port in `DATABASE_URL`, for example:

```env
POSTGRES_PORT=5433
DATABASE_URL=postgresql://postgres:<database-password>@localhost:5433/flask_template
```

Database files are stored in the `postgres_data` named volume and survive
container recreation. PostgreSQL 18 uses `/var/lib/postgresql` as its persistent
volume root.

Alternatively, when using a system PostgreSQL server, create the database with
`createdb flask_template`.

Run migrations:

```bash
uv run flask --app run.py db upgrade
```

Create a migration after model changes:

```bash
uv run flask --app run.py db migrate -m "describe change"
```

## Run Locally

Start the development server:

```bash
uv run flask --app run.py run
```

The API runs at `http://localhost:5000`.

Check the health endpoint:

```bash
curl http://localhost:5000/
```

## Docker

Build and run the API with PostgreSQL:

```bash
docker compose up --build
```

The backend waits for PostgreSQL to become healthy, runs migrations, removes
expired revocation records, then starts Gunicorn as an unprivileged user on
`http://localhost:5000`.

Docker Compose starts a `backend` service and a `database` service. The backend
connects to PostgreSQL through the internal Compose hostname:

```env
DATABASE_URL=postgresql://<database-user>:<database-password>@database:5432/flask_template
```

The API and PostgreSQL ports bind only to `127.0.0.1`. Containers communicate
over the private Compose network while host-side tools can connect through the
configured `POSTGRES_PORT`.

Stop and remove the containers:

```bash
docker compose down
```

`docker compose down` preserves database data. Add `--volumes` only when you
intentionally want to delete the local database.

## Authentication

Register a user:

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "exampleuser",
    "first_name": "Example",
    "last_name": "User",
    "password": "password123456"
  }'
```

Login with an email, username, or `identifier`:

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "user@example.com",
    "password": "password123456"
  }'
```

Call an authenticated endpoint:

```bash
curl http://localhost:5000/auth/me \
  -H "Authorization: Bearer <access-token>"
```

Refresh an access token with a refresh token:

```bash
curl -X POST http://localhost:5000/auth/refresh \
  -H "Authorization: Bearer <refresh-token>"
```

Logout with either token. The complete access/refresh session is revoked:

```bash
curl -X POST http://localhost:5000/auth/logout \
  -H "Authorization: Bearer <access-or-refresh-token>"
```

## API Routes

```text
GET  /                 Health check
POST /auth/register    Create a regular user and return token pair
POST /auth/login       Return the user and token pair
POST /auth/refresh     Return a new access token from a refresh token
POST /auth/logout      Revoke the complete access/refresh token session
GET  /auth/me          Return the current user
GET  /auth/admin-only  Require an admin user
```

Newly registered users use the `regular` role. The base migration creates the
users and token blocklist tables; it does not seed an admin user.

Registration is limited to 5 requests per hour per client address, and login is
limited to 10 requests per minute. The in-memory limiter is suitable for the
default single-worker setup. Configure a shared Flask-Limiter storage URI, such
as Redis, before running multiple workers or application instances.

Request bodies are limited to 1 MiB by default (`MAX_CONTENT_LENGTH`), auth
responses disable caching, and API responses include MIME-sniffing protection.

Expired revocation records are cleaned hourly during authenticated traffic and
at container startup. They can also be removed manually:

```bash
uv run flask --app run.py cleanup-token-blocklist
```

## Registration Validation

```text
email       Valid email, max 255 characters
username    3-100 characters; lowercase letters, numbers, underscores, hyphens
password    12-128 characters
first_name  1-30 characters
last_name   1-30 characters
```

## Quality

Run Ruff:

```bash
uv run ruff format --check .
uv run ruff check .
```

Run the automated tests:

```bash
uv run pytest
```

Audit locked dependencies for published vulnerabilities:

```bash
uvx pip-audit
```

The lockfile was refreshed on 2026-08-26. The audit reported no known
vulnerabilities at that time.

## Project Layout

```text
run.py                         Flask entrypoint
app/__init__.py                App factory
app/config.py                  Environment-based config
app/extensions.py              Flask extension registration
app/routers/index.py           Health endpoint
app/routers/auth.py            Auth routes
app/models/base_model.py       Shared model fields
app/models/user.py             User model and roles
app/models/token_blocklist.py  Revoked JWT storage
migrations/versions/           Alembic migrations
docker/entrypoint.sh           Container DB wait and migration startup
docker-compose.yml             Backend and PostgreSQL services
Dockerfile                     Backend image
```
