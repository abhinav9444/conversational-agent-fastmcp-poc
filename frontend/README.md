# Orion chat UI

A responsive Next.js frontend inspired by the supplied Orion MVP screenshot. It includes the left navigation, daily prospect overview, prioritised prospect rows, and a conversational assistant panel connected to the existing FastAPI `POST /chat` endpoint.

## Run locally (Windows PowerShell)

Start the backend stack first, as described in the repository root README:
- PostgreSQL running with migrations and demo data applied
- MCP server on port 8000
- FastAPI on port 8080

Then open a new terminal at the repository root:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000.

The UI expects FastAPI at `http://localhost:8080` by default. Override `NEXT_PUBLIC_API_URL` in `.env.local` if needed. FastAPI permits local browser requests from localhost:3000. Check http://localhost:8080/health and http://localhost:8080/ready if chat does not respond.

The prospect names shown in the overview are illustrative UI content. Chat answers and tool traces come from the local API; the UI does not claim the illustrative dashboard rows are live database query results yet.
