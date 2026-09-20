"""Project database entity."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    """Return timezone-aware current UTC timestamp."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a unique identifier string."""
    return str(uuid.uuid4())


class Project(Base):
    """Project entity representing an initiative owned by a user."""

    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint(
            "status IN ('planning', 'active', 'completed', 'on_hold')",
            name="check_project_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')",
            name="check_project_priority",
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="medium", index=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False, default="Engineering")
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    owner_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    # Relationships
    owner = relationship("User", back_populates="projects")
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
