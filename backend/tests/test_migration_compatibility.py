"""Integration test verifying migration compatibility from Week 3 schema to Week 4 schema."""

import os
import tempfile
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine, text, inspect
from alembic.config import Config
from alembic import command

from app.core.security import verify_password
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.activity import Activity
from sqlalchemy.orm import sessionmaker


def test_week3_to_week4_migration_preserves_data():
    """Verify upgrading an existing Week 3 database preserves all data and adds Week 4 capabilities."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        test_db_path = tf.name

    try:
        db_url = f"sqlite:///{test_db_path}"
        engine = create_engine(db_url)

        # 1. Simulate Week 3 existing database schema
        with engine.begin() as conn:
            # Week 3 users table (no password_hash, avatar, bio)
            conn.execute(
                text(
                    """
                    CREATE TABLE users (
                        id VARCHAR(64) PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        role VARCHAR(50) NOT NULL DEFAULT 'developer',
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    );
                    """
                )
            )
            # Week 3 projects table (no category, due_date)
            conn.execute(
                text(
                    """
                    CREATE TABLE projects (
                        id VARCHAR(64) PRIMARY KEY,
                        name VARCHAR(120) NOT NULL,
                        description TEXT,
                        status VARCHAR(50) NOT NULL DEFAULT 'planning',
                        priority VARCHAR(50) NOT NULL DEFAULT 'medium',
                        owner_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    );
                    """
                )
            )
            # Week 3 tasks table (no tags, estimated_hours; in-progress hyphen)
            conn.execute(
                text(
                    """
                    CREATE TABLE tasks (
                        id VARCHAR(64) PRIMARY KEY,
                        title VARCHAR(150) NOT NULL,
                        description TEXT,
                        project_id VARCHAR(64) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                        assignee_id VARCHAR(64) REFERENCES users(id) ON DELETE SET NULL,
                        status VARCHAR(50) NOT NULL DEFAULT 'todo',
                        priority VARCHAR(50) NOT NULL DEFAULT 'medium',
                        due_date TIMESTAMP,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    );
                    """
                )
            )

            # Insert existing Week 3 records
            now_iso = datetime.now(timezone.utc).isoformat()
            conn.execute(
                text(
                    """
                    INSERT INTO users (id, name, email, role, created_at, updated_at)
                    VALUES ('usr_alex_rivera', 'Alex Rivera', 'alex.rivera@example.com', 'admin', :now, :now);
                    """
                ),
                {"now": now_iso},
            )
            conn.execute(
                text(
                    """
                    INSERT INTO projects (id, name, description, status, priority, owner_id, created_at, updated_at)
                    VALUES ('proj_cloud_migration', 'Cloud Platform Migration', 'AWS to Hybrid Cloud', 'active', 'high', 'usr_alex_rivera', :now, :now);
                    """
                ),
                {"now": now_iso},
            )
            conn.execute(
                text(
                    """
                    INSERT INTO tasks (id, title, description, project_id, assignee_id, status, priority, due_date, created_at, updated_at)
                    VALUES ('task_vpc_setup', 'Setup VPC Peering', 'Connect clusters', 'proj_cloud_migration', 'usr_alex_rivera', 'in-progress', 'critical', :now, :now, :now);
                    """
                ),
                {"now": now_iso},
            )

            # Create alembic_version table representing Week 3 revision
            conn.execute(
                text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY);")
            )
            conn.execute(
                text("INSERT INTO alembic_version (version_num) VALUES ('001_initial_schema');")
            )

        # 2. Run Alembic upgrade head to Week 4
        alembic_ini_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
        cfg = Config(alembic_ini_path)
        cfg.set_main_option("sqlalchemy.url", db_url)

        # Set environment variable so get_settings() in env.py resolves the test db
        old_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = db_url
        try:
            # Clear Settings cache to ensure env.py gets the test database URL
            from app.core.config import get_settings
            get_settings.cache_clear()

            command.upgrade(cfg, "head")
        finally:
            if old_db_url:
                os.environ["DATABASE_URL"] = old_db_url
            else:
                os.environ.pop("DATABASE_URL", None)
            get_settings.cache_clear()

        # 3. Verify the migrated schema
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        assert "users" in tables
        assert "projects" in tables
        assert "tasks" in tables
        assert "activities" in tables

        user_columns = {c["name"] for c in inspector.get_columns("users")}
        assert "password_hash" in user_columns
        assert "avatar" in user_columns
        assert "bio" in user_columns

        proj_columns = {c["name"] for c in inspector.get_columns("projects")}
        assert "category" in proj_columns
        assert "due_date" in proj_columns

        task_columns = {c["name"] for c in inspector.get_columns("tasks")}
        assert "tags" in task_columns
        assert "estimated_hours" in task_columns

        # 4. Verify existing Week 3 data is preserved and accessible
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            # Query existing user
            alex = session.query(User).filter(User.id == "usr_alex_rivera").first()
            assert alex is not None
            assert alex.name == "Alex Rivera"
            assert alex.email == "alex.rivera@example.com"
            assert alex.role == "admin"
            # Verify password hash was backfilled and authenticates with default Password123!
            assert verify_password("Password123!", alex.password_hash)

            # Query existing project
            proj = session.query(Project).filter(Project.id == "proj_cloud_migration").first()
            assert proj is not None
            assert proj.name == "Cloud Platform Migration"
            assert proj.category == "Engineering"

            # Query existing task
            task = session.query(Task).filter(Task.id == "task_vpc_setup").first()
            assert task is not None
            assert task.title == "Setup VPC Peering"
            # Status should have been normalized from 'in-progress' to 'in_progress'
            assert task.status == "in_progress"
            assert task.tags == "feature"
            assert task.estimated_hours == 4.0

            # 5. Verify Week 4 models can insert new activity log
            activity = Activity(
                user_id=alex.id,
                user_name=alex.name,
                type="project_updated",
                title="Migrated Week 3 Project",
                target_type="project",
                target_id=proj.id,
            )
            session.add(activity)
            session.commit()

            act_count = session.query(Activity).count()
            assert act_count == 1
        finally:
            session.close()

    finally:
        engine.dispose()
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except Exception:
                pass
