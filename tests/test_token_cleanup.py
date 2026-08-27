from unittest.mock import Mock

import pytest
from sqlalchemy.exc import OperationalError

from app import extensions


def test_cleanup_failure_rolls_back_and_releases_lock(app, monkeypatch):
    cleanup = Mock(side_effect=OperationalError("DELETE", {}, Exception("unavailable")))
    rollback = Mock(wraps=extensions.db.session.rollback)
    monkeypatch.setattr(extensions, "cleanup_expired_tokens", cleanup)
    monkeypatch.setattr(extensions.db.session, "rollback", rollback)

    with pytest.raises(OperationalError):
        extensions._cleanup_expired_tokens_if_due()
    rollback.assert_called_once()
    assert "token_blocklist_cleanup_after" not in app.extensions

    cleanup.side_effect = None
    cleanup.return_value = 0
    extensions._cleanup_expired_tokens_if_due()
    assert cleanup.call_count == 2
    extensions._cleanup_expired_tokens_if_due()
    assert cleanup.call_count == 2


def test_cleanup_cli_reports_result(app):
    result = app.test_cli_runner().invoke(args=["cleanup-token-blocklist"])
    assert result.exit_code == 0
    assert "Deleted 0 expired token revocation record(s)." in result.output
