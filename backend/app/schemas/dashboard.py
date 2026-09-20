"""Dashboard statistics schemas."""

from typing import List, Optional
from pydantic import BaseModel
from app.schemas.activity import ActivityResponse


class PriorityCount(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class StatusCount(BaseModel):
    todo: int = 0
    in_progress: int = 0
    done: int = 0


class ProjectProgress(BaseModel):
    id: str
    name: str
    status: str
    priority: str
    total_tasks: int
    completed_tasks: int
    progress_percentage: int


class UpcomingDeadline(BaseModel):
    id: str
    title: str
    project_name: str
    due_date: str
    priority: str
    status: str


class DashboardStatsResponse(BaseModel):
    total_projects: int = 0
    active_projects: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    todo_tasks: int = 0
    overdue_tasks: int = 0
    completion_rate: int = 0
    productivity_score: int = 85
    priority_distribution: PriorityCount
    status_distribution: StatusCount
    projects_progress: List[ProjectProgress] = []
    upcoming_deadlines: List[UpcomingDeadline] = []
    recent_activities: List[ActivityResponse] = []
