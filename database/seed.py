"""Idempotently insert ten sample projects for local demos."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from config import get_settings
from database.models import Project


SAMPLE_PROJECTS: tuple[dict[str, object], ...] = (
    {
        "project_name": "Project Orion",
        "owner": "John Doe",
        "status": "Active",
        "description": "AI agent platform modernization initiative",
        "budget": Decimal("500000.00"),
        "start_date": date(2025, 1, 15),
        "end_date": date(2027, 6, 30),
    },
    {
        "project_name": "Project Phoenix",
        "owner": "Jane Smith",
        "status": "Planning",
        "description": "Resilience and disaster recovery platform refresh",
        "budget": Decimal("325000.00"),
        "start_date": date(2026, 2, 1),
        "end_date": date(2027, 12, 31),
    },
    {
        "project_name": "Project Atlas",
        "owner": "Jane Smith",
        "status": "Active",
        "description": "Enterprise data catalog and governance implementation",
        "budget": Decimal("420000.00"),
        "start_date": date(2025, 7, 1),
        "end_date": date(2027, 3, 31),
    },
    {
        "project_name": "Project Titan",
        "owner": "Michael Chen",
        "status": "On Hold",
        "description": "Legacy infrastructure consolidation",
        "budget": Decimal("780000.00"),
        "start_date": date(2024, 9, 1),
        "end_date": date(2027, 9, 30),
    },
    {
        "project_name": "Project Helios",
        "owner": "Priya Nair",
        "status": "Active",
        "description": "Energy usage analytics and reporting",
        "budget": Decimal("265000.00"),
        "start_date": date(2025, 3, 1),
        "end_date": date(2026, 12, 31),
    },
    {
        "project_name": "Project Nova",
        "owner": "Alex Morgan",
        "status": "Completed",
        "description": "Internal developer portal launch",
        "budget": Decimal("190000.00"),
        "start_date": date(2024, 1, 15),
        "end_date": date(2025, 5, 15),
    },
    {
        "project_name": "Project Aurora",
        "owner": "Sara Patel",
        "status": "Planning",
        "description": "Customer experience modernization",
        "budget": Decimal("610000.00"),
        "start_date": date(2026, 5, 1),
        "end_date": date(2028, 1, 31),
    },
    {
        "project_name": "Project Quantum",
        "owner": "David Kim",
        "status": "Active",
        "description": "Applied machine learning experimentation platform",
        "budget": Decimal("450000.00"),
        "start_date": date(2025, 10, 1),
        "end_date": date(2027, 10, 1),
    },
    {
        "project_name": "Project Polaris",
        "owner": "Maya Rao",
        "status": "At Risk",
        "description": "Identity lifecycle and access governance improvement",
        "budget": Decimal("385000.00"),
        "start_date": date(2025, 4, 1),
        "end_date": date(2027, 4, 1),
    },
    {
        "project_name": "Project Vertex",
        "owner": "Oliver Brown",
        "status": "Active",
        "description": "Observability and service reliability uplift",
        "budget": Decimal("295000.00"),
        "start_date": date(2026, 1, 10),
        "end_date": date(2027, 11, 30),
    },
)


def seed_projects() -> int:
    """Insert missing sample rows and return the number inserted."""
    settings = get_settings()
    engine = create_engine(settings.database_admin_url, pool_pre_ping=True)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    inserted = 0
    try:
        with factory() as session:
            for item in SAMPLE_PROJECTS:
                existing = session.scalar(
                    select(Project.id).where(Project.project_name == item["project_name"])
                )
                if existing is not None:
                    continue
                session.add(Project(id=uuid4(), **item))
                inserted += 1
            session.commit()
    finally:
        engine.dispose()
    return inserted


if __name__ == "__main__":
    count = seed_projects()
    print(f"Inserted {count} project record(s).")
