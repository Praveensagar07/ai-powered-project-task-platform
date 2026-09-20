"""Seed initial realistic development dataset."""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.activity import Activity
from app.models.project import Project
from app.models.task import Task
from app.models.user import User


def seed_database(db: Session) -> None:
    """Seed the database with a default demo user, realistic projects, and tasks if empty."""
    # Check if data already exists
    existing_user = db.query(User).first()
    if existing_user:
        return

    now = datetime.now(timezone.utc)

    # 1. Create Demo User
    demo_user = User(
        name="Praveen Sagar",
        email="praveen@example.com",
        password_hash=hash_password("Password123!"),
        role="Lead Full Stack Engineer",
        avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        bio="Full stack engineer specializing in Python, React, cloud infrastructure, and AI engineering.",
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)

    # 2. Create Projects
    proj1 = Project(
        name="AI-Powered Project Platform",
        description="Unified task and project management ecosystem featuring automated AI task generation and real-time productivity analytics.",
        status="active",
        priority="critical",
        category="Engineering",
        due_date=now + timedelta(days=14),
        owner_id=demo_user.id,
    )

    proj2 = Project(
        name="Developer Productivity Suite",
        description="Core dashboard widgets, telemetry visualization, and personalized productivity metrics tracking.",
        status="active",
        priority="high",
        category="Product",
        due_date=now + timedelta(days=21),
        owner_id=demo_user.id,
    )

    proj3 = Project(
        name="Cloud Infrastructure & CI/CD Pipeline",
        description="Automated Docker containerization, staging pipelines, and production database clustering on PostgreSQL.",
        status="planning",
        priority="medium",
        category="DevOps",
        due_date=now + timedelta(days=30),
        owner_id=demo_user.id,
    )

    db.add_all([proj1, proj2, proj3])
    db.commit()
    db.refresh(proj1)
    db.refresh(proj2)
    db.refresh(proj3)

    # 3. Create Tasks
    tasks = [
        # Project 1 Tasks
        Task(
            title="Design Relational Schema & Database Models",
            description="Create users, projects, tasks, and audit activity entities with foreign keys and cascade constraints.",
            project_id=proj1.id,
            assignee_id=demo_user.id,
            status="done",
            priority="critical",
            due_date=now - timedelta(days=2),
            tags="backend,database",
            estimated_hours=6.0,
        ),
        Task(
            title="Implement JWT Authentication & PBKDF2 Hashing",
            description="Build secure registration, credential verification, and token authentication middleware.",
            project_id=proj1.id,
            assignee_id=demo_user.id,
            status="done",
            priority="high",
            due_date=now - timedelta(days=1),
            tags="security,auth",
            estimated_hours=5.0,
        ),
        Task(
            title="Integrate AI-Assisted Task Generation Workflow",
            description="Create backend AI service with reviewable suggestion flow, allowing users to select and edit tasks.",
            project_id=proj1.id,
            assignee_id=demo_user.id,
            status="in_progress",
            priority="critical",
            due_date=now + timedelta(days=2),
            tags="ai,feature",
            estimated_hours=8.0,
        ),
        Task(
            title="Build Responsive Kanban Board & Filtering UI",
            description="Implement draggable or interactive task cards with instant status transitions and multi-criteria filters.",
            project_id=proj1.id,
            assignee_id=demo_user.id,
            status="in_progress",
            priority="high",
            due_date=now + timedelta(days=4),
            tags="frontend,ui",
            estimated_hours=7.0,
        ),
        Task(
            title="Author Comprehensive Pytest Test Suite",
            description="Cover registration, authorization, project CRUD, task workflows, and error edge cases.",
            project_id=proj1.id,
            assignee_id=demo_user.id,
            status="todo",
            priority="medium",
            due_date=now + timedelta(days=7),
            tags="testing,qa",
            estimated_hours=4.0,
        ),
        # Project 2 Tasks
        Task(
            title="Productivity Score Metric Calculation",
            description="Aggregate completion rate, velocity, and on-time task delivery into unified score.",
            project_id=proj2.id,
            assignee_id=demo_user.id,
            status="done",
            priority="medium",
            due_date=now - timedelta(days=3),
            tags="metrics",
            estimated_hours=3.5,
        ),
        Task(
            title="Dark & Light Mode Theme Context",
            description="Ensure persistent user preference with seamless CSS transitions across components.",
            project_id=proj2.id,
            assignee_id=demo_user.id,
            status="done",
            priority="low",
            due_date=now - timedelta(days=1),
            tags="ui,theme",
            estimated_hours=2.5,
        ),
        Task(
            title="Upcoming Deadlines Alert System",
            description="Highlight imminent deliverables and visually flag overdue items on dashboard.",
            project_id=proj2.id,
            assignee_id=demo_user.id,
            status="todo",
            priority="high",
            due_date=now + timedelta(days=3),
            tags="frontend",
            estimated_hours=3.0,
        ),
    ]

    db.add_all(tasks)
    db.commit()

    # 4. Create Initial Activity Records
    activities = [
        Activity(
            user_id=demo_user.id,
            user_name=demo_user.name,
            user_avatar=demo_user.avatar,
            type="project_created",
            title=f"Initialized '{proj1.name}'",
            description="Created main internship milestone project.",
            target_type="project",
            target_id=proj1.id,
            created_at=now - timedelta(days=3),
        ),
        Activity(
            user_id=demo_user.id,
            user_name=demo_user.name,
            user_avatar=demo_user.avatar,
            type="task_completed",
            title="Completed 'Design Relational Schema & Database Models'",
            description="Schema created and verified with foreign key relationships.",
            target_type="task",
            created_at=now - timedelta(days=2),
        ),
        Activity(
            user_id=demo_user.id,
            user_name=demo_user.name,
            user_avatar=demo_user.avatar,
            type="task_completed",
            title="Completed 'Implement JWT Authentication & PBKDF2 Hashing'",
            description="Secure auth pipeline and tokens verified.",
            target_type="task",
            created_at=now - timedelta(days=1),
        ),
        Activity(
            user_id=demo_user.id,
            user_name=demo_user.name,
            user_avatar=demo_user.avatar,
            type="ai_tasks_generated",
            title="Generated 5 tasks with AI",
            description="Ran AI task generation assistant for project architecture.",
            target_type="ai",
            target_id=proj1.id,
            created_at=now - timedelta(hours=4),
        ),
    ]

    db.add_all(activities)
    db.commit()
