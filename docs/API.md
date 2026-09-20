# REST API Specification

All endpoints are served under the versioned prefix `/api` (configurable via `API_PREFIX`).

Interactive Swagger UI documentation is available at:
`http://localhost:8000/docs`

---

## 1. Authentication Endpoints

### Register User
- **Method:** `POST`
- **Path:** `/api/auth/register`
- **Request Body:**
  ```json
  {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "password": "Password123!",
    "role": "Full Stack Engineer"
  }
  ```
- **Response:** `201 Created`
  ```json
  {
    "user": {
      "id": "uuid-string",
      "name": "Jane Doe",
      "email": "jane@example.com",
      "role": "Full Stack Engineer",
      "avatar": "https://api.dicebear.com/...",
      "bio": "...",
      "created_at": "2026-09-20T12:00:00Z",
      "updated_at": "2026-09-20T12:00:00Z"
    },
    "token": {
      "access_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "expires_in": 86400
    }
  }
  ```

### Login
- **Method:** `POST`
- **Path:** `/api/auth/login`
- **Request Body:**
  ```json
  {
    "email": "jane@example.com",
    "password": "Password123!"
  }
  ```
- **Response:** `200 OK` (returns `user` and `token`)

### Get Current User Profile
- **Method:** `GET`
- **Path:** `/api/auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `200 OK`

---

## 2. Projects Endpoints

### List Projects
- **Method:** `GET`
- **Path:** `/api/projects`
- **Headers:** `Authorization: Bearer <token>`
- **Query Parameters:**
  - `status`: Filter by status (`planning`, `active`, `completed`, `on_hold`)
  - `priority`: Filter by priority (`low`, `medium`, `high`, `critical`)
  - `search`: Search keyword
- **Response:** `200 OK` (Array of `ProjectResponse` objects including `total_tasks`, `completed_tasks`, `progress_percentage`)

### Create Project
- **Method:** `POST`
- **Path:** `/api/projects`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "name": "Mobile Client v2",
    "description": "Cross-platform mobile client built with React Native",
    "status": "active",
    "priority": "high",
    "category": "Mobile",
    "due_date": "2026-11-01T00:00:00Z"
  }
  ```
- **Response:** `201 Created`

### Get Project Details
- **Method:** `GET`
- **Path:** `/api/projects/{id}`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `200 OK`

### Update Project
- **Method:** `PUT`
- **Path:** `/api/projects/{id}`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `200 OK`

### Delete Project
- **Method:** `DELETE`
- **Path:** `/api/projects/{id}`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `200 OK` (Cascades deletion to tasks)

---

## 3. Tasks Endpoints

### List Tasks
- **Method:** `GET`
- **Path:** `/api/tasks`
- **Headers:** `Authorization: Bearer <token>`
- **Query Parameters:** `project_id`, `status`, `priority`, `search`
- **Response:** `200 OK` (Array of `TaskResponse` objects)

### Create Task
- **Method:** `POST`
- **Path:** `/api/tasks`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "title": "Setup OAuth login",
    "description": "Configure Google and GitHub OAuth providers",
    "project_id": "project-uuid",
    "status": "todo",
    "priority": "high",
    "due_date": "2026-10-15T00:00:00Z",
    "tags": "security,auth",
    "estimated_hours": 4.5
  }
  ```
- **Response:** `201 Created`

### Batch Create Tasks
- **Method:** `POST`
- **Path:** `/api/tasks/batch`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:** Array of `TaskCreate` objects (used when saving reviewed AI generated tasks)
- **Response:** `201 Created`

### Quick Status Update
- **Method:** `PATCH`
- **Path:** `/api/tasks/{id}/status`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:** `{"status": "done"}`
- **Response:** `200 OK`

### Delete Task
- **Method:** `DELETE`
- **Path:** `/api/tasks/{id}`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `200 OK`

---

## 4. Dashboard Endpoints

### Get Aggregated Stats
- **Method:** `GET`
- **Path:** `/api/dashboard/stats`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `200 OK`
  ```json
  {
    "total_projects": 3,
    "active_projects": 2,
    "total_tasks": 8,
    "completed_tasks": 4,
    "in_progress_tasks": 2,
    "todo_tasks": 2,
    "overdue_tasks": 0,
    "completion_rate": 50,
    "productivity_score": 88,
    "priority_distribution": {"low": 1, "medium": 3, "high": 2, "critical": 2},
    "status_distribution": {"todo": 2, "in_progress": 2, "done": 4},
    "projects_progress": [...],
    "upcoming_deadlines": [...],
    "recent_activities": [...]
  }
  ```

---

## 5. Activity & Audit Trail

### List Recent Activities
- **Method:** `GET`
- **Path:** `/api/activity`
- **Headers:** `Authorization: Bearer <token>`
- **Query Parameters:** `limit` (default 50), `type` (optional filter)
- **Response:** `200 OK`

---

## 6. AI Endpoints

### Check AI Provider Status
- **Method:** `GET`
- **Path:** `/api/ai/status`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `200 OK` (`provider`, `model`, `mode`, `is_custom_key_configured`)

### Generate Tasks with AI
- **Method:** `POST`
- **Path:** `/api/ai/generate-tasks`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "project_id": "project-uuid",
    "project_name": "Cloud Microservices",
    "project_description": "Scalable Kubernetes platform",
    "goals": "Build API gateway, service discovery, and zero-downtime CI/CD",
    "target_date": "2026-11-01"
  }
  ```
- **Response:** `200 OK` (`tasks` array with `title`, `description`, `priority`, `estimated_hours`, `tags`, and `suggested_approach`)

### Summarize Task with AI
- **Method:** `POST`
- **Path:** `/api/ai/summarize-task`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "title": "Migrate DB to Postgres",
    "description": "Set up replicas and connection pools...",
    "priority": "critical"
  }
  ```
- **Response:** `200 OK` (`summary`, `key_deliverables`, `suggested_action`)
