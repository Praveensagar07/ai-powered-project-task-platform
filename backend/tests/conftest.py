"""Pytest test configuration, database fixtures, and authenticated test clients."""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.main import app
from app.models.project import Project
from app.models.task import Task
from app.models.user import User

# In-memory SQLite engine isolated per test session
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db():
    """Create fresh database tables for each test function and teardown afterwards."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db) -> User:
    """Create a primary test user."""
    user = User(
        name="Test Engineer",
        email="engineer@example.com",
        password_hash=hash_password("StrongPassword123!"),
        role="Senior Full Stack Engineer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def second_user(db) -> User:
    """Create a secondary test user for authorization tests."""
    user = User(
        name="Second Engineer",
        email="second@example.com",
        password_hash=hash_password("AnotherPassword123!"),
        role="Product Designer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user) -> dict:
    """Provide authorization headers for test_user."""
    token = create_access_token({"sub": test_user.id, "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_auth_headers(second_user) -> dict:
    """Provide authorization headers for second_user."""
    token = create_access_token({"sub": second_user.id, "email": second_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_project(db, test_user) -> Project:
    """Create a test project owned by test_user."""
    project = Project(
        name="Test Automation Platform",
        description="End-to-end integration test initiative",
        status="active",
        priority="high",
        category="Engineering",
        owner_id=test_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
