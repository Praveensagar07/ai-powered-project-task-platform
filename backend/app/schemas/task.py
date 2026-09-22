"""Task Pydantic schemas."""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

TaskStatus = Literal["todo", "in_progress", "done"]
TaskPriority = Literal["low", "medium", "high", "critical"]


class TaskBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=180, description="Task title")
    description: Optional[str] = Field(None, max_length=3000, description="Detailed description")
    project_id: str = Field(..., description="Associated project ID")
    assignee_id: Optional[str] = Field(None, description="Assigned user ID")
    status: TaskStatus = Field("todo", description="Workflow state")
    priority: TaskPriority = Field("medium", description="Urgency priority")
    due_date: Optional[datetime] = Field(None, description="Due date")
    tags: Optional[str] = Field("feature", max_length=255, description="Comma-delimited tags")
    estimated_hours: Optional[float] = Field(4.0, ge=0.1, le=1000.0, description="Estimated work hours")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=180)
    description: Optional[str] = Field(None, max_length=3000)
    project_id: Optional[str] = None
    assignee_id: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    tags: Optional[str] = Field(None, max_length=255)
    estimated_hours: Optional[float] = Field(None, ge=0.1, le=1000.0)


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskPriorityUpdate(BaseModel):
    priority: TaskPriority


class TaskResponse(TaskBase):
    id: str
    project_name: Optional[str] = None
    assignee_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
