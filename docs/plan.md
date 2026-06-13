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

| id | tier | owner | content | status |
|---|---|---|---|---|
| contracts-v1 | T0 | Shikher | Publish `relay-contracts` v1: ConditionPassport JSON schema, OpenAPI for relay-ml + relay-api public routes | pending |
| repo-scaffold | T0 | Shikher | Create 5 GitHub repos, branch `main`, `relay-dev` docker-compose, README per repo | pending |
| ml-dataset | T0 | Bhavya | Download HF e-commerce defects + Kaggle fit dataset; document in `relay-ml/data/README.md` | pending |
| ml-health | T0 | Bhavya | `relay-ml`: FastAPI skeleton, `GET /health`, Docker, `.env.example` | pending |
| api-skeleton | T0 | Shikher | `relay-api`: FastAPI skeleton, Postgres + Redis docker, Alembic init | pending |
| engine-skeleton | T0 | Shikher | `relay-engine`: Go chi/fiber skeleton, `GET /health` | pending |
| web-shell | T0 | Shikher | `relay-web`: Next + shadcn layout, nav, placeholder routes | pending |
| ml-grade-image | T1 | Bhavya | `POST /grade-image` → ConditionPassport (CNN baseline + optional Bedrock T2) | pending |
| ml-grade-video | T1 | Bhavya | `POST /grade-video` → keyframe pipeline + aggregated passport | pending |
| ml-fit-flags | T1 | Bhavya | `POST /fit-flags` → article flags (rules stub → MultiFlags stretch) | pending |
| ml-confidence | T1 | Bhavya | Return `confidence` + `model_tier_used`; document escalation threshold | pending |
| api-returns | T1 | Shikher | Return intake API, S3 upload, call relay-ml, persist passport | pending |
| api-mock-ml | T1 | Shikher | Mock ML client until Bhavya URL live; swap via `ML_SERVICE_URL` | pending |
| engine-disposition | T1 | Shikher | Go: `POST /disposition/score` — rule engine (exchange/rescue/p2p/…) | pending |
| engine-rescue-ttl | T1 | Shikher | Go: Rescue listing TTL + geo radius scoring | pending |
| api-rescue | T1 | Shikher | Rescue feed + claim APIs; guardrails v1 (eligibility, chain cap) | pending |
| api-exchange | T1 | Shikher | Exchange-first routing when reason=size + SKU in stock | pending |
| api-seed | T1 | Shikher | `scripts/seed.py` — users, catalog, wishes, demo geo | pending |
| web-checkout-insight | T1 | Shikher | Fit insight banner on PDP/checkout (fashion) | pending |
| web-return-wizard | T1 | Shikher | Return flow: reason → upload → grade result → outcome | pending |
| web-rescue-feed | T1 | Shikher | Rescue cards + countdown TTL | pending |
| api-wishlist | T2 | Shikher | Reverse Wishlist CRUD + match on return graded | pending |
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
| **Return + grade** | Photo upload → Condition Passport JSON |
| **Disposition engine** | Go service scores: exchange · rescue · p2p · refurb · donate · recycle |
| **Exchange-first** | Return reason size/fit + exchange SKU in stock → offer swap before warehouse |
| **Return Rescue** | Geo + TTL feed; nearby buyer claims; Zomato-inspired |
| **Guardrails** | Eligibility score, chain depth cap, net-carbon gate (v1 can be rule stubs) |

### P1 — T2 differentiators

| Feature | Description |
|---|---|
| **Reverse Wishlist** | Buyer posts demand; match when return graded |
| **P2P one-click list** | From return flow; escrow stub; LifeLedger passport shown |
| **Warranty chain** | Electronics: remaining warranty + repair events on passport |
| **LifeLedger verify** | QR → hash check on Polygon Amoy testnet |

### P2 — supporting

| Feature | Description |
|---|---|
| **Green credits** | Earn on *kept* rescue/exchange (14-day rule) — not purchase volume |
| **Impact Wallet** | Net CO₂ vs baseline (simple formula OK for demo) |

### T3 — stretch (Lego add-on; pitch optional)

RL disposition hook · Pair Rescue · Donation routing · Full MultiFlags · ClickHouse analytics

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
| POST | `/disposition/score` | `{ unit_id, passport, return_reason, user_id, geo }` | `{ channel, score, reasons[], guardrails_applied[] }` |
| POST | `/match/rescue` | `{ unit_id, geo, radius_km }` | ranked user ids |
| POST | `/match/wishlist` | `{ unit_id, passport }` | ranked wish ids |

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

-- matching
reverse_wishlist (id, user_id, category, size, max_price, geo_lat, geo_lng, expires_at)
rescue_listings (id, unit_id, discount_pct, expires_at, status, claimed_by)
p2p_listings (id, unit_id, seller_id, price, status, escrow_status)

-- trust
lifeledger_events (id, unit_id, event_type, tx_hash, passport_hash, created_at)
warranty_records (id, unit_id, months_remaining, repair_events JSONB)

-- incentives
green_credit_ledger (id, user_id, amount, reason, unlock_at, created_at)
```

**pgvector:** `reverse_wishlist.embedding`, `product_units.embedding` (optional T2).

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

### Reverse Wishlist

Seed 20–50 wishes in demo; expire 30 days; match on category + size + price + geo.

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

**Env vars:** `AWS_REGION`, `BEDROCK_MODEL_T2`, `BEDROCK_MODEL_T3`, `OPENAI_API_KEY` (fallback).

**Cost:** CNN first always. Log `model_tier_used` for Shikher's Impact/cost story.

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
| 12–20 | Video keyframes, `/grade-video`, confidence calibration |
| 20–28 | Bedrock T2/T3 escalation, `/fit-flags` rules |
| 28–36 | Docker, deploy Railway/AWS, hand Shikher URL |
| 36–48 | MultiFlags stretch OR hard-case tuning OR help demo recording |

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
- [ ] `MLClient` interface + mock + real HTTP impl
- [ ] Celery task: `grade_return_task` → call relay-ml → save passport
- [ ] LifeLedger stub (DB only) until T2

**relay-engine:**
- [ ] Disposition rule matrix (see below)
- [ ] Rescue TTL scorer (geo haversine, default 3km)
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

**relay-web pages (T1):**
- [ ] `/` — product grid
- [ ] `/products/[id]` — PDP + fit insight
- [ ] `/checkout` — bracketing warning (optional)
- [ ] `/returns/new` — wizard
- [ ] `/rescue` — feed + countdown
- [ ] `/account/fit-profile` — mock history

### T2 — Differentiators

- [ ] Reverse wishlist UI + APIs
- [ ] P2P listing flow (electronics tab)
- [ ] Warranty chain display
- [ ] LifeLedger Solidity + Polygon Amoy + QR page
- [ ] Green credits (14-day unlock)
- [ ] `/demo/reset` button (admin)

### T3 — Stretch

- [ ] RL hook interface in Go
- [ ] Pair Rescue matcher
- [ ] Donation routing
- [ ] Lambda Rescue expiry

### Shikher 48h schedule (suggested)

| Hours | Focus |
|---|---|
| 0–8 | All repos + contracts + compose + seed script skeleton |
| 8–16 | API returns + mock ML + Go disposition v1 |
| 16–24 | Web return wizard + rescue feed (mock data) |
| 24–32 | Wire real relay-ml URL; exchange-first; guardrails |
| 32–40 | T2 features (wishlist, p2p, LifeLedger) |
| 40–48 | Deploy AWS + Railway backup + demo video + submission |

---

## §10 Integration matrix

| From → To | Protocol | Data |
|---|---|---|
| relay-web → relay-api | REST JSON | UI requests |
| relay-api → relay-ml | REST multipart/JSON | Images, passports |
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
| 0:25–1:20 | Fashion: fit insight → return → grade passport → exchange OR rescue |
| 1:20–1:50 | Reverse wishlist match notification + claim countdown |
| 1:50–2:20 | Electronics: P2P list + warranty on LifeLedger + QR verify |
| 2:20–2:50 | Ops dashboard: chain depth, transfer_count |
| 2:50–3:00 | HLD slide: Go engine + Bedrock tiers + scale |

### Page list

| Route | Tier | Owner |
|---|---|---|
| `/` | T0 | Shikher |
| `/products/[id]` | T1 | Shikher |
| `/returns/new` | T1 | Shikher |
| `/rescue` | T1 | Shikher |
| `/wishlist` | T2 | Shikher |
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
BEDROCK_MODEL_T2=anthropic.claude-3-haiku-...
BEDROCK_MODEL_T3=amazon.nova-pro-v1:0
OPENAI_API_KEY=           # fallback
CNN_MODEL_PATH=./models/grade_cnn_v1.pt
CONFIDENCE_THRESHOLD_T2=0.85
CONFIDENCE_THRESHOLD_T3=0.75
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
  Shikher: returns API + Go disposition + rescue + web wizard + seed + mock→real ML
  Bhavya:  CNN v1 + /grade-image + /grade-video + /fit-flags rules

M2 (parallel) — TARGET: T2 demo
  Shikher: wishlist + p2p + LifeLedger + warranty UI
  Bhavya:  Bedrock tiers + confidence tuning + optional MultiFlags

M3 — Deploy + video + submission
  Shikher: AWS + Railway + PPT + README
  Bhavya:  support hard cases + demo assets

M4 (stretch) — T3
  Both: RL hook, Pair Rescue, analytics
```

---

*Last updated: 2026-06-13 · Maintained alongside [`context.md`](./context.md)*
