"""Activity logging and timeline service."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.schemas.activity import ActivityResponse


class ActivityService:
    """Retrieves and manages audit activity records."""

    @staticmethod
    def list_activities(
        db: Session,
        user_id: str,
        limit: int = 50,
        activity_type: Optional[str] = None,
    ) -> List[ActivityResponse]:
        """Fetch chronological activity feed for user's actions."""
        query = db.query(Activity).filter(Activity.user_id == user_id)

        if activity_type and activity_type != "all":
            query = query.filter(Activity.type == activity_type)

        records = query.order_by(Activity.created_at.desc()).limit(limit).all()
        return [ActivityResponse.model_validate(r) for r in records]
