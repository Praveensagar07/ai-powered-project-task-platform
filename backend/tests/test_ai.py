"""AI endpoints and resilience verification tests."""

import pytest


def test_ai_status_endpoint(client, auth_headers):
    response = client.get("/api/ai/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "model" in data
    assert "mode" in data
    assert data["status"] == "ready"


def test_ai_generate_tasks(client, auth_headers, test_project):
    payload = {
        "project_id": test_project.id,
        "project_name": test_project.name,
        "project_description": "Building cloud native application",
        "goals": "Deliver MVP with complete authentication and task dashboard",
        "target_date": "2026-10-15",
    }
    response = client.post("/api/ai/generate-tasks", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) >= 3
    assert "suggested_approach" in data
    assert "provider_mode" in data

    # Verify task structure
    task_0 = data["tasks"][0]
    assert "title" in task_0
    assert "description" in task_0
    assert "priority" in task_0
    assert task_0["priority"] in ["low", "medium", "high", "critical"]
    assert "estimated_hours" in task_0


def test_ai_summarize_task(client, auth_headers):
    payload = {
        "title": "Migrate Database to PostgreSQL Cluster",
        "description": "Set up PostgreSQL read-replicas, configure connection pooling, and verify zero downtime switchover.",
        "priority": "critical",
    }
    response = client.post("/api/ai/summarize-task", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "key_deliverables" in data
    assert "suggested_action" in data
    assert len(data["key_deliverables"]) > 0


def test_ai_project_description(client, auth_headers):
    payload = {
        "title": "AI Task Intelligence",
        "category": "Machine Learning",
        "goals": "Automate agile planning and summarize engineering deliverables",
    }
    response = client.post("/api/ai/project-description", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "description" in data
    assert "key_outcomes" in data
    assert len(data["description"]) > 20


def test_ai_productivity_suggestions(client, auth_headers):
    response = client.get("/api/ai/productivity-suggestions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "focus_tasks" in data
    assert "productivity_tip" in data
