"""Dashboard metrics and KPI aggregation API."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.activity import Activity
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.activity import ActivityResponse
from app.schemas.dashboard import (
    DashboardStatsResponse,
    PriorityCount,
    ProjectProgress,
    StatusCount,
    UpcomingDeadline,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
    summary="Get user dashboard aggregated metrics",
    description="Computes real-time statistics, progress percentages, priority distributions, upcoming deadlines, and recent activities for the current user.",
)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardStatsResponse:
    now = datetime.now(timezone.utc)

    # 1. Projects
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    total_projects = len(projects)
    active_projects = sum(1 for p in projects if p.status == "active")

    # 2. Tasks
    tasks = (
        db.query(Task)
        .join(Project, Task.project_id == Project.id)
        .filter((Project.owner_id == current_user.id) | (Task.assignee_id == current_user.id))
        .all()
    )
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "done")
    in_progress_tasks = sum(1 for t in tasks if t.status == "in_progress")
    todo_tasks = sum(1 for t in tasks if t.status == "todo")

    # Overdue tasks
    overdue_tasks = 0
    for t in tasks:
        if t.due_date and t.status != "done":
            # ensure timezone-aware comparison
            due = t.due_date if t.due_date.tzinfo else t.due_date.replace(tzinfo=timezone.utc)
            if due < now:
                overdue_tasks += 1

    completion_rate = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    # 3. Priority distribution
    priority_dist = PriorityCount(
        low=sum(1 for t in tasks if t.priority == "low"),
        medium=sum(1 for t in tasks if t.priority == "medium"),
        high=sum(1 for t in tasks if t.priority == "high"),
        critical=sum(1 for t in tasks if t.priority == "critical"),
    )

    # 4. Status distribution
    status_dist = StatusCount(
        todo=todo_tasks,
        in_progress=in_progress_tasks,
        done=completed_tasks,
    )

    # 5. Project progress list
    progress_list = []
    for p in projects:
        p_tasks = p.tasks or []
        p_total = len(p_tasks)
        p_done = sum(1 for t in p_tasks if t.status == "done")
        p_pct = int((p_done / p_total) * 100) if p_total > 0 else 0
        progress_list.append(
            ProjectProgress(
                id=p.id,
                name=p.name,
                status=p.status,
                priority=p.priority,
                total_tasks=p_total,
                completed_tasks=p_done,
                progress_percentage=p_pct,
            )
        )

    # 6. Upcoming deadlines (sorted closest first)
    deadlines = []
    future_tasks = []
    for t in tasks:
        if t.due_date and t.status != "done":
            due = t.due_date if t.due_date.tzinfo else t.due_date.replace(tzinfo=timezone.utc)
            future_tasks.append((due, t))

    future_tasks.sort(key=lambda x: x[0])
    for due, t in future_tasks[:6]:
        deadlines.append(
            UpcomingDeadline(
                id=t.id,
                title=t.title,
                project_name=t.project.name if t.project else "Project",
                due_date=due.strftime("%b %d, %Y"),
                priority=t.priority,
                status=t.status,
            )
        )

    # 7. Recent activities
    recent_acts = (
        db.query(Activity)
        .filter(Activity.user_id == current_user.id)
        .order_by(Activity.created_at.desc())
        .limit(8)
        .all()
    )
    activities_response = [ActivityResponse.model_validate(a) for a in recent_acts]

    # Productivity score calculation
    productivity_score = 70
    if total_tasks > 0:
        productivity_score = min(100, max(20, int((completed_tasks * 1.2 / max(total_tasks, 1)) * 80 + 20)))

    return DashboardStatsResponse(
        total_projects=total_projects,
        active_projects=active_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        todo_tasks=todo_tasks,
        overdue_tasks=overdue_tasks,
        completion_rate=completion_rate,
        productivity_score=productivity_score,
        priority_distribution=priority_dist,
        status_distribution=status_dist,
        projects_progress=progress_list,
        upcoming_deadlines=deadlines,
        recent_activities=activities_response,
    )
