"""Authentication and authorization tests."""

import pytest
from app.models.user import User


def test_register_success(client, db):
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "Password123!",
        "role": "Frontend Architect",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == "jane@example.com"
    assert data["user"]["name"] == "Jane Doe"
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]

    # Verify password was hashed in database
    user_in_db = db.query(User).filter(User.email == "jane@example.com").first()
    assert user_in_db is not None
    assert user_in_db.password_hash != "Password123!"
    assert user_in_db.password_hash.startswith("pbkdf2_sha256$")


def test_register_duplicate_email(client, test_user):
    payload = {
        "name": "Duplicate User",
        "email": test_user.email,
        "password": "Password123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert "already exists" in data["error"]["message"].lower()


def test_register_invalid_short_password(client):
    payload = {
        "name": "Short Pass",
        "email": "short@example.com",
        "password": "123",  # under 6 chars
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "StrongPassword123!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"]["access_token"]
    assert data["user"]["email"] == test_user.email


def test_login_wrong_password(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "WrongPassword999!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert "invalid email or password" in data["error"]["message"].lower()


def test_login_nonexistent_user(client):
    payload = {
        "email": "ghost@example.com",
        "password": "Password123!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401


def test_get_me_authenticated(client, auth_headers, test_user):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


def test_get_me_unauthenticated(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_logout_authenticated(client, auth_headers):
    response = client.post("/api/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    assert "logged out" in response.json()["message"].lower()
