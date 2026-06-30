# Relay — Technical Build Plan (HackOn PS #2)

> **Purpose:** Single technical source of truth between brainstorm (`context.md`) and implementation.  
> **Audience:** Shikher, Bhavya, and coding agents (Codex, Cursor, etc.).  
> **Brainstorm / decisions log:** see `[context.md](./context.md)` — this file is *how we build*, not *why we chose*.

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

## Run / Restart (local) — backend + infra + seed

> All repos are cloned as siblings; run `docker compose` from `relay-dev/`. On Windows use `127.0.0.1` (not `localhost`) for host→container calls — Docker Desktop's IPv6 (`::1`) proxy black-holes.

```bash
cd relay-dev

# 1) Start ALL backend services + infra
#    (postgres[pgvector] + redis + relay-ml + relay-engine + relay-api + relay-worker)
docker compose --profile apps up -d --build
#    infra ONLY (postgres + redis): omit the profile →  docker compose up -d

# 2) Apply DB migrations (schema → head = 0005)
docker compose exec relay-api alembic upgrade head

# 3) Seed real demo data (DB + LifeLedger + S3 product images)
docker compose exec relay-api python -m scripts.seed
#    …or the equivalent canonical endpoint:  POST http://127.0.0.1:8010/demo/reset

# 4) (optional) end-to-end smoke check  → expect: SMOKE_OK
docker compose exec relay-api python scripts/smoke.py

# Health:  http://127.0.0.1:8010/health (api) · :8001 (ml) · :8002 (engine)
# Frontend (run separately):  cd relay-web ; npm install ; npm run dev  → http://localhost:3000
```

**Notes**

- **Real Bedrock grading:** set `GRADING_MODE=bedrock_only` (compose default is `mock`); AWS creds live in `relay-ml/.env`. `/embed`, `/wish-score`, `/fit-flags` use Bhavya's real models regardless of mode.
- **S3 seeding** needs S3 creds in `relay-api/.env` (bucket `relay-media-s3`, `us-east-1`); product/listing images upload there as public URLs.
- **Frontend → API:** point relay-web at `VITE_API_URL=http://127.0.0.1:8010` (the compose `relay-web` default `http://localhost:8000` is stale).
- **Full wipe & restart:** `docker compose down -v` (drops the pg volume) → repeat steps 1–3.

---

## To Do (task board)

Copy status into PR descriptions. **Definition of Done (DoD)** = code merged + acceptance criteria met + demo path still works at declared tier.

> **Build order — backend-first, UI last (LOCKED Session 6c).** Shikher builds in this sequence regardless of tier labels:
> **1) schema** (DB migrations + contracts) → **2) API endpoint design** (route signatures, request/response) → **3) high-level flow** (services talk: return → grade → disposition → match → credits) → **4) wire all logic** (real engine/ML/persistence, integration-tested via API) → **5) UI last** — all `web-`* tasks are **deferred to a final UI phase**; when the design is ready, Shikher only wires the existing backend to it. Tier labels on `web-`* rows indicate which backend tier they pair with, not when they're built. T1/T2 acceptance is validated via API + integration tests until the UI phase.


| id                                                           | tier         | owner   | content                                                                                                                                                                                                                                         | status                                                                                                                                                       |
| ------------------------------------------------------------ | ------------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| contracts-v1                                                 | T0           | Shikher | Publish `relay-contracts` v1: ConditionPassport JSON schema, OpenAPI for relay-ml + relay-api public routes                                                                                                                                     | ✅ done                                                                                                                                                       |
| contracts-embed                                              | T0           | Both    | Add `/embed` + `/wish-score` to relay-ml OpenAPI; vector + wish-score schemas                                                                                                                                                                   | ✅ done                                                                                                                                                       |
| repo-scaffold                                                | T0           | Shikher | Create 5 GitHub repos, branch `main`, `relay-dev` docker-compose, README per repo                                                                                                                                                               | ✅ done (repos + compose + relay-dev README)                                                                                                                  |
| ml-dataset                                                   | T0           | Bhavya  | Download HF e-commerce defects + Kaggle fit dataset; document in `relay-ml/data/README.md`                                                                                                                                                      | ✅ done (branch `feat/ml-dataset`)                                                                                                                            |
| ml-health                                                    | T0           | Bhavya  | `relay-ml`: FastAPI skeleton, `GET /health`, Docker, `.env.example`                                                                                                                                                                             | ✅ done (merge PR #1 → main)                                                                                                                                  |
| api-skeleton                                                 | T0           | Shikher | `relay-api`: FastAPI skeleton, Postgres + Redis docker, Alembic init                                                                                                                                                                            | ✅ done (pytest 2/2; /health)                                                                                                                                 |
| engine-skeleton                                              | T0           | Shikher | `relay-engine`: Go chi/fiber skeleton, `GET /health`                                                                                                                                                                                            | ✅ done (go build ok)                                                                                                                                         |
| db-schema                                                    | T0           | Shikher | Alembic migration v1 — all §6 tables + pgvector extension (schema-first, before endpoints)                                                                                                                                                      | ✅ done (applied live on pg16: 15 tables, vector+pgcrypto, 2 HNSW indexes)                                                                                    |
| web-shell                                                    | **UI phase** | Shikher | `relay-web`: Next + shadcn — **deferred to final UI phase** (backend-first)                                                                                                                                                                     | ✅ done (UI phase shipped)                                                                                                                                    |
| ml-grade-image                                               | T1           | Bhavya  | `POST /grade-image` → ConditionPassport (CNN baseline + optional Bedrock T2)                                                                                                                                                                    | ✅ done (Bedrock grade path live)                                                                                                                             |
| ml-bedrock-only                                              | T1           | Bhavya  | `GRADING_MODE=bedrock_only` escape hatch — real ConditionPassport via Nova Lite from image, **no CNN** (demo-safe; T2 cost/req)                                                                                                                 | ✅ done                                                                                                                                                       |
| ml-grade-video                                               | T1           | Bhavya  | `POST /grade-video` → keyframe pipeline + aggregated passport                                                                                                                                                                                   | ✅ done (Bedrock keyframe path)                                                                                                                               |
| ml-fit-flags                                                 | T1           | Bhavya  | `POST /fit-flags` → article flags (rules stub → MultiFlags stretch)                                                                                                                                                                             | ✅ done                                                                                                                                                       |
| ml-confidence                                                | T1           | Bhavya  | Return `confidence` + `model_tier_used`; document escalation threshold                                                                                                                                                                          | ✅ done                                                                                                                                                       |
| ml-passport-align                                            | T0           | Bhavya  | Align Pydantic `ConditionPassport` to `relay-contracts` v1 (add `schema_version`, `packaging_state=missing`, `vertical` enum, optional vs required)                                                                                             | ✅ done                                                                                                                                                       |
| api-returns                                                  | T1           | Shikher | Return intake API, S3 upload, call relay-ml, persist passport                                                                                                                                                                                   | ✅ done (create→media→grade→passport persisted; S3 deferred, synchronous grade for demo)                                                                      |
| api-mock-ml                                                  | T1           | Shikher | Mock ML client until Bhavya URL live; swap via `ML_SERVICE_URL`                                                                                                                                                                                 | ✅ done (swappable `MLClient` Protocol+Mock+HTTP; `USE_MOCK_ML`)                                                                                              |
| engine-disposition                                           | T1           | Shikher | Go: `POST /disposition/score` — rule engine (exchange/rescue/p2p/…)                                                                                                                                                                             | ✅ done (real Go rule engine + guardrails; verified 5 cases; `USE_MOCK_ENGINE=false`)                                                                         |
| engine-rescue-ttl                                            | T1           | Shikher | Go: Rescue listing TTL + geo radius scoring                                                                                                                                                                                                     | ✅ done (geo radius + TTL on `/rescue/feed`, relay-api per §6 reconciliation)                                                                                 |
| api-rescue                                                   | T1           | Shikher | Rescue feed + claim APIs; guardrails v1 (eligibility, chain cap)                                                                                                                                                                                | ✅ done (feed + claim; guardrails: eligibility, return-rate, chain cap, status)                                                                               |
| api-exchange                                                 | T1           | Shikher | Exchange-first routing when reason=size + SKU in stock                                                                                                                                                                                          | ✅ done (engine exchange-first + relay-api `exchange_available` check)                                                                                        |
| api-bracketing                                               | T1           | Shikher | Bracketing detection: flag cart/checkout when ≥3 size/variant of same product (strict); expose on cart insight                                                                                                                                  | ✅ done (≥3 strict; suggests fit-profile size; on `GET /cart`)                                                                                                |
| ml-embed                                                     | T1           | Bhavya  | `POST /embed` → 384-d vector from passport attrs / wish text (sentence-transformer or Bedrock Titan)                                                                                                                                            | ✅ done                                                                                                                                                       |
| api-embeddings                                               | T1           | Shikher | Call relay-ml `/embed`; persist `product_units.embedding` + `reverse_wishlist.embedding`; pgvector cosine index                                                                                                                                 | ✅ done (units + wishes embedded via ML `/embed`; HNSW cosine index live)                                                                                     |
| engine-match-vector                                          | T1           | Shikher | Go/SQL cosine match: unit ↔ wishlist via pgvector ANN (real matching, not geo-only)                                                                                                                                                             | ✅ done (pgvector `<=>` cosine × wish_score in relay-api per §6; geo+price filters)                                                                           |
| api-seed                                                     | T1           | Shikher | `scripts/seed.py` — users, catalog, wishes, demo geo, bracketing carts                                                                                                                                                                          | ✅ done (`services/seed.py` + `scripts/seed.py` + `POST /demo/reset`)                                                                                         |
| web-checkout-insight                                         | T1           | Shikher | Fit insight banner on PDP/checkout (fashion)                                                                                                                                                                                                    | ✅ done (UI phase shipped)                                                                                                                                    |
| web-bracketing                                               | T1           | Shikher | Active bracketing interceptor at checkout (warn + fit suggestion, not passive)                                                                                                                                                                  | ✅ done (UI phase shipped)                                                                                                                                    |
| web-return-wizard                                            | T1           | Shikher | Return flow: reason → upload → grade result → outcome                                                                                                                                                                                           | ✅ done (UI phase shipped)                                                                                                                                    |
| web-rescue-feed                                              | T1           | Shikher | Rescue cards + countdown TTL                                                                                                                                                                                                                    | ✅ done (UI phase shipped)                                                                                                                                    |
| api-wishlist                                                 | T2           | Shikher | Reverse Wishlist CRUD + pgvector match on return graded (uses `api-embeddings`)                                                                                                                                                                 | ✅ done (create w/ embed+wish_score; `GET /wishlist/matches` cosine)                                                                                          |
| ml-wish-score                                                | T2           | Bhavya  | Wish confidence score (logistic reg on wish-age, user purchase history, category affinity) → ranking input                                                                                                                                      | ✅ done                                                                                                                                                       |
| engine-demand-weight                                         | T2           | Shikher | Disposition scoring weights open-wish demand (wishlist as routing input, not post-match lookup)                                                                                                                                                 | ✅ done (demand term in engine score; `nearest_km` drives net-carbon)                                                                                         |
| engine-pair-rescue                                           | T2           | Shikher | Pair Rescue: bipartite A↔B swap match (each return satisfies other's wish, geo-bounded) — promoted from T3                                                                                                                                      | ✅ done (`services/pair_rescue.py` + `GET /rescue/pair-matches`; cosine both-ways + geo; writes `pair_rescue_matches`)                                        |
| engine-rescue-decay                                          | T2           | Shikher | Rescue decay pricing: discount rises as TTL drops (time-decay formula); countdown = price clock                                                                                                                                                 | ✅ done (decay recomputed on feed/ops read; base 15%→max 45%)                                                                                                 |
| api-seller-signals                                           | T2           | Shikher | Seller-side return-signal aggregation per SKU+reason → catalog-fix recommendation (surfaced on ops)                                                                                                                                             | ✅ done (threshold-gated; `/ops/seller-signals` + `/ops/high-return-skus`)                                                                                    |
| ml-return-cluster                                            | T3           | Bhavya  | Stretch: cluster free-text return reasons (NLP) to power seller signals beyond reason codes                                                                                                                                                     | ✅ done                                                                                                                                                       |
| api-ops-dashboard                                            | T2           | Shikher | Ops API: high-return SKUs (relay-ml flagged), live rescue TTL list, chain-depth view, seller signals                                                                                                                                            | ✅ done (`/ops/high-return-skus`, `/ops/rescue-live`, `/ops/chain-depth`, `/ops/impact`)                                                                      |
| web-ops-dashboard                                            | **UI phase** | Shikher | Ops/seller view: flagged SKUs table + return-reason insight + rescue TTL countdown + chain depth                                                                                                                                                | ✅ done (UI phase shipped)                                                                                                                                    |
| api-impact                                                   | T2           | Shikher | Impact Wallet net CO₂ via hard-coded per-channel constants (see §7 Carbon model)                                                                                                                                                                | ✅ done (`/users/me/impact`; impact_events + green credits on disposition)                                                                                    |
| api-p2p                                                      | T2           | Shikher | One-click P2P list + escrow stub                                                                                                                                                                                                                | ✅ done (`POST /p2p/listings`; AI-suggested price default; escrow stub)                                                                                       |
| api-warranty                                                 | T2           | Shikher | Warranty chain records on electronics units                                                                                                                                                                                                     | ✅ done (`GET /units/{id}/warranty` + repair-event append; seeded on electronics)                                                                             |
| api-lifeledger                                               | T2           | Shikher | Polygon Amoy write + QR verify endpoint                                                                                                                                                                                                         | ✅ done (swappable `LedgerClient` mock+web3; anchors GRADED/channel events; verify recomputes hash → tamper-evident. Real Amoy write ready, needs funded key) |
| web-p2p-warranty                                             | T2           | Shikher | Electronics tab: P2P list + warranty + LifeLedger viewer                                                                                                                                                                                        | ✅ done (UI phase shipped)                                                                                                                                    |
| web-lifeledger-qr                                            | T2           | Shikher | QR scan verify UI                                                                                                                                                                                                                               | ✅ done (UI phase shipped)                                                                                                                                    |
| api-credits                                                  | T2           | Shikher | Green credits (keep-based, 14-day rule) — P2 supporting                                                                                                                                                                                         | ✅ done (credits written with `unlock_at = now+14d`; wallet exposes locked vs spendable balance)                                                              |
| api-early-access                                             | T2           | Shikher | Pillar 5 flywheel: credits buy ACCESS not discounts — lifetime-credit tier gates an early-access embargo window on the Rescue feed                                                                                                              | ✅ done (`/rescue/feed` embargo filter keyed on lifetime credits; `/users/me/impact` exposes tier; seed gives demo user the tier, buyer none)                 |
| ml-bedrock-tiers                                             | T2           | Bhavya  | T0–T3 Bedrock escalation in relay-ml (confidence-gated)                                                                                                                                                                                         | ✅ done                                                                                                                                                       |
| ml-multiflags                                                | T3           | Bhavya  | Stretch: simplified MultiFlags on ModCloth aggregates                                                                                                                                                                                           | ✅ done                                                                                                                                                       |
| engine-rl-hook                                               | T3           | Shikher | Disposition interface for future RL; rules remain default                                                                                                                                                                                       | ✅ done (`Scorer` interface + `RuleScorer` default + `RLScorer` fallback stub; `DISPOSITION_SCORER` env)                                                      |
| **— Track B — Second Life (resell + republish) — see §19 —** |              |         |                                                                                                                                                                                                                                                 |                                                                                                                                                              |
| trackb-resale-pricer                                         | T2           | Shikher | Deterministic fallback resale pricer (`condition × age × original_price`); `list_price` = MEAN of `price_range`; unifies rescue + resale pricing (§19.6)                                                                                        | ✅ done (fallback pricer live ahead of ML)                                                                                                                    |
| trackb-grade-and-price                                       | T2           | Bhavya  | `POST /grade-and-price` → resale grade + `price_range` (ConditionPassport-compatible + resale fields); see §5 + §8 B4.2                                                                                                                         | specced (api fallback live; real model = Bhavya)                                                                                                             |
| trackb-db                                                    | T2           | Shikher | Additive migration: `resale_listings` + `order_items.delivered_at` + `products.image_url` (§6 Track B additions)                                                                                                                                | in progress                                                                                                                                                  |
| trackb-return-window                                         | T2           | Shikher | Return-window gating: order items expose `returnable`/`resellable`/`days_to_return_deadline` (`return_window_days`=7) (§19.2)                                                                                                                   | in progress                                                                                                                                                  |
| trackb-second-life                                           | T2           | Shikher | Second Life endpoints: buyer resell, combined catalogue, stub checkout, seller refurbished + relist (escrow/ownership/ledger stub) (§19.3–19.4)                                                                                                 | in progress                                                                                                                                                  |
| trackb-price-fit                                             | T2           | Shikher | Genie / reverse-wishlist `price_fit` flag when wish `max_price` is within a band of an item's `list_price` (§19.6)                                                                                                                              | in progress                                                                                                                                                  |
| trackb-seed-assets                                           | T2           | Shikher | `seed_assets/` real product manifest + images served statically; `/demo/reset` builds full REAL DB + LifeLedger (catalogue, orders, returns, refurb, listings, passports, credits) (§19.7)                                                      | in progress                                                                                                                                                  |
| web-second-life                                              | **UI phase** | Shikher | Buyer Second Life catalogue page + Second Life section on landing below the motto (§19.9)                                                                                                                                                       | in progress                                                                                                                                                  |
| web-seller-shell                                             | **UI phase** | Shikher | Seller persona lands on Ops; nav = Ops + order tracking; returned/REFURBISHED units show "relist for resale" upload (§19.8)                                                                                                                     | in progress                                                                                                                                                  |
| **— Track C — Return-grading decisions (§20) —**             |              |         |                                                                                                                                                                                                                                                 |                                                                                                                                                              |
| trackc-size-pristine                                         | T2           | Shikher | Size/fit return = pristine asset: floor resale grade to A / "Like New", clear cosmetic defects, disposition/pricing at MINIMAL discount (§20.1)                                                                                                 | ✅ done                                                                                                                                                       |
| trackc-size-gate                                             | T2           | Shikher | Next-owner size-match gate in `matching.py`: candidate passes only if unit size == wish size OR fit_profile confidence > 0.7 (PRD §7) (§20.2)                                                                                                   | ✅ done                                                                                                                                                       |
| trackc-verification                                          | T2           | Both    | Expected-context verification: relay-api sends `expected_size/color/title`; relay-ml enriches the grade prompt → additive `verification` block (no extra image/call); surfaced on ConditionPassport + ResaleListing; relay-api fallback (§20.3) | ✅ done (relay-ml prompt change flagged for Bhavya)                                                                                                           |
| trackc-wrong-item                                            | T2           | Shikher | `wrong_item` fully gated: flagged `return_to_seller`, no grade/passport/GRADED/listing; `_REASON_FIX` pick-pack seller signal (§20.4)                                                                                                           | ✅ done                                                                                                                                                       |
| trackc-exchange                                              | T2           | Shikher | `POST /orders/items/{id}/exchange`: in-window, no ML grade; replacement line (`exchanged_from_id`) + pristine returned unit → Path-A rescue at original/minimal discount + `EXCHANGED` event (§20.5)                                            | ✅ done                                                                                                                                                       |
| trackc-db-0005                                               | T2           | Shikher | Additive migration 0005: `product_units.size`, `order_items.return_state`, `order_items.exchanged_from_id` (`verification` lives in passport JSON) (§20.6)                                                                                      | ✅ done                                                                                                                                                       |
| trackc-seed-smoke                                            | T2           | Shikher | Seed: size-pristine rescue, `wrong_item` flagged + ops signal, completed exchange (EXCHANGED + pending pickup); `scripts/smoke.py` asserts all five → SMOKE_OK (§20.7)                                                                          | ✅ done                                                                                                                                                       |
| **— Track D — Finals MVP hardening (§21) —**                 |              |         |                                                                                                                                                                                                                                                 |                                                                                                                                                              |
| trackd-return-confidence                                     | T2.5         | Shikher | Prevention upgrade: `Return Confidence` / `KeepScore` layer for cart + PDP using user fit history, SKU return health, review/fit signals, bracketing, and safer interventions (§21.1)                                                           | ✅ done (smoke-verified)                                                                                                                                       |
| trackd-grading-productize                                    | T2.5         | Bhavya  | Productize Bedrock grading: prompt registry/versioning, confidence bands, capture-quality gates, grading audit trail, bbox/defect overlays where available (§21.2)                                                                              | planned                                                                                                                                                      |
| trackd-genie-infra                                           | T2.5         | Bhavya  | Genie as marketplace matching engine: multi-stage retrieve→rerank, match reasons, waiting state, price/size/geo/trust/freshness fit, aggressive false-positive rejection (§21.3)                                                                | planned                                                                                                                                                      |
| trackd-rescue-dispatch                                       | T2.5         | Shikher | Rescue Dispatch Score: Uber/FoodMatch-style weighted bipartite matching over buyer demand × unit TTL × distance × price acceptance × carbon × failed-claim risk (§21.4)                                                                         | ✅ done (smoke-verified)                                                                                                                                       |
| trackd-mvp-bug-sweep                                         | T2.5         | Shikher | Async MVP bug sweep while Track D lands: lifecycle/state correctness, E2E flow checks, frontend copy, reliability issues found during usage                                                                                                     | ongoing                                                                                                                                                      |
| deploy-aws                                                   | T2           | Shikher | ECS/RDS/S3 deploy path                                                                                                                                                                                                                          | pending                                                                                                                                                      |
| deploy-railway                                               | T2           | Shikher | Railway compose backup + seeded demo                                                                                                                                                                                                            | pending                                                                                                                                                      |
| finals-presentation                                          | T2           | Both    | Finals presentation narrative + live walkthrough plan; no separate demo-video requirement unless the rules change                                                                                                                               | pending                                                                                                                                                      |
| submission                                                   | T2           | Shikher | GitHub links, PPT, README, docs                                                                                                                                                                                                                 | pending                                                                                                                                                      |


---

## Document map


| Section | Contents                                                                                       |
| ------- | ---------------------------------------------------------------------------------------------- |
| §1      | Problem & positioning (brief — details in context.md)                                          |
| §2      | What we are building (features + priorities)                                                   |
| §3      | Architecture HLD                                                                               |
| §4      | Repos, branching, PR flow                                                                      |
| §5      | Shared contracts (schemas + APIs)                                                              |
| §6      | Data model (Postgres)                                                                          |
| §7      | Feature specs + guardrails                                                                     |
| §8      | **Bhavya — full track** (research, data, ML, endpoints, freedom to improve)                    |
| §9      | **Shikher — full track** (platform, integration, UI, infra)                                    |
| §10     | Integration matrix (who calls whom)                                                            |
| §11     | Lego tiers + 48h schedule                                                                      |
| §12     | Demo script + UI pages                                                                         |
| §13     | Deploy (AWS + Railway)                                                                         |
| §14     | Submission checklist                                                                           |
| §15     | Research paper bank (Bhavya)                                                                   |
| §16     | Dataset catalog                                                                                |
| §17     | Environment variables                                                                          |
| §18     | Definition of Done + sync cadence                                                              |
| §19     | **Track B — Second Life** (resell + republish, grade-and-price, seeding, seller/buyer UX)      |
| §20     | **Track C — Return-grading decisions** (size returns, verification, wrong-item gate, exchange) |
| §21     | **Track D — Finals MVP hardening** (prevention, grading, Genie, Rescue dispatch)               |


---

## §1 Problem & positioning (summary)

**Problem Statement #2:** Returned/unused products should find their next best owner via AI disposition, quality grading, refurbished trust, green incentives, P2P resale, and return prevention.

**Our reframe (do not pitch as generic return prediction):**

- **Disposition:** where should *this unit* go?
- **Matching:** *who* is the next owner?

**Avoid:** Returnformer clone, EarthScore-only gamification, Amazon UI clone, token-dumping Bedrock on every image.

**Full brainstorm:** `[context.md](./context.md)` §1–22.

---

## §2 What we are building

### P0 — must work for T1 demo (fashion primary path)


| Feature                    | Description                                                                                                                                         |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Fit Intelligence**       | Checkout/PDP insight: user fit profile + article flags; exchange nudge — not scary "23% return risk"                                                |
| **Bracketing interceptor** | Active checkout flag when cart has ≥3 size/variant of same product (strict; the ~40%-of-fashion-returns driver) → fit suggestion + "keep one" nudge |
| **Return + grade**         | Photo upload → Condition Passport JSON (CNN **or** `bedrock_only` real-grade fallback)                                                              |
| **Disposition engine**     | Go service scores: exchange · rescue · p2p · refurb · donate · recycle                                                                              |
| **Exchange-first**         | Return reason size/fit + exchange SKU in stock → offer swap before warehouse                                                                        |
| **Return Rescue**          | Geo + TTL feed; nearby buyer claims; Zomato-inspired                                                                                                |
| **Next-owner matching**    | pgvector cosine match (unit embedding ↔ Reverse Wishlist embedding) — real vector retrieval, not geo-only                                           |
| **Guardrails**             | Eligibility score, chain depth cap, net-carbon gate (uses §7 carbon constants)                                                                      |


### P1 — T2 differentiators


| Feature                         | Description                                                                                                                                                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Reverse Wishlist**            | Buyer posts demand; pgvector match when return graded                                                                                                                                                               |
| **Demand-weighted disposition** | Open wishes feed the disposition score itself — high local demand for a SKU pulls routing toward rescue/p2p (routing input, not post-match lookup)                                                                  |
| **Wish confidence scoring**     | Rank matches by buyer intent (wish-age, purchase history, category affinity) — lightweight ML, not a flat lookup                                                                                                    |
| **Pair Rescue**                 | Bipartite A↔B swap: each user's return satisfies the other's wish, geo-bounded — near-zero-carbon, no resale intermediary (promoted from T3)                                                                        |
| **Rescue decay pricing**        | Discount rises as TTL drops (15%→30%→45%); countdown becomes a price clock — optimizes recovery value over time                                                                                                     |
| **Ops / seller dashboard**      | Second persona: high-return SKUs flagged by relay-ml, **seller return-signal aggregation** (e.g. "34% return rate, reason: color mismatch → fix photos"), live rescue listings with TTL countdown, chain-depth view |
| **P2P one-click list**          | From return flow; escrow stub; LifeLedger passport shown                                                                                                                                                            |
| **Warranty chain**              | Electronics: remaining warranty + repair events on passport                                                                                                                                                         |
| **LifeLedger verify**           | QR → hash check on Polygon Amoy testnet                                                                                                                                                                             |


### P2 — supporting


| Feature           | Description                                                                                                                                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Green credits** | Earn on *kept* rescue/exchange (14-day rule) — not purchase volume. **Spend = ACCESS, not discounts:** lifetime credits ≥ threshold unlock early access to the Rescue feed (see §7 Impact Wallet / early-access flywheel) |
| **Impact Wallet** | Net CO₂ vs baseline using **hard-coded per-channel constants** (rescue = 2.4 kg saved) — see §7 Carbon model. Shows CO₂, locked/spendable balance, and early-access tier                                                  |


### T3 — stretch (Lego add-on; pitch optional)

RL disposition hook · Donation routing · Full MultiFlags · return-reason NLP clustering · ClickHouse analytics

### Dual vertical demo


| Vertical        | Live demo                                                    | Screen time |
| --------------- | ------------------------------------------------------------ | ----------- |
| **Fashion**     | Fit insight → return → grade → exchange OR rescue + wishlist | ~70%        |
| **Electronics** | Return → video grade → P2P + warranty + LifeLedger QR        | ~30%        |


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


| Service             | Repo            | Language   | Owns                                                                                                        |
| ------------------- | --------------- | ---------- | ----------------------------------------------------------------------------------------------------------- |
| **relay-web**       | relay-web       | TypeScript | All UI, Zustand stores, API client                                                                          |
| **relay-api**       | relay-api       | Python     | BFF, auth stub, orders/returns/wishlist/p2p/credits, Celery workers, DB migrations, seed, LifeLedger client |
| **relay-engine**    | relay-engine    | Go         | Disposition scoring, Rescue geo/TTL, match ranking (calls pgvector via API or direct read)                  |
| **relay-ml**        | relay-ml        | Python     | Image/video grading, fit flags, CNN weights, Bedrock tier orchestration                                     |
| **relay-contracts** | relay-contracts | YAML/JSON  | OpenAPI + JSON Schema — no runtime                                                                          |


### Scale story (for judges — design for this, ship minimal)


| Concern        | 48h ship                 | Scale path                      |
| -------------- | ------------------------ | ------------------------------- |
| API throughput | ECS Fargate 1–2 tasks    | HPA / EKS                       |
| Grade backlog  | Celery + Redis/SQS       | SageMaker batch + Bedrock batch |
| Rescue TTL     | Redis keys + Celery beat | Lambda + EventBridge            |
| Wishlist match | pgvector ANN             | Dedicated vector DB             |
| LifeLedger     | Polygon Amoy             | Managed chain / AWS QLDB        |
| Analytics      | Postgres queries         | ClickHouse (T3)                 |


### AI tier pipeline (Bhavya owns logic; Shikher consumes output)


| Tier  | Trigger                      | Model                             | Owner  |
| ----- | ---------------------------- | --------------------------------- | ------ |
| T0    | Every image                  | Rules / Nova Micro — reject blur  | Bhavya |
| T1    | confidence path default      | Bhavya CNN OR Nova Lite           | Bhavya |
| T2    | confidence < threshold       | Claude Haiku structured extract   | Bhavya |
| T3    | high value OR still low conf | Nova Pro / OpenAI                 | Bhavya |
| Video | 5–8 keyframes                | T1 on each → aggregate max damage | Bhavya |


**Rule:** `relay-api` never calls Bedrock directly for grading — always `relay-ml`.

`**GRADING_MODE` escape hatch (demo safety):** relay-ml supports a service-level mode so the perception pillar works even if the CNN isn't trained in 48h:


| `GRADING_MODE`  | Behavior                                                                                                                                    | Use                                                            |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `cnn` (default) | CNN T1 → Bedrock escalation on low confidence                                                                                               | Production path                                                |
| `bedrock_only`  | **Skip CNN entirely** — every request graded by Nova Lite from image description → real ConditionPassport (`model_tier_used: bedrock-only`) | Demo-safe; slower/pricier per call but no trained model needed |
| `mock`          | Deterministic stub passport (no AI)                                                                                                         | Shikher local dev before ML URL is live                        |


This is server-side env only — **no contract change**. `bedrock_only` is a *real* grade fallback, distinct from Shikher's `mock` client.

---

## §4 Repos, branching, PR flow

### Repositories


| Repo                   | Owner       | Clone required for Bhavya daily? |
| ---------------------- | ----------- | -------------------------------- |
| `relay-contracts`      | Both review | Read-only                        |
| `relay-ml`             | **Bhavya**  | **Yes — primary workspace**      |
| `relay-api`            | Shikher     | Optional (integration only)      |
| `relay-engine`         | Shikher     | No                               |
| `relay-web`            | Shikher     | No                               |
| `relay-dev` (optional) | Shikher     | Optional — docker-compose only   |


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


| Repo            | Gate                      |
| --------------- | ------------------------- |
| relay-contracts | Spectral/OpenAPI lint     |
| relay-ml        | `pytest` + `docker build` |
| relay-api       | `pytest` + `docker build` |
| relay-engine    | `go test ./...`           |
| relay-web       | `npm run build`           |


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


| Method | Path               | Request                                                                                                                  | Response                                                                                                                                                        |
| ------ | ------------------ | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/health`          | —                                                                                                                        | `{ "status": "ok", "model_loaded": true }`                                                                                                                      |
| POST   | `/grade-image`     | `multipart: image`, `unit_id`, `category`, `**expected_size?`, `expected_color?`, `product_title?**` (additive — §20)    | `ConditionPassport` (+ optional `verification`)                                                                                                                 |
| POST   | `/grade-images`    | `multipart: images[1–8]`, `unit_id`, `category`, `**expected_*?**`                                                       | `ConditionPassport` (+ optional `verification`)                                                                                                                 |
| POST   | `/grade-video`     | `multipart: video` OR `keyframes[]`, `unit_id`                                                                           | `ConditionPassport`                                                                                                                                             |
| POST   | `/fit-flags`       | `{ "sku_id", "brand?", "category?" }`                                                                                    | `{ "flags": [...], "confidence" }`                                                                                                                              |
| POST   | `/embed`           | `{ "text"? , "category"?, "grade"?, "size"?, "vertical"? }`                                                              | `{ "vector": [float × 384], "model": "..." }`                                                                                                                   |
| POST   | `/wish-score`      | `{ "wish_age_days", "user_purchase_count", "category_affinity", "has_fit_profile" }`                                     | `{ "score": 0.0–1.0, "model": "logreg_v1" }`                                                                                                                    |
| POST   | `/grade-and-price` | `multipart: images[1–8]` OR `video`, `unit_id`, `category`, `original_price`, `age_days`, `vertical?`, `**expected_*?**` | `ConditionPassport` + resale fields (`resale_grade`, `price_range`, `currency`, `pricing_rationale`) (+ optional `verification`) — see response below + §8 B4.2 |


> `**expected_*` + `verification` are ADDITIVE (Session 8, §20) — flagged for Bhavya.** All three `expected_`* Form fields are optional; when omitted the prompt and response are byte-for-byte the old behaviour. When present, the **same** grade prompt (no second image, no extra Bedrock call) is asked to ALSO report `observed_color` / `color_match` / `item_match`, returned as a `verification: { color_match, item_match, observed_color?, expected_color? }` block (states: `match|mismatch|unknown`). relay-api fills a best-effort `verification` if relay-ml omits it.

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

### grade-and-price response (resale grading + pricing — Track B, see §19)

> A **second lens** on grading. Return-disposition grading (`/grade-image`) asks *"where should this unit go?"*; resale grading asks *"what is it worth to the next buyer, and how confident are we?"* The response is **ConditionPassport-compatible** (same core fields) **plus** resale fields. We deliberately return a **price range, not an absolute price** — an absolute number is over-confident and reads as harsh. relay-api lists the **mean** of the range; the range is the contract.

```json
{
  "schema_version": "1.0.0",
  "unit_id": "uuid",
  "grade": "A+ | A | B+ | B | C | D",
  "grade_numeric": 0.82,
  "category": "fashion | electronics | ...",
  "vertical": "fashion | electronics",
  "defects": [
    { "type": "scuff", "severity": "minor", "bbox": [x, y, w, h], "description": "optional string" }
  ],
  "packaging_state": "sealed | opened | damaged | missing",
  "confidence": 0.91,
  "media_hashes": ["sha256..."],
  "graded_at": "ISO8601",
  "model_tier_used": "cnn-v1 | bedrock-only | T2 | T3",

  "resale_grade": "Like New | Very Good | Good | Acceptable",
  "price_range": { "min": 1799.0, "max": 2199.0 },
  "currency": "INR",
  "pricing_rationale": "Grade A (minor scuff) · 95 days old · steady category demand"
}
```

- **Price drivers:** visual condition (`grade_numeric`), `age_days`, and `original_price` are the primary signals; market/category demand is Bhavya's to research and improve.
- **relay-api already ships a deterministic FALLBACK pricer** so the flow works *before* this endpoint exists. Treat it as the reference floor (match or beat it):

```
condition_factor = clamp(grade_numeric, 0.30, 0.95)
age_factor       = max(0.45, 1 - age_days / 720)
base             = original_price * condition_factor * age_factor
price_range      = [base * 0.9, base * 1.1]
list_price       = mean(price_range)        # = base ; this is what relay-api lists
```

### relay-api public API (Shikher — Bhavya may call for testing)


| Method | Path                                     | Notes                                                                                                                                                                                                                                                              |
| ------ | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GET    | `/health`                                |                                                                                                                                                                                                                                                                    |
| GET    | `/products`                              | Demo catalog — **now returns `image_url`** (Track B §19)                                                                                                                                                                                                           |
| GET    | `/products/{id}`                         | PDP + fit flags proxy                                                                                                                                                                                                                                              |
| GET    | `/users/me/fit-profile`                  |                                                                                                                                                                                                                                                                    |
| POST   | `/returns`                               | Start return                                                                                                                                                                                                                                                       |
| POST   | `/returns/{id}/media`                    | Upload to S3 → trigger grade job                                                                                                                                                                                                                                   |
| GET    | `/returns/{id}/passport`                 |                                                                                                                                                                                                                                                                    |
| POST   | `/returns/{id}/disposition`              | Calls relay-engine                                                                                                                                                                                                                                                 |
| GET    | `/rescue/feed`                           | Geo query `?lat=&lng=`                                                                                                                                                                                                                                             |
| POST   | `/rescue/{id}/claim`                     | Guardrails enforced                                                                                                                                                                                                                                                |
| POST   | `/wishlist`                              | Reverse wishlist                                                                                                                                                                                                                                                   |
| GET    | `/wishlist/matches`                      |                                                                                                                                                                                                                                                                    |
| POST   | `/p2p/listings`                          | One-click from return                                                                                                                                                                                                                                              |
| GET    | `/lifeledger/{unit_id}/verify`           |                                                                                                                                                                                                                                                                    |
| POST   | `/demo/reset`                            | Re-seed (hidden) — canonical seeder; writes REAL DB + ledger (§19.7)                                                                                                                                                                                               |
| GET    | `/orders`                                | Order history; items add `delivered_at`, `returnable`, `resellable`, `days_to_return_deadline` (Track B §19.2)                                                                                                                                                     |
| POST   | `/orders/items/{order_item_id}/resell`   | Buyer resells an out-of-window owned item (multipart files) → `resale_listings` `source=p2p`; calls grade-and-price (§19.4)                                                                                                                                        |
| POST   | `/orders/items/{order_item_id}/return`   | Order-line return `{ reason, pickup_slot? }` → `ReturnEvent`. `**wrong_item` is fully GATED** → flagged `return_to_seller`, no grade/passport/listing (§20)                                                                                                        |
| POST   | `/orders/items/{order_item_id}/exchange` | In-window exchange `{ new_size?, new_variant?, pickup_slot? }` → `ExchangeResult { exchange_id, replacement{order_item_id,size,variant,title}, rescue_listing{id,list_price,...} }`. NO ML grade; pristine returned unit → Path-A rescue + `EXCHANGED` event (§20) |
| GET    | `/second-life`                           | Combined Second Life catalogue (p2p + certified) (§19.4)                                                                                                                                                                                                           |
| POST   | `/second-life/{listing_id}/buy`          | Stub checkout — escrow `held→released`, ownership transfer, `P2P_SOLD` ledger event (§19.3)                                                                                                                                                                        |
| GET    | `/seller/refurbished`                    | Seller's relist-eligible REFURBISHED units (§19.8)                                                                                                                                                                                                                 |
| POST   | `/seller/units/{unit_id}/relist`         | Seller republish → `resale_listings` `source=certified` (multipart files) (§19.4)                                                                                                                                                                                  |


### relay-engine API (Shikher — internal)


| Method | Path                 | Request                                                       | Response                                                            |
| ------ | -------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------- |
| POST   | `/disposition/score` | `{ unit_id, passport, return_reason, user_id, geo, demand? }` | `{ channel, score, reasons[], guardrails_applied[] }`               |
| POST   | `/match/rescue`      | `{ unit_id, geo, radius_km }`                                 | ranked user ids (× wish_score)                                      |
| POST   | `/match/wishlist`    | `{ unit_id, passport }`                                       | ranked wish ids (× wish_score)                                      |
| POST   | `/match/pair-rescue` | `{ geo, radius_km }`                                          | `[{ unit_a, unit_b, user_a, user_b, distance_km }]` bipartite swaps |


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

### Track B additions — Second Life (resell + republish)

Additive only — two new nullable columns on existing tables + buyer order history + one new listings table (full feature spec in §19):

```sql
-- catalog: static asset URL so resale + catalogue cards render REAL images
ALTER TABLE products ADD COLUMN image_url TEXT;          -- served from seed_assets/ (§19.7)

-- buyer purchase history — source of truth for ownership, age, and return window
orders (id, user_id, status, placed_at, created_at)
order_items (id, order_id, product_id, unit_id, sku, size, qty, unit_price,
             delivered_at,            -- NEW: drives age_days + return-window gating (§19.2)
             created_at)

-- Second Life listings — BOTH contributor lanes land in one table / one catalogue
resale_listings (
  id, unit_id,
  source,              -- 'p2p' (buyer resell) | 'certified' (seller republish)
  title, category, vertical, image_url,
  resale_grade,        -- resale-oriented condition label from grade-and-price
  original_price,
  price_range_min, price_range_max,     -- the contract: a range, not an absolute price
  list_price,          -- = MEAN(price_range); what the catalogue shows
  age_days, lister_label, ships, fulfillment,
  status,              -- listed | held | sold | expired
  escrow_status,       -- none | held | released  (demo stub)
  passport_id, lifeledger_unit_id,
  created_at
)
```

- `order_items.delivered_at` + `original_price` are the price drivers handed to `grade-and-price`; `delivered_at` + `return_window_days` (default 7) decide `returnable` vs `resellable`.
- `resale_listings` unifies both lanes; ownership transfer + escrow + ledger events are **stubbed** for the demo (mirrors the existing rescue "claim locally" pattern). See §19.

---

## §7 Feature specs + guardrails

> Full risk audit: `[context.md](./context.md)` §21.

### Return Rescue — return chain problem

**Implement in relay-engine + relay-api:**


| Guardrail          | Implementation                                                                 |
| ------------------ | ------------------------------------------------------------------------------ |
| Rescue eligibility | `users.return_rate < 0.4` AND `users.rescue_eligible`                          |
| One active rescue  | Block claim if user has open rescue < 14 days                                  |
| Chain depth cap    | `product_units.transfer_count >= 3` → disposition forced refurb/donate/recycle |
| Net carbon gate    | `saved_warehouse_km > delivery_km` (stub constants OK demo)                    |
| Fashion size match | Require wishlist size match OR fit_profile confidence > 0.7                    |
| Keep-it credits    | `green_credit_ledger.unlock_at = now + 14 days`                                |


### Exchange-first

Trigger when `return_reason IN ('too_small','too_large','fit')` AND exchange SKU `in_stock` within FC → UI shows exchange CTA before Rescue/P2P.

### Bracketing interceptor (prevention — P0/T1)

> **Why:** Size/variant bracketing — buying multiple sizes intending to return most — drives a large share of fashion returns. Catching it at the cart is the most concrete, data-rich prevention moment (more provable than a passive fit banner).

**Detection (relay-api, `cart_items`):** at checkout, group cart by `product_id`; if a product appears with **≥3 distinct `size`/`variant`** rows → bracketing flagged (strict threshold — avoids false positives on legitimate 2-item buys).


| Signal                              | UI response                                                                                                                    |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| 3+ sizes same product               | Active banner: *"You have 3 sizes of ** — keep the one that fits. Your fit profile suggests **L**."* + one-tap "remove extras" |
| Bracketing + known high return rate | Stronger nudge + exchange-friendly messaging (no fear scoring)                                                                 |
| Bracketing on `critical_fit` SKU    | Surface article fit flag inline                                                                                                |


**Guardrail:** advisory, never blocks purchase. Counts toward "returns prevented" demo metric.

### Carbon model (Impact Wallet + net-carbon gate)

> **Anchor stat:** US product returns generated ~**15 million metric tons of CO₂** in a year (Optoro / returns-industry research, cited in ScienceDirect reverse-logistics work). Per-item constants below are **demo estimates anchored to that** — hard-coded, visible on the passport/Impact Wallet, and used by the Rescue net-carbon guardrail.

**Per-channel CO₂ saved vs baseline (new purchase + warehouse return + restock), kg CO₂e:**


| Channel      | `co2_saved_kg` | Rationale                                             |
| ------------ | -------------- | ----------------------------------------------------- |
| `exchange`   | 1.8            | avoids reverse leg + new outbound; one local swap     |
| `rescue`     | **2.4**        | skips warehouse round-trip; hyperlocal last-mile only |
| `p2p_resale` | 3.1            | displaces a new-item purchase + avoids warehouse      |
| `refurb`     | 2.0            | life extension minus processing                       |
| `donate`     | 1.5            | landfill diversion + social value                     |
| `recycle`    | 0.6            | material recovery only                                |


**Net formula (demo):** `net_co2_saved = channel_const − (delivery_km × 0.12)` where `0.12 kg CO₂/km` is a light-vehicle last-mile factor.

**Net-carbon gate (guardrail):** only surface Rescue when `net_co2_saved > 0` (i.e. `rescue_const(2.4) − delivery_km×0.12 > 0` ⇒ ~≤20 km radius). Replaces the prior "stub constants OK" note.

### Impact Wallet — credits buy ACCESS, not discounts (the flywheel)

> **Why:** green credits with a 14-day hold redeemable as a discount = cashback with a green badge — a loyalty pattern judges have seen since 2019. Making credits buy *access* turns the reward into the system itself.

**Mechanic:** lifetime green credits (locked + unlocked) define a **participation tier**. When `lifetime_credits ≥ RESCUE_EARLY_ACCESS_CREDIT_THRESHOLD` (default 100), the user gets **early access** to the Rescue feed: they see new listings during an embargo window (`RESCUE_EARLY_ACCESS_WINDOW_SECONDS`, default 600 = 10 min) *before* those listings go public. Below the tier, embargoed listings are hidden until the window elapses.

- **Circular** — you rescue items → you earn credits → you get a better position to rescue more. The reward *is* deeper participation in the loop, not a price cut.
- **Scarce** — combined with decay pricing (price falls as TTL runs out), a 10-minute head start is a real, visible edge on the best listings.
- **~Zero cost** — it's a filter on `GET /rescue/feed` keyed on the caller's lifetime-credit total; each embargoed listing is flagged `early_access=true` with an `early_access_until` timestamp for the UI badge.

**Kept from the original:** the 2.4 kg CO₂/rescue constant and the locked (14-day) vs spendable balance split. Only the *spend* changed from discount → access.

**Implementation:** `app/services/rescue.py` (`lifetime_credits`, `has_early_access`, `is_embargoed`, `early_access_until`); `GET /rescue/feed` applies the embargo filter; `GET /users/me/impact` returns `lifetime_credits`, `early_access`, `early_access_threshold`. Demo seed: the demo user holds 150 prior credits (early-access tier); the buyer holds 0 — the gap is the demo.

### Next-owner matching (pgvector — T1)

Embed each graded unit and each wish (`category + grade + size + vertical`) via relay-ml `/embed`; rank wishes by cosine similarity (pgvector ANN), then apply geo + price + guardrail filters. Final rank also multiplies by **wish confidence** (below). Falls back to rule/geo match if embedding unavailable.

### Reverse Wishlist

Seed 20–50 wishes in demo; expire 30 days; match on **embedding cosine × wish_score** + size + price + geo.

### Wish confidence scoring (T2 — Bhavya `ml-wish-score`)

Not all wishes are equal. Score buyer intent `0–1` so ranking favours high-intent buyers:


| Feature                          | Signal                                                    |
| -------------------------------- | --------------------------------------------------------- |
| `wish_age_days`                  | recent wish = higher intent (decays toward 30-day expiry) |
| `user_purchase_count` (category) | bought similar before = higher intent                     |
| `category_affinity`              | browse/buy affinity for the category                      |
| `has_fit_profile`                | complete fit profile = serious buyer                      |


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


| Panel                                              | Source                                                                        |
| -------------------------------------------------- | ----------------------------------------------------------------------------- |
| High-return SKUs flagged                           | aggregate `return_events` + relay-ml fit flags per SKU                        |
| Catalog-fix recommendations                        | seller-signal aggregation per `sku + reason_code` (e.g. "fix photos")         |
| Items in rescue (live TTL countdown + decay price) | `rescue_listings` where `status=active`, `expires_at`, `current_discount_pct` |
| Chain-depth watch                                  | `product_units.transfer_count` approaching cap (≥3 → forced refurb/donate)    |
| Net impact rollup                                  | sum `impact_events.co2_saved_kg`                                              |


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

1. `**ML_SERVICE_URL**` reachable from relay-api (local Docker or Railway).
2. **Stable OpenAPI** per §5 — breaking changes need contracts PR + heads-up.
3. `**confidence` + `model_tier_used**` on every grade response — drives his guardrails/display.
4. `**passport_hash**` — SHA-256 of canonical JSON (document algorithm in README).
5. **Docker image** that runs on CPU for demo (GPU nice, not required).
6. **Contract-aligned passport** (`ml-passport-align`, T0): the current Pydantic `ConditionPassport` drifts from `relay-contracts` v1 — add `schema_version: "1.0.0"`, add `"missing"` to `packaging_state`, make `vertical` an enum (`fashion|electronics`), and relax fields the contract marks optional (`category`, `disposition_hint`, `packaging_state`, `passport_hash`). Fix before `/grade-image` ships so relay-api/engine validation passes.

### What you can use from Shikher (when ready)


| Shikher endpoint                               | Your use                          |
| ---------------------------------------------- | --------------------------------- |
| `GET relay-api/health`                         | Integration smoke test            |
| `POST relay-api/demo/seed`                     | Reset demo data during ML testing |
| Sample `unit_id` + categories from seed script | Consistent test fixtures          |


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


| Priority | Dataset                  | URL                                                                                                              | Use                                 |
| -------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| **P0**   | E-commerce defect images | [HuggingFace](https://huggingface.co/datasets/prajwalkothwal/ai-generated-ecommerce-images)                      | Train/eval grade CNN; 12 categories |
| **P0**   | Clothing fit             | [Kaggle rmisra/clothing-fit-dataset](https://www.kaggle.com/rmisra/clothing-fit-dataset-for-size-recommendation) | Fit flags / MultiFlags              |
| **P1**   | ASOS GraphReturns        | [OSF](https://osf.io/c793h/)                                                                                     | Return graph research               |
| **P1**   | Amazon Berkeley Objects  | HF/Berkeley                                                                                                      | Clean baseline images               |
| **P2**   | MVTec AD                 | Official                                                                                                         | Electronics anomaly pretrain        |
| **P2**   | Kaputt paper dataset     | arXiv 2510.05903                                                                                                 | If obtainable — retail logistics    |


**Document in `relay-ml/data/README.md`:** what you downloaded, license, train/val split.

**Minimum viable for 48h:** HF defects (6K) + Kaggle fit.

---

### B2 — Model architecture (recommended; you may improve)

**Multi-task CNN (MobileNetV3-Small or EfficientNet-Lite):**


| Head          | Classes                        |
| ------------- | ------------------------------ |
| `grade`       | A+ … D (ordinal/regression)    |
| `category`    | fashion / electronics / …      |
| `defect_type` | multi-label from HF categories |
| `confidence`  | calibrated softmax max prob    |


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

`**POST /embed` (T1, `ml-embed`):** return a 384-d vector for a unit or a wish.

- Input: free `text` OR structured `{ category, grade, size, vertical }`.
- Model: `sentence-transformers/all-MiniLM-L6-v2` (CPU, ~80 MB) or Bedrock Titan Embeddings.
- relay-api calls this for both `product_units` and `reverse_wishlist`; you only return the vector.
- Keep the model name in the response (`model`) so Shikher can store provenance.

`**POST /wish-score` (T2, `ml-wish-score`):** buyer-intent score `0–1`.

- Features: `wish_age_days`, `user_purchase_count`, `category_affinity`, `has_fit_profile`.
- Model: logistic regression (`logreg_v1`) on seed/synthetic labels; explainable coefficients.
- Used by relay-engine matching as a rank multiplier (and feeds demand-weighted disposition).

`**ml-return-cluster` (T3 stretch):** cluster free-text return reasons (e.g. embeddings + KMeans) so seller signals go beyond fixed reason codes ("color not as shown" variants collapse to one signal).

**Contract:** add `/embed` + `/wish-score` to `relay-contracts` relay-ml OpenAPI (`contracts-embed`) before relay-api wires them.

---

### B4.2 — Resale grading + pricing (`POST /grade-and-price`, Track B)

> A **second lens** on grading. Return-disposition grading (`/grade-image`) answers *"where should this unit go?"*; resale grading answers *"what is it worth to the next buyer, and how confident are we?"* Same media in — but the output adds a resale condition label + a **price range**. Powers the Second Life marketplace (§19); `/grade-image` is untouched.

**Why a range, not an absolute price:** an absolute price is over-confident and reads as harsh ("your item is worth ₹1,842"). You return a `price_range {min, max}`; relay-api lists the **mean**. The range *is* the contract — **you own the pricing algorithm inside it** (comps, depreciation curves, demand — your call).

**Request (multipart/form-data — mirrors `/grade-image`):**

- `images` (1–8 JPEG/PNG) **OR** `video`
- `unit_id` (str), `category` (str)
- `original_price` (float), `age_days` (number — days since delivery)
- `vertical` (optional: `fashion` | `electronics`)

**Response:** a ConditionPassport (all §5 core fields: `schema_version`, `unit_id`, `grade`, `grade_numeric`, `category`, `vertical`, `defects[]`, `packaging_state`, `confidence`, `media_hashes[]`, `graded_at`, `model_tier_used`) **plus** resale fields:


| Field               | Type                         | Meaning                                                                              |
| ------------------- | ---------------------------- | ------------------------------------------------------------------------------------ |
| `resale_grade`      | str                          | resale-oriented condition label (e.g. `Like New`, `Very Good`, `Good`, `Acceptable`) |
| `price_range`       | `{ min: float, max: float }` | trustworthy band; relay-api lists the mean                                           |
| `currency`          | str                          | `"INR"`                                                                              |
| `pricing_rationale` | str                          | short driver explanation (condition + age + market)                                  |


**Price drivers:** visual condition (your grade) + `age_days` + `original_price` are the primary signals; market/category demand is yours to research.

**Reference fallback (already shipped in relay-api — match or beat it):** so the flow works *before* this endpoint lands. It is the floor, not the ceiling:

```
condition_factor = clamp(grade_numeric, 0.30, 0.95)
age_factor       = max(0.45, 1 - age_days / 720)
base             = original_price * condition_factor * age_factor
price_range      = [base * 0.9, base * 1.1]
list_price       = mean(price_range)        # = base
```

Improve the model freely — just keep the `price_range` contract so relay-api can keep listing the mean. Full JSON example in §5 (*grade-and-price response*).

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

#### `POST /grade-and-price`

- [ ] Accepts the same media as `/grade-image` (1–8 images OR video) + `original_price`, `age_days`, `category`, `vertical?`
- [ ] Returns a valid ConditionPassport **plus** `resale_grade`, `price_range {min,max}`, `currency`, `pricing_rationale`
- [ ] `price_range.min ≤ price_range.max`; both > 0; mean is sane vs `original_price`
- [ ] Monotonic sanity: higher grade OR lower `age_days` ⇒ higher mean price
- [ ] Matches/beats the deterministic reference pricer when uncertain

#### `GET /health`

- [ ] `{ "status": "ok", "model_loaded": true, "cnn_version": "v1" }`

---

### B6 — Room to innovate (not rigid)

Bhavya is explicitly encouraged to improve:


| Area                | Default plan                 | You may do better                       |
| ------------------- | ---------------------------- | --------------------------------------- |
| CNN architecture    | MobileNetV3 multi-head       | EfficientNet, ViT-small, ensemble       |
| Bedrock prompts     | Hand-crafted JSON extraction | Prompt registry + eval set              |
| Fit flags           | Rules → MultiFlags           | SizeFlags Bayesian, ASOS graph features |
| Video               | FFmpeg keyframes             | Uniform sampling + coverage scoring     |
| Confidence          | Softmax max                  | Temperature scaling, MC dropout         |
| Defect localization | bbox optional                | Grad-CAM → pseudo bbox                  |


**If you change response schema → PR `relay-contracts` first.**

---

### B7 — Research papers (read order)


| #   | Paper                                              | Action                          |
| --- | -------------------------------------------------- | ------------------------------- |
| 1   | Raj 2026 — Edge CNN + DRL reverse logistics (IJCA) | Architecture inspiration        |
| 2   | SizeFlags (arXiv 2106.03532)                       | Fit flags production approach   |
| 3   | MultiFlags (SCITEPRESS 2025)                       | Stretch goal                    |
| 4   | Returnformer (MDPI 2026)                           | Know baseline; don't replicate  |
| 5   | McKinsey reverse logistics AI 2025                 | Disposition framing for slides  |
| 6   | SIGIR eCom'22 When Volatility Reigns               | Second-hand matching context    |
| 7   | Gamification C2C (CentAUR)                         | Warn Shikher on moral licensing |
| 8   | TRUCE circular platform (MDPI 2025)                | LifeLedger trust narrative      |


Full list: `[context.md](./context.md)` §6.

---

### B8 — Bhavya 48h schedule (suggested)


| Hours | Focus                                                                                           |
| ----- | ----------------------------------------------------------------------------------------------- |
| 0–4   | Skeleton, datasets download, EDA notebook                                                       |
| 4–12  | CNN train v1, `/grade-image` CPU inference                                                      |
| 12–20 | Video keyframes, `/grade-video`, confidence calibration, `/embed` (unblocks Shikher's pgvector) |
| 20–28 | Bedrock T2/T3 escalation, `/fit-flags` rules, `bedrock_only` mode                               |
| 28–36 | `/wish-score` logreg, Docker, deploy Railway/AWS, hand Shikher URL                              |
| 36–48 | MultiFlags OR return-reason clustering OR hard-case tuning OR demo recording                    |


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


| Condition                        | Channel               |
| -------------------------------- | --------------------- |
| reason=fit + exchange in stock   | `exchange`            |
| grade ≥ B + wishlist match + geo | `rescue`              |
| grade ≥ B + electronics          | `p2p_resale`          |
| grade ≥ B + fashion + no rescue  | `p2p_resale`          |
| grade C + refurb demand          | `refurb`              |
| grade D + value low              | `donate` or `recycle` |
| transfer_count ≥ 3               | block rescue/p2p      |


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


| Hours | Focus                                                                                                                             |
| ----- | --------------------------------------------------------------------------------------------------------------------------------- |
| 0–6   | **Schema**: relay-api + relay-engine skeletons, Alembic migration v1 (all §6 tables + pgvector), contracts-embed                  |
| 6–12  | **Endpoint design**: relay-api routes (returns, rescue, wishlist, p2p, ops) + engine routes — signatures + stubs + mock ML client |
| 12–20 | **High-level flow**: return → grade (mock→real ml) → disposition (engine rules) → persist passport; seed script                   |
| 20–28 | **Wire logic**: rescue TTL + guardrails + exchange-first + bracketing + pgvector match (call `/embed`)                            |
| 28–36 | **T2 logic**: demand-weighted disposition, Pair Rescue, decay pricing, seller signals, wishlist, p2p, LifeLedger, credits/impact  |
| 36–42 | Integration test full flows via API; deploy AWS + Railway backup (seeded)                                                         |
| 42–48 | **UI phase**: wire `web-`* to ready backend; demo video; submission                                                               |


---

## §10 Integration matrix


| From → To                | Protocol            | Data                                                                                                                       |
| ------------------------ | ------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| relay-web → relay-api    | REST JSON           | UI requests                                                                                                                |
| relay-api → relay-ml     | REST multipart/JSON | Images, passports, **embeddings (`/embed`)**, **wish scores (`/wish-score`)**, **resale grade+price (`/grade-and-price`)** |
| relay-api → relay-engine | REST JSON           | Passport + context                                                                                                         |
| relay-api → Postgres     | SQL                 | Everything persistent                                                                                                      |
| relay-api → Redis        | Redis protocol      | Rescue TTL, Celery                                                                                                         |
| relay-api → S3           | AWS SDK             | Media                                                                                                                      |
| relay-api → Polygon      | web3.py / HTTP RPC  | LifeLedger txs                                                                                                             |
| Celery → relay-ml        | REST                | Async grading                                                                                                              |
| Bhavya tests → relay-api | REST                | Optional seed/reset                                                                                                        |


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


| Gate   | Criteria                                                                                        |
| ------ | ----------------------------------------------------------------------------------------------- |
| **T0** | All health checks green in docker-compose; web navigable                                        |
| **T1** | Fashion path end-to-end with **real** relay-ml grade (or documented mock with ≤1 click to swap) |
| **T2** | T1 + wishlist match OR rescue claim + LifeLedger verify                                         |
| **T3** | Any stretch feature live                                                                        |


### If time slips


| Cut order (last to first)  | Keep                           |
| -------------------------- | ------------------------------ |
| T3 stretch                 | T2                             |
| Impact Wallet / credits UI | Core rescue                    |
| Full Bedrock T3            | CNN + Haiku                    |
| Blockchain live verify     | DB-stored hash + "verify mock" |
| Electronics path           | Fashion path                   |


**Never cut:** Condition Passport, disposition, one matching feature (Rescue OR wishlist), guardrails mention in demo.

---

## §12 Demo script + UI pages

### 3-minute video beats


| Time      | Scene                                                                                             |
| --------- | ------------------------------------------------------------------------------------------------- |
| 0:00–0:25 | Problem + return chain risk + our guardrails                                                      |
| 0:25–0:45 | Prevention: **bracketing interceptor** at checkout (3 sizes → keep one) + fit insight             |
| 0:45–1:20 | Fashion: return → grade passport → exchange OR rescue (net CO₂ shown)                             |
| 1:20–1:45 | Reverse wishlist **pgvector match** (demand-weighted) + decay-price claim countdown               |
| 1:45–2:05 | **Pair Rescue**: A↔B swap, no money, near-zero carbon — the most circular 20s                     |
| 2:05–2:30 | Electronics: P2P list + warranty on LifeLedger + QR verify                                        |
| 2:30–2:55 | **Ops/seller dashboard**: flagged SKUs + "fix your photos" signal + live rescue TTL + chain depth |
| 2:55–3:00 | HLD slide: Go engine + Bedrock tiers + scale                                                      |


### Page list


| Route                                | Tier | Owner   |
| ------------------------------------ | ---- | ------- |
| `/`                                  | T0   | Shikher |
| `/products/[id]`                     | T1   | Shikher |
| `/checkout` (bracketing interceptor) | T1   | Shikher |
| `/returns/new`                       | T1   | Shikher |
| `/rescue`                            | T1   | Shikher |
| `/wishlist`                          | T2   | Shikher |
| `/ops` (seller/ops dashboard)        | T2   | Shikher |
| `/p2p/sell/[returnId]`               | T2   | Shikher |
| `/lifeledger/[unitId]`               | T2   | Shikher |
| `/demo/reset`                        | T2   | Shikher |


---

## §13 Deploy

### AWS (primary)


| Service                           | Runs                                             |
| --------------------------------- | ------------------------------------------------ |
| ECS Fargate                       | relay-api, relay-engine, relay-ml, celery worker |
| RDS PostgreSQL                    | db.t3.micro + pgvector                           |
| ElastiCache Redis OR Redis on ECS | cache + celery                                   |
| S3                                | media + optional static                          |
| SQS                               | celery broker (prod)                             |
| Bedrock                           | ap-south-1 or us-east-1                          |
| CloudFront + S3 OR Vercel         | relay-web                                        |


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

See `[context.md](./context.md)` §6 and Bhavya §B7.

---

## §16 Dataset catalog

See `[context.md](./context.md)` §27 and Bhavya §B1.

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
RETURN_WINDOW_DAYS=7             # Track B: resell unlocks when the return window expires (§19.2)
SEED_ASSETS_DIR=./seed_assets    # Track B: real product manifest + images served statically (§19.7)
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

## §19 Track B — Second Life (resell + republish)

> **What:** a buyer-facing **Second Life** marketplace that gives a second owner to items that are past their moment — fed by two contributor lanes but presented as one catalogue.
> **Status:** specced + in progress. relay-api already ships the deterministic fallback pricer (§19.6) and the rescue/claim pattern Track B reuses; the real `grade-and-price` model (Bhavya, §8 B4.2) and the Second Life UI are landing.
> **Relation to Track A:** Track A (return → grade → disposition → rescue/match) optimizes *final placement of returns*. Track B opens the same trust + pricing machinery to *items users already own*, closing the circular loop on the buyer side. Same passport, same LifeLedger, same pricer — new surface.

### §19.1 Two lanes, one catalogue


| Lane                 | Who                         | Trigger                                                                | `source`    | Branding                                  |
| -------------------- | --------------------------- | ---------------------------------------------------------------------- | ----------- | ----------------------------------------- |
| **Buyer resell**     | a user who bought on Amazon | their item's **return window has EXPIRED** (owned, not already listed) | `p2p`       | peer-to-peer listing                      |
| **Seller republish** | an Amazon seller            | a unit returned to them was graded **REFURBISHED**                     | `certified` | platform-backed **Certified Second-Life** |


Both lanes write `resale_listings` and surface in the **same** `GET /second-life` catalogue; `source` drives the badge (peer vs certified) and fulfillment copy. `**order_id` + LifeLedger are the source of truth** for ownership, age (time since purchased/delivered), and status.

### §19.2 Return-window gating

Order items expose two mutually-exclusive states so resell unlocks exactly when the return option closes:


| Field on order item       | Meaning                                                                           |
| ------------------------- | --------------------------------------------------------------------------------- |
| `delivered_at`            | when the buyer received it — anchors both `age_days` and the return clock         |
| `returnable`              | `now − delivered_at ≤ return_window_days` (still inside the Amazon return window) |
| `resellable`              | window expired **AND** buyer still owns the unit **AND** not already listed       |
| `days_to_return_deadline` | countdown shown in order history                                                  |


**Config:** `return_window_days` (default **7**). An item is never simultaneously `returnable` and `resellable` — resell becomes available the moment the return window closes.

### §19.3 Payments are STUBBED (demo)

No real payments. Checkout mirrors the existing rescue **"claim locally"** pattern:


| Step                                               | State change                                                               |
| -------------------------------------------------- | -------------------------------------------------------------------------- |
| 1. buyer hits `POST /second-life/{listing_id}/buy` | escrow `none → held`; listing `listed → held`                              |
| 2. ownership transfer                              | set `owner_id`; `transfer_count++` (chain-depth cap from §7 still applies) |
| 3. settle                                          | escrow `held → released`; listing `held → sold`                            |
| 4. trust + incentives                              | append `P2P_SOLD` LifeLedger event; award impact + green credits           |


Escrow lifecycle: `none → held → released`. This is the same mechanic as rescue claiming — no new payment integration for the demo.

### §19.4 Endpoints (relay-api — canonical signatures in §5)


| Method | Path                                   | Purpose                                                                                                                                                               |
| ------ | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/products`                            | now returns `image_url` (served from `seed_assets/`)                                                                                                                  |
| GET    | `/orders`                              | items add `delivered_at`, `returnable`, `resellable`, `days_to_return_deadline`                                                                                       |
| POST   | `/orders/items/{order_item_id}/resell` | **buyer resell** (multipart files) → `resale_listings` `source=p2p`; backend reads `age_days` + `original_price` from db/ledger and calls `grade-and-price`           |
| GET    | `/second-life`                         | combined catalogue (p2p + certified)                                                                                                                                  |
| POST   | `/second-life/{listing_id}/buy`        | stub checkout (§19.3)                                                                                                                                                 |
| GET    | `/seller/refurbished`                  | seller's relist-eligible REFURBISHED units                                                                                                                            |
| POST   | `/seller/units/{unit_id}/relist`       | **seller republish** (multipart files) → `resale_listings` `source=certified`; backend pulls `age_days` + `original_price` from db/ledger and calls `grade-and-price` |


### §19.5 `ResaleListing` shape

```json
{
  "id": "uuid",
  "unit_id": "uuid",
  "source": "p2p | certified",
  "title": "string",
  "category": "fashion | electronics | ...",
  "vertical": "fashion | electronics",
  "image_url": "https://.../seed_assets/...",
  "resale_grade": "Like New | Very Good | Good | Acceptable",
  "original_price": 2999.0,
  "price_range": { "min": 1799.0, "max": 2199.0 },
  "list_price": 1999.0,
  "age_days": 95,
  "lister_label": "Resold by a verified buyer | Amazon Certified Second-Life",
  "ships": "string",
  "fulfillment": "peer | fba",
  "status": "listed | held | sold | expired",
  "escrow_status": "none | held | released",
  "passport_id": "uuid",
  "lifeledger_unit_id": "uuid"
}
```

`list_price` is always the **MEAN** of `price_range` (the range is the contract; §19.6).

### §19.6 Return-item pricing unification + `price_fit`

One pricer, two surfaces — resale pricing also applies to the existing return/rescue side:

- **Unified pricing:** when a returned item is graded (Track A), also compute a `price_range` (via `grade-and-price`, or the deterministic fallback). **Rescue listings carry `list_price` = MEAN of the range**; the rescue decay discount (§7 *Rescue decay pricing*) applies *relative to that `list_price`*.
- **Fallback formula (reference floor — already shipped in relay-api):**

```
condition_factor = clamp(grade_numeric, 0.30, 0.95)
age_factor       = max(0.45, 1 - age_days / 720)
base             = original_price * condition_factor * age_factor
price_range      = [base * 0.9, base * 1.1]
list_price       = mean(price_range)        # = base
```

- `**price_fit` (Genie / reverse-wishlist):** when a wish's `max_price` falls within a band of an item's `list_price`, set a `price_fit` flag so strongly price-matched matches surface first. Complements the §7 cosine × `wish_score` ranking — `price_fit` is an additional surfacing signal, not a replacement.

### §19.7 Seeding — everything is REAL DB + LifeLedger data (crucial)

No client-side mocks. The demo runs entirely off seeded **real** Postgres + LifeLedger state.

**New `seed_assets/` folder (in relay-api):** a `manifest.json` of **REAL products** — `title`, `brand`, `category`, `vertical`, `original_price`, `product_url`, `sizes`, image filenames — plus the real product images, **served statically** so `image_url` resolves.

**The seeder must build:**


| Seeded data                                                  | Why                                                        |
| ------------------------------------------------------------ | ---------------------------------------------------------- |
| Heavily-populated Layer-1 Amazon catalogue (currently empty) | catalogue, PDPs, resell source                             |
| Buyer + seller order history with `delivered_at` mixes       | some in-window (`returnable`), some expired (`resellable`) |
| Returned units + REFURBISHED units ready for seller relist   | feeds `/seller/refurbished` + certified lane               |
| Path A / Path B rescue listings                              | Track A demo intact                                        |
| Second Life `resale_listings` (p2p + certified)              | populated Second Life catalogue on first load              |
| Passports + full ledger chains + tiered credits              | trust + Impact Wallet + early-access tier                  |
| Seller persona seeded with REAL sold/returned data           | its Ops + order UI is populated, not empty                 |


`**/demo/reset` remains the canonical seeder** (writes real DB + ledger). Stale/duplicate reset cruft + hardcoded client mock fallbacks are being removed.

### §19.8 Seller UX

- The seller persona does **NOT** land on the buyer relay landing page.
- Its landing **IS the Ops dashboard** (§7 *Ops / seller dashboard*, `/ops`).
- Seller nav has **exactly two destinations**: **(1) Ops** (landing), **(2) Order history tracking**.
- In order tracking, returned + **REFURBISHED** units show a **"relist for resale"** affordance that opens an **image-upload interface**. The backend pulls `age_days` + `original_price` from db/ledger and calls `grade-and-price` → the result becomes a `certified` `resale_listing`.

### §19.9 Buyer UX

- New **"Second Life" catalogue page** (route `/second-life`) listing the combined p2p + certified catalogue.
- The buyer **landing page features a Second Life section below the motto**.
- In buyer order history, items past the return window (`resellable`) show a **"resell"** affordance → image upload → `grade-and-price` → `p2p` `resale_listing`.

---

## §20 Return-grading decisions (Session 8)

> **Status:** built + verified on the live stack (smoke `SMOKE_OK`). Five product decisions on *how a return is graded and where it goes*. All additive — existing flows, contracts, and the LifeLedger hash are unchanged unless the new inputs are supplied.

### §20.1 Size-return = pristine asset (grade boost + minimal discount)

A return whose `reason ∈ {too_small, too_large, fit}` (and **not** `defective` / `not_as_described`) was never used — it just didn't fit. So on the **return-grade path** we treat it as pristine:

- **Grade boost** (`services/grading.py::apply_pristine_size_boost`): floor the resale grade to **Grade A / "Like New"** (`size_return_pristine_grade=A`, numeric `0.9`) if the model graded it lower, **clear cosmetic defects**, set `packaging_state=sealed`, and steer `disposition_hint=p2p_resale`. Applied to the `ConditionPassport` **before** hashing, so the anchored hash covers the boosted grade.
- **Minimal discount** (`routers/returns.py::compute_disposition` → `services/rescue.py::create_listing_for_disposition(discount_pct=…)`): a size return is re-listed at only `size_return_minimal_discount_pct=0.07` (near original price), **never** the deep rescue markdown. The `discount_pct` override also **forces Path A** (local pickup-anchored) so a neighbour can intercept it before it leaves.

### §20.2 Next-owner size-match gate (PRD §7 "size match OR fit confidence > 0.7")

`services/matching.py` previously filtered only on cosine + geo + price. Added a hard **size gate**: when a wish specifies a `size`, a candidate unit passes only if

```
unit.size == wish.size   OR   fit_confidence(wisher, category) > 0.7
```

`fit_confidence` = `matching_fit_profile_confidence` (0.8) when the wisher has a stored `fit_profile` entry for that category's axis (`tops` / `bottoms` / `shoes`), else `0.0`. So a confident wisher can still match an inexact size; everyone else needs an exact match. `unit.size` now flows through checkout, returns, and exchange (see §20.6) and is surfaced on `WishMatch.size`.

### §20.3 Expected-context verification (cheap, prompt-fields-only)

Chosen over the costly catalogue-image compare. **No second image, no extra Bedrock call.**

- **relay-api** (`grading.py`, `resale.py`) sends the order's `expected_size` (`order_item.size`), `expected_color` (`order_item.variant` or `product_metadata.color`), and `product_title` (`Product.title`) as **optional multipart Form fields** to the grade endpoints.
- **relay-ml (ADDITIVE — flagged for Bhavya):** `bedrock_tiers.py` appends a verification suffix to the **same** grade prompt only when expected context is present, asking the model to also report `observed_color` / `color_match` / `item_match`. `grade_mock`, `grade_bedrock_only`, and `grade_multi_image_bedrock` build the block; omitted context ⇒ byte-for-byte the old behaviour.
- **Shape (LOCKED — frontend reads it on `ConditionPassport` AND `ResaleListing`):**

```json
"verification": {
  "color_match": "match" | "mismatch" | "unknown",
  "item_match":  "match" | "mismatch" | "unknown",
  "observed_color": "string?",
  "expected_color": "string?"
}
```

- **Persistence:** stored inside the existing `condition_passports.passport` JSON (no new column); surfaced on `ResaleListing.verification` via `resale.py::_passport_verification`.
- **relay-api fallback** (`grading.py::ensure_verification`): if relay-ml omits `verification`, relay-api attaches a best-effort one (`color_match` computed only if the passport exposes an observed colour, else `unknown`).

### §20.4 `wrong_item` — fully gated

When `reason == "wrong_item"` the buyer got the wrong product — there is nothing to grade. The flow (`routers/returns.py` and `services/order_actions.py::record_order_item_return`) **records a flagged return and stops**: status `flagged`, `order_items.return_state = "return_to_seller"`, and **no** grade-endpoint call, **no** `ConditionPassport`, **no** `GRADED` LifeLedger anchor, **no** unit status mutation, **no** rescue/disposition/second-life listing. `wrong_item` (and `not_as_described`) added to `_REASON_FIX` in `routers/ops.py` → surfaces a seller fulfilment signal: *"audit pick-pack accuracy + SKU-to-bin mapping"*.

### §20.5 Exchange flow (in-window, no ML grade)

`POST /orders/items/{order_item_id}/exchange` body `{ new_size?, new_variant?, pickup_slot? }` → `ExchangeResult` (`services/order_actions.py::exchange_order_item`). Allowed **only within the return window**:

1. **No ML grading.** Mint a **replacement** order + line for the new size/variant on the same product, linked back via `order_items.exchanged_from_id`; anchor a `PURCHASED` event on the replacement unit.
2. **Returned unit → pristine** via a deterministic Grade A / "Like New" passport (`model_tier_used=exchange-pristine`); `order_items.return_state = "exchanged"`; anchor an `**EXCHANGED`** LifeLedger event (not `GRADED`).
3. **Auto-list on Path-A rescue** at `exchange_minimal_discount_pct=0.05` (≈ original price), pickup-anchored TTL, so a local buyer can intercept before pickup → cuts the warehouse round-trip. Records an `exchange` `ImpactEvent`.

### §20.6 DB — migration `0005_return_grading_decisions` (additive)

Purely additive on top of 0004 (no drops/retypes → applies cleanly on the seeded DB):


| Column                                                | Purpose                                                                |
| ----------------------------------------------------- | ---------------------------------------------------------------------- |
| `product_units.size` (String)                         | physical size of the unit → powers the §20.2 size-match gate           |
| `order_items.return_state` (String)                   | post-return disposition: `return_to_seller` (wrong_item) / `exchanged` |
| `order_items.exchanged_from_id` (UUID FK→order_items) | replacement line links back to the original                            |


The `verification` block needs no column — it lives in `condition_passports.passport` (§20.3).

### §20.7 Seed + smoke

`/demo/reset` now also seeds: **(a)** a `too_small` size-return live on rescue as a **Grade A, 7%-discount** listing; **(b)** two `wrong_item` **flagged** backpack records (no passport/listing) that dominate the ops seller-signals; **(c)** a completed **exchange** — returned unit live on rescue at ≈ original price with an `EXCHANGED` event + pending pickup, plus a size-11 sneaker that the size-match gate filters out. New `/demo/reset` counts: `wrong_item_flagged`, `exchanges`, `size_return_unit`, `exchange_unit`, `gate_mismatch_unit`. `scripts/smoke.py` asserts all five decisions (pristine grade + minimal discount, gate filtering, `verification` on a graded return + ResaleListing, `wrong_item` → nothing created + ops signal, exchange → replacement + rescue + `EXCHANGED`) while keeping every prior assertion green → **SMOKE_OK**.

---

## §21 Track D — Finals MVP hardening

> **Status:** next phase after qualification. Tracks A/B/C made Relay broad and demo-capable; Track D makes it feel like an MVP Amazon could pilot: stronger prevention, better Bedrock inspection, production-grade Genie matching, and dispatch-style Rescue allocation. Shikher and Bhavya can work async because each stream has a clear owner and HTTP/JSON boundary.

### §21.0 Ownership + async contract


| Stream                             | Owner   | Why                                                                                                        |
| ---------------------------------- | ------- | ---------------------------------------------------------------------------------------------------------- |
| **Return Confidence / prevention** | Shikher | Sits in cart/PDP/order context, uses API + seller signals + frontend interventions                         |
| **Bedrock grading productization** | Bhavya  | ML-owned prompt/version/confidence/audit improvements in `relay-ml`                                        |
| **Genie marketplace matching**     | Bhavya  | Matching quality is now ML/product intelligence: retrieval, rerank, explanations, false-positive rejection |
| **Rescue Dispatch Score**          | Shikher | Local routing/allocation belongs with engine/API, TTL, carbon, buyer eligibility, and UI                   |
| **Bug sweep / E2E polish**         | Shikher | Ongoing as issues appear while both tracks land                                                            |


**Rule:** Shikher owns API shape + UI integration for his streams; Bhavya owns `relay-ml` internals + response quality for her streams. If Bhavya needs a new API field, add it as optional first and keep old clients working.

### §21.1 Return Confidence — prevention beyond bracketing

> **Status:** ✅ built + smoke-verified (Session 16, Shikher). Shipped as a deterministic, explainable layer (no model dependency) so it always works live and degrades gracefully if relay-ml is down. Endpoints: `GET /cart/return-confidence` + `GET /products/{id}/return-confidence?size=` → `keep_score`, `confidence_band` (high/medium/low), risk `drivers`, customer-positive `interventions`, and a per-product `items[]` breakdown. Signals wired: bracketing / duplicate-variant, **shared** SKU return-health (`services/return_signals.py` — the SAME source `routers/ops.py` reads, so prevention + seller dashboard tell one story), user fit-profile size match/uncertainty, relay-ml fit flags (best-effort), first-time brand, and a *silent* user-return-rate factor (never surfaced to the shopper, per guardrail). UI: `components/relay/ReturnConfidence.tsx` on the Amazon cart + PDP — leads with the recommended ACTION (one-tap "keep size M, drop the spares" / "size M is the safer pick"), never a "you'll return this" warning. `scripts/smoke.py` asserts the three required driver types (bracketing, sku_return_health, user fit) + an actionable intervention. **Next (optional):** swap the heuristic for a learned user×product×SKU model (Returnformer/COP-HGNN framing) behind the same response shape.
>
> **Status — Phase 1 Fit Profiles ("who are you shopping for?", Session 17, Shikher):** ✅ built + smoke-verified. True Fit-style personalization that also solves *buying for someone else*. A shopper owns a set of profiles — `You` (self) + people they buy for (partner/child/parent) modelled like Google Photos people groups — each holding **wardrobe anchors** (a known brand + the size that person wears, the strongest size signal) instead of raw body measurements. Selecting a profile re-scores Return Confidence for *their* size; picking a non-self profile suppresses personal-to-the-buyer signals (own brand history / own return rate). **No-migration storage:** the whole state lives in `users.fit_profile` (JSONB) with the legacy flat axis keys kept as a mirror of the self profile, so `matching.py` / `bracketing.py` keep working unchanged (`services/fit_profiles.py`). New: `app/schemas/fit_profiles.py`, `app/services/fit_profiles.py`, `GET/POST/DELETE /users/me/fit-profiles` + `POST …/active`, a `profile_id` query on both return-confidence endpoints, and `recommended_size`/`recommended_reason` + `profile_id`/`profile_name`/`for_self` on the response. Frontend: `components/relay/FitProfileSelector.tsx` (Amazon-native "Shopping for ▾" with one-time, non-blocking brand+size capture and add-person), an inline **"Recommended for <profile>: <size>"** line on the PDP next to the size grid (boxed widget removed), and the cart card now shows the active profile. Seed: buyer has `You` + `Priya (partner, tops S)` + `Aarav (child, no size yet)` so the *same* hoodie recommends M for the buyer and S for Priya.
>
> **Status — Cart redesign + Phase 2 (history) + Phase 3 (electronics), Session 18, Shikher:** ✅ built + smoke-verified (`SMOKE_OK`; static checks pass). Three changes:
> - **Cart un-loud (UX):** the accumulated Return Confidence banner felt like friction-to-buy. Replaced with quiet **per-product nudges** (`components/relay/CartLineNudge.tsx`) under each line — at most one muted line, and *nothing* when the item's a keeper: a duplicate pair shows one "2 sizes in your bag" + a one-tap "Keep size M", a fit/SKU signal shows a muted one-liner, a confident pick shows a faint "Looks like a keeper". The aggregate card is gone from the cart (the rich widget still lives on the PDP).
> - **Phase 2 — history-based anchor inference:** `return_confidence._history_fit_map` fills any *unsaved* size axis from the buyer's own **KEPT** order history (most-recent kept size per axis, excluding returned/return-evented lines), SELF only. A profile-less shopper still gets a sharp pick; copy reads "your recent" vs "your usual" so it's honest about its basis. (Order→profile attribution for non-self + a cross-brand universal-size graph remain deferred.)
> - **Phase 3 — electronics "fit-for-purpose":** non-fashion items get no size penalty; instead the scorer emits a deterministic **compatibility checklist** per category (`_compat_checklist`) as a confidence-builder (the biggest "not as described" killer), carried on the new `intervention.items[]`. PDP renders `components/relay/FitForPurpose.tsx` ("Will this work for you?" checklist + the shared SKU expectation note + a returns reassurance) in place of the size grid; the selector is fashion-only. Smoke asserts the electronics checklist + `keep_score` 0.92.

Current prevention is too thin: fit insight + "3 sizes in cart" bracketing is useful, but not enough for finals. We will upgrade it into a non-punitive **Return Confidence** layer: *"how confident are we this order will be kept, and what intervention helps the customer buy one item with confidence?"*

**Research nudge**


| Source                          | Takeaway for Relay                                                                                                                                                                                                                                                                             |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Returnformer**                | Predicts returns before payment using user-product bipartite graphs, Node2Vec/topological embeddings, Graph Transformer attention, and global return patterns. We should not clone it fully now, but we should use its framing: prevention is a graph/user-product problem, not one cart rule. |
| **COP-HGNN return prediction**  | Customer, order, and product nodes together predict returns better than isolated features; repeat-customer history matters most.                                                                                                                                                               |
| **Early Bird Catches the Worm** | Fashion returns can be predicted before purchase using product embeddings, body/size embeddings, and engineered checkout features.                                                                                                                                                             |
| **Amazon Fashion Fit Insights** | Amazon uses size-system relationships, reviews, product details, purchase/keep history, and LLM-extracted fit feedback; seller tools surface return health, benchmarks, feedback summaries, and size chart defects.                                                                            |


**MVP design**

`GET /cart/return-confidence` or an extension to `GET /cart` should return:

```json
{
  "confidence_band": "high | medium | low",
  "keep_score": 0.0,
  "drivers": [
    { "type": "size_uncertainty", "label": "First purchase from this brand", "severity": "medium" },
    { "type": "sku_return_health", "label": "This SKU has elevated too-small returns", "severity": "high" }
  ],
  "interventions": [
    { "type": "size_recommendation", "label": "Buy M only", "action": "remove_extra_sizes" },
    { "type": "fit_review", "label": "Customers like you say this runs small" }
  ]
}
```

**Signals**

- User: kept vs returned sizes, brand/category fit confidence, return rate, rescue/keep history.
- Product/SKU: return rate, dominant reason, seller signal, size-chart health, review-derived fit flags.
- Cart/order: bracketing, duplicate variants, first-time brand, high-risk category, price/impulse pattern.
- Intervention: one-size recommendation, exchange assurance, lower-return alternative, seller size-chart warning.

**Guardrail:** do not show "you are likely to return this" to the user. Customer copy should be confidence-building: "Buy one with confidence", "Size M is the safer pick", "Fast exchange available if fit is off." Internal ops can see risk drivers.

**Acceptance**

- Cart/PDP exposes `Return Confidence` with at least 3 driver types: bracketing, SKU return health, user fit confidence.
- UI shows recommended action, not only a warning.
- Ops can reuse the same SKU return-health drivers so prevention and seller dashboard tell one story.

### §21.2 Bedrock grading productization

We should present Bedrock as the current MVP grading engine. CNN becomes the cost-optimization tier, not the thing we pretend is live when the checkpoint is absent.

**Research nudge**

AWS Nova visual-inspection examples recommend strict JSON, defect criteria in the system prompt, bounding boxes where available, reference/context comparison, low-temperature deterministic inference, schema validation, prompt templates, and human/second-pass review for low-confidence cases. Nova Pro is stronger for difficult visual inspection; Nova Lite is acceptable for fast MVP grading.

**Bhavya scope**

- Add prompt registry/versioning: `grading_fashion_v1`, `grading_electronics_v1`, `resale_pricing_v1`, `match_rank_v1`.
- Return grading audit metadata: `model_tier_used`, `bedrock_model_id`, `prompt_version`, `confidence_band`, `fallback_reason?`, `expected_context_used`.
- Add capture-quality gates: blurry, low light, object not visible, missing required angle.
- Add confidence bands:
  - `auto_pass`: safe to route/list.
  - `needs_review`: show passport but mark as lower confidence / require better media for production.
  - `reject_reupload`: ask for better image/video.
- Improve multi-image aggregation: front/back/label/damage close-up; worst defect wins, but size/fit returns can still use Track C pristine override.
- If Nova returns bounding boxes, keep them in `defects[].bbox` so UI can show visual defect overlays later.

**Acceptance**

- Every grade response has stable audit metadata and prompt version.
- Invalid/low-quality media no longer silently produces overconfident passports.
- Existing API remains backward-compatible: old clients can ignore new metadata.

### §21.3 Genie as marketplace matching infrastructure

Genie should feel like demand capture for a volatile second-hand marketplace, not a search form. The current retrieve → taxonomy/Bedrock rerank is the right foundation; Track D makes the outcome explainable and stricter.

**Research nudge**


| Marketplace              | Relevant pattern                                                                                                                                                |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Vinted**               | Three-stage recommendations: ANN retrieval from two-tower embeddings, explicit preferences like size, implicit preferences from clicks/purchases, then ranking. |
| **Mercari**              | Search uses retrieval plus ML reranking, with freshness boosting because used listings age quickly.                                                             |
| **Etsy**                 | Candidate generation + ranker optimized for multiple outcomes such as favorite and purchase.                                                                    |
| **Facebook Marketplace** | Multiple models predict relevance, seller/content quality, engagement, and policy/integrity risk.                                                               |


**Bhavya scope**

Turn Genie into **Demand Radar**:

```text
final_score =
  intent_match
  x size_fit
  x price_fit
  x geo_fit
  x trust_fit
  x freshness_boost
  x condition_acceptance
```

Return match reasons with each match:

```json
{
  "score": 0.91,
  "match_reasons": [
    { "type": "intent_match", "label": "Exact laptop match", "score": 0.98 },
    { "type": "price_fit", "label": "Within your INR 45,000 budget", "score": 1.0 },
    { "type": "condition_fit", "label": "Grade A meets your minimum condition", "score": 0.9 },
    { "type": "freshness", "label": "Returned 12 minutes ago", "score": 0.8 }
  ],
  "rejected_reasons": []
}
```

**Waiting state**

If no match passes the floor, Genie should still feel alive:

- "Watching nearby returns."
- "2 candidates rejected: wrong size, above budget."
- "Price alert armed."
- "You will get early access if your Rescue tier qualifies."

**Acceptance**

- No cross-category false positives; wrong-category candidates must be rejected before/after rerank.
- Matches expose visible reasons: intent, size, price, geo/trust/freshness where available.
- Empty state is useful and persistent, not "nothing happened."

### §21.4 Rescue Dispatch Score

> **Status:** ✅ built + smoke-verified (Session 20, Shikher). Shipped as a transparent per-(unit × viewer) **dispatch score** computed in **relay-engine** (Go, `POST /dispatch/score`) with a byte-for-byte **relay-api fallback** (`MockEngineClient.score_dispatch`) so the feed never 500s if the engine is down. Each rescue listing now carries `dispatch_score` (0..1) + `dispatch_reasons[]` — a weighted sum of `demand_intent + distance_savings + ttl_urgency + price_acceptance + buyer_keep_probability + carbon_saved − failed_claim_risk − chain_depth_risk` (weights env-tunable, identical in Go + Python). `app/services/dispatch.py` assembles inputs (reusing `disposition.build_demand_signal`, `matching` price/size fit, `carbon.net_co2_saved`, grade, haversine distance) and computes `viewer_wish_match`. `/rescue/feed` sorts by score (owned units pinned), attaches reasons, and layers a **capped match-based early-access lead** on top of the existing credit tiers (**hybrid_lead**) so a strong in-radius wish-match sees an item slightly sooner — guardrails (eligibility, chain depth, net carbon, status) unchanged. Pair Rescue reuses the same framing (zero-payment swap, lowest-carbon local swap). UI: `DispatchReasons.tsx` chips on rescue + pair cards, feed trusts backend order; risk chips (`claim_risk`/`chain_depth`) reserve slots so a guardrail caveat is never crowded out of the 3-chip cap. Hardening: `wish_score` now uses the LLM grade timeout + deterministic mock fallback (creating a wish never 500s on an ML hiccup).

Return Rescue is strong, but it should move from "nearby feed sorted by time" to "local marketplace dispatch." Use Uber/FoodMatch-style thinking: build a graph of candidate units and candidate buyers, weight each edge by business utility, then allocate early exposure to the best edges first.

**Research nudge**

Ride-hailing and delivery systems often use:

- maximum-weight bipartite matching between supply and demand,
- edge utility = immediate reward + future-state value,
- dynamic waiting windows,
- cancellation/failure penalties,
- batching/routing signals,
- pricing as a supply-demand lever.

FoodMatch maps food delivery assignment to graph matching and batching in dynamic road networks. Ride-hailing work uses RL/value functions to account for future spatial imbalance. We do not need full RL now; a transparent utility score is enough for MVP.

**MVP score**

```text
rescue_dispatch_score =
  demand_intent
  + distance_savings
  + ttl_urgency
  + price_acceptance
  + buyer_keep_probability
  + carbon_saved
  - failed_claim_risk
  - chain_depth_risk
```

**Shikher scope**

- Add `dispatch_score` and `dispatch_reasons` to rescue feed/listing internals.
- Use early-access windows more intelligently: best-matched buyers see the item first, not just highest-credit users.
- Keep current feed stable, but sort/label with dispatch reasons: "best local fit", "highest carbon save", "price likely to clear".
- Connect Pair Rescue to the same utility framing: pair swaps are a special bipartite match with very high carbon score and no payment.
- Optional later: courier-route boost if a pickup route already passes near a buyer.

**Acceptance**

- Rescue cards can explain why they are surfaced: nearby, high wish intent, price fit, TTL urgent, carbon positive.
- Dispatch score never violates existing guardrails: eligibility, chain depth, net carbon, status.
- Existing decay pricing remains, but it becomes one input to dispatch instead of the whole story.

### §21.5 Phase plan


| Phase                      | Shikher                                                                           | Bhavya                                                             | Integration                                                                      |
| -------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| **D0 — Contract pass**     | Draft API shapes for `return-confidence`, rescue dispatch reasons, frontend DTOs  | Draft grading metadata + Genie match-reason response shape         | Agree optional fields; no breaking contracts                                     |
| **D1 — Independent build** | Implement Return Confidence + Rescue Dispatch Score with deterministic heuristics | Implement prompt registry/audit + Genie reason/rerank improvements | Both work async; mock/fallbacks keep app running                                 |
| **D2 — UI + seed**         | Add confidence widgets, dispatch labels, richer ops reuse, seed edge cases        | Provide stable examples for grading bands + match reasons          | Seed must show high/medium/low confidence and accepted/rejected Genie candidates |
| **D3 — E2E hardening**     | Full purchase→prevention→return→route→match→ops flow; bug sweep                   | Tune prompt/rerank thresholds from observed failures               | Final walkthrough becomes live-MVP, not scripted demo                            |


### §21.6 Finals narrative

Track D lets us say:

> Relay is not a resale page. It is a **product-user-unit graph** that prevents avoidable returns, grades unavoidable returns, routes each physical unit, and dispatches it to the next best owner with trust.

Do not pitch random buzzwords. Pitch the actual intelligence stack:

- Returnformer/HGNN-inspired **Return Confidence** for prevention.
- Nova/Bedrock **visual inspection** with audit metadata.
- Vinted/Mercari-style **retrieve → rerank marketplace matching** for Genie.
- Uber/FoodMatch-style **dispatch scoring** for Return Rescue.
- Seller Ops closes the loop by feeding SKU issues back into prevention.

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

*Last updated: 2026-06-14 (Session 6 — bracketing(≥3), ops persona, carbon constants, pgvector-T1, Bedrock-only grading; + demand-weighted disposition, wish-score, Pair Rescue, seller signals, rescue decay pricing; embeddings/wish-score assigned to Bhavya) · Maintained alongside `[context.md](./context.md)`*

*Session 7 — **Track B (Second Life: resell + republish)** added (§19); new relay-ml `POST /grade-and-price` contract for Bhavya (§5 + §8 B4.2); resale pricing unified with rescue + `price_fit` (§19.6); `resale_listings` / `order_items.delivered_at` / `products.image_url` data model (§6); real `seed_assets/` seeding spec (§19.7); seller/buyer UX (§19.8–19.9). Task board: all ML(Bedrock) / backend / seeding / frontend-migration rows flipped to ✅ done; Track B rows added as specced/in-progress; **deploy + demo + submission left pending (honest).***

*Session 8 — **Track C — Return-grading decisions** added (§20), backend built to the LOCKED frontend shapes: (1a) size/fit return = pristine asset → Grade-A boost + minimal-discount Path-A listing; (1b) next-owner size-match gate in `matching.py` (size eq OR fit confidence > 0.7); (2) expected-context `verification` — additive `expected_size/color/title` Form fields enrich the **same** grade prompt (no extra image/call — **relay-ml change flagged for Bhavya**) → locked `verification` block on ConditionPassport + ResaleListing, with a relay-api fallback; (3) `wrong_item` fully gated (flagged return-to-seller, no grade/anchor/listing) + pick-pack seller signal; (4) new `POST /orders/items/{id}/exchange` (in-window, no ML grade, replacement line + pristine returned unit → Path-A rescue + `EXCHANGED` event). Additive migration `0005` (`product_units.size`, `order_items.return_state`, `order_items.exchanged_from_id`; `verification` in passport JSON). Seed + `scripts/smoke.py` extended for all five → **SMOKE_OK**. Task board: Track C rows ✅ done.*