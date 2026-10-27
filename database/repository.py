"""Repository pattern for read-only project lookup."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from database.db import get_session_factory
from database.models import Project


class ProjectRepository:
    """Encapsulate all project queries used by the MCP layer."""

    def __init__(self, session_factory: sessionmaker[Session] | None = None) -> None:
        self._session_factory = session_factory

    def get_by_name(self, project_name: str) -> Project | None:
        """Find a project by name without case sensitivity."""
        factory = self._session_factory or get_session_factory()
        statement = select(Project).where(
            func.lower(Project.project_name) == project_name.strip().lower()
        )
        with factory() as session:
            return session.scalar(statement)
