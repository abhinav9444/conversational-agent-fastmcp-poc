-- Reference DDL for the Project Orion POC.
-- The Alembic migration in database/migrations/versions is used by Docker Compose.

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    budget NUMERIC(14, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    CONSTRAINT uq_projects_project_name UNIQUE (project_name)
);

GRANT SELECT ON TABLE projects TO orion_reader;
