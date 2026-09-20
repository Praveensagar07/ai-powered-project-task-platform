"""User database entity."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    """Return timezone-aware current UTC timestamp."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a unique identifier string."""
    return str(uuid.uuid4())


class User(Base):
    """User entity representing an authenticated account."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="Full Stack Engineer")
    avatar: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True, default="Passionate developer building smart digital products.")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    # Relationships
    projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    assigned_tasks = relationship(
        "Task",
        back_populates="assignee",
    )
    activities = relationship(
        "Activity",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
