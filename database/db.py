"""SQLAlchemy engine and session factory for the MCP data-access layer."""

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return the application engine, configured with the read-only DB credentials."""
    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
    )


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Return a reusable SQLAlchemy session factory."""
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)
