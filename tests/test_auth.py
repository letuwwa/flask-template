from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.extensions import cleanup_expired_tokens, db
from app.models import TokenBlocklist


REGISTER_PAYLOAD = {
    "email": "user@example.com",
    "username": "exampleuser",
    "first_name": "Example",
    "last_name": "User",
    "password": "password123456",
}


def register(client):
    response = client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    return response.get_json()["tokens"]


def test_logout_revokes_access_and_refresh_tokens(client):
    tokens = register(client)

    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    assert (
        client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/auth/refresh",
            headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
        ).status_code
        == 401
    )


def test_refresh_preserves_session_revocation(client):
    tokens = register(client)
    refreshed = client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    assert refreshed.status_code == 200
    access_token = refreshed.get_json()["access_token"]

    assert (
        client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
        ).status_code
        == 200
    )
    assert (
        client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        ).status_code
        == 401
    )


def test_cleanup_deletes_only_expired_revocations(app):
    now = datetime.now(timezone.utc)
    db.session.add_all(
        [
            TokenBlocklist(
                jti="expired",
                token_type="access",
                user_id="user",
                expires_at=now - timedelta(minutes=1),
            ),
            TokenBlocklist(
                jti="active",
                token_type="access",
                user_id="user",
                expires_at=now + timedelta(minutes=1),
            ),
        ]
    )
    db.session.commit()

    assert cleanup_expired_tokens() == 1
    remaining = db.session.scalars(select(TokenBlocklist)).one()
    assert remaining.jti == "active"


def test_login_is_rate_limited(client):
    responses = [
        client.post(
            "/auth/login",
            json={"identifier": "missing@example.com", "password": "wrong"},
        )
        for _ in range(11)
    ]

    assert all(response.status_code == 401 for response in responses[:10])
    assert responses[10].status_code == 429
    assert responses[10].get_json() == {"message": "Rate limit exceeded"}
