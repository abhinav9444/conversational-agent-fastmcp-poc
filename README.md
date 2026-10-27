# Project Orion — Lonza Business Development Conversational Agent

A laptop-local proof of concept for a conversational agent that retrieves fictional business-development prospect records through FastMCP and PostgreSQL. The records are synthetic demo data, not Lonza's real customers or pipeline.

## Architecture

```text
Business Development Manager
        |
        v
FastAPI chat API  <---->  Local LLM (Ollama / LM Studio)
        |                         |
        |                   MCP tool selection
        v                         |
MCP client gateway  <--------------+
        |
        v
FastMCP server: get_prospects
        |
        v
SQLAlchemy repository (read-only role)
        |
        v
PostgreSQL: prospects table
```

The agent uses MCP discovery and tool calls for prospect facts. The LLM does not connect directly to PostgreSQL and must summarize only records returned by the tool.

## Local setup (Windows / PowerShell)

Prerequisites: Python 3.12, PostgreSQL 18, and Ollama or LM Studio running locally.

1. Activate the repository virtual environment and install dependencies:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   python --version
   python -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

2. In pgAdmin or psql, create the database if it does not already exist:

   ```sql
   CREATE DATABASE orion;
   ```

3. Connect to the `orion` database as a PostgreSQL superuser and run the role setup file from the repository root:

   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -p 5432 -d orion -W -f database/init/001_roles.sql
   ```

   The script creates `orion_admin` and `orion_reader`. The admin role creates/updates tables; the reader role is transaction-read-only and receives SELECT access only. The passwords in the development script and `.env.example` are local demo defaults; change them consistently before sharing the environment.

4. Confirm `.env` contains valid local URLs (update the passwords if you changed them):

   ```dotenv
   DATABASE_ADMIN_URL=postgresql+psycopg://orion_admin:orion_admin_dev@localhost:5432/orion
   DATABASE_URL=postgresql+psycopg://orion_reader:orion_reader_dev@localhost:5432/orion
   MCP_SERVER_URL=http://localhost:8000/mcp
   LLM_BASE_URL=http://localhost:11434/v1
   LLM_API_KEY=local-only
   LLM_MODEL=qwen2.5:3b
   ```

5. Run migrations and seed the ten fictional prospects:

   ```powershell
   alembic upgrade head
   python -m database.seed
   ```

6. Start Ollama with the model pulled (one-time setup: `ollama pull qwen2.5:3b`), then start the MCP server in terminal 1:

   ```powershell
   python -m mcp_server.server
   ```

7. Start the API in terminal 2:

   ```powershell
   uvicorn api.main:app --reload --port 8080
   ```

8. Open http://localhost:8080/docs. Use `POST /chat` with:

   ```json
   {"message":"Show me high-risk prospects in Europe"}
   ```

   Check `GET /ready` to confirm MCP tool discovery succeeded. The response includes `tools_invoked` so the demo can show when `get_prospects` was used.

## Database design

The `prospects` table contains `prospect_id` (UUID PK), `company_name`, `industry`, `opportunity_description`, `opportunity_stage`, `opportunity_value_usd`, `region`, `risk_level`, `created_at`, and `updated_at`. Check constraints validate stage, region, risk, and nonnegative opportunity values. Indexes cover company name, industry, and opportunity stage.

The MCP tool accepts optional `industry`, `stage`, `region`, and `risk_level` filters. SQLAlchemy query construction keeps values parameterized. Results are sorted by opportunity value descending and limited to 100 records.

## Useful SQL examples

```sql
-- All prospects
SELECT * FROM prospects ORDER BY opportunity_value_usd DESC;

-- Industry
SELECT * FROM prospects WHERE industry ILIKE 'Biotech';

-- Stage
SELECT * FROM prospects WHERE opportunity_stage = 'Negotiation';

-- High-value opportunities
SELECT * FROM prospects WHERE opportunity_value_usd > 1000000 ORDER BY opportunity_value_usd DESC;

-- High risk
SELECT * FROM prospects WHERE risk_level = 'High';

-- Europe
SELECT * FROM prospects WHERE region = 'Europe';
```

## Tests

Run unit tests with `pytest`. They use SQLite/fakes and do not require a running PostgreSQL instance or LLM.

## Security and future work

- Keep MCP access read-only through `orion_reader`; migrations and seeding use `orion_admin`.
- Use parameterized SQL, bounded results, and input validation.
- For multi-BDM usage, add an `owner_bdm` column and enforce authorization/row-level security before exposing personal pipeline data.
- Add audit events, pooling/observability, and a proper updated-at trigger before production use.
- Replace demo passwords and restrict PostgreSQL to localhost for this laptop-only POC.
