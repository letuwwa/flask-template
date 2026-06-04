# To Do
1. JWT Auth
2. User jwt-protected endpoint
3. User not-protected endpoint
5. Docker pre-settings 
6. Docs

## Environment

Runtime configuration is loaded from environment variables. For local development,
copy `.env.example` to `.env` and adjust the values.

Required variables:

- `DATABASE_URL`: SQLAlchemy database URL.

Optional variables:

- `SECRET_KEY`: Flask secret key. Use a secure random value outside local development.
- `FLASK_DEBUG`: Enables Flask debug mode when set to `true`, `1`, `yes`, or `on`.
- `CORS_ORIGINS`: `*` or a comma-separated list of allowed origins.
