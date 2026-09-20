"""Project management service with strict ownership authorization and progress metrics."""

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate


class ProjectService:
    """Manages project operations with database transactions and ownership enforcement."""

    @staticmethod
    def _to_response(project: Project) -> ProjectResponse:
        total = len(project.tasks) if project.tasks else 0
        completed = sum(1 for t in project.tasks if t.status == "done") if project.tasks else 0
        pct = int((completed / total) * 100) if total > 0 else 0

        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            priority=project.priority,
            category=project.category,
            due_date=project.due_date,
            owner_id=project.owner_id,
            created_at=project.created_at,
            updated_at=project.updated_at,
            total_tasks=total,
            completed_tasks=completed,
            progress_percentage=pct,
        )

    @classmethod
    def list_projects(
        cls,
        db: Session,
        user_id: str,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[ProjectResponse]:
        """List all projects owned by the user, with optional filters."""
        query = db.query(Project).filter(Project.owner_id == user_id)

        if status_filter and status_filter != "all":
            query = query.filter(Project.status == status_filter)
        if priority_filter and priority_filter != "all":
            query = query.filter(Project.priority == priority_filter)
        if search:
            pattern = f"%{search.strip().lower()}%"
            query = query.filter(
                (Project.name.ilike(pattern)) | (Project.description.ilike(pattern))
            )

        projects = query.order_by(Project.created_at.desc()).all()
        return [cls._to_response(p) for p in projects]

    @classmethod
    def get_project(cls, db: Session, project_id: str, user_id: str) -> ProjectResponse:
        """Retrieve a specific project, verifying ownership authorization."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )
        if project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have authorization to view this private project.",
            )
        return cls._to_response(project)

    @classmethod
    def create_project(cls, db: Session, user: User, data: ProjectCreate) -> ProjectResponse:
        """Create a new project owned by current user."""
        project = Project(
            name=data.name.strip(),
            description=data.description.strip() if data.description else None,
            status=data.status,
            priority=data.priority,
            category=data.category or "Engineering",
            due_date=data.due_date,
            owner_id=user.id,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        # Log activity
        activity = Activity(
            user_id=user.id,
            user_name=user.name,
            user_avatar=user.avatar,
            type="project_created",
            title=f"Created project '{project.name}'",
            description=f"Initialized new {project.priority} priority project in {project.category}.",
            target_type="project",
            target_id=project.id,
        )
        db.add(activity)
        db.commit()

        return cls._to_response(project)

    @classmethod
    def update_project(
        cls, db: Session, project_id: str, user: User, data: ProjectUpdate
    ) -> ProjectResponse:
        """Update existing project details after verifying ownership."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )
        if project.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this project.",
            )

        update_dict = data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(project, key, val)

        db.commit()
        db.refresh(project)

        # Log activity
        activity = Activity(
            user_id=user.id,
            user_name=user.name,
            user_avatar=user.avatar,
            type="project_updated",
            title=f"Updated project '{project.name}'",
            description="Modified project specifications.",
            target_type="project",
            target_id=project.id,
        )
        db.add(activity)
        db.commit()

        return cls._to_response(project)

    @classmethod
    def delete_project(cls, db: Session, project_id: str, user: User) -> dict:
        """Delete a project and cascade delete all its tasks, verifying ownership."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )
        if project.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this project.",
            )

        name = project.name
        db.delete(project)
        db.commit()

        # Log activity
        activity = Activity(
            user_id=user.id,
            user_name=user.name,
            user_avatar=user.avatar,
            type="project_deleted",
            title=f"Deleted project '{name}'",
            description="Removed project and all associated tasks.",
            target_type="project",
            target_id=project_id,
        )
        db.add(activity)
        db.commit()

        return {"message": f"Project '{name}' was deleted successfully."}
