"""Task operations, status transitions, batch creation, and filtering tests."""

import pytest


def test_create_task_success(client, auth_headers, test_project):
    payload = {
        "title": "Build Authentication Flow",
        "description": "Implement login and register with JWT tokens",
        "project_id": test_project.id,
        "status": "todo",
        "priority": "high",
        "tags": "security,auth",
        "estimated_hours": 5.0,
    }
    response = client.post("/api/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["status"] == "todo"
    assert data["priority"] == "high"
    assert data["project_id"] == test_project.id


def test_create_task_invalid_project(client, auth_headers):
    payload = {
        "title": "Orphan Task",
        "project_id": "non-existent-id",
        "status": "todo",
        "priority": "low",
    }
    response = client.post("/api/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 404


def test_unauthorized_user_cannot_add_task(client, second_auth_headers, test_project):
    payload = {
        "title": "Unauthorized Task",
        "project_id": test_project.id,
        "status": "todo",
    }
    response = client.post("/api/tasks", json=payload, headers=second_auth_headers)
    assert response.status_code == 403


def test_task_status_transition(client, auth_headers, test_project):
    # Create task
    task = client.post(
        "/api/tasks",
        json={"title": "Test Status Transition", "project_id": test_project.id, "status": "todo"},
        headers=auth_headers,
    ).json()

    # Move to in_progress
    patch_res = client.patch(
        f"/api/tasks/{task['id']}/status",
        json={"status": "in_progress"},
        headers=auth_headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "in_progress"

    # Move to done
    done_res = client.patch(
        f"/api/tasks/{task['id']}/status",
        json={"status": "done"},
        headers=auth_headers,
    )
    assert done_res.status_code == 200
    assert done_res.json()["status"] == "done"


def test_batch_create_tasks(client, auth_headers, test_project):
    payload = [
        {"title": "Subtask 1", "project_id": test_project.id, "status": "todo", "priority": "high"},
        {"title": "Subtask 2", "project_id": test_project.id, "status": "todo", "priority": "medium"},
    ]
    response = client.post("/api/tasks/batch", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Subtask 1"
    assert data[1]["title"] == "Subtask 2"


def test_search_and_filter_tasks(client, auth_headers, test_project):
    client.post(
        "/api/tasks",
        json={"title": "Write Documentation", "project_id": test_project.id, "status": "todo", "priority": "low"},
        headers=auth_headers,
    )
    client.post(
        "/api/tasks",
        json={"title": "Database Optimization", "project_id": test_project.id, "status": "in_progress", "priority": "critical"},
        headers=auth_headers,
    )

    # Filter by status
    res = client.get("/api/tasks?status=in_progress", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert all(t["status"] == "in_progress" for t in data)

    # Filter by priority
    res_p = client.get("/api/tasks?priority=critical", headers=auth_headers)
    assert res_p.status_code == 200
    data_p = res_p.json()
    assert all(t["priority"] == "critical" for t in data_p)

    # Search keyword
    res_s = client.get("/api/tasks?search=Documentation", headers=auth_headers)
    assert res_s.status_code == 200
    data_s = res_s.json()
    assert any("Documentation" in t["title"] for t in data_s)


def test_delete_task(client, auth_headers, test_project):
    task = client.post(
        "/api/tasks",
        json={"title": "Task to Delete", "project_id": test_project.id},
        headers=auth_headers,
    ).json()

    del_res = client.delete(f"/api/tasks/{task['id']}", headers=auth_headers)
    assert del_res.status_code == 200
    assert "deleted successfully" in del_res.json()["message"].lower()

    get_res = client.get(f"/api/tasks/{task['id']}", headers=auth_headers)
    assert get_res.status_code == 404
