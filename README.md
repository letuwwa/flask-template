# Flask Template

## Auth

JWT auth is available under `/auth`.

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`

Use `Authorization: Bearer <token>` for protected endpoints. Login accepts
`identifier`, `email`, or `username` plus `password`.

Set `JWT_SECRET_KEY` in production. It must be at least 32 bytes, unless
`SECRET_KEY` is already at least 32 bytes.

## To Do

1. Docker pre-settings
2. Docs

## What's done

1. Clean project structure
2. Env variables support
3. DB base model and migrations setup
4. JWT auth
