from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.models import Base, Project
from database.repository import ProjectRepository


def test_repository_matches_project_name_case_insensitively() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        session.add(
            Project(
                project_name="Project Orion",
                owner="John Doe",
                status="Active",
                description="AI agent platform modernization initiative",
                budget=Decimal("500000.00"),
                start_date=date(2025, 1, 15),
                end_date=date(2027, 6, 30),
            )
        )
        session.commit()

    record = ProjectRepository(factory).get_by_name("  PROJECT ORION ")
    assert record is not None
    assert record.owner == "John Doe"
    assert float(record.budget) == 500000.0
    assert ProjectRepository(factory).get_by_name("Missing Project") is None
    engine.dispose()
