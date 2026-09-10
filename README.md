# AEGIS

**Autonomous Engineering Intelligence & Guarded Software Recovery**

AEGIS is a code-aware software engineering and incident-response platform.
It investigates a reported issue, retrieves grounded evidence from a
repository, reproduces the problem in an isolated sandbox, generates a
minimal patch, verifies it with tests and security checks, pauses for human
approval on anything risky, and can simulate a release and recommend
rollback — with a full audit trail behind every step.

Full specification: [`docs/AEGIS_Master_Build_Document.md`](docs/AEGIS_Master_Build_Document.md).
Day-to-day operating rules for coding sessions: [`CLAUDE.md`](CLAUDE.md).

> **Build status: Day 1 of 56.** This is the project scaffold. The API,
> web UI, database schema, retrieval pipeline, and agent runtime are not
> implemented yet — they arrive incrementally over the next 7 weeks. See
> "Current status" in `CLAUDE.md` for exactly what exists right now.

## What's here today (Day 1)

- Monorepo folder structure (`apps/`, `agents/`, `domain/`, `rag/`, `mcp/`,
  `sandbox/`, `db/`, `evals/`, `observability/`, `tests/`, `docs/`, `infra/`).
- `infra/docker-compose.yml` wiring three services:
  - `db` — real PostgreSQL 16 with a health check.
  - `api` — a minimal FastAPI container (placeholder root route only;
    `/health`, real config, and DB wiring land on Day 2–3).
  - `web` — a minimal Next.js container (placeholder page only; layout,
    navigation, and the typed API client land on Day 4).
- `.env.example` with the configuration categories the full system will need.

Nothing here fakes functionality: the `api` and `web` containers currently
return static placeholder responses, not real product behavior. That's
intentional for Day 1 — the goal is a clean, reproducible local startup.

## Prerequisites

- Docker and Docker Compose (Docker Desktop, or the Docker Engine + Compose
  plugin on Linux).

## Local setup (one command)

```bash
git clone <this-repo-url> AEGIS
cd AEGIS
cp .env.example .env
docker compose -f infra/docker-compose.yml --env-file .env up --build
```

Then check:

- API placeholder: http://localhost:8000/ → `{"service": "aegis-api", "status": "day1-scaffold"}`
- Web placeholder: http://localhost:3000/ → "AEGIS — Day 1 scaffold" page
- Database: PostgreSQL listening on `localhost:5432` (credentials from `.env`)

To stop:

```bash
docker compose -f infra/docker-compose.yml down
```

To stop and wipe the database volume:

```bash
docker compose -f infra/docker-compose.yml down -v
```

## Note on verification

These files were authored and their Compose/YAML syntax was validated, but
they have **not** been run against a live Docker daemon (this authoring
environment has no Docker installed). Please run the command above and treat
the result as the real Day 1 acceptance check: *a clean clone starts
infrastructure*. If anything fails to build or start, that's a genuine Day 1
bug to report/fix before moving to Day 2 — not something to paper over.

## Repository layout

See `docs/AEGIS_Master_Build_Document.md` §5 for the full target tree and the
rationale behind each top-level folder.

## License

TBD.
