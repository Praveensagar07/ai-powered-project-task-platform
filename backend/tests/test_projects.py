"""Project CRUD and ownership authorization tests."""

import pytest


def test_create_project(client, auth_headers):
    payload = {
        "name": "E-Commerce Microservices",
        "description": "Distributed checkout and payment gateway",
        "status": "active",
        "priority": "critical",
        "category": "Engineering",
    }
    response = client.post("/api/projects", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["status"] == "active"
    assert data["priority"] == "critical"
    assert data["total_tasks"] == 0
    assert data["completed_tasks"] == 0


def test_list_projects(client, auth_headers, test_project):
    response = client.get("/api/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == test_project.id


def test_get_project_detail(client, auth_headers, test_project):
    response = client.get(f"/api/projects/{test_project.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_project.id
    assert data["name"] == test_project.name


def test_update_project(client, auth_headers, test_project):
    payload = {
        "name": "Updated Platform Title",
        "priority": "critical",
    }
    response = client.put(f"/api/projects/{test_project.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Platform Title"
    assert data["priority"] == "critical"


def test_delete_project(client, auth_headers, test_project):
    response = client.delete(f"/api/projects/{test_project.id}", headers=auth_headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"].lower()

    # Verify not found after delete
    get_res = client.get(f"/api/projects/{test_project.id}", headers=auth_headers)
    assert get_res.status_code == 404


def test_user_cannot_access_other_users_project(client, second_auth_headers, test_project):
    # Second user attempts to retrieve test_user's project
    response = client.get(f"/api/projects/{test_project.id}", headers=second_auth_headers)
    assert response.status_code == 403
    assert "authorization" in response.json()["error"]["message"].lower()


def test_user_cannot_delete_other_users_project(client, second_auth_headers, test_project):
    # Second user attempts to delete test_user's project
    response = client.delete(f"/api/projects/{test_project.id}", headers=second_auth_headers)
    assert response.status_code == 403
