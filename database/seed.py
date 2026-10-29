"""Idempotently seed ten fictional prospects for the local Lonza demo."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from config import get_settings
from database.models import Prospect


SAMPLE_PROSPECTS: tuple[dict[str, object], ...] = (
    {
        "company_name": "Northstar Cellworks",
        "industry": "Cell & Gene Therapy",
        "opportunity_description": "Process development and GMP manufacturing support for an early-stage autologous cell therapy.",
        "opportunity_stage": "Qualified",
        "opportunity_value_usd": Decimal("1850000.00"),
        "region": "North America",
        "risk_level": "Medium",
    },
    {
        "company_name": "HelixNova Biologics",
        "industry": "Biotech",
        "opportunity_description": "Scale-up and analytical development for a novel monoclonal antibody program.",
        "opportunity_stage": "Negotiation",
        "opportunity_value_usd": Decimal("2400000.00"),
        "region": "Europe",
        "risk_level": "High",
    },
    {
        "company_name": "CedarBridge Pharma",
        "industry": "Pharma",
        "opportunity_description": "Commercial supply planning and technology transfer for a specialty injectable.",
        "opportunity_stage": "Proposal Sent",
        "opportunity_value_usd": Decimal("1250000.00"),
        "region": "Europe",
        "risk_level": "Low",
    },
    {
        "company_name": "BluePeak Therapeutics",
        "industry": "Biotech",
        "opportunity_description": "Early clinical biologics manufacturing and process characterization.",
        "opportunity_stage": "In Discussion",
        "opportunity_value_usd": Decimal("875000.00"),
        "region": "North America",
        "risk_level": "Medium",
    },
    {
        "company_name": "Asterion Vector Labs",
        "industry": "Cell & Gene Therapy",
        "opportunity_description": "Viral vector process development with a potential path to clinical manufacturing.",
        "opportunity_stage": "New",
        "opportunity_value_usd": Decimal("3100000.00"),
        "region": "APAC",
        "risk_level": "High",
    },
    {
        "company_name": "Meridian Contract Services",
        "industry": "CDMO",
        "opportunity_description": "Drug product fill-finish and packaging services for a late-stage program.",
        "opportunity_stage": "Qualified",
        "opportunity_value_usd": Decimal("980000.00"),
        "region": "Europe",
        "risk_level": "Low",
    },
    {
        "company_name": "Redwood Immunology",
        "industry": "Biotech",
        "opportunity_description": "Clinical manufacturing slot for an immunology biologic with an accelerated timeline.",
        "opportunity_stage": "Proposal Sent",
        "opportunity_value_usd": Decimal("1650000.00"),
        "region": "North America",
        "risk_level": "High",
    },
    {
        "company_name": "Eastwind BioPharma",
        "industry": "Pharma",
        "opportunity_description": "Analytical testing and stability services for a regional product launch.",
        "opportunity_stage": "Closed Won",
        "opportunity_value_usd": Decimal("720000.00"),
        "region": "APAC",
        "risk_level": "Low",
    },
    {
        "company_name": "SilverFern Bioprocess",
        "industry": "CDMO",
        "opportunity_description": "Process validation and manufacturing support for a biosimilar candidate.",
        "opportunity_stage": "Negotiation",
        "opportunity_value_usd": Decimal("2150000.00"),
        "region": "Europe",
        "risk_level": "Medium",
    },
    {
        "company_name": "Cobalt Ridge Therapeutics",
        "industry": "Biotech",
        "opportunity_description": "Development services for a recombinant protein entering first-in-human studies.",
        "opportunity_stage": "Closed Lost",
        "opportunity_value_usd": Decimal("540000.00"),
        "region": "North America",
        "risk_level": "Low",
    },
)


def seed_prospects() -> int:
    """Insert missing sample companies and return the number inserted."""
    settings = get_settings()
    engine = create_engine(settings.database_admin_url, pool_pre_ping=True)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    inserted = 0
    try:
        with factory() as session:
            for item in SAMPLE_PROSPECTS:
                existing = session.scalar(
                    select(Prospect.prospect_id).where(
                        Prospect.company_name == item["company_name"]
                    )
                )
                if existing is not None:
                    continue
                session.add(Prospect(prospect_id=uuid4(), **item))
                inserted += 1
            session.commit()
    finally:
        engine.dispose()
    return inserted


if __name__ == "__main__":
    count = seed_prospects()
    print(f"Inserted {count} prospect record(s).")
