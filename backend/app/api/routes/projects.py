"""Projects API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get(
    "",
    response_model=List[ProjectResponse],
    summary="List all user projects",
    description="Returns projects belonging to the authenticated user with optional filtering by status, priority, or search term.",
)
def list_projects(
    status: Optional[str] = Query(None, description="Filter by status ('planning', 'active', 'completed', 'on_hold')"),
    priority: Optional[str] = Query(None, description="Filter by priority ('low', 'medium', 'high', 'critical')"),
    search: Optional[str] = Query(None, description="Search keyword matching title or description"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ProjectResponse]:
    return ProjectService.list_projects(
        db,
        user_id=current_user.id,
        status_filter=status,
        priority_filter=priority,
        search=search,
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Creates a project owned by the authenticated user and initializes activity log.",
)
def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    return ProjectService.create_project(db, user=current_user, data=data)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
    description="Retrieves a specific project, verifying ownership authorization.",
)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    return ProjectService.get_project(db, project_id=project_id, user_id=current_user.id)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Modifies an existing project owned by the authenticated user.",
)
def update_project(
    project_id: str,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    return ProjectService.update_project(
        db, project_id=project_id, user=current_user, data=data
    )


@router.delete(
    "/{project_id}",
    summary="Delete project",
    description="Permanently deletes a project and cascade-deletes all associated tasks.",
)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return ProjectService.delete_project(db, project_id=project_id, user=current_user)
