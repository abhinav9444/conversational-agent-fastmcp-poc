-- Reference DDL for the Lonza Business Development POC.
-- Alembic migrations are the source of truth for application deployments.

CREATE TABLE IF NOT EXISTS prospects (
    prospect_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT NOT NULL,
    industry TEXT NOT NULL,
    opportunity_description TEXT NOT NULL,
    opportunity_stage TEXT NOT NULL CHECK (
        opportunity_stage IN (
            'New', 'Qualified', 'In Discussion', 'Proposal Sent',
            'Negotiation', 'Closed Won', 'Closed Lost'
        )
    ),
    opportunity_value_usd NUMERIC(14, 2) NOT NULL CHECK (opportunity_value_usd >= 0),
    region TEXT NOT NULL CHECK (region IN ('North America', 'Europe', 'APAC')),
    risk_level TEXT NOT NULL CHECK (risk_level IN ('Low', 'Medium', 'High')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_prospects_company_name ON prospects (company_name);
CREATE INDEX IF NOT EXISTS ix_prospects_industry ON prospects (industry);
CREATE INDEX IF NOT EXISTS ix_prospects_opportunity_stage ON prospects (opportunity_stage);

GRANT SELECT ON TABLE prospects TO orion_reader;
