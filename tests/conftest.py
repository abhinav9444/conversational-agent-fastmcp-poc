from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from database.models import Project


@pytest.fixture
def sample_project() -> Project:
    return Project(
        id=uuid4(),
        project_name="Project Orion",
        owner="John Doe",
        status="Active",
        description="AI agent platform modernization initiative",
        budget=Decimal("500000.00"),
        start_date=date(2025, 1, 15),
        end_date=date(2027, 6, 30),
    )
