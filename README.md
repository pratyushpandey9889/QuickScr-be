# QuickScribe Enterprise Accelerator

QuickScribe is a production-oriented starter platform for turning BRDs, SOPs, flowcharts, Excel files, SharePoint documents, SAP process documents, and Nagare JIT sequence workflows into structured software delivery artifacts.

## What It Generates

1. Executive summary and business process understanding
2. As-Is and To-Be process flows
3. Functional and non-functional requirements
4. Entity model, ER diagram, and SQL scripts for PostgreSQL, SQL Server, and MySQL
5. REST API design with schemas, validation rules, and errors
6. Frontend workbench design
7. Nagare JIT call-off, delivery, inventory, and line feeding rules
8. SharePoint, SAP, AI agent, vector store, and database integration designs
9. Agent accuracy profile with confidence estimate, validation depth, citation policy, and review gates
10. Test cases, UAT scenarios, deployment guide, risks, and assumptions

## Agent Accuracy Levels

QuickScribe supports four selectable accuracy levels:

| Level | Target | Use Case |
| --- | --- | --- |
| Fast Draft | 70% | Rapid first-pass extraction and early process discovery |
| Balanced | 82% | Default analysis with requirement, entity, integration, risk, and assumption checks |
| High Accuracy | 90% | Cross-artifact validation with stronger citation and review expectations |
| Audit Grade | 95% | Regulated workflows with mandatory evidence, reviewer gates, and export controls |

The selected level is returned in `accuracy_profile` with estimated confidence, retrieval top-k, model temperature, enabled checks, escalation rules, and whether human review is required.

## Repository Layout

```text
backend/              FastAPI app, domain models, services, routes, and tests
frontend/             Next.js, TypeScript, Tailwind workbench
database/             PostgreSQL, SQL Server, and MySQL schema scripts
docs/                 Architecture, API, and UAT documentation
infra/azure/          Azure Bicep starter
docker-compose.yml    Local stack with PostgreSQL, backend, and frontend
```

## Local Backend

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev,documents]"
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000/docs`.

## Local Frontend

```bash
cd frontend
npm install
npm run dev
```

The workbench is available at `http://127.0.0.1:3000/`.

On Windows, this repository path contains `!`, which can confuse Next/Webpack. Use the helper scripts from the repository root:

```bat
scripts\start-backend.cmd
scripts\start-frontend.cmd
```

If the UI shows `Failed to fetch`, restart both scripts. The frontend now calls `/api/v1` through a Next.js rewrite, and the backend allows both `http://localhost:3000` and `http://127.0.0.1:3000`.

## Docker Compose

```bash
docker compose up --build
```

## Key Environment Variables

Copy `.env.example` to `.env` and configure Azure AD, PostgreSQL, SharePoint, SAP, OpenAI, and vector store settings.

## Production Notes

- Replace the in-memory repository with a SQLAlchemy PostgreSQL repository.
- Add Alembic migrations for schema evolution.
- Add a background worker for large files, SharePoint delta sync, vector indexing, and SAP reconciliation.
- Enforce JWT validation and RBAC outside `APP_ENV=local`.
- Configure Key Vault and managed identity before enabling enterprise integrations.
