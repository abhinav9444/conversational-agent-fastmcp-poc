"""Create the projects table.

Revision ID: 0001_create_projects
Revises:
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import Uuid

revision = "0001_create_projects"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_name", sa.String(length=255), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("budget", sa.Numeric(14, 2), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.UniqueConstraint("project_name", name="uq_projects_project_name"),
    )
    op.execute("GRANT SELECT ON TABLE projects TO orion_reader")


def downgrade() -> None:
    op.execute("REVOKE SELECT ON TABLE projects FROM orion_reader")
    op.drop_table("projects")
