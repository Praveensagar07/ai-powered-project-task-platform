# Architecture Specification

## AI-Powered Project & Task Management Platform
**Innovation Hacks — Full Stack Development Internship (Week 4 Final Project)**

---

## 1. System Overview

The **AI-Powered Project & Task Management Platform** is a full-stack, enterprise-grade project and task tracking ecosystem with deep backend-integrated AI capabilities. It consolidates the foundational progress established throughout the internship:
- **Week 1:** Developer Productivity Dashboard (React, Tailwind CSS, Component Systems)
- **Week 2:** REST API Architecture (FastAPI, Schemas, Resource Routing)
- **Week 3:** Relational Data Layer (PostgreSQL / SQLite, SQLAlchemy 2.0, Foreign Keys & Cascades)
- **Week 4 (Final):** End-to-End Integrated Platform with JWT Authentication, Security, AI Workflows, and Dynamic Telemetry.

```
+-------------------------------------------------------------------------+
|                              FRONTEND                                   |
|   React 18  *  TypeScript  *  Vite  *  Tailwind CSS  *  Lucide Icons     |
|   - AuthContext (JWT, Session Persistence)                              |
|   - Dynamic Views: Dashboard, Kanban & List Tasks, Projects, Activity   |
|   - Interactive AI Workflows (Task Generation, Summarizer, Descriptions) |
|   - ThemeContext (Dark/Light mode) & ToastContext System                |
+------------------------------------+------------------------------------+
                                     |
                          HTTPS / REST API JSON
                                     |
+------------------------------------v------------------------------------+
|                           BACKEND REST API                              |
|                  FastAPI  *  Pydantic v2  *  PyJWT                      |
|   - Router Hierarchy: /auth, /projects, /tasks, /dashboard, /ai         |
|   - Security: PBKDF2-HMAC-SHA256 (100k rounds) & Bearer Token Guard     |
|   - Server-Side Authorization: Resource Ownership Validation            |
|   - Exception Handling & Observability Tracing (X-Request-ID, Latency)   |
+-----------------+-----------------------------------+-------------------+
                  |                                   |
                  v                                   v
+-----------------------------------+   +---------------------------------+
|          DATABASE LAYER           |   |       AI COPILOT SERVICE        |
|  SQLAlchemy 2.0 ORM & SQLite / PG |   | - Provider: OpenAI / Gemini     |
|  - Users (Credentials, Profile)   |   | - Schema Validation (Pydantic)  |
|  - Projects (Initiatives, Scope)  |   | - Fallback Heuristic Generator  |
|  - Tasks (Workflow, Status, Due)  |   | - Task Extraction & Scoping     |
|  - Activities (Audit Trails)      |   +---------------------------------+
+-----------------------------------+
```

---

## 2. Key Architecture Layers

### 2.1 Frontend Architecture (`/frontend`)
- **Framework & Tooling:** React 18 with TypeScript running on Vite for sub-second hot module reloading and optimized tree-shaken production bundles.
- **Routing:** React Router v6 with `ProtectedRoute` guards and an `AppLayout` shell featuring responsive sidebar navigation, top bar controls, and theme switching.
- **State Management:** Modular React Contexts (`AuthContext`, `ThemeContext`, `ToastContext`) paired with custom domain service hooks for low complexity and predictable state flow.
- **API Communication Layer:** Centralized `services/api.ts` client wrapper handling Bearer token injection, session refresh, automatic 401 expiration handling, and structured error normalization.

### 2.2 Backend Architecture (`/backend`)
- **FastAPI Core:** Asynchronous ASGI application with strict Pydantic v2 input/output serialization.
- **Security & Cryptography:** 
  - Passwords hashed using PBKDF2 with SHA-256 and unique 16-byte random salts across 100,000 iterations.
  - Signed JSON Web Tokens (JWT) using HS256 with 24-hour expiration.
  - Strict server-side authorization ensuring users can only read, update, or delete resources they own.
- **Observability Middleware:** Every incoming request receives a unique `X-Request-ID` correlation identifier and response duration metric `X-Process-Time`.

### 2.3 Database Layer (`SQLAlchemy 2.0`)
- **Engine Compatibility:** Dual engine compatibility supporting zero-config SQLite (`sqlite:///./app_data.db`) for instant local development and production PostgreSQL (`postgresql+psycopg://...`) with connection pooling (`pool_size`, `max_overflow`, `pool_pre_ping`).
- **Relational Integrity:**
  - Foreign key cascading deletion on `Project -> Task`.
  - Set-null reassignment on user deletion.
  - Table-level CHECK constraints for status and priority enumerations.
  - Unique database indexes on email addresses.

### 2.4 AI Integration Flow
AI capabilities are mediated entirely through backend endpoints to prevent exposing credentials to the client.
1. The client issues an authenticated request to `POST /api/ai/generate-tasks`.
2. The backend constructs a structured prompt enforcing strict JSON output conforming to agile task specifications.
3. If `AI_API_KEY` is supplied, the service queries the configured LLM API (OpenAI or Gemini standard endpoints).
4. If `AI_API_KEY` is absent or the external service fails, the service falls back to a deterministic domain-aware heuristic generator.
5. All AI outputs are validated against Pydantic schemas prior to returning to the user.
6. The user **reviews, edits, and selects** generated tasks before approving them for database persistence.
