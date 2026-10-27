"""MCP tools. Database access is kept behind this layer."""

import logging
from time import perf_counter
from typing import Annotated, Any

from pydantic import Field, ValidationError

from database.repository import ProjectRepository
from mcp_server.schemas import ProjectInformation, ProjectLookupInput

logger = logging.getLogger(__name__)
_repository = ProjectRepository()


def get_project_information(
    project_name: Annotated[str, Field(min_length=1, max_length=255)],
) -> dict[str, Any]:
    """Look up a project by name in the read-only project catalog.

    Returns its owner, status, description, budget, and project dates. If there is
    no match, returns an error object with the message 'Project not found'.
    """
    started = perf_counter()
    logger.info("mcp_tool_started tool=get_project_information project_name=%r", project_name)
    try:
        try:
            lookup = ProjectLookupInput(project_name=project_name)
        except ValidationError:
            return {
                "error": "Invalid input",
                "message": "project_name must contain 1-255 non-whitespace characters.",
            }

        project = _repository.get_by_name(lookup.project_name)
        if project is None:
            logger.info(
                "mcp_tool_not_found tool=get_project_information project_name=%r",
                lookup.project_name,
            )
            return {"error": "Project not found", "project_name": lookup.project_name}

        record = ProjectInformation(
            id=str(project.id),
            project_name=project.project_name,
            owner=project.owner,
            status=project.status,
            description=project.description,
            budget=float(project.budget),
            start_date=project.start_date.isoformat(),
            end_date=project.end_date.isoformat() if project.end_date else None,
        )
        return record.model_dump(mode="json")
    except Exception:
        logger.exception("mcp_tool_failed tool=get_project_information")
        return {"error": "Data retrieval failed"}
    finally:
        elapsed_ms = (perf_counter() - started) * 1000
        logger.info(
            "mcp_tool_finished tool=get_project_information elapsed_ms=%.2f",
            elapsed_ms,
        )
