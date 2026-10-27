"""Replace the project demo table with business-development prospects.

Revision ID: 0002_prospects
Revises: 0001_create_projects
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import Uuid

revision = "0002_prospects"
down_revision = "0001_create_projects"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("projects")
    op.create_table(
        "prospects",
        sa.Column("prospect_id", Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("company_name", sa.Text(), nullable=False),
        sa.Column("industry", sa.Text(), nullable=False),
        sa.Column("opportunity_description", sa.Text(), nullable=False),
        sa.Column("opportunity_stage", sa.Text(), nullable=False),
        sa.Column("opportunity_value_usd", sa.Numeric(14, 2), nullable=False),
        sa.Column("region", sa.Text(), nullable=False),
        sa.Column("risk_level", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "opportunity_stage IN ('New', 'Qualified', 'In Discussion', 'Proposal Sent', 'Negotiation', 'Closed Won', 'Closed Lost')",
            name="ck_prospects_opportunity_stage",
        ),
        sa.CheckConstraint("region IN ('North America', 'Europe', 'APAC')", name="ck_prospects_region"),
        sa.CheckConstraint("risk_level IN ('Low', 'Medium', 'High')", name="ck_prospects_risk_level"),
        sa.CheckConstraint("opportunity_value_usd >= 0", name="ck_prospects_value_nonnegative"),
    )
    op.create_index("ix_prospects_company_name", "prospects", ["company_name"])
    op.create_index("ix_prospects_industry", "prospects", ["industry"])
    op.create_index("ix_prospects_opportunity_stage", "prospects", ["opportunity_stage"])
    op.execute("GRANT SELECT ON TABLE prospects TO orion_reader")


def downgrade() -> None:
    op.execute("REVOKE SELECT ON TABLE prospects FROM orion_reader")
    op.drop_index("ix_prospects_opportunity_stage", table_name="prospects")
    op.drop_index("ix_prospects_industry", table_name="prospects")
    op.drop_index("ix_prospects_company_name", table_name="prospects")
    op.drop_table("prospects")
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
