# Relay

> AI-graded second-life commerce. Every returned or unused product gets a verifiable
> **Condition Passport** and is routed to its next best owner — exchange, hyperlocal
> rescue, P2P resale, refurbish, donate, or recycle — instead of the landfill.

**Amazon HackOn — Problem Statement #2 (sustainable commerce / returns).**

`relay-dev` is the **orchestration + documentation hub**. It holds the shared docs and the
local `docker-compose` that wires every service together. It contains no application code.

---

## Repository map

| Repo | Language | Owner | Responsibility |
|---|---|---|---|
| [`relay-dev`](.) | — | Shikher | Docs (`context.md`, `plan.md`), docker-compose, project hub |
| `relay-contracts` | YAML / JSON | Shikher | OpenAPI + JSON Schema — single source of truth, no runtime |
| `relay-web` | TypeScript | Shikher | Next.js UI, Zustand, API client |
| `relay-api` | Python | Shikher | FastAPI BFF, auth stub, returns/wishlist/p2p/credits, Celery, DB, LifeLedger client |
| `relay-engine` | Go | Shikher | Disposition scoring, Rescue geo/TTL, match ranking |
| `relay-ml` | Python | Bhavya | Image/video grading, fit flags, CNN + Bedrock tier orchestration |

**Clone all repos as siblings** so docker-compose build contexts resolve:

```
Hackon/
├── relay-dev/        <- run docker compose from here
├── relay-contracts/
├── relay-web/
├── relay-api/
├── relay-engine/
└── relay-ml/
```

---

## Docs (start here)

| Doc | What it is |
|---|---|
| [`docs/plan.md`](./docs/plan.md) | The build plan — features, architecture (HLD), task board, per-owner tracks, demo script, deploy |
| [`docs/context.md`](./docs/context.md) | The "why" — brainstorm, decisions, research, risk audit, hackathon positioning |

Contracts live in the separate `relay-contracts` repo (implement exactly; change via PR).

---

## Local development

### Prerequisites
- Docker + Docker Compose v2
- (per service) Python 3.11+, Go 1.22+, Node 20+

### 1. Start infrastructure (Postgres + Redis) — use this now

```bash
cd relay-dev
cp .env.example .env        # optional; sensible defaults baked in
docker compose up -d        # brings up postgres (pgvector) + redis only
docker compose ps
```

- Postgres: `localhost:5432`  user/pass/db = `relay`/`relay`/`relay` (pgvector ready)
- Redis: `localhost:6379`

Each app service connects to these by running locally against `localhost`, or in-network
once containerized (see below).

### 2. Run app services (once each repo has a Dockerfile)

App services sit behind the `apps` profile so they never try to build a repo that isn't
scaffolded yet. Enable when ready:

```bash
docker compose --profile apps up -d --build
```

Bring up selectively as repos come online, e.g.:

```bash
docker compose --profile apps up -d --build relay-ml
```

### Service ports

| Service | Port | Health |
|---|---|---|
| relay-web | 3000 | — |
| relay-api | 8000 | `GET /health` |
| relay-ml | 8001 | `GET /health` |
| relay-engine | 8002 | `GET /health` |
| postgres | 5432 | `pg_isready` |
| redis | 6379 | `redis-cli ping` |

### Internal service URLs (inside the compose network)
- `ML_SERVICE_URL = http://relay-ml:8001`
- `ENGINE_SERVICE_URL = http://relay-engine:8002`
- `DATABASE_URL = postgresql://relay:relay@postgres:5432/relay`
- `REDIS_URL = redis://redis:6379/0`

---

## Environment & secrets

- `relay-dev/.env` configures only Postgres/Redis for compose (no secrets; safe defaults).
- **Service secrets** (AWS creds, `BEDROCK_MODEL_T2/T3`, `OPENAI_API_KEY`, LifeLedger signer
  key) live in each repo's own `.env` and are **never committed**. See `plan.md` §17.

---

## Dev workflow

- Default branch is **`main`** on every repo.
- **Contracts are law.** Implement against `relay-contracts`; any shape change = PR to
  `relay-contracts` (bump `VERSION`, update `CHANGELOG.md`) reviewed by the other owner
  *before* implementing.
- `relay-ml` is independent — Bhavya owns it and integrates over HTTP via the contract;
  no need to check out web/engine for daily ML work.
- Definition of Done = merged + acceptance criteria met + demo path still works at the
  declared Lego tier (`plan.md` §1, §11).

---

## Deployment

AWS primary (ECS Fargate · RDS Postgres+pgvector · ElastiCache/Redis · S3 · SQS · Bedrock),
Railway as backup for the demo video. Details in [`docs/plan.md`](./docs/plan.md) §13.
