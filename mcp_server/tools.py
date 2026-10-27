"""MCP tools. Database access is kept behind this layer."""

import logging
from time import perf_counter
from typing import Annotated, Any

from pydantic import Field, ValidationError

from database.repository import ProspectRepository

logger = logging.getLogger(__name__)
_repository = ProspectRepository()

Industry = Annotated[str | None, Field(default=None, max_length=100)]
Stage = Annotated[str | None, Field(default=None, max_length=50)]
Region = Annotated[str | None, Field(default=None, max_length=50)]
RiskLevel = Annotated[str | None, Field(default=None, max_length=20)]


def get_prospects(
    industry: Industry = None,
    stage: Stage = None,
    region: Region = None,
    risk_level: RiskLevel = None,
) -> dict[str, Any]:
    """Retrieve fictional business-development prospects with optional filters.

    Valid industry filters include Biotech, Pharma, CDMO, and Cell & Gene Therapy.
    Valid stages are New, Qualified, In Discussion, Proposal Sent, Negotiation,
    Closed Won, and Closed Lost. Valid regions are North America, Europe, and APAC.
    Valid risk levels are Low, Medium, and High. Returns a JSON object containing
    a prospects array and total_count. Results are read-only.
    """
    started = perf_counter()
    logger.info(
        "mcp_tool_started tool=get_prospects industry=%r stage=%r region=%r risk_level=%r",
        industry, stage, region, risk_level,
    )
    try:
        filters = {
            "industry": industry,
            "stage": stage,
            "region": region,
            "risk_level": risk_level,
        }
        try:
            for name, value in filters.items():
                if value is not None and not value.strip():
                    raise ValueError(f"{name} must not be blank")
            if stage and stage not in {
                "New", "Qualified", "In Discussion", "Proposal Sent",
                "Negotiation", "Closed Won", "Closed Lost",
            }:
                raise ValueError("stage is not a supported opportunity stage")
            if region and region not in {"North America", "Europe", "APAC"}:
                raise ValueError("region is not supported")
            if risk_level and risk_level not in {"Low", "Medium", "High"}:
                raise ValueError("risk_level must be Low, Medium, or High")
        except (ValidationError, ValueError) as exc:
            return {"error": "Invalid input", "message": str(exc)}

        rows = _repository.get_prospects(
            industry=industry,
            stage=stage,
            region=region,
            risk_level=risk_level,
        )
        prospects = [
            {
                "prospect_id": str(row.prospect_id),
                "company_name": row.company_name,
                "industry": row.industry,
                "opportunity_description": row.opportunity_description,
                "opportunity_stage": row.opportunity_stage,
                "opportunity_value_usd": float(row.opportunity_value_usd),
                "region": row.region,
                "risk_level": row.risk_level,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            }
            for row in rows
        ]
        return {"prospects": prospects, "total_count": len(prospects)}
    except Exception:
        logger.exception("mcp_tool_failed tool=get_prospects")
        return {"error": "Data retrieval failed", "prospects": []}
    finally:
        logger.info("mcp_tool_finished tool=get_prospects elapsed_ms=%.2f", (perf_counter() - started) * 1000)
