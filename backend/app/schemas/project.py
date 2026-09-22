"""Project Pydantic schemas."""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

ProjectStatus = Literal["planning", "active", "completed", "on_hold", "archived"]
ProjectPriority = Literal["low", "medium", "high", "critical"]


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, description="Project title")
    description: Optional[str] = Field(None, max_length=2000, description="Project overview")
    status: ProjectStatus = Field("active", description="Lifecycle status")
    priority: ProjectPriority = Field("medium", description="Priority level")
    category: Optional[str] = Field("Engineering", max_length=60, description="Category or department")
    due_date: Optional[datetime] = Field(None, description="Target completion date")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    category: Optional[str] = Field(None, max_length=60)
    due_date: Optional[datetime] = None


class ProjectResponse(ProjectBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    total_tasks: int = 0
    completed_tasks: int = 0
    progress_percentage: int = 0

    model_config = ConfigDict(from_attributes=True)
