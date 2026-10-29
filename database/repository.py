"""Repository pattern for read-only prospect lookup and filtering."""

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from database.db import get_session_factory
from database.models import Prospect


class ProspectRepository:
    """Encapsulate all prospect queries used by the MCP layer."""

    def __init__(self, session_factory: sessionmaker[Session] | None = None) -> None:
        self._session_factory = session_factory

    def get_prospects(
        self,
        industry: str | None = None,
        stage: str | None = None,
        region: str | None = None,
        risk_level: str | None = None,
        limit: int = 100,
    ) -> list[Prospect]:
        """Return prospects matching any supplied filters, newest first."""
        factory = self._session_factory or get_session_factory()
        statement = select(Prospect)
        for column, value in (
            (Prospect.industry, industry),
            (Prospect.opportunity_stage, stage),
            (Prospect.region, region),
            (Prospect.risk_level, risk_level),
        ):
            if value:
                statement = statement.where(column.ilike(value.strip()))
        statement = statement.order_by(Prospect.opportunity_value_usd.desc(), Prospect.company_name).limit(limit)
        with factory() as session:
            return list(session.scalars(statement).all())
