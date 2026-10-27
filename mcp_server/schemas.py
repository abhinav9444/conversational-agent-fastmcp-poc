"""Pydantic validation schemas for MCP input/output."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


ProjectName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
]


class ProjectLookupInput(BaseModel):
    """Validated name for a project lookup."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    project_name: ProjectName


class ProjectInformation(BaseModel):
    """Stable JSON shape returned for a project record."""

    id: str
    project_name: str
    owner: str
    status: str
    description: str
    budget: float = Field(ge=0)
    start_date: str
    end_date: str | None
