"""24-step local end-to-end verification script for AI-Powered Project & Task Management Platform.

Executes and verifies:
1. Register new user
2. Login with that user -> receive JWT
3. Fetch dashboard stats
4. Create Project 1 (E-Commerce Platform, priority: high)
5. Create Project 2 (Mobile App Redesign, priority: medium)
6. List all projects -> verify both are returned
7. Trigger AI task generation for Project 1 -> verify >= 3 tasks generated
8. Review and selectively add generated tasks to Project 1 (add 3 AI tasks)
9. Create 2 manual tasks in Project 1 with different priorities
10. Fetch all tasks for Project 1 -> verify at least 5 tasks exist
11. Update Task 1 status to in_progress
12. Update Task 2 status to done
13. Request AI task summary for Task 1 -> verify summary returned
14. Filter tasks by status=in_progress -> verify Task 1 returned
15. Filter tasks by status=done -> verify Task 2 returned
16. Fetch dashboard stats again -> verify metrics reflect updated task counts
17. Fetch activity feed -> verify activities logged for: project_created, task_created, task_status_changed
18. Update Project 1 status to completed
19. Delete one manual task from Project 1
20. Verify task deletion in task list and project task count
21. Logout user (clear token)
22. Attempt to fetch protected route without token -> verify 401 Unauthorized
23. Attempt to fetch with invalid token -> verify 401 Unauthorized
24. Log back in with registered credentials -> verify session restored
"""

import sys
import uuid
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

def run_24_step_verification():
    print("=" * 70)
    print("STARTING 24-STEP END-TO-END VERIFICATION")
    print("=" * 70)

    client = TestClient(app)
    unique_suffix = uuid.uuid4().hex[:6]
    test_email = f"capstone_e2e_{unique_suffix}@example.com"
    test_password = "SecurePassword2026!"
    user_name = f"Capstone Engineer {unique_suffix}"

    # ----------------------------------------------------
    # Step 1: Register new user
    # ----------------------------------------------------
    print("\n[Step 1/24] Registering new user...")
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "name": user_name,
            "email": test_email,
            "password": test_password,
            "role": "Lead Architect",
        },
    )
    assert reg_resp.status_code == 201, f"Step 1 Failed: {reg_resp.text}"
    reg_data = reg_resp.json()
    assert "token" in reg_data, "Token missing in registration"
    assert reg_data["user"]["email"] == test_email
    print(f"  [OK] User registered: {test_email} (ID: {reg_data['user']['id']})")

    # ----------------------------------------------------
    # Step 2: Login with that user -> receive JWT
    # ----------------------------------------------------
    print("\n[Step 2/24] Logging in with user...")
    login_resp = client.post(
        "/api/auth/login",
        json={"email": test_email, "password": test_password},
    )
    assert login_resp.status_code == 200, f"Step 2 Failed: {login_resp.text}"
    login_data = login_resp.json()
    token = login_data["token"]["access_token"]
    assert token, "Token missing in login response"
    auth_headers = {"Authorization": f"Bearer {token}"}
    print(f"  [OK] JWT Token acquired: {token[:20]}...")

    # ----------------------------------------------------
    # Step 3: Fetch dashboard stats
    # ----------------------------------------------------
    print("\n[Step 3/24] Fetching initial dashboard stats...")
    stats_resp1 = client.get("/api/dashboard/stats", headers=auth_headers)
    assert stats_resp1.status_code == 200, f"Step 3 Failed: {stats_resp1.text}"
    stats1 = stats_resp1.json()
    print(f"  [OK] Dashboard initialized (Projects: {stats1['total_projects']}, Tasks: {stats1['total_tasks']})")

    # ----------------------------------------------------
    # Step 4: Create Project 1 (E-Commerce Platform, priority: high)
    # ----------------------------------------------------
    print("\n[Step 4/24] Creating Project 1...")
    p1_resp = client.post(
        "/api/projects",
        headers=auth_headers,
        json={
            "name": "E-Commerce Platform NextGen",
            "description": "Enterprise cloud-native digital storefront with AI search",
            "priority": "high",
            "category": "Engineering",
            "status": "active",
        },
    )
    assert p1_resp.status_code == 201, f"Step 4 Failed: {p1_resp.text}"
    project_1 = p1_resp.json()
    p1_id = project_1["id"]
    print(f"  [OK] Project 1 created: '{project_1['name']}' (ID: {p1_id})")

    # ----------------------------------------------------
    # Step 5: Create Project 2 (Mobile App Redesign, priority: medium)
    # ----------------------------------------------------
    print("\n[Step 5/24] Creating Project 2...")
    p2_resp = client.post(
        "/api/v1/projects",  # Testing /api/v1 prefix compatibility here
        headers=auth_headers,
        json={
            "name": "Mobile App Redesign",
            "description": "iOS and Android client overhaul with fluent UI",
            "priority": "medium",
            "category": "Design",
            "status": "planning",
        },
    )
    assert p2_resp.status_code == 201, f"Step 5 Failed: {p2_resp.text}"
    project_2 = p2_resp.json()
    p2_id = project_2["id"]
    print(f"  [OK] Project 2 created via /api/v1: '{project_2['name']}' (ID: {p2_id})")

    # ----------------------------------------------------
    # Step 6: List all projects -> verify both are returned
    # ----------------------------------------------------
    print("\n[Step 6/24] Listing all projects...")
    proj_list_resp = client.get("/api/projects", headers=auth_headers)
    assert proj_list_resp.status_code == 200, f"Step 6 Failed: {proj_list_resp.text}"
    projects = proj_list_resp.json()
    project_ids = [p["id"] for p in projects]
    assert p1_id in project_ids, "Project 1 not in list"
    assert p2_id in project_ids, "Project 2 not in list"
    print(f"  [OK] Found {len(projects)} projects; both created projects confirmed present.")

    # ----------------------------------------------------
    # Step 7: Trigger AI task generation for Project 1
    # ----------------------------------------------------
    print("\n[Step 7/24] Triggering AI task generation for Project 1...")
    ai_gen_resp = client.post(
        "/api/ai/generate-tasks",
        headers=auth_headers,
        json={
            "project_id": p1_id,
            "project_name": project_1["name"],
            "project_description": project_1["description"],
            "goals": "Implement payment processing, catalog search, and checkout flow",
            "target_date": "2026-11-30",
        },
    )
    assert ai_gen_resp.status_code == 200, f"Step 7 Failed: {ai_gen_resp.text}"
    ai_result = ai_gen_resp.json()
    generated_tasks = ai_result.get("tasks", [])
    assert len(generated_tasks) >= 3, f"Expected at least 3 AI tasks, got {len(generated_tasks)}"
    print(f"  [OK] AI generated {len(generated_tasks)} tasks via provider mode: {ai_result.get('provider_mode')}")

    # ----------------------------------------------------
    # Step 8: Review and selectively add generated tasks to Project 1
    # ----------------------------------------------------
    print("\n[Step 8/24] Reviewing and selectively creating 3 AI tasks...")
    ai_task_ids = []
    for i, ai_t in enumerate(generated_tasks[:3]):
        task_payload = {
            "title": ai_t["title"],
            "description": ai_t.get("description", ""),
            "project_id": p1_id,
            "status": "todo",
            "priority": ai_t.get("priority", "medium"),
            "estimated_hours": float(ai_t.get("estimated_hours", 4.0)),
            "tags": "ai-generated",
        }
        create_t_resp = client.post("/api/tasks", headers=auth_headers, json=task_payload)
        assert create_t_resp.status_code == 201, f"Step 8 Failed on task {i}: {create_t_resp.text}"
        saved_task = create_t_resp.json()
        ai_task_ids.append(saved_task["id"])
        print(f"  [OK] Added AI task {i+1}: '{saved_task['title']}' ({saved_task['priority']})")

    # ----------------------------------------------------
    # Step 9: Create 2 manual tasks in Project 1 with different priorities
    # ----------------------------------------------------
    print("\n[Step 9/24] Creating 2 manual tasks...")
    manual_1_resp = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={
            "title": "Setup OAuth2 Social Auth Provider",
            "description": "Configure Google and GitHub Single Sign-On credentials",
            "project_id": p1_id,
            "status": "todo",
            "priority": "critical",
            "estimated_hours": 6.0,
            "tags": "auth,security",
        },
    )
    assert manual_1_resp.status_code == 201, f"Step 9 Failed (manual 1): {manual_1_resp.text}"
    manual_1 = manual_1_resp.json()

    manual_2_resp = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={
            "title": "Configure Prometheus Performance Metrics",
            "description": "Add timing histograms and request rate counters",
            "project_id": p1_id,
            "status": "todo",
            "priority": "low",
            "estimated_hours": 2.0,
            "tags": "devops,metrics",
        },
    )
    assert manual_2_resp.status_code == 201, f"Step 9 Failed (manual 2): {manual_2_resp.text}"
    manual_2 = manual_2_resp.json()
    print(f"  [OK] Created Manual Task 1: '{manual_1['title']}' (priority: {manual_1['priority']})")
    print(f"  [OK] Created Manual Task 2: '{manual_2['title']}' (priority: {manual_2['priority']})")

    # ----------------------------------------------------
    # Step 10: Fetch all tasks for Project 1 -> verify >= 5 tasks
    # ----------------------------------------------------
    print("\n[Step 10/24] Fetching all tasks for Project 1...")
    p1_tasks_resp = client.get(f"/api/tasks?project_id={p1_id}", headers=auth_headers)
    assert p1_tasks_resp.status_code == 200, f"Step 10 Failed: {p1_tasks_resp.text}"
    p1_tasks = p1_tasks_resp.json()
    assert len(p1_tasks) >= 5, f"Expected >= 5 tasks, got {len(p1_tasks)}"
    print(f"  [OK] Project 1 has {len(p1_tasks)} tasks total (3 AI + 2 Manual).")

    # ----------------------------------------------------
    # Step 11: Update Task 1 status to in_progress
    # ----------------------------------------------------
    task_1_id = ai_task_ids[0]
    print(f"\n[Step 11/24] Updating Task 1 ({task_1_id}) status to in_progress...")
    t1_patch = client.patch(
        f"/api/tasks/{task_1_id}/status",
        headers=auth_headers,
        json={"status": "in_progress"},
    )
    assert t1_patch.status_code == 200, f"Step 11 Failed: {t1_patch.text}"
    assert t1_patch.json()["status"] == "in_progress"
    print("  [OK] Task 1 status successfully updated to in_progress.")

    # ----------------------------------------------------
    # Step 12: Update Task 2 status to done
    # ----------------------------------------------------
    task_2_id = ai_task_ids[1]
    print(f"\n[Step 12/24] Updating Task 2 ({task_2_id}) status to done...")
    t2_patch = client.patch(
        f"/api/tasks/{task_2_id}/status",
        headers=auth_headers,
        json={"status": "done"},
    )
    assert t2_patch.status_code == 200, f"Step 12 Failed: {t2_patch.text}"
    assert t2_patch.json()["status"] == "done"
    print("  [OK] Task 2 status successfully updated to done.")

    # ----------------------------------------------------
    # Step 13: Request AI task summary for Task 1
    # ----------------------------------------------------
    print(f"\n[Step 13/24] Requesting AI summary for Task 1...")
    ai_sum_resp = client.post(
        "/api/ai/summarize-task",
        headers=auth_headers,
        json={
            "title": t1_patch.json()["title"],
            "description": t1_patch.json().get("description") or "Implementation task",
            "priority": t1_patch.json()["priority"],
        },
    )
    assert ai_sum_resp.status_code == 200, f"Step 13 Failed: {ai_sum_resp.text}"
    sum_data = ai_sum_resp.json()
    assert "summary" in sum_data, "Summary missing from AI response"
    assert "key_deliverables" in sum_data
    print(f"  [OK] AI Summary received: {sum_data['summary'][:60]}...")

    # ----------------------------------------------------
    # Step 14: Filter tasks by status=in_progress -> verify Task 1 returned
    # ----------------------------------------------------
    print("\n[Step 14/24] Filtering tasks by status=in_progress...")
    inp_tasks_resp = client.get(f"/api/tasks?project_id={p1_id}&status=in_progress", headers=auth_headers)
    assert inp_tasks_resp.status_code == 200, f"Step 14 Failed: {inp_tasks_resp.text}"
    inp_tasks = inp_tasks_resp.json()
    inp_ids = [t["id"] for t in inp_tasks]
    assert task_1_id in inp_ids, "Task 1 not found in in_progress filtered tasks"
    print(f"  [OK] Verified: Task 1 present in in_progress results.")

    # ----------------------------------------------------
    # Step 15: Filter tasks by status=done -> verify Task 2 returned
    # ----------------------------------------------------
    print("\n[Step 15/24] Filtering tasks by status=done...")
    done_tasks_resp = client.get(f"/api/tasks?project_id={p1_id}&status=done", headers=auth_headers)
    assert done_tasks_resp.status_code == 200, f"Step 15 Failed: {done_tasks_resp.text}"
    done_tasks = done_tasks_resp.json()
    done_ids = [t["id"] for t in done_tasks]
    assert task_2_id in done_ids, "Task 2 not found in done filtered tasks"
    print(f"  [OK] Verified: Task 2 present in done results.")

    # ----------------------------------------------------
    # Step 16: Fetch dashboard stats again -> verify updated metrics
    # ----------------------------------------------------
    print("\n[Step 16/24] Fetching updated dashboard stats...")
    stats_resp2 = client.get("/api/dashboard/stats", headers=auth_headers)
    assert stats_resp2.status_code == 200, f"Step 16 Failed: {stats_resp2.text}"
    stats2 = stats_resp2.json()
    assert stats2["total_projects"] >= 2
    assert stats2["total_tasks"] >= 5
    assert stats2["completed_tasks"] >= 1
    assert stats2["in_progress_tasks"] >= 1
    print(f"  [OK] Dashboard verified: {stats2['total_projects']} projects, {stats2['total_tasks']} tasks, {stats2['completed_tasks']} completed.")

    # ----------------------------------------------------
    # Step 17: Fetch activity feed -> verify audit entries
    # ----------------------------------------------------
    print("\n[Step 17/24] Fetching activity feed...")
    act_resp = client.get("/api/activity", headers=auth_headers)
    assert act_resp.status_code == 200, f"Step 17 Failed: {act_resp.text}"
    activities = act_resp.json()
    act_types = [a["type"] for a in activities]
    assert "project_created" in act_types, "project_created activity missing"
    assert "task_created" in act_types, "task_created activity missing"
    assert "task_status_changed" in act_types, "task_status_changed activity missing"
    print(f"  [OK] Activity feed verified: {len(activities)} activities logged with all expected event types.")

    # ----------------------------------------------------
    # Step 18: Update Project 1 status to completed
    # ----------------------------------------------------
    print("\n[Step 18/24] Updating Project 1 status to completed...")
    p1_update = client.put(
        f"/api/projects/{p1_id}",
        headers=auth_headers,
        json={"status": "completed"},
    )
    assert p1_update.status_code == 200, f"Step 18 Failed: {p1_update.text}"
    assert p1_update.json()["status"] == "completed"
    print("  [OK] Project 1 status set to completed.")

    # ----------------------------------------------------
    # Step 19: Delete one manual task from Project 1
    # ----------------------------------------------------
    del_task_id = manual_2["id"]
    print(f"\n[Step 19/24] Deleting manual task {del_task_id}...")
    del_resp = client.delete(f"/api/tasks/{del_task_id}", headers=auth_headers)
    assert del_resp.status_code == 200, f"Step 19 Failed: {del_resp.text}"
    print("  [OK] Manual task deleted successfully.")

    # ----------------------------------------------------
    # Step 20: Verify task deletion in task list and project task count
    # ----------------------------------------------------
    print("\n[Step 20/24] Verifying task deletion...")
    get_del_resp = client.get(f"/api/tasks/{del_task_id}", headers=auth_headers)
    assert get_del_resp.status_code == 404, "Deleted task still retrievable via direct ID"

    p1_tasks_after = client.get(f"/api/tasks?project_id={p1_id}", headers=auth_headers).json()
    assert all(t["id"] != del_task_id for t in p1_tasks_after), "Deleted task still present in project task list"
    print(f"  [OK] Task deletion confirmed (remaining tasks in Project 1: {len(p1_tasks_after)}).")

    # ----------------------------------------------------
    # Step 21: Logout user (clear token)
    # ----------------------------------------------------
    print("\n[Step 21/24] Performing user logout...")
    logout_resp = client.post("/api/auth/logout", headers=auth_headers)
    assert logout_resp.status_code == 200, f"Step 21 Failed: {logout_resp.text}"
    print("  [OK] Logout endpoint executed, client token discarded.")

    # ----------------------------------------------------
    # Step 22: Attempt to fetch protected route without token -> verify 401
    # ----------------------------------------------------
    print("\n[Step 22/24] Testing unauthenticated request (no token)...")
    no_token_resp = client.get("/api/auth/me")
    assert no_token_resp.status_code == 401, f"Expected 401, got {no_token_resp.status_code}"
    print(f"  [OK] Unauthenticated access correctly rejected with HTTP 401.")

    # ----------------------------------------------------
    # Step 23: Attempt to fetch with invalid token -> verify 401
    # ----------------------------------------------------
    print("\n[Step 23/24] Testing invalid token access...")
    bad_token_resp = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid.token.value.123"},
    )
    assert bad_token_resp.status_code == 401, f"Expected 401, got {bad_token_resp.status_code}"
    print(f"  [OK] Invalid token correctly rejected with HTTP 401.")

    # ----------------------------------------------------
    # Step 24: Log back in with registered credentials -> verify session restored
    # ----------------------------------------------------
    print("\n[Step 24/24] Re-logging in to restore session...")
    relogin_resp = client.post(
        "/api/auth/login",
        json={"email": test_email, "password": test_password},
    )
    assert relogin_resp.status_code == 200, f"Step 24 Failed: {relogin_resp.text}"
    new_token = relogin_resp.json()["token"]["access_token"]
    verify_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_token}"})
    assert verify_me.status_code == 200
    assert verify_me.json()["email"] == test_email
    print(f"  [OK] Session successfully restored for {verify_me.json()['name']}!")

    print("\n" + "=" * 70)
    print("ALL 24 END-TO-END VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_24_step_verification()
