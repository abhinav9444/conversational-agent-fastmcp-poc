"""SQLAlchemy schema for the Lonza business-development POC."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Index, Numeric, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import Uuid


class Base(DeclarativeBase):
    """Base class for ORM models."""


class Prospect(Base):
    """One fictional prospect/opportunity used by the local demo."""

    __tablename__ = "prospects"
    __table_args__ = (
        CheckConstraint(
            "opportunity_stage IN ('New', 'Qualified', 'In Discussion', "
            "'Proposal Sent', 'Negotiation', 'Closed Won', 'Closed Lost')",
            name="ck_prospects_opportunity_stage",
        ),
        CheckConstraint(
            "region IN ('North America', 'Europe', 'APAC')",
            name="ck_prospects_region",
        ),
        CheckConstraint(
            "risk_level IN ('Low', 'Medium', 'High')",
            name="ck_prospects_risk_level",
        ),
        CheckConstraint("opportunity_value_usd >= 0", name="ck_prospects_value_nonnegative"),
        Index("ix_prospects_company_name", "company_name"),
        Index("ix_prospects_industry", "industry"),
        Index("ix_prospects_opportunity_stage", "opportunity_stage"),
    )

    prospect_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    industry: Mapped[str] = mapped_column(Text, nullable=False)
    opportunity_description: Mapped[str] = mapped_column(Text, nullable=False)
    opportunity_stage: Mapped[str] = mapped_column(Text, nullable=False)
    opportunity_value_usd: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    region: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
