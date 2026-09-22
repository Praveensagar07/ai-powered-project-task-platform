"""Tests for database URL normalization and configuration validation."""

import pytest
from app.core.config import normalize_database_url, Settings


def test_normalize_postgres_scheme():
    """Verify postgres:// is normalized to postgresql+psycopg://."""
    raw = "postgres://fakeuser:fakepassword@localhost:5432/testdb"
    normalized = normalize_database_url(raw)
    assert normalized == "postgresql+psycopg://fakeuser:fakepassword@localhost:5432/testdb"


def test_normalize_postgresql_scheme():
    """Verify postgresql:// is normalized to postgresql+psycopg://."""
    raw = "postgresql://fakeuser:fakepassword@localhost:5432/testdb"
    normalized = normalize_database_url(raw)
    assert normalized == "postgresql+psycopg://fakeuser:fakepassword@localhost:5432/testdb"


def test_normalize_psycopg_scheme_idempotent():
    """Verify postgresql+psycopg:// is preserved without double manipulation."""
    raw = "postgresql+psycopg://fakeuser:fakepassword@localhost:5432/testdb"
    normalized = normalize_database_url(raw)
    assert normalized == "postgresql+psycopg://fakeuser:fakepassword@localhost:5432/testdb"


def test_normalize_strips_whitespace_and_quotes():
    """Verify leading/trailing whitespace and enclosing quotes are safely stripped."""
    cases = [
        "  postgres://user:pass@localhost:5432/db  \n",
        "\tpostgresql://user:pass@localhost:5432/db\t",
        '"postgres://user:pass@localhost:5432/db"',
        "'postgresql://user:pass@localhost:5432/db'",
        ' " postgresql+psycopg://user:pass@localhost:5432/db " ',
    ]
    expected = "postgresql+psycopg://user:pass@localhost:5432/db"
    for case in cases:
        assert normalize_database_url(case) == expected


def test_normalize_sqlite_and_none_fallback():
    """Verify SQLite schemes are preserved and None defaults to local SQLite file."""
    assert normalize_database_url(None) == "sqlite:///./app_data.db"
    assert normalize_database_url("sqlite:///./app_data.db") == "sqlite:///./app_data.db"
    assert normalize_database_url("sqlite:///:memory:") == "sqlite:///:memory:"


def test_malformed_database_url_raises_safe_error():
    """Verify malformed URLs raise safe ValueError without exposing sensitive details."""
    malformed_inputs = [
        "",
        "   ",
        "invalid-url-without-protocol",
        "http://database-server:5432/db",
        "mysql://user:pass@localhost/db",
    ]
    for bad_url in malformed_inputs:
        with pytest.raises(ValueError) as exc_info:
            normalize_database_url(bad_url)
        assert "Invalid DATABASE_URL configuration" in str(exc_info.value)
        # Verify no raw password or secret is printed in the error message
        assert "pass" not in str(exc_info.value).lower()
