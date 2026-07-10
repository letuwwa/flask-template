# Flask Template

Flask starter with PostgreSQL, SQLAlchemy, Alembic migrations, JWT auth,
password hashing, refresh/logout token handling, and role-based admin
protection.

## Requirements

- Python 3.14+
- PostgreSQL
- uv

## Setup

Install dependencies:
```bash
uv sync
```

Create local env file:
```bash
cp .env.example .env
```

Generate a JWT secret and put it in `.env`:
```bash
openssl rand -hex 32
```

Required env values:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/flask_template
SECRET_KEY=<long-random-secret>
JWT_SECRET_KEY=<long-random-secret>
FLASK_DEBUG=false
CORS_ORIGINS=*
```

## Database

Create the database if needed:
```bash
createdb flask_template
```

Run migrations:
```bash
uv run flask db upgrade
```

Create a migration after model changes:
```bash
uv run flask db migrate -m "describe change"
```

## Run

```bash
uv run flask --app run.py run
```

The API is served at `http://localhost:5000`.

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

Login with an email or username:
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "user@example.com",
    "password": "password123456"
  }'
```

Use token:
```bash
curl http://localhost:5000/auth/me \
  -H "Authorization: Bearer <jwt-token>"
```

## Auth Endpoints

```text
POST /auth/register      Create a regular user and return token pair
POST /auth/login         Return the user and token pair
POST /auth/refresh       Return a new access token from a refresh token
POST /auth/logout        Revoke the presented access or refresh token
GET  /auth/me            Return the current user
GET  /auth/admin-only    Require an admin user
```

Newly registered users use the `regular` role. The base migration creates the
users and token blocklist tables; it does not seed an admin user.

## Quality

Run Ruff:
```bash
uv run ruff check .
```

## Key Files

```text
run.py                         Flask entrypoint
app/__init__.py                App factory
app/routers/auth.py            Auth routes
app/config.py                  Env settings
app/models/user.py             User model and roles
app/models/token_blocklist.py  Revoked token model
migrations/versions/           DB migrations
```

## Status

Done:
- Clean project structure
- Env variables support
- DB base model and migrations setup
- JWT auth with refresh/logout and role-based admin protection

To do:
- Docker pre-settings
- Docs
