"""Tests for API version compatibility across both /api and /api/v1 prefixes."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize("prefix", ["/api", "/api/v1"])
def test_root_endpoint_versioning(client: TestClient, prefix: str):
    """Test that the system root responds with API prefixes."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["api"] == "/api"
    assert data["api_v1"] == "/api/v1"


@pytest.mark.parametrize("prefix", ["/api", "/api/v1"])
def test_auth_me_both_prefixes(client: TestClient, auth_headers: dict, test_user, prefix: str):
    """Test /auth/me under both /api and /api/v1."""
    response = client.get(f"{prefix}/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name


@pytest.mark.parametrize("prefix", ["/api", "/api/v1"])
def test_projects_crud_both_prefixes(client: TestClient, auth_headers: dict, prefix: str):
    """Test project list and create under both /api and /api/v1."""
    # Create project
    create_resp = client.post(
        f"{prefix}/projects",
        headers=auth_headers,
        json={
            "name": f"Prefix Test Project {prefix}",
            "description": "Testing prefix routing",
            "priority": "high",
            "category": "Engineering",
        },
    )
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]

    # List projects
    list_resp = client.get(f"{prefix}/projects", headers=auth_headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert isinstance(items, list)
    assert any(p["id"] == project_id for p in items)

    # Get single project
    get_resp = client.get(f"{prefix}/projects/{project_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == f"Prefix Test Project {prefix}"


@pytest.mark.parametrize("prefix", ["/api", "/api/v1"])
def test_tasks_crud_both_prefixes(client: TestClient, auth_headers: dict, test_project, prefix: str):
    """Test task operations under both /api and /api/v1."""
    # Create task
    create_resp = client.post(
        f"{prefix}/tasks",
        headers=auth_headers,
        json={
            "title": f"Prefix Test Task {prefix}",
            "description": "Task created via prefix test",
            "project_id": test_project.id,
            "status": "todo",
            "priority": "medium",
            "estimated_hours": 3.5,
        },
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    # List tasks
    list_resp = client.get(f"{prefix}/tasks?project_id={test_project.id}", headers=auth_headers)
    assert list_resp.status_code == 200
    tasks = list_resp.json()
    assert isinstance(tasks, list)
    assert any(t["id"] == task_id for t in tasks)


@pytest.mark.parametrize("prefix", ["/api", "/api/v1"])
def test_dashboard_stats_both_prefixes(client: TestClient, auth_headers: dict, prefix: str):
    """Test dashboard stats under both /api and /api/v1."""
    response = client.get(f"{prefix}/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_projects" in data
    assert "total_tasks" in data
    assert "completion_rate" in data
    assert "priority_distribution" in data


@pytest.mark.parametrize("prefix", ["/api", "/api/v1"])
def test_activity_both_prefixes(client: TestClient, auth_headers: dict, prefix: str):
    """Test activity timeline under both /api and /api/v1."""
    response = client.get(f"{prefix}/activity", headers=auth_headers)
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, list)


@pytest.mark.parametrize("prefix", ["/api", "/api/v1"])
def test_ai_generate_tasks_both_prefixes(client: TestClient, auth_headers: dict, test_project, prefix: str):
    """Test AI task generation under both /api and /api/v1."""
    payload = {
        "project_id": test_project.id,
        "project_name": test_project.name,
        "project_description": "Building cloud native application",
        "goals": "Deliver MVP with complete authentication and task dashboard",
        "target_date": "2026-10-15",
    }
    response = client.post(
        f"{prefix}/ai/generate-tasks",
        headers=auth_headers,
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) >= 3
    assert "suggested_approach" in data
