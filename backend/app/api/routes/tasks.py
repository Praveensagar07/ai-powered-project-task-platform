"""Tasks API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskPriorityUpdate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "",
    response_model=List[TaskResponse],
    summary="List tasks",
    description="Retrieves tasks belonging to the current user's projects with filtering by project, status, priority, and search.",
)
def list_tasks(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status ('todo', 'in_progress', 'done')"),
    priority: Optional[str] = Query(None, description="Filter by priority ('low', 'medium', 'high', 'critical')"),
    search: Optional[str] = Query(None, description="Search term in title, description, or project"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    return TaskService.list_tasks(
        db,
        user_id=current_user.id,
        project_id=project_id,
        status_filter=status,
        priority_filter=priority,
        search=search,
    )


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a task under a specified project after verifying ownership.",
)
def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    return TaskService.create_task(db, user=current_user, data=data)


@router.post(
    "/batch",
    response_model=List[TaskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Batch create tasks (e.g. approved AI generated tasks)",
    description="Creates multiple tasks at once under a project.",
)
def create_tasks_batch(
    tasks_data: List[TaskCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    created = []
    for item in tasks_data:
        task_res = TaskService.create_task(db, user=current_user, data=item)
        created.append(task_res)
    return created


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID",
    description="Retrieves a single task, verifying project ownership or assignee rights.",
)
def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    return TaskService.get_task(db, task_id=task_id, user_id=current_user.id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
    description="Updates task properties with authorization verification.",
)
def update_task(
    task_id: str,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    return TaskService.update_task(db, task_id=task_id, user=current_user, data=data)


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Quick update task status",
    description="Updates only the workflow status of a task ('todo', 'in_progress', 'done').",
)
def update_task_status(
    task_id: str,
    status_data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    return TaskService.update_task(
        db, task_id=task_id, user=current_user, data=TaskUpdate(status=status_data.status)
    )


@router.patch(
    "/{task_id}/priority",
    response_model=TaskResponse,
    summary="Quick update task priority",
    description="Updates only the priority of a task.",
)
def update_task_priority(
    task_id: str,
    priority_data: TaskPriorityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    return TaskService.update_task(
        db, task_id=task_id, user=current_user, data=TaskUpdate(priority=priority_data.priority)
    )


@router.delete(
    "/{task_id}",
    summary="Delete task",
    description="Removes a task from a project.",
)
def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return TaskService.delete_task(db, task_id=task_id, user=current_user)
