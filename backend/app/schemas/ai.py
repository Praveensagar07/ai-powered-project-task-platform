"""AI Feature Pydantic schemas."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class AITaskItem(BaseModel):
    title: str = Field(..., min_length=3, max_length=180, description="Task title")
    description: str = Field(..., max_length=1500, description="Detailed actionable steps")
    priority: Literal["low", "medium", "high", "critical"] = Field("medium", description="Suggested priority")
    estimated_hours: float = Field(4.0, ge=0.5, le=100.0, description="Estimated work hours")
    tags: str = Field("ai-generated", description="Suggested tags")


class AITaskGenerationRequest(BaseModel):
    project_id: str = Field(..., description="Target project ID")
    project_name: str = Field(..., min_length=2, max_length=120)
    project_description: Optional[str] = Field(None, max_length=2000)
    goals: str = Field(..., min_length=3, max_length=1000, description="Primary goal or milestones")
    target_date: Optional[str] = Field(None, description="Optional target deadline")


class AITaskGenerationResponse(BaseModel):
    project_id: str
    suggested_approach: str
    tasks: List[AITaskItem]
    provider_mode: str = Field("live", description="'live' or 'fallback-heuristic'")


class AISummarizeRequest(BaseModel):
    task_id: Optional[str] = None
    title: str = Field(..., min_length=2, max_length=180)
    description: Optional[str] = Field(None, max_length=3000)
    priority: Optional[str] = Field("medium")


class AISummarizeResponse(BaseModel):
    summary: str
    key_deliverables: List[str]
    suggested_action: str
    provider_mode: str = "live"


class AIProjectDescriptionRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=120)
    category: Optional[str] = Field("Engineering")
    goals: str = Field(..., min_length=3, max_length=1000)


class AIProjectDescriptionResponse(BaseModel):
    description: str
    key_outcomes: List[str]
    provider_mode: str = "live"


class AIProductivityResponse(BaseModel):
    focus_tasks: List[str]
    productivity_tip: str
    bottleneck_warning: Optional[str] = None
    provider_mode: str = "live"
