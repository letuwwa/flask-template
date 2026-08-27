from unittest.mock import Mock

import psycopg2
import pytest

from docker import wait_for_db


def test_database_wait_closes_successful_connection(monkeypatch):
    connection = Mock()
    connect = Mock(return_value=connection)
    monkeypatch.setattr(wait_for_db.psycopg2, "connect", connect)

    wait_for_db.wait_for_database("postgresql://localhost/test")

    connection.close.assert_called_once_with()
    assert 2 <= connect.call_args.kwargs["connect_timeout"] <= 5


def test_database_wait_retries_and_obeys_deadline(monkeypatch):
    clock = [0.0]
    connect = Mock(side_effect=psycopg2.OperationalError("unavailable"))
    monkeypatch.setattr(wait_for_db.psycopg2, "connect", connect)
    monkeypatch.setattr(wait_for_db.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        wait_for_db.time,
        "sleep",
        lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )

    with pytest.raises(psycopg2.OperationalError, match="unavailable"):
        wait_for_db.wait_for_database("postgresql://localhost/test", timeout=3)

    assert clock[0] == 3
    assert connect.call_count == 3
    assert all(
        2 <= call.kwargs["connect_timeout"] <= 3 for call in connect.call_args_list
    )


@pytest.mark.parametrize("timeout", [0, -1])
def test_database_wait_rejects_nonpositive_timeout(timeout):
    with pytest.raises(ValueError, match="at least 1"):
        wait_for_db.wait_for_database("postgresql://localhost/test", timeout=timeout)


def test_database_wait_does_not_retry_invalid_dsn(monkeypatch):
    connect = Mock(side_effect=psycopg2.ProgrammingError("invalid DSN"))
    monkeypatch.setattr(wait_for_db.psycopg2, "connect", connect)

    with pytest.raises(psycopg2.ProgrammingError):
        wait_for_db.wait_for_database("invalid")
    connect.assert_called_once()
