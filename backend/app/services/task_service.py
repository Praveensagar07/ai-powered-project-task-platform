"""Task management service with authorization, status workflows, and activity tracking."""

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate


class TaskService:
    """Manages tasks with project ownership validation and lifecycle transitions."""

    @staticmethod
    def _to_response(task: Task) -> TaskResponse:
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            assignee_id=task.assignee_id,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            tags=task.tags,
            estimated_hours=task.estimated_hours,
            project_name=task.project.name if task.project else None,
            assignee_name=task.assignee.name if task.assignee else None,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    @classmethod
    def list_tasks(
        cls,
        db: Session,
        user_id: str,
        project_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[TaskResponse]:
        """List tasks belonging to user's projects or assigned to user."""
        query = (
            db.query(Task)
            .join(Project, Task.project_id == Project.id)
            .filter((Project.owner_id == user_id) | (Task.assignee_id == user_id))
        )

        if project_id and project_id != "all":
            query = query.filter(Task.project_id == project_id)
        if status_filter and status_filter != "all":
            query = query.filter(Task.status == status_filter)
        if priority_filter and priority_filter != "all":
            query = query.filter(Task.priority == priority_filter)
        if search:
            pattern = f"%{search.strip().lower()}%"
            query = query.filter(
                (Task.title.ilike(pattern))
                | (Task.description.ilike(pattern))
                | (Project.name.ilike(pattern))
            )

        tasks = query.order_by(Task.created_at.desc()).all()
        return [cls._to_response(t) for t in tasks]

    @classmethod
    def get_task(cls, db: Session, task_id: str, user_id: str) -> TaskResponse:
        """Retrieve task details and verify access rights."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        # Check that user owns project or is assigned to task
        if task.project.owner_id != user_id and task.assignee_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to view this task.",
            )
        return cls._to_response(task)

    @classmethod
    def create_task(cls, db: Session, user: User, data: TaskCreate) -> TaskResponse:
        """Create a new task under a project owned by the user."""
        project = db.query(Project).filter(Project.id == data.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target project does not exist.",
            )
        if project.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only add tasks to projects you own.",
            )

        # Default assignee to project owner if None
        assignee_id = data.assignee_id if data.assignee_id else user.id

        task = Task(
            title=data.title.strip(),
            description=data.description.strip() if data.description else None,
            project_id=data.project_id,
            assignee_id=assignee_id,
            status=data.status,
            priority=data.priority,
            due_date=data.due_date,
            tags=data.tags or "task",
            estimated_hours=data.estimated_hours or 4.0,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        # Log activity
        activity = Activity(
            user_id=user.id,
            user_name=user.name,
            user_avatar=user.avatar,
            type="task_created",
            title=f"Created task '{task.title}'",
            description=f"Added to project '{project.name}' with {task.priority} priority.",
            target_type="task",
            target_id=task.id,
        )
        db.add(activity)
        db.commit()

        return cls._to_response(task)

    @classmethod
    def update_task(
        cls, db: Session, task_id: str, user: User, data: TaskUpdate
    ) -> TaskResponse:
        """Update an existing task with permission verification."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        if task.project.owner_id != user.id and task.assignee_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have authorization to update this task.",
            )

        old_status = task.status
        update_dict = data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(task, key, val)

        db.commit()
        db.refresh(task)

        # Log status transition or update
        if "status" in update_dict and update_dict["status"] != old_status:
            act_type = "task_completed" if update_dict["status"] == "done" else "task_status_changed"
            title = f"Completed task '{task.title}'" if update_dict["status"] == "done" else f"Moved '{task.title}' to {task.status}"
            activity = Activity(
                user_id=user.id,
                user_name=user.name,
                user_avatar=user.avatar,
                type=act_type,
                title=title,
                description=f"Status transitioned from {old_status} to {task.status}.",
                target_type="task",
                target_id=task.id,
            )
        else:
            activity = Activity(
                user_id=user.id,
                user_name=user.name,
                user_avatar=user.avatar,
                type="task_updated",
                title=f"Updated task '{task.title}'",
                description="Task details updated.",
                target_type="task",
                target_id=task.id,
            )
        db.add(activity)
        db.commit()

        return cls._to_response(task)

    @classmethod
    def delete_task(cls, db: Session, task_id: str, user: User) -> dict:
        """Delete a task if user owns the project."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        if task.project.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owners can delete tasks.",
            )

        title = task.title
        db.delete(task)
        db.commit()

        # Log activity
        activity = Activity(
            user_id=user.id,
            user_name=user.name,
            user_avatar=user.avatar,
            type="task_deleted",
            title=f"Deleted task '{title}'",
            description="Task removed from project.",
            target_type="task",
            target_id=task_id,
        )
        db.add(activity)
        db.commit()

        return {"message": f"Task '{title}' was deleted successfully."}
