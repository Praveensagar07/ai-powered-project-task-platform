"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-22 13:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="Full Stack Engineer"),
        sa.Column("avatar", sa.String(length=255), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. Create projects table
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("priority", sa.String(length=50), nullable=False, server_default="medium"),
        sa.Column("category", sa.String(length=60), nullable=False, server_default="Engineering"),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owner_id", sa.String(length=64), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('planning', 'active', 'completed', 'on_hold')",
            name="check_project_status",
        ),
        sa.CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')",
            name="check_project_priority",
        ),
    )
    op.create_index("ix_projects_id", "projects", ["id"])
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_priority", "projects", ["priority"])
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])

    # 3. Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assignee_id", sa.String(length=64), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="todo"),
        sa.Column("priority", sa.String(length=50), nullable=False, server_default="medium"),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tags", sa.String(length=255), nullable=True, server_default="feature"),
        sa.Column("estimated_hours", sa.Float(), nullable=True, server_default="4.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('todo', 'in_progress', 'done')",
            name="check_task_status",
        ),
        sa.CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')",
            name="check_task_priority",
        ),
    )
    op.create_index("ix_tasks_id", "tasks", ["id"])
    op.create_index("ix_tasks_project_id", "tasks", ["project_id"])
    op.create_index("ix_tasks_assignee_id", "tasks", ["assignee_id"])
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_priority", "tasks", ["priority"])
    op.create_index("ix_tasks_due_date", "tasks", ["due_date"])

    # 4. Create activities table
    op.create_table(
        "activities",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_name", sa.String(length=100), nullable=False),
        sa.Column("user_avatar", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_type", sa.String(length=50), nullable=False, server_default="general"),
        sa.Column("target_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_activities_id", "activities", ["id"])
    op.create_index("ix_activities_user_id", "activities", ["user_id"])
    op.create_index("ix_activities_type", "activities", ["type"])
    op.create_index("ix_activities_created_at", "activities", ["created_at"])


def downgrade() -> None:
    op.drop_table("activities")
    op.drop_table("tasks")
    op.drop_table("projects")
    op.drop_table("users")
