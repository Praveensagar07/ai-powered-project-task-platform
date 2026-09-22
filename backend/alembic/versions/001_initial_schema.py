"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-20 12:00:00.000000

Baseline migration representing the Week 3 schema.
Safely detects whether baseline tables already exist to prevent duplicate table creation.
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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # 1. users table
    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("email", sa.String(length=120), nullable=False),
            sa.Column("role", sa.String(length=50), nullable=False, server_default="developer"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_users_id", "users", ["id"])
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. projects table
    if "projects" not in existing_tables:
        op.create_table(
            "projects",
            sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="planning"),
            sa.Column("priority", sa.String(length=50), nullable=False, server_default="medium"),
            sa.Column("owner_id", sa.String(length=64), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.CheckConstraint(
                "status IN ('planning', 'active', 'completed', 'archived')",
                name="check_project_status",
            ),
            sa.CheckConstraint(
                "priority IN ('low', 'medium', 'high', 'critical')",
                name="check_project_priority",
            ),
        )
        op.create_index("ix_projects_id", "projects", ["id"])
        op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
        op.create_index("ix_projects_status", "projects", ["status"])

    # 3. tasks table
    if "tasks" not in existing_tables:
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
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.CheckConstraint(
                "status IN ('todo', 'in-progress', 'done')",
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


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "tasks" in existing_tables:
        op.drop_table("tasks")
    if "projects" in existing_tables:
        op.drop_table("projects")
    if "users" in existing_tables:
        op.drop_table("users")
