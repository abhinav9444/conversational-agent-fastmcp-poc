-- Run as a PostgreSQL superuser against the orion database.
-- Development-only credentials: replace both passwords before sharing this environment.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'orion_admin') THEN
        CREATE ROLE orion_admin LOGIN PASSWORD 'orion_admin_dev';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'orion_reader') THEN
        CREATE ROLE orion_reader LOGIN PASSWORD 'orion_reader_dev';
    END IF;
END
$$;

ALTER ROLE orion_reader SET default_transaction_read_only = on;
GRANT CONNECT ON DATABASE orion TO orion_reader;
GRANT USAGE ON SCHEMA public TO orion_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO orion_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE orion_admin IN SCHEMA public
    GRANT SELECT ON TABLES TO orion_reader;
