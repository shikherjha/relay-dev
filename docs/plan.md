# Relay — Technical Build Plan (HackOn PS #2)

> **Purpose:** Single technical source of truth between brainstorm (`context.md`) and implementation.  
> **Audience:** Shikher, Bhavya, and coding agents (Codex, Cursor, etc.).  
> **Brainstorm / decisions log:** see [`context.md`](./context.md) — this file is *how we build*, not *why we chose*.

---

## Overview

**Relay** is a reverse-logistics routing engine + next-owner matching platform for Amazon HackOn Problem Statement #2 (circular commerce / second life for products). Every returned physical unit gets a **Condition Passport**, a disposition decision (exchange · rescue · P2P · refurb · donate · recycle), and a matched next buyer — with **LifeLedger** (blockchain) for tamper-proof trust.

**Sub-brand:** LifeLedger — on-chain event log for passport hashes and lifecycle events.

**Pitch (one line):** *Relay is Amazon's disposition brain — grade, route, match, verify. We optimize final placement, not resales.*

**Build model:** Iterative **Lego tiers** (T0→T3). Lower tiers always demo-able if upper tiers slip. Agentic AI accelerates T2/T3; **T1 must work without it.**

**Languages:** Python + Go only (no Java, no Node backend).  
**Frontend:** Next.js 14 + TypeScript + Zustand + shadcn/ui.  
**Deploy:** AWS primary · Railway backup (demo video).  
**Repos:** 4 code repos + 1 contracts repo (multi-repo, not monorepo).

---

## To Do (task board)

Copy status into PR descriptions. **Definition of Done (DoD)** = code merged + acceptance criteria met + demo path still works at declared tier.

> **Build order — backend-first, UI last (LOCKED Session 6c).** Shikher builds in this sequence regardless of tier labels:
> **1) schema** (DB migrations + contracts) → **2) API endpoint design** (route signatures, request/response) → **3) high-level flow** (services talk: return → grade → disposition → match → credits) → **4) wire all logic** (real engine/ML/persistence, integration-tested via API) → **5) UI last** — all `web-*` tasks are **deferred to a final UI phase**; when the design is ready, Shikher only wires the existing backend to it. Tier labels on `web-*` rows indicate which backend tier they pair with, not when they're built. T1/T2 acceptance is validated via API + integration tests until the UI phase.

| id | tier | owner | content | status |
|---|---|---|---|---|
| contracts-v1 | T0 | Shikher | Publish `relay-contracts` v1: ConditionPassport JSON schema, OpenAPI for relay-ml + relay-api public routes | ✅ done |
| contracts-embed | T0 | Both | Add `/embed` + `/wish-score` to relay-ml OpenAPI; vector + wish-score schemas | pending |
| repo-scaffold | T0 | Shikher | Create 5 GitHub repos, branch `main`, `relay-dev` docker-compose, README per repo | ✅ done (repos + compose + relay-dev README) |
| ml-dataset | T0 | Bhavya | Download HF e-commerce defects + Kaggle fit dataset; document in `relay-ml/data/README.md` | ✅ done (branch `feat/ml-dataset`) |
| ml-health | T0 | Bhavya | `relay-ml`: FastAPI skeleton, `GET /health`, Docker, `.env.example` | ✅ done (merge PR #1 → main) |
| api-skeleton | T0 | Shikher | `relay-api`: FastAPI skeleton, Postgres + Redis docker, Alembic init | ✅ done (pytest 2/2; /health) |
| engine-skeleton | T0 | Shikher | `relay-engine`: Go chi/fiber skeleton, `GET /health` | ✅ done (go build ok) |
| db-schema | T0 | Shikher | Alembic migration v1 — all §6 tables + pgvector extension (schema-first, before endpoints) | ✅ done (applied live on pg16: 15 tables, vector+pgcrypto, 2 HNSW indexes) |
| web-shell | **UI phase** | Shikher | `relay-web`: Next + shadcn — **deferred to final UI phase** (backend-first) | deferred |
| ml-grade-image | T1 | Bhavya | `POST /grade-image` → ConditionPassport (CNN baseline + optional Bedrock T2) | pending |
| ml-bedrock-only | T1 | Bhavya | `GRADING_MODE=bedrock_only` escape hatch — real ConditionPassport via Nova Lite from image, **no CNN** (demo-safe; T2 cost/req) | pending |
| ml-grade-video | T1 | Bhavya | `POST /grade-video` → keyframe pipeline + aggregated passport | pending |
| ml-fit-flags | T1 | Bhavya | `POST /fit-flags` → article flags (rules stub → MultiFlags stretch) | pending |
| ml-confidence | T1 | Bhavya | Return `confidence` + `model_tier_used`; document escalation threshold | pending |
| ml-passport-align | T0 | Bhavya | Align Pydantic `ConditionPassport` to `relay-contracts` v1 (add `schema_version`, `packaging_state=missing`, `vertical` enum, optional vs required) | pending |
| api-returns | T1 | Shikher | Return intake API, S3 upload, call relay-ml, persist passport | pending |
| api-mock-ml | T1 | Shikher | Mock ML client until Bhavya URL live; swap via `ML_SERVICE_URL` | pending |
| engine-disposition | T1 | Shikher | Go: `POST /disposition/score` — rule engine (exchange/rescue/p2p/…) | pending |
| engine-rescue-ttl | T1 | Shikher | Go: Rescue listing TTL + geo radius scoring | pending |
| api-rescue | T1 | Shikher | Rescue feed + claim APIs; guardrails v1 (eligibility, chain cap) | pending |
| api-exchange | T1 | Shikher | Exchange-first routing when reason=size + SKU in stock | pending |
| api-bracketing | T1 | Shikher | Bracketing detection: flag cart/checkout when ≥3 size/variant of same product (strict); expose on cart insight | pending |
| ml-embed | T1 | Bhavya | `POST /embed` → 384-d vector from passport attrs / wish text (sentence-transformer or Bedrock Titan) | pending |
| api-embeddings | T1 | Shikher | Call relay-ml `/embed`; persist `product_units.embedding` + `reverse_wishlist.embedding`; pgvector cosine index | pending |
| engine-match-vector | T1 | Shikher | Go/SQL cosine match: unit ↔ wishlist via pgvector ANN (real matching, not geo-only) | pending |
| api-seed | T1 | Shikher | `scripts/seed.py` — users, catalog, wishes, demo geo, bracketing carts | pending |
| web-checkout-insight | T1 | Shikher | Fit insight banner on PDP/checkout (fashion) | pending |
| web-bracketing | T1 | Shikher | Active bracketing interceptor at checkout (warn + fit suggestion, not passive) | pending |
| web-return-wizard | T1 | Shikher | Return flow: reason → upload → grade result → outcome | pending |
| web-rescue-feed | T1 | Shikher | Rescue cards + countdown TTL | pending |
| api-wishlist | T2 | Shikher | Reverse Wishlist CRUD + pgvector match on return graded (uses `api-embeddings`) | pending |
| ml-wish-score | T2 | Bhavya | Wish confidence score (logistic reg on wish-age, user purchase history, category affinity) → ranking input | pending |
| engine-demand-weight | T2 | Shikher | Disposition scoring weights open-wish demand (wishlist as routing input, not post-match lookup) | pending |
| engine-pair-rescue | T2 | Shikher | Pair Rescue: bipartite A↔B swap match (each return satisfies other's wish, geo-bounded) — promoted from T3 | pending |
| engine-rescue-decay | T2 | Shikher | Rescue decay pricing: discount rises as TTL drops (time-decay formula); countdown = price clock | pending |
| api-seller-signals | T2 | Shikher | Seller-side return-signal aggregation per SKU+reason → catalog-fix recommendation (surfaced on ops) | pending |
| ml-return-cluster | T3 | Bhavya | Stretch: cluster free-text return reasons (NLP) to power seller signals beyond reason codes | pending |
| api-ops-dashboard | T2 | Shikher | Ops API: high-return SKUs (relay-ml flagged), live rescue TTL list, chain-depth view, seller signals | pending |
| web-ops-dashboard | T2 | Shikher | Ops/seller view: flagged SKUs table + return-reason insight + rescue TTL countdown + chain depth | pending |
| api-impact | T2 | Shikher | Impact Wallet net CO₂ via hard-coded per-channel constants (see §7 Carbon model) | pending |
| api-p2p | T2 | Shikher | One-click P2P list + escrow stub | pending |
| api-warranty | T2 | Shikher | Warranty chain records on electronics units | pending |
| api-lifeledger | T2 | Shikher | Polygon Amoy write + QR verify endpoint | pending |
| web-p2p-warranty | T2 | Shikher | Electronics tab: P2P list + warranty + LifeLedger viewer | pending |
| web-lifeledger-qr | T2 | Shikher | QR scan verify UI | pending |
| api-credits | T2 | Shikher | Green credits (keep-based, 14-day rule) — P2 supporting | pending |
| ml-bedrock-tiers | T2 | Bhavya | T0–T3 Bedrock escalation in relay-ml (confidence-gated) | pending |
| ml-multiflags | T3 | Bhavya | Stretch: simplified MultiFlags on ModCloth aggregates | pending |
| engine-rl-hook | T3 | Shikher | Disposition interface for future RL; rules remain default | pending |
| deploy-aws | T2 | Shikher | ECS/RDS/S3 deploy path | pending |
| deploy-railway | T2 | Shikher | Railway compose backup + seeded demo | pending |
| demo-video | T2 | Both | Record 3-min walkthrough on Railway/AWS | pending |
| submission | T2 | Shikher | GitHub links, PPT, README, docs | pending |

---

## Document map

| Section | Contents |
|---|---|
| §1 | Problem & positioning (brief — details in context.md) |
| §2 | What we are building (features + priorities) |
| §3 | Architecture HLD |
| §4 | Repos, branching, PR flow |
| §5 | Shared contracts (schemas + APIs) |
| §6 | Data model (Postgres) |
| §7 | Feature specs + guardrails |
| §8 | **Bhavya — full track** (research, data, ML, endpoints, freedom to improve) |
| §9 | **Shikher — full track** (platform, integration, UI, infra) |
| §10 | Integration matrix (who calls whom) |
| §11 | Lego tiers + 48h schedule |
| §12 | Demo script + UI pages |
| §13 | Deploy (AWS + Railway) |
| §14 | Submission checklist |
| §15 | Research paper bank (Bhavya) |
| §16 | Dataset catalog |
| §17 | Environment variables |
| §18 | Definition of Done + sync cadence |

---

## §1 Problem & positioning (summary)

**Problem Statement #2:** Returned/unused products should find their next best owner via AI disposition, quality grading, refurbished trust, green incentives, P2P resale, and return prevention.

**Our reframe (do not pitch as generic return prediction):**
- **Disposition:** where should *this unit* go?
- **Matching:** *who* is the next owner?

**Avoid:** Returnformer clone, EarthScore-only gamification, Amazon UI clone, token-dumping Bedrock on every image.

**Full brainstorm:** [`context.md`](./context.md) §1–22.

---

## §2 What we are building

### P0 — must work for T1 demo (fashion primary path)

| Feature | Description |
|---|---|
| **Fit Intelligence** | Checkout/PDP insight: user fit profile + article flags; exchange nudge — not scary "23% return risk" |
| **Bracketing interceptor** | Active checkout flag when cart has ≥3 size/variant of same product (strict; the ~40%-of-fashion-returns driver) → fit suggestion + "keep one" nudge |
| **Return + grade** | Photo upload → Condition Passport JSON (CNN **or** `bedrock_only` real-grade fallback) |
| **Disposition engine** | Go service scores: exchange · rescue · p2p · refurb · donate · recycle |
| **Exchange-first** | Return reason size/fit + exchange SKU in stock → offer swap before warehouse |
| **Return Rescue** | Geo + TTL feed; nearby buyer claims; Zomato-inspired |
| **Next-owner matching** | pgvector cosine match (unit embedding ↔ Reverse Wishlist embedding) — real vector retrieval, not geo-only |
| **Guardrails** | Eligibility score, chain depth cap, net-carbon gate (uses §7 carbon constants) |

### P1 — T2 differentiators

| Feature | Description |
|---|---|
| **Reverse Wishlist** | Buyer posts demand; pgvector match when return graded |
| **Demand-weighted disposition** | Open wishes feed the disposition score itself — high local demand for a SKU pulls routing toward rescue/p2p (routing input, not post-match lookup) |
| **Wish confidence scoring** | Rank matches by buyer intent (wish-age, purchase history, category affinity) — lightweight ML, not a flat lookup |
| **Pair Rescue** | Bipartite A↔B swap: each user's return satisfies the other's wish, geo-bounded — near-zero-carbon, no resale intermediary (promoted from T3) |
| **Rescue decay pricing** | Discount rises as TTL drops (15%→30%→45%); countdown becomes a price clock — optimizes recovery value over time |
| **Ops / seller dashboard** | Second persona: high-return SKUs flagged by relay-ml, **seller return-signal aggregation** (e.g. "34% return rate, reason: color mismatch → fix photos"), live rescue listings with TTL countdown, chain-depth view |
| **P2P one-click list** | From return flow; escrow stub; LifeLedger passport shown |
| **Warranty chain** | Electronics: remaining warranty + repair events on passport |
| **LifeLedger verify** | QR → hash check on Polygon Amoy testnet |

### P2 — supporting

| Feature | Description |
|---|---|
| **Green credits** | Earn on *kept* rescue/exchange (14-day rule) — not purchase volume |
| **Impact Wallet** | Net CO₂ vs baseline using **hard-coded per-channel constants** (rescue = 2.4 kg saved) — see §7 Carbon model |

### T3 — stretch (Lego add-on; pitch optional)

RL disposition hook · Donation routing · Full MultiFlags · return-reason NLP clustering · ClickHouse analytics

### Dual vertical demo

| Vertical | Live demo | Screen time |
|---|---|---|
| **Fashion** | Fit insight → return → grade → exchange OR rescue + wishlist | ~70% |
| **Electronics** | Return → video grade → P2P + warranty + LifeLedger QR | ~30% |

---

## §3 Architecture HLD

### Logical flow

```mermaid
flowchart TB
  WEB["relay-web\nNext · Zustand · shadcn"]
  API["relay-api\nFastAPI · Celery · DB"]
  ENG["relay-engine\nGo · disposition · rescue TTL"]
  ML["relay-ml\nBhavya · grade · fit-flags"]
  DB[("PostgreSQL + pgvector")]
  REDIS[("Redis")]
  S3[("S3")]
  SQS[("SQS / Redis broker")]
  BED["Bedrock / OpenAI"]
  CHAIN["LifeLedger\nPolygon Amoy"]

  WEB --> API
  API --> ENG
  API --> ML
  API --> DB
  API --> REDIS
  API --> S3
  API --> SQS
  ML --> BED
  ML --> S3
  API --> CHAIN
  ENG --> DB
```

### Service responsibilities

| Service | Repo | Language | Owns |
|---|---|---|---|
| **relay-web** | relay-web | TypeScript | All UI, Zustand stores, API client |
| **relay-api** | relay-api | Python | BFF, auth stub, orders/returns/wishlist/p2p/credits, Celery workers, DB migrations, seed, LifeLedger client |
| **relay-engine** | relay-engine | Go | Disposition scoring, Rescue geo/TTL, match ranking (calls pgvector via API or direct read) |
| **relay-ml** | relay-ml | Python | Image/video grading, fit flags, CNN weights, Bedrock tier orchestration |
| **relay-contracts** | relay-contracts | YAML/JSON | OpenAPI + JSON Schema — no runtime |

### Scale story (for judges — design for this, ship minimal)

| Concern | 48h ship | Scale path |
|---|---|---|
| API throughput | ECS Fargate 1–2 tasks | HPA / EKS |
| Grade backlog | Celery + Redis/SQS | SageMaker batch + Bedrock batch |
| Rescue TTL | Redis keys + Celery beat | Lambda + EventBridge |
| Wishlist match | pgvector ANN | Dedicated vector DB |
| LifeLedger | Polygon Amoy | Managed chain / AWS QLDB |
| Analytics | Postgres queries | ClickHouse (T3) |

### AI tier pipeline (Bhavya owns logic; Shikher consumes output)

| Tier | Trigger | Model | Owner |
|---|---|---|---|
| T0 | Every image | Rules / Nova Micro — reject blur | Bhavya |
| T1 | confidence path default | Bhavya CNN OR Nova Lite | Bhavya |
| T2 | confidence < threshold | Claude Haiku structured extract | Bhavya |
| T3 | high value OR still low conf | Nova Pro / OpenAI | Bhavya |
| Video | 5–8 keyframes | T1 on each → aggregate max damage | Bhavya |

**Rule:** `relay-api` never calls Bedrock directly for grading — always `relay-ml`.

**`GRADING_MODE` escape hatch (demo safety):** relay-ml supports a service-level mode so the perception pillar works even if the CNN isn't trained in 48h:

| `GRADING_MODE` | Behavior | Use |
|---|---|---|
| `cnn` (default) | CNN T1 → Bedrock escalation on low confidence | Production path |
| `bedrock_only` | **Skip CNN entirely** — every request graded by Nova Lite from image description → real ConditionPassport (`model_tier_used: bedrock-only`) | Demo-safe; slower/pricier per call but no trained model needed |
| `mock` | Deterministic stub passport (no AI) | Shikher local dev before ML URL is live |

This is server-side env only — **no contract change**. `bedrock_only` is a *real* grade fallback, distinct from Shikher's `mock` client.

---

## §4 Repos, branching, PR flow

### Repositories

| Repo | Owner | Clone required for Bhavya daily? |
|---|---|---|
| `relay-contracts` | Both review | Read-only |
| `relay-ml` | **Bhavya** | **Yes — primary workspace** |
| `relay-api` | Shikher | Optional (integration only) |
| `relay-engine` | Shikher | No |
| `relay-web` | Shikher | No |
| `relay-dev` (optional) | Shikher | Optional — docker-compose only |

### Local layout

```
~/relay/
├── relay-contracts/
├── relay-ml/          ← Bhavya
├── relay-api/         ← Shikher
├── relay-engine/      ← Shikher
├── relay-web/         ← Shikher
└── relay-dev/         ← docker-compose up
```

### Branching & PR conventions

1. **Default branch:** `main` (always deployable at current tier).
2. **Feature branches:** `feat/<task-id>-short-desc` e.g. `feat/ml-grade-image`.
3. **Bhavya:** branch off `relay-ml/main` → PR to `relay-ml/main`. Tag Shikher for review on contract-breaking changes only.
4. **Shikher:** sets up all repos first (T0); Bhavya starts once `relay-contracts` v1 + `relay-ml` skeleton exist.
5. **Cross-repo integration:** when Bhavya publishes ML URL, Shikher opens PR in `relay-api` updating `ML_SERVICE_URL` only.
6. **Contract changes:** PR to `relay-contracts` first → both implement second.

### CI (minimal)

| Repo | Gate |
|---|---|
| relay-contracts | Spectral/OpenAPI lint |
| relay-ml | `pytest` + `docker build` |
| relay-api | `pytest` + `docker build` |
| relay-engine | `go test ./...` |
| relay-web | `npm run build` |

---

## §5 Shared contracts

> **Source repo:** `relay-contracts` — implement exactly; propose improvements via PR.

### ConditionPassport (JSON Schema v1)

```json
{
  "unit_id": "uuid",
  "grade": "A+ | A | B+ | B | C | D",
  "grade_numeric": 0.0,
  "category": "fashion | electronics | ...",
  "vertical": "fashion | electronics",
  "disposition_hint": "exchange | rescue | p2p_resale | refurb | donate | recycle | restock",
  "defects": [
    {
      "type": "scuff | crack | stain | missing_part | ...",
      "severity": "minor | moderate | major",
      "bbox": [x, y, w, h],
      "description": "optional string"
    }
  ],
  "packaging_state": "sealed | opened | damaged",
  "confidence": 0.94,
  "media_hashes": ["sha256..."],
  "passport_hash": "sha256 of canonical JSON",
  "graded_at": "ISO8601",
  "model_tier_used": "T0 | T1 | T2 | T3 | cnn-v1",
  "warranty_months_remaining": 0,
  "repair_events": []
}
```

**Bhavya produces this.** Shikher persists to Postgres + submits `passport_hash` to LifeLedger.

### relay-ml OpenAPI (Bhavya implements)

| Method | Path | Request | Response |
|---|---|---|---|
| GET | `/health` | — | `{ "status": "ok", "model_loaded": true }` |
| POST | `/grade-image` | `multipart: image`, `unit_id`, `category` | `ConditionPassport` |
| POST | `/grade-video` | `multipart: video` OR `keyframes[]`, `unit_id` | `ConditionPassport` |
| POST | `/fit-flags` | `{ "sku_id", "brand?", "category?" }` | `{ "flags": [...], "confidence" }` |
| POST | `/embed` | `{ "text"? , "category"?, "grade"?, "size"?, "vertical"? }` | `{ "vector": [float × 384], "model": "..." }` |
| POST | `/wish-score` | `{ "wish_age_days", "user_purchase_count", "category_affinity", "has_fit_profile" }` | `{ "score": 0.0–1.0, "model": "logreg_v1" }` |

**Fit flags response shape:**

```json
{
  "sku_id": "SKU-123",
  "flags": [
    { "type": "runs_large", "message": "Size down recommended", "confidence": 0.87 },
    { "type": "true_to_size", "message": "...", "confidence": 0.72 }
  ],
  "source": "rules_v1 | multiflags_v1"
}
```

### relay-api public API (Shikher — Bhavya may call for testing)

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | |
| GET | `/products` | Demo catalog |
| GET | `/products/{id}` | PDP + fit flags proxy |
| GET | `/users/me/fit-profile` | |
| POST | `/returns` | Start return |
| POST | `/returns/{id}/media` | Upload to S3 → trigger grade job |
| GET | `/returns/{id}/passport` | |
| POST | `/returns/{id}/disposition` | Calls relay-engine |
| GET | `/rescue/feed` | Geo query `?lat=&lng=` |
| POST | `/rescue/{id}/claim` | Guardrails enforced |
| POST | `/wishlist` | Reverse wishlist |
| GET | `/wishlist/matches` | |
| POST | `/p2p/listings` | One-click from return |
| GET | `/lifeledger/{unit_id}/verify` | |
| POST | `/demo/reset` | Re-seed (hidden) |

### relay-engine API (Shikher — internal)

| Method | Path | Request | Response |
|---|---|---|---|
| POST | `/disposition/score` | `{ unit_id, passport, return_reason, user_id, geo, demand? }` | `{ channel, score, reasons[], guardrails_applied[] }` |
| POST | `/match/rescue` | `{ unit_id, geo, radius_km }` | ranked user ids (× wish_score) |
| POST | `/match/wishlist` | `{ unit_id, passport }` | ranked wish ids (× wish_score) |
| POST | `/match/pair-rescue` | `{ geo, radius_km }` | `[{ unit_a, unit_b, user_a, user_b, distance_km }]` bipartite swaps |

---

## §6 Data model (Postgres — relay-api owns migrations)

### Core tables

```sql
-- users (demo auth stub)
users (id, email, name, return_rate, fit_profile JSONB, rescue_eligible BOOL, created_at)

-- catalog
products (id, sku, title, category, vertical, price, metadata JSONB)
product_units (id, product_id, serial, status, owner_id, transfer_count, geo_lat, geo_lng)

-- returns
return_events (id, unit_id, user_id, reason_code, status, created_at)
condition_passports (id, unit_id, return_id, passport JSONB, passport_hash, graded_at)

-- matching (pgvector embeddings are T1, not optional)
reverse_wishlist (id, user_id, category, size, max_price, geo_lat, geo_lng, expires_at, embedding VECTOR(384), wish_score)
rescue_listings (id, unit_id, base_discount_pct, current_discount_pct, expires_at, ttl_seconds, status, claimed_by)
pair_rescue_matches (id, unit_a, unit_b, user_a, user_b, distance_km, status, created_at)  -- A↔B swap
p2p_listings (id, unit_id, seller_id, price, status, escrow_status)

-- prevention
cart_items (id, user_id, product_id, sku, size, variant, qty, created_at)  -- powers bracketing detection

-- trust
lifeledger_events (id, unit_id, event_type, tx_hash, passport_hash, created_at)
warranty_records (id, unit_id, months_remaining, repair_events JSONB)

-- incentives
green_credit_ledger (id, user_id, amount, reason, unlock_at, created_at)
impact_events (id, user_id, unit_id, channel, co2_saved_kg, created_at)  -- Impact Wallet ledger
```

**pgvector (T1):** `product_units.embedding VECTOR(384)` + `reverse_wishlist.embedding VECTOR(384)`. Embedding = encode(`category + grade + size + vertical`). Cosine ANN index for next-owner matching. **relay-ml owns embedding generation** via `POST /embed` (Bhavya, `ml-embed`); relay-api calls it for both units (from passport attrs) and wishes (from wish text), persists the vector, and runs the cosine query. Falls back to rule/geo match if `/embed` unavailable.

**Seller signals:** derived view over `return_events` grouped by `sku + reason_code` → return rate + dominant reason (powers the ops catalog-fix recommendation). Bhavya `ml-return-cluster` (T3) can enrich with free-text NLP clustering.

---

## §7 Feature specs + guardrails

> Full risk audit: [`context.md`](./context.md) §21.

### Return Rescue — return chain problem

**Implement in relay-engine + relay-api:**

| Guardrail | Implementation |
|---|---|
| Rescue eligibility | `users.return_rate < 0.4` AND `users.rescue_eligible` |
| One active rescue | Block claim if user has open rescue < 14 days |
| Chain depth cap | `product_units.transfer_count >= 3` → disposition forced refurb/donate/recycle |
| Net carbon gate | `saved_warehouse_km > delivery_km` (stub constants OK demo) |
| Fashion size match | Require wishlist size match OR fit_profile confidence > 0.7 |
| Keep-it credits | `green_credit_ledger.unlock_at = now + 14 days` |

### Exchange-first

Trigger when `return_reason IN ('too_small','too_large','fit')` AND exchange SKU `in_stock` within FC → UI shows exchange CTA before Rescue/P2P.

### Bracketing interceptor (prevention — P0/T1)

> **Why:** Size/variant bracketing — buying multiple sizes intending to return most — drives a large share of fashion returns. Catching it at the cart is the most concrete, data-rich prevention moment (more provable than a passive fit banner).

**Detection (relay-api, `cart_items`):** at checkout, group cart by `product_id`; if a product appears with **≥3 distinct `size`/`variant`** rows → bracketing flagged (strict threshold — avoids false positives on legitimate 2-item buys).

| Signal | UI response |
|---|---|
| 3+ sizes same product | Active banner: *"You have 3 sizes of <item> — keep the one that fits. Your fit profile suggests **L**."* + one-tap "remove extras" |
| Bracketing + known high return rate | Stronger nudge + exchange-friendly messaging (no fear scoring) |
| Bracketing on `critical_fit` SKU | Surface article fit flag inline |

**Guardrail:** advisory, never blocks purchase. Counts toward "returns prevented" demo metric.

### Carbon model (Impact Wallet + net-carbon gate)

> **Anchor stat:** US product returns generated ~**15 million metric tons of CO₂** in a year (Optoro / returns-industry research, cited in ScienceDirect reverse-logistics work). Per-item constants below are **demo estimates anchored to that** — hard-coded, visible on the passport/Impact Wallet, and used by the Rescue net-carbon guardrail.

**Per-channel CO₂ saved vs baseline (new purchase + warehouse return + restock), kg CO₂e:**

| Channel | `co2_saved_kg` | Rationale |
|---|---|---|
| `exchange` | 1.8 | avoids reverse leg + new outbound; one local swap |
| `rescue` | **2.4** | skips warehouse round-trip; hyperlocal last-mile only |
| `p2p_resale` | 3.1 | displaces a new-item purchase + avoids warehouse |
| `refurb` | 2.0 | life extension minus processing |
| `donate` | 1.5 | landfill diversion + social value |
| `recycle` | 0.6 | material recovery only |

**Net formula (demo):** `net_co2_saved = channel_const − (delivery_km × 0.12)` where `0.12 kg CO₂/km` is a light-vehicle last-mile factor.

**Net-carbon gate (guardrail):** only surface Rescue when `net_co2_saved > 0` (i.e. `rescue_const(2.4) − delivery_km×0.12 > 0` ⇒ ~≤20 km radius). Replaces the prior "stub constants OK" note.

### Next-owner matching (pgvector — T1)

Embed each graded unit and each wish (`category + grade + size + vertical`) via relay-ml `/embed`; rank wishes by cosine similarity (pgvector ANN), then apply geo + price + guardrail filters. Final rank also multiplies by **wish confidence** (below). Falls back to rule/geo match if embedding unavailable.

### Reverse Wishlist

Seed 20–50 wishes in demo; expire 30 days; match on **embedding cosine × wish_score** + size + price + geo.

### Wish confidence scoring (T2 — Bhavya `ml-wish-score`)

Not all wishes are equal. Score buyer intent `0–1` so ranking favours high-intent buyers:

| Feature | Signal |
|---|---|
| `wish_age_days` | recent wish = higher intent (decays toward 30-day expiry) |
| `user_purchase_count` (category) | bought similar before = higher intent |
| `category_affinity` | browse/buy affinity for the category |
| `has_fit_profile` | complete fit profile = serious buyer |

**Model:** logistic regression (`logreg_v1`) — lightweight, explainable, trains on seed/synthetic labels. Output `wish_score` stored on `reverse_wishlist`, used as a multiplier in match ranking. Keeps matching non-trivial without heavyweight ML.

### Demand-weighted disposition (T2 — `engine-demand-weight`)

> The disposition engine should treat **open wishes as a routing input**, not just a post-decision notification target.

When scoring a returned unit, relay-engine queries open wishes matching the unit (embedding + geo) and folds a **demand term** into the channel score:

```
demand_score = Σ over matching open wishes ( wish_score × geo_decay(distance) )
channel_score(rescue|p2p) += w_demand × normalize(demand_score)
```

- 3 high-intent wishes for a size-M Nike hoodie within 10 km → strong pull toward `rescue`/`p2p`.
- Zero wishes for the returned Sony headphones → demand term ≈ 0 → routing leans `refurb`/`restock`.
- Makes disposition a real multi-objective optimization (value + carbon + SLA + **demand**), not a static rule lookup. Rules remain the floor; demand re-weights among viable channels.

### Pair Rescue (T2 — `engine-pair-rescue`, promoted from T3)

> The most genuinely circular flow: two users swap, no money, near-zero added logistics.

Bipartite match: find pairs `(A, B)` where **A's returned unit satisfies B's open wish AND B's returned unit satisfies A's wish**, both within geo proximity.

- Match condition: `embed(unitA) ~ wishB` AND `embed(unitB) ~ wishA` AND `distance(A,B) ≤ radius`.
- Greedy/Hungarian assignment over candidate pairs; demo uses seeded data (3 h build).
- Carbon: one local leg each, no warehouse, no resale intermediary → lowest net CO₂ of any channel.
- Writes `pair_rescue_matches`; both sides earn keep-based credits after 14-day hold.

### Rescue decay pricing (T2 — `engine-rescue-decay`)

Discount **increases as TTL runs out** so recovery value is optimized over time:

```
current_discount_pct = base + (max - base) × (1 - ttl_remaining / ttl_total)
# e.g. base=15%, max=45%  → 15% at start, ~30% at 50% TTL, 45% near expiry
```

- One formula in the Go engine; recomputed on each `/rescue/feed` read (or Celery beat).
- The countdown becomes a **price clock** — strong demo visual.
- Guardrail: floor at AI-suggested price; never below recovery-cost threshold.

### Seller-side return-signal aggregation (T2 — `api-seller-signals`)

Closes the loop from reactive (handle returns) to **proactive (fix what causes returns)** — makes Relay feel like infrastructure.

- Aggregate `return_events` by `sku + reason_code`; when return rate or a single reason crosses a threshold, emit a catalog-fix recommendation.
- Example surfaced on ops: *"SKU X — 34% return rate; primary reason: color mismatch → update product photos."*
- Reason codes power the demo; `ml-return-cluster` (T3, Bhavya) can cluster free-text reasons for richer signals.

### Ops / seller dashboard (T2)

Read-only second persona over existing data — no new pipeline:

| Panel | Source |
|---|---|
| High-return SKUs flagged | aggregate `return_events` + relay-ml fit flags per SKU |
| Catalog-fix recommendations | seller-signal aggregation per `sku + reason_code` (e.g. "fix photos") |
| Items in rescue (live TTL countdown + decay price) | `rescue_listings` where `status=active`, `expires_at`, `current_discount_pct` |
| Chain-depth watch | `product_units.transfer_count` approaching cap (≥3 → forced refurb/donate) |
| Net impact rollup | sum `impact_events.co2_saved_kg` |

### P2P

AI-suggested price from grade; show Condition Passport; escrow status `held` → `released` on confirm.

### LifeLedger

Events: `GRADED | RESCUED | P2P_LISTED | P2P_SOLD | EXCHANGED | DONATED | RECYCLED | REGRADE_REQUESTED`  
Only backend signer writes chain. QR verify recomputes passport hash.

---

## §8 Bhavya — full track

> **Your repo:** `relay-ml` — you have full ownership. Improve approaches below if research suggests better — update `relay-contracts` via PR when response shapes change.

### Mission

Build the **perception layer**: image/video grading + fit flags → structured **ConditionPassport**. Optimize for **engineering efficiency** (CNN handles 80%, Bedrock escalates on low confidence), not token dumping.

### What Shikher needs from you

1. **`ML_SERVICE_URL`** reachable from relay-api (local Docker or Railway).
2. **Stable OpenAPI** per §5 — breaking changes need contracts PR + heads-up.
3. **`confidence` + `model_tier_used`** on every grade response — drives his guardrails/display.
4. **`passport_hash`** — SHA-256 of canonical JSON (document algorithm in README).
5. **Docker image** that runs on CPU for demo (GPU nice, not required).
6. **Contract-aligned passport** (`ml-passport-align`, T0): the current Pydantic `ConditionPassport` drifts from `relay-contracts` v1 — add `schema_version: "1.0.0"`, add `"missing"` to `packaging_state`, make `vertical` an enum (`fashion|electronics`), and relax fields the contract marks optional (`category`, `disposition_hint`, `packaging_state`, `passport_hash`). Fix before `/grade-image` ships so relay-api/engine validation passes.

### What you can use from Shikher (when ready)

| Shikher endpoint | Your use |
|---|---|
| `GET relay-api/health` | Integration smoke test |
| `POST relay-api/demo/seed` | Reset demo data during ML testing |
| Sample `unit_id` + categories from seed script | Consistent test fixtures |

You do **not** need relay-web or relay-engine checked out for daily work.

---

### B0 — Setup (parallel to Shikher T0)

- [ ] Clone `relay-ml`, `relay-contracts`
- [ ] Python 3.11+, `poetry` or `uv` + `requirements.txt`
- [ ] Folder layout:

```
relay-ml/
├── app/
│   ├── main.py              # FastAPI
│   ├── routers/
│   │   ├── grade.py
│   │   └── fit.py
│   ├── models/              # CNN inference
│   ├── pipelines/
│   │   ├── image_grade.py
│   │   ├── video_keyframes.py
│   │   └── bedrock_tiers.py
│   └── schemas/             # Pydantic mirrors contracts
├── training/
│   ├── train_cnn.ipynb
│   └── datasets/
├── models/                  # .pt weights (git-lfs or release artifact)
├── tests/
├── Dockerfile
├── .env.example
└── README.md
```

- [ ] `GET /health` returning model load status
- [ ] AWS credentials for Bedrock in `.env` (never commit)

---

### B1 — Datasets (download first)

| Priority | Dataset | URL | Use |
|---|---|---|---|
| **P0** | E-commerce defect images | [HuggingFace](https://huggingface.co/datasets/prajwalkothwal/ai-generated-ecommerce-images) | Train/eval grade CNN; 12 categories |
| **P0** | Clothing fit | [Kaggle rmisra/clothing-fit-dataset](https://www.kaggle.com/rmisra/clothing-fit-dataset-for-size-recommendation) | Fit flags / MultiFlags |
| **P1** | ASOS GraphReturns | [OSF](https://osf.io/c793h/) | Return graph research |
| **P1** | Amazon Berkeley Objects | HF/Berkeley | Clean baseline images |
| **P2** | MVTec AD | Official | Electronics anomaly pretrain |
| **P2** | Kaputt paper dataset | arXiv 2510.05903 | If obtainable — retail logistics |

**Document in `relay-ml/data/README.md`:** what you downloaded, license, train/val split.

**Minimum viable for 48h:** HF defects (6K) + Kaggle fit.

---

### B2 — Model architecture (recommended; you may improve)

**Multi-task CNN (MobileNetV3-Small or EfficientNet-Lite):**

| Head | Classes |
|---|---|
| `grade` | A+ … D (ordinal/regression) |
| `category` | fashion / electronics / … |
| `defect_type` | multi-label from HF categories |
| `confidence` | calibrated softmax max prob |

**Training:**
- Split HF dataset 80/10/10
- Augment: rotation, lighting, synthetic scuff overlay (Raj 2026 paper idea)
- Export `models/grade_cnn_v1.pt`
- Target: **>85% grade accuracy** on val (demo OK at 80%+)

**Video pipeline:**
1. FFmpeg extract 5–8 keyframes (scene change)
2. Run CNN each frame
3. Aggregate: worst grade wins; union defects
4. Optional Bedrock T2 on worst frame only

---

### B3 — Bedrock tier orchestration (in relay-ml)

```python
# Pseudocode — implement in pipelines/bedrock_tiers.py
def grade_image(image_bytes, unit_id, category):
    if is_blurry(image_bytes):
        return reject("T0")
    passport = cnn_predict(image_bytes)
    if passport.confidence >= 0.85:
        return passport  # T1
    passport = bedrock_haiku_extract(image_bytes)  # T2
    if passport.confidence >= 0.75:
        return passport
    return bedrock_nova_pro(image_bytes)  # T3
```

**Env vars:** `AWS_REGION`, `BEDROCK_MODEL_T2`, `BEDROCK_MODEL_T3`, `OPENAI_API_KEY` (fallback), `GRADING_MODE`.

**Cost:** CNN first always. Log `model_tier_used` for Shikher's Impact/cost story.

#### `GRADING_MODE=bedrock_only` — the "skip CNN" escape hatch (T1, demo-safe)

If the CNN isn't trained in time, the grading pillar must **still produce real grades**. Implement a mode that bypasses the CNN entirely and grades every request with **Nova Lite** directly:

```python
# pipelines/bedrock_tiers.py
def grade_image(image_bytes, unit_id, category):
    if settings.grading_mode == "bedrock_only":
        return bedrock_nova_lite_grade(image_bytes, unit_id, category)  # model_tier_used="bedrock-only"
    if settings.grading_mode == "mock":
        return stub_passport(unit_id, category)
    # default "cnn" path:
    if is_blurry(image_bytes): return reject("T0")
    passport = cnn_predict(image_bytes)
    if passport.confidence >= 0.85: return passport      # T1
    passport = bedrock_haiku_extract(image_bytes)        # T2
    return passport if passport.confidence >= 0.75 else bedrock_nova_pro(image_bytes)  # T3
```

- Slower + pricier per call than CNN, but **no trained model required** → safe for the demo video.
- Returns a valid ConditionPassport per contract; only `model_tier_used` differs.
- Keep CNN path as default so the engineering/cost narrative still holds when the model lands.

**References:**
- `aws-samples/sample-generative-visual-inspection` (Nova Pro defects)
- `aws-samples/aws-smart-product-onboarding` (tier costs)

---

### B4 — Fit flags (`POST /fit-flags`)

**T1 (ship first):** Rule stub + ModCloth aggregate stats per category:
- `runs_large`, `runs_small`, `true_to_size`, `critical_fit`

**T2/T3 stretch:** Simplified **MultiFlags** (SCITEPRESS 2025) or **SizeFlags** (Zalando arXiv 2106.03532):
- Bayesian flags from too-big/too-small return reason counts
- Output matches §5 schema

**Do NOT build Returnformer as hero** — know it ([MDPI 2026](https://www.mdpi.com/1099-4300/28/1/72)), don't clone.

---

### B4.1 — Matching support (embeddings + wish scoring)

These are yours now — they give the matching story real ML depth and keep relay-api lean.

**`POST /embed` (T1, `ml-embed`):** return a 384-d vector for a unit or a wish.
- Input: free `text` OR structured `{ category, grade, size, vertical }`.
- Model: `sentence-transformers/all-MiniLM-L6-v2` (CPU, ~80 MB) or Bedrock Titan Embeddings.
- relay-api calls this for both `product_units` and `reverse_wishlist`; you only return the vector.
- Keep the model name in the response (`model`) so Shikher can store provenance.

**`POST /wish-score` (T2, `ml-wish-score`):** buyer-intent score `0–1`.
- Features: `wish_age_days`, `user_purchase_count`, `category_affinity`, `has_fit_profile`.
- Model: logistic regression (`logreg_v1`) on seed/synthetic labels; explainable coefficients.
- Used by relay-engine matching as a rank multiplier (and feeds demand-weighted disposition).

**`ml-return-cluster` (T3 stretch):** cluster free-text return reasons (e.g. embeddings + KMeans) so seller signals go beyond fixed reason codes ("color not as shown" variants collapse to one signal).

**Contract:** add `/embed` + `/wish-score` to `relay-contracts` relay-ml OpenAPI (`contracts-embed`) before relay-api wires them.

---

### B5 — Endpoints acceptance criteria

#### `POST /grade-image`
- [ ] Accepts JPEG/PNG ≤ 10MB
- [ ] Returns valid ConditionPassport per schema
- [ ] `passport_hash` stable for same input
- [ ] Latency < 3s on CPU with CNN-only path
- [ ] 422 on blur/empty

#### `POST /grade-video`
- [ ] Accepts MP4 ≤ 50MB OR list of images
- [ ] Returns passport with `media_hashes[]` length ≥ 3
- [ ] `model_tier_used` reflects highest tier used

#### `POST /fit-flags`
- [ ] Returns ≥1 flag for known SKUs in seed data
- [ ] `confidence` on each flag

#### `POST /embed`
- [ ] Returns a 384-length float vector for text or structured attrs
- [ ] Deterministic for identical input; `model` name included
- [ ] Latency < 1s on CPU

#### `POST /wish-score`
- [ ] Returns `score` in 0–1 with `model: "logreg_v1"`
- [ ] Monotonic sanity: newer wish + more purchases + fit profile ⇒ higher score

#### `GET /health`
- [ ] `{ "status": "ok", "model_loaded": true, "cnn_version": "v1" }`

---

### B6 — Room to innovate (not rigid)

Bhavya is explicitly encouraged to improve:

| Area | Default plan | You may do better |
|---|---|---|
| CNN architecture | MobileNetV3 multi-head | EfficientNet, ViT-small, ensemble |
| Bedrock prompts | Hand-crafted JSON extraction | Prompt registry + eval set |
| Fit flags | Rules → MultiFlags | SizeFlags Bayesian, ASOS graph features |
| Video | FFmpeg keyframes | Uniform sampling + coverage scoring |
| Confidence | Softmax max | Temperature scaling, MC dropout |
| Defect localization | bbox optional | Grad-CAM → pseudo bbox |

**If you change response schema → PR `relay-contracts` first.**

---

### B7 — Research papers (read order)

| # | Paper | Action |
|---|---|---|
| 1 | Raj 2026 — Edge CNN + DRL reverse logistics (IJCA) | Architecture inspiration |
| 2 | SizeFlags (arXiv 2106.03532) | Fit flags production approach |
| 3 | MultiFlags (SCITEPRESS 2025) | Stretch goal |
| 4 | Returnformer (MDPI 2026) | Know baseline; don't replicate |
| 5 | McKinsey reverse logistics AI 2025 | Disposition framing for slides |
| 6 | SIGIR eCom'22 When Volatility Reigns | Second-hand matching context |
| 7 | Gamification C2C (CentAUR) | Warn Shikher on moral licensing |
| 8 | TRUCE circular platform (MDPI 2025) | LifeLedger trust narrative |

Full list: [`context.md`](./context.md) §6.

---

### B8 — Bhavya 48h schedule (suggested)

| Hours | Focus |
|---|---|
| 0–4 | Skeleton, datasets download, EDA notebook |
| 4–12 | CNN train v1, `/grade-image` CPU inference |
| 12–20 | Video keyframes, `/grade-video`, confidence calibration, `/embed` (unblocks Shikher's pgvector) |
| 20–28 | Bedrock T2/T3 escalation, `/fit-flags` rules, `bedrock_only` mode |
| 28–36 | `/wish-score` logreg, Docker, deploy Railway/AWS, hand Shikher URL |
| 36–48 | MultiFlags OR return-reason clustering OR hard-case tuning OR demo recording |

---

## §9 Shikher — full track

### Mission

Platform lead: repos, integration, Go engine, Python API, frontend, deploy, demo, submission. **Consume Bhavya's HTTP contract — never fork his ML code into relay-api.**

### T0 — Scaffold (you first; Bhavya unblocked after contracts + ml skeleton)

- [ ] Create GitHub repos (5); add Bhavya collaborator
- [ ] `relay-contracts` v1 — schemas + OpenAPI
- [ ] `relay-dev/docker-compose.yml` — postgres, redis, all services
- [ ] `relay-api` — FastAPI + Alembic + Celery config
- [ ] `relay-engine` — Go chi router + config
- [ ] `relay-web` — Next 14 + shadcn init + Relay theme (teal/amber)
- [ ] `relay-ml` — empty skeleton PR for Bhavya to take over OR create and transfer

### T1 — Core demo path

**relay-api:**
- [ ] Auth stub (fixed demo users `fashion_user`, `electronics_user`, `rescue_buyer`)
- [ ] Product catalog CRUD (seeded)
- [ ] Return flow + S3 presigned upload
- [ ] `MLClient` interface + mock + real HTTP impl (`mock` independent of relay-ml `GRADING_MODE`)
- [ ] Celery task: `grade_return_task` → call relay-ml → save passport
- [ ] **Bracketing detection** on `/cart` / checkout (≥3 size/variant same product, strict)
- [ ] **Embeddings**: call relay-ml `/embed` for units + wishes; persist to pgvector; cosine index (generation owned by Bhavya)
- [ ] **Impact events**: write `co2_saved_kg` per disposition from §7 constants
- [ ] LifeLedger stub (DB only) until T2

**relay-engine:**
- [ ] Disposition rule matrix (see below)
- [ ] Rescue TTL scorer (geo haversine, default 3km)
- [ ] **Net-carbon gate** using §7 constants (`rescue 2.4 − km×0.12 > 0`)
- [ ] **pgvector cosine match** (unit ↔ wishlist) — real next-owner matching
- [ ] Guardrails module

**Disposition rule matrix v1:**

| Condition | Channel |
|---|---|
| reason=fit + exchange in stock | `exchange` |
| grade ≥ B + wishlist match + geo | `rescue` |
| grade ≥ B + electronics | `p2p_resale` |
| grade ≥ B + fashion + no rescue | `p2p_resale` |
| grade C + refurb demand | `refurb` |
| grade D + value low | `donate` or `recycle` |
| transfer_count ≥ 3 | block rescue/p2p |

**Demand re-weighting (T2):** rules above set viable channels; the **demand term** (open-wish `Σ wish_score × geo_decay`) then re-ranks among them — strong local demand pulls toward `rescue`/`p2p`, zero demand leans `refurb`/`restock`. See §7 Demand-weighted disposition.

**relay-web pages (T1):**
- [ ] `/` — product grid
- [ ] `/products/[id]` — PDP + fit insight
- [ ] `/checkout` — **active bracketing interceptor** (warn + fit suggestion, not optional)
- [ ] `/returns/new` — wizard
- [ ] `/rescue` — feed + countdown
- [ ] `/account/fit-profile` — mock history

### T2 — Differentiators

- [ ] Reverse wishlist UI + APIs (pgvector match × wish_score)
- [ ] **Demand-weighted disposition** in relay-engine (open wishes feed the score)
- [ ] **Pair Rescue** bipartite matcher in relay-engine (promoted from T3) + `/rescue` swap UI
- [ ] **Rescue decay pricing** formula in relay-engine + price-clock on rescue feed
- [ ] **Seller return-signal aggregation** (api) → ops catalog-fix recommendations
- [ ] **Ops / seller dashboard** (`/ops`): flagged SKUs + return-reason insight + live rescue TTL/decay + chain depth
- [ ] P2P listing flow (electronics tab)
- [ ] Warranty chain display
- [ ] LifeLedger Solidity + Polygon Amoy + QR page
- [ ] Green credits (14-day unlock)
- [ ] Impact Wallet (net CO₂ from §7 constants)
- [ ] `/demo/reset` button (admin)

### T3 — Stretch

- [ ] RL hook interface in Go (demand-weighted scorer is the bridge to this)
- [ ] Donation routing
- [ ] Lambda Rescue expiry

### Shikher 48h schedule (suggested)

**Backend-first (UI is the final phase, not interleaved):**

| Hours | Focus |
|---|---|
| 0–6 | **Schema**: relay-api + relay-engine skeletons, Alembic migration v1 (all §6 tables + pgvector), contracts-embed |
| 6–12 | **Endpoint design**: relay-api routes (returns, rescue, wishlist, p2p, ops) + engine routes — signatures + stubs + mock ML client |
| 12–20 | **High-level flow**: return → grade (mock→real ml) → disposition (engine rules) → persist passport; seed script |
| 20–28 | **Wire logic**: rescue TTL + guardrails + exchange-first + bracketing + pgvector match (call `/embed`) |
| 28–36 | **T2 logic**: demand-weighted disposition, Pair Rescue, decay pricing, seller signals, wishlist, p2p, LifeLedger, credits/impact |
| 36–42 | Integration test full flows via API; deploy AWS + Railway backup (seeded) |
| 42–48 | **UI phase**: wire `web-*` to ready backend; demo video; submission |

---

## §10 Integration matrix

| From → To | Protocol | Data |
|---|---|---|
| relay-web → relay-api | REST JSON | UI requests |
| relay-api → relay-ml | REST multipart/JSON | Images, passports, **embeddings (`/embed`)**, **wish scores (`/wish-score`)** |
| relay-api → relay-engine | REST JSON | Passport + context |
| relay-api → Postgres | SQL | Everything persistent |
| relay-api → Redis | Redis protocol | Rescue TTL, Celery |
| relay-api → S3 | AWS SDK | Media |
| relay-api → Polygon | web3.py / HTTP RPC | LifeLedger txs |
| Celery → relay-ml | REST | Async grading |
| Bhavya tests → relay-api | REST | Optional seed/reset |

**Env wiring (relay-api):**
```
ML_SERVICE_URL=http://relay-ml:8001
RELAY_ENGINE_URL=http://relay-engine:8002
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

---

## §11 Lego tiers + milestone gates

### Tier gates (demo must pass before promoting)

| Gate | Criteria |
|---|---|
| **T0** | All health checks green in docker-compose; web navigable |
| **T1** | Fashion path end-to-end with **real** relay-ml grade (or documented mock with ≤1 click to swap) |
| **T2** | T1 + wishlist match OR rescue claim + LifeLedger verify |
| **T3** | Any stretch feature live |

### If time slips

| Cut order (last to first) | Keep |
|---|---|
| T3 stretch | T2 |
| Impact Wallet / credits UI | Core rescue |
| Full Bedrock T3 | CNN + Haiku |
| Blockchain live verify | DB-stored hash + "verify mock" |
| Electronics path | Fashion path |

**Never cut:** Condition Passport, disposition, one matching feature (Rescue OR wishlist), guardrails mention in demo.

---

## §12 Demo script + UI pages

### 3-minute video beats

| Time | Scene |
|---|---|
| 0:00–0:25 | Problem + return chain risk + our guardrails |
| 0:25–0:45 | Prevention: **bracketing interceptor** at checkout (3 sizes → keep one) + fit insight |
| 0:45–1:20 | Fashion: return → grade passport → exchange OR rescue (net CO₂ shown) |
| 1:20–1:45 | Reverse wishlist **pgvector match** (demand-weighted) + decay-price claim countdown |
| 1:45–2:05 | **Pair Rescue**: A↔B swap, no money, near-zero carbon — the most circular 20s |
| 2:05–2:30 | Electronics: P2P list + warranty on LifeLedger + QR verify |
| 2:30–2:55 | **Ops/seller dashboard**: flagged SKUs + "fix your photos" signal + live rescue TTL + chain depth |
| 2:55–3:00 | HLD slide: Go engine + Bedrock tiers + scale |

### Page list

| Route | Tier | Owner |
|---|---|---|
| `/` | T0 | Shikher |
| `/products/[id]` | T1 | Shikher |
| `/checkout` (bracketing interceptor) | T1 | Shikher |
| `/returns/new` | T1 | Shikher |
| `/rescue` | T1 | Shikher |
| `/wishlist` | T2 | Shikher |
| `/ops` (seller/ops dashboard) | T2 | Shikher |
| `/p2p/sell/[returnId]` | T2 | Shikher |
| `/lifeledger/[unitId]` | T2 | Shikher |
| `/demo/reset` | T2 | Shikher |

---

## §13 Deploy

### AWS (primary)

| Service | Runs |
|---|---|
| ECS Fargate | relay-api, relay-engine, relay-ml, celery worker |
| RDS PostgreSQL | db.t3.micro + pgvector |
| ElastiCache Redis OR Redis on ECS | cache + celery |
| S3 | media + optional static |
| SQS | celery broker (prod) |
| Bedrock | ap-south-1 or us-east-1 |
| CloudFront + S3 OR Vercel | relay-web |

### Railway (backup)

- One project, multi-service from `relay-dev/docker-compose.railway.yml`
- Run `seed.py` on deploy
- **Record demo video here** if AWS unstable

### Demo redundancy

1. Live AWS URL  
2. Railway URL (pre-recorded video)  
3. Zustand offline snapshot in web (network fail during live pitch)

---

## §14 Submission checklist (HackOn S6 pattern)

- [ ] GitHub org/repos linked (all 5)
- [ ] README per repo: problem, run locally, env vars, architecture link
- [ ] Demo video **< 3 min** — product not slides
- [ ] PPT 8–12 slides: problem, solution, HLD, scale, metrics, guardrails
- [ ] Working prototype URL (AWS or Railway)
- [ ] `context.md` + `plan.md` in hackathon root or relay-dev docs
- [ ] Tech: AWS Bedrock usage documented
- [ ] Optional: architecture diagram PNG export

---

## §15 Research paper bank

See [`context.md`](./context.md) §6 and Bhavya §B7.

---

## §16 Dataset catalog

See [`context.md`](./context.md) §27 and Bhavya §B1.

---

## §17 Environment variables

### relay-ml (Bhavya)

```bash
PORT=8001
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
GRADING_MODE=cnn               # cnn | bedrock_only | mock  (bedrock_only = skip-CNN demo-safe fallback)
BEDROCK_MODEL_T1=amazon.nova-lite-v1:0   # used by bedrock_only path
BEDROCK_MODEL_T2=anthropic.claude-3-haiku-...
BEDROCK_MODEL_T3=amazon.nova-pro-v1:0
OPENAI_API_KEY=           # fallback
CNN_MODEL_PATH=./models/grade_cnn_v1.pt
CONFIDENCE_THRESHOLD_T2=0.85
CONFIDENCE_THRESHOLD_T3=0.75
EMBEDDING_MODEL=all-MiniLM-L6-v2         # 384-dim; /embed (sentence-transformer or Bedrock Titan)
WISH_SCORE_MODEL_PATH=./models/wish_logreg_v1.pkl   # /wish-score logistic regression
```

### relay-api (Shikher)

```bash
PORT=8000
DATABASE_URL=postgresql://relay:relay@postgres:5432/relay
REDIS_URL=redis://redis:6379/0
ML_SERVICE_URL=http://relay-ml:8001
RELAY_ENGINE_URL=http://relay-engine:8002
S3_BUCKET=relay-media
AWS_REGION=ap-south-1
RESCUE_DISCOUNT_BASE=0.15        # decay pricing floor
RESCUE_DISCOUNT_MAX=0.45         # decay pricing ceiling near TTL expiry
PAIR_RESCUE_RADIUS_KM=10
POLYGON_RPC_URL=https://rpc-amoy.polygon.technology
LIFELEDGER_PRIVATE_KEY=     # testnet only
CELERY_BROKER_URL=redis://redis:6379/1
```

### relay-web (Shikher)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## §18 Definition of Done + sync

### PR Definition of Done

- [ ] Linked task id from To Do table
- [ ] Tests or manual steps in PR description
- [ ] No secrets committed
- [ ] Contract unchanged OR relay-contracts PR merged first
- [ ] Demo tier still passes locally

### Sync cadence

- **Daily 15 min** (or per milestone): demo walkthrough, blockers, contract changes
- **Async:** GitHub issues per task id; tag owner

### Agent handoff (Codex / Cursor)

When spawning an agent on **relay-ml**, paste:
1. This file §8 + §5 + §16  
2. Link to `relay-contracts` OpenAPI  
3. Current task id from To Do table  

When spawning on **relay-api/web/engine**, paste:
1. This file §9 + §5 + §6 + §10  
2. Current `ML_SERVICE_URL` status (mock vs live)

---

## Sequencing summary

```
M0 (parallel)
  Shikher: repos + contracts + compose + api/engine/web skeletons
  Bhavya:  ml skeleton + datasets + /health

M1 (parallel) — TARGET: T1 demo
  Shikher: returns API + Go disposition + rescue + bracketing(≥3) + pgvector match + carbon constants + web wizard + seed + mock→real ML
  Bhavya:  CNN v1 + /grade-image + bedrock_only escape hatch + /grade-video + /fit-flags rules + /embed + passport contract align

M2 (parallel) — TARGET: T2 demo
  Shikher: wishlist + demand-weighted disposition + pair rescue + rescue decay pricing + seller signals + ops/seller dashboard + Impact Wallet + p2p + LifeLedger + warranty UI
  Bhavya:  Bedrock tiers + confidence tuning + /wish-score (logreg) + optional MultiFlags

M3 — Deploy + video + submission
  Shikher: AWS + Railway + PPT + README
  Bhavya:  support hard cases + demo assets

M4 (stretch) — T3
  Both: RL hook, donation routing, return-reason clustering, analytics
```

---

*Last updated: 2026-06-14 (Session 6 — bracketing(≥3), ops persona, carbon constants, pgvector-T1, Bedrock-only grading; + demand-weighted disposition, wish-score, Pair Rescue, seller signals, rescue decay pricing; embeddings/wish-score assigned to Bhavya) · Maintained alongside [`context.md`](./context.md)*
