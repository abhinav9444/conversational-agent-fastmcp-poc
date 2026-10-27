from decimal import Decimal
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.models import Base, Prospect
from database.repository import ProspectRepository


def test_repository_filters_prospects_and_sorts_by_value() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        session.add_all([
            Prospect(
                prospect_id=uuid4(), company_name="Small Bio", industry="Biotech",
                opportunity_description="Early research", opportunity_stage="Qualified",
                opportunity_value_usd=Decimal("250000.00"), region="Europe", risk_level="Low",
            ),
            Prospect(
                prospect_id=uuid4(), company_name="Large Bio", industry="Biotech",
                opportunity_description="Clinical manufacturing", opportunity_stage="Negotiation",
                opportunity_value_usd=Decimal("2400000.00"), region="Europe", risk_level="High",
            ),
            Prospect(
                prospect_id=uuid4(), company_name="Asia Pharma", industry="Pharma",
                opportunity_description="Testing services", opportunity_stage="New",
                opportunity_value_usd=Decimal("700000.00"), region="APAC", risk_level="Medium",
            ),
        ])
        session.commit()

    repo = ProspectRepository(factory)
    europe_biotech = repo.get_prospects(industry="Biotech", region="Europe")
    assert [row.company_name for row in europe_biotech] == ["Large Bio", "Small Bio"]
    assert len(repo.get_prospects(risk_level="High")) == 1
    assert len(repo.get_prospects(stage="Negotiation")) == 1
    assert len(repo.get_prospects(region="North America")) == 0
    engine.dispose()
