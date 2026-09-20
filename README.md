# AI-Powered Project & Task Management Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00.svg?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)

A modern, full-stack, enterprise-grade project and task management ecosystem featuring **backend-orchestrated AI copilot workflows**, real-time developer productivity analytics, strict server-side authorization checks, and dual SQLite/PostgreSQL persistence.

Developed as the **Week 4 Final Internship Project** for the **Innovation Hacks Full Stack Development Internship**.

---

## Internship Submission

- **Organization:** Innovation Hacks
- **Track:** Full Stack Development Internship
- **Milestone:** Week 4 — Task 4 (Final Integrated Application)
- **Repository:** [https://github.com/Praveensagar07/ai-powered-project-task-platform](https://github.com/Praveensagar07/ai-powered-project-task-platform)
- **Author:** Praveen Sagar

---

## Architecture Evolution

This project unifies and evolves the concepts, types, APIs, and relational models developed across the preceding three internship weeks into a cohesive production application:

```
[Week 1: Developer Productivity Dashboard]
  - React, Tailwind CSS design language, KPI widgets, dark mode
                         ↓
[Week 2: RESTful Backend API]
  - FastAPI schemas, standardized envelopes, input validations
                         ↓
[Week 3: Persistent Relational Data Layer]
  - SQLAlchemy 2.0 ORM, ACID transactions, foreign keys, cascades
                         ↓
[Week 4: AI-Powered Project & Task Management Platform (Final)]
  - Full-stack monorepo, JWT authentication, PBKDF2 cryptography,
    backend AI task generation with review flow, live activity logging
```

---

## Features

### 1. Authentication & Security
- **Registration & Login:** Secure account creation with email uniqueness enforcement and password strength checks.
- **PBKDF2-HMAC-SHA256 Hashing:** 100,000 rounds of cryptographic salting and constant-time digest verification. Passwords are never stored or logged in plaintext.
- **JWT Session Tokens:** Signed Bearer tokens (`HS256`) with automatic 401 expiration handling.
- **Protected Routes:** Server-side and client-side guards preventing unauthorized access.

### 2. Real-Time Developer Dashboard
- **Live Database Metrics:** Total projects, active initiatives, completed tasks, and backlog counts computed directly from SQL queries.
- **Productivity Score Engine:** Velocity algorithm rating engineering execution out of 100.
- **Project Progress Bars:** Visual completion rates calculated per project.
- **Priority Distribution:** Breakdown across Low, Medium, High, and Critical items.
- **Upcoming Deadlines & Audit Activity:** Live chronological timeline.

### 3. Project Management (Full CRUD)
- **Create, Read, Update, Delete:** Organize projects by status (`planning`, `active`, `completed`, `on_hold`), priority, category, and target delivery date.
- **Cascade Deletion:** Deleting a project safely purges all child tasks in an ACID transaction.
- **Server-Side Authorization:** Users can only view, modify, or delete projects they own.

### 4. Task Workflows (Kanban & List Views)
- **Task Management:** Full task creation, assignee linking, estimated hours, and tags.
- **Instant Status Progression:** Cycle tasks seamlessly (`todo` → `in_progress` → `done`).
- **Multi-Criteria Filtering & Search:** Filter concurrently by project, status, priority, and free-text search across titles and descriptions.

### 5. AI Copilot Integration
- **AI-Assisted Task Generation:** Generates actionable agile milestone breakdowns from project goals and deadlines.
- **Interactive Review & Edit Workflow:** AI outputs are validated against strict Pydantic schemas and presented to the user to **review, edit, and selectively approve** before database insertion.
- **Task Summarization:** One-click executive summary, key deliverable checklist, and recommended next action for any task.
- **Project Description Assistance:** Generates professional technical project descriptions.
- **Zero-Crash Heuristic Fallback:** If `AI_API_KEY` is omitted or unavailable, the backend automatically transitions to an intelligent local heuristic generator, ensuring the platform remains 100% operational in offline or demo environments.

### 6. User Experience & Design System
- **Theme Support:** Instant toggle between Dark Mode and Light Mode with persistence.
- **Toast Notifications:** Feedback system for user actions and error handling.
- **Responsive Layout:** Optimized from mobile devices (320px, 375px, 430px) through tablets (768px) and desktop screens (1024px, 1440px).

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide React, React Router v6 |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, PyJWT, HTTPX |
| **Database** | SQLAlchemy 2.0, SQLite (local zero-config) & PostgreSQL (production-ready) |
| **AI Integration** | OpenAI / Gemini REST API standard + Resilient Fallback Heuristics |
| **Testing** | Pytest (30 passing tests), FastAPI TestClient, TypeScript Compiler |
| **Deployment** | Configured for Render, Railway, Vercel, and Docker |

---

## Repository Structure

```
ai-powered-project-task-platform/
├── .env.example                # Documented configuration template
├── .gitignore                  # Security-first gitignore rules
├── README.md                   # Comprehensive project documentation
├── docs/
│   ├── ARCHITECTURE.md         # Full architectural specification
│   ├── API.md                  # REST API endpoints & payloads
│   └── DEPLOYMENT.md           # Production deployment guide
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/         # auth, projects, tasks, dashboard, activity, ai
│   │   │   ├── deps.py         # DB session & JWT current_user dependencies
│   │   │   └── router.py       # Versioned API router
│   │   ├── core/               # config, security (PBKDF2/JWT), error handlers
│   │   ├── db/                 # base, session, seed demo data
│   │   ├── models/             # User, Project, Task, Activity ORM entities
│   │   ├── schemas/            # Pydantic v2 input & output contracts
│   │   ├── services/           # Business logic & server-side authorization
│   │   └── main.py             # ASGI entrypoint & observability middleware
│   ├── tests/                  # 30 comprehensive pytest test suites
│   ├── requirements.txt
│   └── pytest.ini
└── frontend/
    ├── src/
    │   ├── components/         # UI primitives, layout, AI modals, project/task cards
    │   ├── context/            # AuthContext, ThemeContext, ToastContext
    │   ├── pages/              # Login, Register, Dashboard, Projects, Tasks, Activity, Settings
    │   ├── services/           # Centralized API clients (auth, projects, tasks, ai, dashboard)
    │   ├── types/              # TypeScript domain interfaces
    │   ├── App.tsx             # Root router with ProtectedRoute
    │   └── main.tsx
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    └── tailwind.config.js
```

---

## Database Architecture

```
+--------------------+           1:N           +--------------------+
|       users        |------------------------<|      projects      |
+--------------------+                         +--------------------+
| id (PK)            |                         | id (PK)            |
| name               |                         | name               |
| email (UNIQUE)     |                         | description        |
| password_hash      |                         | status (CHECK)     |
| role               |                         | priority (CHECK)   |
| avatar             |                         | category           |
| bio                |                         | due_date           |
| created_at         |                         | owner_id (FK)      |
+--------------------+                         +--------------------+
          |                                              |
          | 1:N (Assignee)                               | 1:N (CASCADE)
          v                                              v
+--------------------+                         +--------------------+
|     activities     |                         |       tasks        |
+--------------------+                         +--------------------+
| id (PK)            |                         | id (PK)            |
| user_id (FK)       |                         | project_id (FK)    |
| user_name          |                         | assignee_id (FK)   |
| type               |                         | title              |
| title              |                         | description        |
| description        |                         | status (CHECK)     |
| target_type        |                         | priority (CHECK)   |
| target_id          |                         | due_date           |
| created_at         |                         | tags               |
+--------------------+                         | estimated_hours    |
                                               +--------------------+
```

---

## Local Setup & Quickstart

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**

### 1. Clone the Repository
```bash
git clone https://github.com/Praveensagar07/ai-powered-project-task-platform.git
cd ai-powered-project-task-platform
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```
*(Default settings run immediately on local SQLite with intelligent AI heuristics without requiring third-party API keys).*

### 3. Start Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
- API Root: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`

### 4. Start Frontend (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```
- Application URL: `http://localhost:5173`

### 5. Demo Credentials
Click **"Fill Demo Credentials"** on the login screen, or sign in manually:
- **Email:** `praveen@example.com`
- **Password:** `Password123!`

---

## Running Automated Tests

### Backend Test Suite (Pytest)
```bash
cd backend
python -m pytest
```
*Executes 30 automated integration and unit tests covering authentication, password hashing, ownership checks, project & task CRUD, batch tasks, filtering, dashboard aggregation, and AI generation.*

### Frontend Type Check & Build
```bash
cd frontend
npm run build
```
*Verifies 100% clean TypeScript typing with zero errors and outputs production distribution bundle.*

---

## Screenshots

| View | Description |
| :--- | :--- |
| **Login & Demo Access** | Split-pane authentication with password validation and one-click demo login |
| **Developer Dashboard** | Real-time KPI cards, completion progress, productivity score, and recent activity |
| **Projects Overview** | Grid layout showing completion percentages, task counts, categories, and AI triggers |
| **Kanban Task Board** | Dynamic 3-column workflow (To Do, In Progress, Done) with inline status transitions |
| **AI Task Generation Modal** | Prompt input, automated task breakdown, selection checkboxes, and inline editing |
| **Task Details & AI Summary** | Deep inspection of deliverables, tags, due dates, and AI executive briefing |

---

## Demo Video

- **Video Walkthrough:** *(Link to demonstration video will be attached here)*

---

## License

This project was built for the **Innovation Hacks Full Stack Development Internship**. All rights reserved.
