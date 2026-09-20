"""Main FastAPI application entrypoint for AI-Powered Project & Task Management Platform."""

import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.error_handlers import register_error_handlers
from app.db.base import Base
import app.models  # noqa: F401
from app.db.seed import seed_database
from app.db.session import SessionLocal, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager handling startup initialization and teardown."""
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)

    # Seed initial demo dataset if enabled
    if settings.seed_demo_data:
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()

    yield
    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
# AI-Powered Project & Task Management Platform REST API

Official Week 4 Final Project for the **Innovation Hacks Full Stack Development Internship**.

### Key Architectural Capabilities
- **Authentication & Security:** JWT Access Tokens, PBKDF2-HMAC-SHA256 password hashing, server-side authorization checks.
- **Relational Persistence:** Users, Projects, Tasks, and Audit Activity entities managed via SQLAlchemy 2.0 with foreign keys & cascades.
- **AI Integration:** AI-Assisted Task Generation with interactive user review & selection, task summarization, and project scoping.
- **Observability:** Centralized exception handling, structured JSON envelopes, and request tracing headers.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 1. Register Centralized Error Handlers
register_error_handlers(app)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)


# 3. Observability Middleware
@app.middleware("http")
async def add_observability_headers(request: Request, call_next) -> Response:
    """Inject request ID and response timing metrics."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"
    return response


# 4. Root & Health Endpoints
@app.get(
    "/",
    tags=["System"],
    summary="API Root Information",
)
def root_info() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "docs": "/docs",
        "redoc": "/redoc",
        "api": settings.api_prefix,
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Health Status Check",
)
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.app_version,
        "environment": settings.app_env,
    }


# 5. Include API routes
app.include_router(api_router, prefix=settings.api_prefix)
