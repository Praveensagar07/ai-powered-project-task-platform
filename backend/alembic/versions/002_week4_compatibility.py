"""002_week4_compatibility

Revision ID: 002_week4_compatibility
Revises: 001_initial_schema
Create Date: 2026-09-22 14:00:00.000000

Non-destructive compatibility migration from Week 3 to Week 4:
- Reuses existing users, projects, and tasks tables without data loss.
- Safely adds missing Week 4 columns (users.password_hash, avatar, bio; projects.category, due_date; tasks.tags, estimated_hours).
- Sets safe default values and backfills password_hash so existing Week 3 users can authenticate immediately with 'Password123!'.
- Updates status check constraints to support both Week 3 ('archived', 'in-progress') and Week 4 ('on_hold', 'in_progress') values.
- Creates the new activities audit table and indices.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

from app.core.security import hash_password

# revision identifiers, used by Alembic.
revision: str = "002_week4_compatibility"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Default secure hash for "Password123!" computed using application cryptography
DEFAULT_PASSWORD_HASH = hash_password("Password123!")
DEFAULT_AVATAR = (
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
)
DEFAULT_BIO = "Passionate developer building smart digital products."


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # ----------------------------------------------------
    # 1. Upgrade users table (add auth & profile fields)
    # ----------------------------------------------------
    if "users" in existing_tables:
        user_cols = {col["name"] for col in inspector.get_columns("users")}
        with op.batch_alter_table("users") as batch_op:
            if "password_hash" not in user_cols:
                batch_op.add_column(
                    sa.Column(
                        "password_hash",
                        sa.String(length=255),
                        nullable=False,
                        server_default=DEFAULT_PASSWORD_HASH,
                    )
                )
            if "avatar" not in user_cols:
                batch_op.add_column(
                    sa.Column(
                        "avatar",
                        sa.String(length=255),
                        nullable=False,
                        server_default=DEFAULT_AVATAR,
                    )
                )
            if "bio" not in user_cols:
                batch_op.add_column(
                    sa.Column(
                        "bio",
                        sa.Text(),
                        nullable=True,
                        server_default=DEFAULT_BIO,
                    )
                )

    # ----------------------------------------------------
    # 2. Upgrade projects table (add category & due_date)
    # ----------------------------------------------------
    if "projects" in existing_tables:
        proj_cols = {col["name"] for col in inspector.get_columns("projects")}
        with op.batch_alter_table("projects") as batch_op:
            if "category" not in proj_cols:
                batch_op.add_column(
                    sa.Column(
                        "category",
                        sa.String(length=60),
                        nullable=False,
                        server_default="Engineering",
                    )
                )
            if "due_date" not in proj_cols:
                batch_op.add_column(
                    sa.Column("due_date", sa.DateTime(timezone=True), nullable=True)
                )

        proj_indexes = {ix["name"] for ix in inspector.get_indexes("projects")}
        if "ix_projects_priority" not in proj_indexes:
            op.create_index("ix_projects_priority", "projects", ["priority"])

        # Update check constraints on PostgreSQL
        if bind.dialect.name == "postgresql":
            op.execute("ALTER TABLE projects DROP CONSTRAINT IF EXISTS check_project_status")
            op.execute(
                "ALTER TABLE projects ADD CONSTRAINT check_project_status "
                "CHECK (status IN ('planning', 'active', 'completed', 'archived', 'on_hold'))"
            )

    # ----------------------------------------------------
    # 3. Upgrade tasks table (add tags & estimated_hours)
    # ----------------------------------------------------
    if "tasks" in existing_tables:
        task_cols = {col["name"] for col in inspector.get_columns("tasks")}
        with op.batch_alter_table("tasks") as batch_op:
            if "tags" not in task_cols:
                batch_op.add_column(
                    sa.Column(
                        "tags",
                        sa.String(length=255),
                        nullable=True,
                        server_default="feature",
                    )
                )
            if "estimated_hours" not in task_cols:
                batch_op.add_column(
                    sa.Column(
                        "estimated_hours",
                        sa.Float(),
                        nullable=True,
                        server_default="4.0",
                    )
                )

        task_indexes = {ix["name"] for ix in inspector.get_indexes("tasks")}
        if "ix_tasks_due_date" not in task_indexes:
            op.create_index("ix_tasks_due_date", "tasks", ["due_date"])

        # STEP 1: Remove and replace OLD check constraint on PostgreSQL BEFORE updating existing task rows
        # This prevents psycopg.errors.CheckViolation when updating 'in-progress' -> 'in_progress'
        if bind.dialect.name == "postgresql":
            op.execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS check_task_status")
            # Install transitional constraint allowing both 'in_progress' and 'in-progress'
            op.execute(
                "ALTER TABLE tasks ADD CONSTRAINT check_task_status "
                "CHECK (status IN ('todo', 'in_progress', 'in-progress', 'done'))"
            )

        # STEP 2: Now that constraint allows 'in_progress', normalize existing task rows
        op.execute("UPDATE tasks SET status = 'in_progress' WHERE status = 'in-progress'")

        # STEP 3: Tighten to final application statuses ('todo', 'in_progress', 'done')
        if bind.dialect.name == "postgresql":
            op.execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS check_task_status")
            op.execute(
                "ALTER TABLE tasks ADD CONSTRAINT check_task_status "
                "CHECK (status IN ('todo', 'in_progress', 'done'))"
            )

        # STEP 4: Verify no invalid task statuses remain
        invalid_count = bind.execute(
            sa.text("SELECT COUNT(*) FROM tasks WHERE status NOT IN ('todo', 'in_progress', 'done')")
        ).scalar()
        if invalid_count and invalid_count > 0:
            raise ValueError(f"Migration error: found {invalid_count} tasks with invalid status after normalization")


    # ----------------------------------------------------
    # 4. Create activities table if not present
    # ----------------------------------------------------
    if "activities" not in existing_tables:
        op.create_table(
            "activities",
            sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
            sa.Column(
                "user_id",
                sa.String(length=64),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "activities" in existing_tables:
        op.drop_table("activities")

    if "tasks" in existing_tables:
        task_indexes = {ix["name"] for ix in inspector.get_indexes("tasks")}
        if "ix_tasks_due_date" in task_indexes:
            op.drop_index("ix_tasks_due_date", table_name="tasks")
        with op.batch_alter_table("tasks") as batch_op:
            batch_op.drop_column("estimated_hours")
            batch_op.drop_column("tags")

    if "projects" in existing_tables:
        proj_indexes = {ix["name"] for ix in inspector.get_indexes("projects")}
        if "ix_projects_priority" in proj_indexes:
            op.drop_index("ix_projects_priority", table_name="projects")
        with op.batch_alter_table("projects") as batch_op:
            batch_op.drop_column("due_date")
            batch_op.drop_column("category")

    if "users" in existing_tables:
        with op.batch_alter_table("users") as batch_op:
            batch_op.drop_column("bio")
            batch_op.drop_column("avatar")
            batch_op.drop_column("password_hash")
