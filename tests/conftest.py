from decimal import Decimal
from uuid import uuid4

import pytest

from database.models import Prospect


@pytest.fixture
def sample_prospect() -> Prospect:
    return Prospect(
        prospect_id=uuid4(),
        company_name="HelixNova Biologics",
        industry="Biotech",
        opportunity_description="Scale-up and analytical development for a monoclonal antibody program.",
        opportunity_stage="Negotiation",
        opportunity_value_usd=Decimal("2400000.00"),
        region="Europe",
        risk_level="High",
    )
