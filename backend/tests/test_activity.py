"""Activity audit log tests."""

import pytest


def test_activity_logged_on_project_and_task_lifecycle(client, auth_headers):
    # 1. Create project
    proj_res = client.post(
        "/api/projects",
        json={"name": "Activity Test Project", "priority": "medium"},
        headers=auth_headers,
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Create task
    task_res = client.post(
        "/api/tasks",
        json={"title": "Audit Task", "project_id": proj_id, "status": "todo"},
        headers=auth_headers,
    )
    assert task_res.status_code == 201
    task_id = task_res.json()["id"]

    # 3. Complete task
    patch_res = client.patch(
        f"/api/tasks/{task_id}/status",
        json={"status": "done"},
        headers=auth_headers,
    )
    assert patch_res.status_code == 200

    # 4. Fetch activity feed
    activity_res = client.get("/api/activity", headers=auth_headers)
    assert activity_res.status_code == 200
    activities = activity_res.json()
    assert len(activities) >= 3

    types = [a["type"] for a in activities]
    assert "project_created" in types
    assert "task_created" in types
    assert "task_completed" in types


def test_dashboard_stats_endpoint(client, auth_headers, test_project):
    client.post(
        "/api/tasks",
        json={"title": "Dashboard Metric Task", "project_id": test_project.id, "status": "done"},
        headers=auth_headers,
    )
    res = client.get("/api/dashboard/stats", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_projects" in data
    assert "total_tasks" in data
    assert "completion_rate" in data
    assert "priority_distribution" in data
    assert data["total_projects"] >= 1
    assert data["total_tasks"] >= 1
