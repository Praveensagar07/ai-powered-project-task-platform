"""Activity Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ActivityBase(BaseModel):
    type: str = Field(..., max_length=64, description="Activity type identifier")
    title: str = Field(..., max_length=200, description="Short activity description")
    description: Optional[str] = Field(None, description="Extended activity details")
    target_type: str = Field("general", max_length=50)
    target_id: Optional[str] = Field(None, max_length=64)


class ActivityCreate(ActivityBase):
    user_id: str
    user_name: str
    user_avatar: Optional[str] = None


class ActivityResponse(ActivityBase):
    id: str
    user_id: str
    user_name: str
    user_avatar: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
