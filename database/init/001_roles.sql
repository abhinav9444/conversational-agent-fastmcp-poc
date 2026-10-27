-- Development-only reader role. Update this password and the Compose URL together
-- before sharing this environment. PostgreSQL runs this file on first volume init only.
CREATE ROLE orion_reader LOGIN PASSWORD 'orion_reader_dev';
ALTER ROLE orion_reader SET default_transaction_read_only = on;
