"""Activity / audit trail database entity."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    """Return timezone-aware current UTC timestamp."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a unique identifier string."""
    return str(uuid.uuid4())


class Activity(Base):
    """Activity entity logging actions for audit and dashboard feed."""

    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid, index=True)
    user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False, default="general")
    target_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, index=True
    )

    # Relationships
    user = relationship("User", back_populates="activities")
