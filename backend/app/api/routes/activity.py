"""Activity feed API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.activity import ActivityResponse
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/activity", tags=["Activity"])


@router.get(
    "",
    response_model=List[ActivityResponse],
    summary="Get user activity log",
    description="Returns chronological audit trail of project creations, task modifications, and AI generation actions.",
)
def list_activities(
    limit: int = Query(50, ge=1, le=200, description="Max activities to return"),
    type: Optional[str] = Query(None, description="Filter by activity type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ActivityResponse]:
    return ActivityService.list_activities(
        db, user_id=current_user.id, limit=limit, activity_type=type
    )
