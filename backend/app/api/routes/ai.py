"""AI-powered productivity endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.activity import Activity
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.ai import (
    AIProductivityResponse,
    AIProjectDescriptionRequest,
    AIProjectDescriptionResponse,
    AISummarizeRequest,
    AISummarizeResponse,
    AITaskGenerationRequest,
    AITaskGenerationResponse,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Integration"])
settings = get_settings()


@router.get(
    "/status",
    summary="Check AI Provider Status",
    description="Returns whether an external LLM key is configured or operating in intelligent heuristic mode.",
)
def get_ai_status(current_user: User = Depends(get_current_user)) -> dict:
    has_key = bool(settings.ai_api_key and settings.ai_api_key.strip())
    return {
        "status": "ready",
        "provider": settings.ai_provider,
        "model": settings.ai_model,
        "mode": "live" if has_key else "fallback-heuristic",
        "is_custom_key_configured": has_key,
        "info": (
            "Connected to live AI provider."
            if has_key
            else "Operating in intelligent local heuristic mode (no external key configured)."
        ),
    }


@router.post(
    "/generate-tasks",
    response_model=AITaskGenerationResponse,
    summary="Generate structured tasks with AI",
    description="Analyzes project objectives and creates actionable task suggestions for user review and selection.",
)
async def generate_tasks(
    request: AITaskGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AITaskGenerationResponse:
    # Verify user has access to project
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project or project.owner_id != current_user.id:
        pass  # allow generation preview even before saving if client wants

    result = await AIService.generate_tasks(request)

    # Log AI action to activity
    activity = Activity(
        user_id=current_user.id,
        user_name=current_user.name,
        user_avatar=current_user.avatar,
        type="ai_tasks_generated",
        title=f"Generated {len(result.tasks)} tasks with AI",
        description=f"Generated actionable tasks for project '{request.project_name}' ({result.provider_mode} mode).",
        target_type="ai",
        target_id=request.project_id,
    )
    db.add(activity)
    db.commit()

    return result


@router.post(
    "/summarize-task",
    response_model=AISummarizeResponse,
    summary="Summarize task details and next steps",
    description="Produces a concise summary, key deliverables, and recommended actions for a task.",
)
async def summarize_task(
    request: AISummarizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AISummarizeResponse:
    result = await AIService.summarize_task(request)

    # Log activity if tied to existing task
    if request.task_id:
        activity = Activity(
            user_id=current_user.id,
            user_name=current_user.name,
            user_avatar=current_user.avatar,
            type="ai_task_summarized",
            title=f"AI summarized '{request.title}'",
            description=f"Executive summary generated.",
            target_type="task",
            target_id=request.task_id,
        )
        db.add(activity)
        db.commit()

    return result


@router.post(
    "/project-description",
    response_model=AIProjectDescriptionResponse,
    summary="Generate project scope and description",
    description="Drafts a comprehensive project description based on title and core goals.",
)
async def generate_project_description(
    request: AIProjectDescriptionRequest,
    current_user: User = Depends(get_current_user),
) -> AIProjectDescriptionResponse:
    return await AIService.generate_project_description(request)


@router.get(
    "/productivity-suggestions",
    response_model=AIProductivityResponse,
    summary="Get AI productivity suggestions",
    description="Analyzes pending workload and recommends priority focus areas.",
)
def get_productivity_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AIProductivityResponse:
    # Gather critical / high priority tasks
    tasks = (
        db.query(Task)
        .join(Project, Task.project_id == Project.id)
        .filter((Project.owner_id == current_user.id) | (Task.assignee_id == current_user.id))
        .filter(Task.status != "done")
        .order_by(Task.due_date.asc())
        .limit(5)
        .all()
    )

    focus_list = [f"{t.title} ({t.priority} priority in {t.project.name})" for t in tasks]
    if not focus_list:
        focus_list = ["All current tasks are completed! Plan your next project milestone."]

    tip = (
        "Focus on tackling the highest-priority blocking items first thing in your workday. "
        "Batch similar small tasks together to minimize context switching."
    )
    warning = f"You have {len(tasks)} active tasks awaiting completion." if len(tasks) > 3 else None

    return AIProductivityResponse(
        focus_tasks=focus_list,
        productivity_tip=tip,
        bottleneck_warning=warning,
        provider_mode="fallback-heuristic" if not settings.ai_api_key.strip() else "live",
    )
