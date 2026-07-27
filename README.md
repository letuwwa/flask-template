# Flask Template

Flask API starter with PostgreSQL, SQLAlchemy, Alembic migrations, JWT auth,
password hashing, refresh token support, logout token revocation, CORS, Docker,
and role-based admin protection.

## Stack

- Python 3.14+
- Flask 3
- PostgreSQL 17
- SQLAlchemy and Flask-Migrate
- Flask-JWT-Extended
- uv
- Ruff

## Requirements

- Python 3.14+
- uv
- PostgreSQL for local development, or Docker Compose for the full stack

## Local Setup

Install dependencies:

```bash
uv sync
```

Create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flask_template
SECRET_KEY=<long-random-secret>
JWT_SECRET_KEY=<long-random-secret>
FLASK_DEBUG=true
CORS_ORIGINS=*
```

Generate suitable local secrets:

```bash
openssl rand -hex 32
```

`DATABASE_URL` is required. `JWT_SECRET_KEY` is required unless `SECRET_KEY` is
at least 32 bytes. In debug mode only, the app can fall back to development
secrets.

## Database

Create the local database if it does not exist:

```bash
createdb flask_template
```

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

The backend waits for PostgreSQL to become healthy, runs migrations, then starts
Flask on `http://localhost:5000`.

Docker Compose starts a `backend` service and a `database` service. The backend
connects to PostgreSQL through the internal Compose hostname:

```env
DATABASE_URL=postgresql://postgres:postgres@database:5432/flask_template
```

PostgreSQL is exposed to the host on port `5432`.

Database data is not mounted to a named volume, so recreating the PostgreSQL
container resets local Docker database state.

Stop and remove the containers:

```bash
docker compose down
```

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

Logout by revoking the presented access or refresh token:

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
POST /auth/logout      Revoke the presented access or refresh token
GET  /auth/me          Return the current user
GET  /auth/admin-only  Require an admin user
```

Newly registered users use the `regular` role. The base migration creates the
users and token blocklist tables; it does not seed an admin user.

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
uv run ruff check .
```

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
