# Amazon Hackon — Problem Statement #2: Circular Commerce Ecosystem

> **Single source of truth** for Shikher + Bhavya. Brainstorm decisions, architecture, research, and progress logs live here.

---

## 0. Meta

| Field | Value |
|---|---|
| **Event** | Amazon Hackon |
| **Problem** | #2 — Sustainable commerce / second life for products |
| **Team** | 2 people |
| **Shikher** | Team lead — backend, frontend, system architecture, scaling, ML/AI pipeline integration & deployment, connecting Bhavya's work |
| **Bhavya** | ML/AI — research papers, training data, model training, exposing models, photo/video AI pipeline |
| **Working mode** | Parallel tracks; Shikher owns integration layer |
| **Phase** | Session 2 — Decisions locked, pre-implementation |
| **Product name (working)** | **Relay** (see §15 for alternates) |
| **Platform** | Web-first (desktop/laptop demo priority) |
| **Demo categories** | Fashion + Electronics (dual vertical demo) |
| **Last updated** | 2026-06-15 (Session 8 — Track C: return-grading decisions) |

---

## 1. Problem Statement (verbatim summary)

Millions of returned, underused, or discarded products are still usable. Returns hurt customers, sellers, and the planet. Trust in refurbished/second-hand is low.

**Vision:** An intelligent ecosystem where returned/unused products automatically find their **next best owner**.

**Pillars in the brief:**
1. AI disposition — resell / refurbish / donate / recycle / exchange
2. Smart quality grading — image/video analysis
3. Personalized recommendations for **certified refurbished**
4. Sustainable incentives — green credits
5. Easy **peer-to-peer resale** inside Amazon's trusted ecosystem
6. **Predictive return prevention** before purchase

**Our north star:** Build the future of sustainable commerce where every product gets a meaningful second life.

---

## 2. Strategic Positioning (avoid generic AI slop)

### What NOT to lead with
- **Generic return prediction** — saturated commercially (Returnalyze raised $6M; Returnformer graph-transformer paper exists). Building "will this user return?" as the hero feature = table stakes, not differentiation.
- **Token-dumping Bedrock calls** on every image — expensive, slow, not an engineering story.
- **Points-only gamification** — research shows eco-points fail without trust; can even cause moral licensing → overconsumption.

### What TO lead with (reframe)
> **"Reverse Logistics Routing Engine" + "Next-Owner Matching"**

Not a returns classifier. A **circular-economy decision + matching system** that answers two questions for every physical item:

1. **Disposition:** What should happen to this unit? (restock · refurb · P2P · donate · recycle · exchange)
2. **Matching:** *Who* is the next best owner, and through which channel?

This reframing is **research-backed** (McKinsey 2025, Optoro/Ciclo/G2RL industry, RL-based green reverse logistics papers) and **maps directly to the problem statement** while avoiding the crowded "return prediction" lane.

### Elevator pitch (draft)
*"Circulate — Amazon's AI routing layer that grades every return in seconds, routes it to the highest-value second life, and matches it to the right buyer before it ever hits a landfill. Prevention at checkout. Rescue in transit. Trust through a Condition Passport."*

---

## 3. Concept Map — How the pieces connect

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRE-PURCHASE LAYER                              │
│  Fit profile · bracketing detection · exchange nudge · risk insight   │
│  (SizeFlags-style article flags, NOT clone of Returnformer)             │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ fewer bad purchases
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      RETURN / UNUSED TRIGGER                            │
│  Customer initiates return · Trade-in · "Rescue" claim · unused listing │
└───────────────────────────────┬─────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   PERCEPTION LAYER (Bhavya + Bedrock)                   │
│  Tiered vision: category → condition grade → defect localize → video  │
│  Output: Condition Passport (structured JSON, not prose)                │
└───────────────────────────────┬─────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              DISPOSITION ENGINE (Shikher — core differentiator)         │
│  Multi-objective scorer: recovery value · carbon · SLA · channel capacity │
│  Routes: Renewed pipeline · Resale · P2P · Donate · Recycle · Exchange  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   NEXT-OWNER MATCHING (NOT generic recsys)              │
│  Buyer-item matching · hyperlocal rescue · refurbished personalization  │
│  Volatile inventory · short TTL · geo + taste + trust + price sensitivity │
└───────────────────────────────┬─────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              TRUST + INCENTIVES LAYER                                     │
│  Condition Passport · green credits · impact dashboard · social proof   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Module Deep-Dives

### 4.1 Auto-Matching — Is it recommendation?

**Partially, but the core problem is different.**

| Concept | What it optimizes | Analogy |
|---|---|---|
| **Product recommendation** | "What SKU might you buy from catalog?" | Amazon homepage |
| **Disposition routing** | "Where should this *specific unit* go?" | Optoro, Ciclo, G2RL, UPS AI disposition (Dec 2024) |
| **Next-owner matching** | "Which *buyer* should get this *specific unit*?" | Zomato Food Rescue, Vinted retrieval, FB Marketplace similarity |
| **Refurbished personalization** | "Which certified renewed item fits *your* trust + taste profile?" | Renewed storefront + condition prefs |

**Our matching has 3 sub-problems:**

#### A) Disposition routing (supply-side)
Score each returned unit across channels:
- **Restock** — like-new, demand exists, margin positive
- **Amazon Resale / Renewed** — needs refurb pipeline
- **P2P marketplace** — good condition, high demand category, seller willing
- **Donate** — low recovery value, high social impact
- **Recycle** — end of life
- **Exchange** — same SKU swap (size/color) faster than full return cycle

**Demand-weighted (Session 6b):** the scorer folds in **open Reverse Wishlist demand** (Σ wish_score × geo_decay) so routing is pulled toward `rescue`/`p2p` where real local demand exists — disposition becomes optimization, not a static rule. **Pair Rescue** is the extreme case: A↔B bipartite swap when two returns satisfy each other's wishes.

**Industry:** Optoro, ReturnPro, Ciclo, G2RL DecisionAI, McKinsey "single AI-driven decision engine."

**Research:**
- Green reverse logistics with RL + genetic algorithms (ScienceDirect 2024)
- Agentic AI + evolutionary optimization for fuzzy multi-objective reverse logistics (Springer 2025)
- Edge CNN + DRL for disposition + carbon-aware routing (Raj 2026, IJCA) — **94.2% classification, 18–23% emission reduction** — strong reference architecture for Bhavya

#### B) Hyperlocal "Rescue" matching (Zomato-inspired) ⭐ creative differentiator
**Zomato Food Rescue (Nov 2024):** When order canceled after pickup, it surfaces to users within **3 km** for **minutes** at discount. Original customer excluded. Freshness guards.

**Our adaptation — "Return Rescue" / "Circulate Now":**
- Return pickup already en route OR customer cancels before delivery
- Item surfaces to nearby users who expressed interest in category + size + max discount
- **Minutes-level TTL** — avoids warehouse round-trip
- Carbon win: skip warehouse leg entirely
- Amazon already has last-mile density — this is plausible at hackathon narrative level

**Not identical to Zomato:** physical goods aren't perishable like food, but **fashion seasonality, impulse buyers, and warehouse cost** create similar urgency.

#### C) Next-buyer matching for refurbished / P2P (demand-side)
Once disposition = resell/P2P/refurb, match to buyers using:
- Visual similarity embeddings (FB Marketplace, Mercari vector search)
- User fit profile (sizes, return history, brand affinity)
- Trust score (buyer acceptance rate on renewed items)
- Price sensitivity + green credit balance

**Research:** SIGIR eCom'22 "When Volatility Reigns" — second-hand marketplaces have **hours/days item lifespan**, cold-start is organic, near-duplicates abound. Vinted 3-stage retrieve→rank. Mercari CF + vector search with freshness bias.

---

### 4.2 Item Classification & Quality Grading (Bedrock-optimized)

**Goal:** Structured Condition Passport, not chatty LLM output.

#### Tiered inference pipeline (engineering marvel, not token dump)

| Tier | Model (Bedrock) | When | Output |
|---|---|---|---|
| **T0 — Gate** | Nova Micro / rules | Every image | Category, reject blurry/empty |
| **T1 — Fast grade** | Nova Lite OR Bhavya's fine-tuned MobileNet | 80% of items | Grade A–D, disposition hint |
| **T2 — Attribute extract** | Claude Haiku | Needs structured fields | Defects list, packaging state |
| **T3 — Hard cases** | Nova Pro | Low confidence / high value | Bounding boxes, nuanced damage |
| **T4 — Batch** | Batch inference | Warehouse backlog | 50% cheaper (AWS docs) |

**Video strategy (don't send full video to LLM):**
1. Customer records 15–30s guided sweep (UI shows angles)
2. Extract 5–8 keyframes (scene change + coverage check)
3. Run T0–T2 on keyframes; aggregate via voting / max damage score
4. Optional: Nova Pro on worst frame only

**AWS references:**
- `aws-samples/sample-generative-visual-inspection` — Nova Pro defect detection, zero-shot
- `aws-samples/aws-smart-product-onboarding` — tiered Bedrock cost table
- `aws-samples/sample-retail_genai_style_classifier` — batch inference pattern

**Bhavya's track:**
- Gather/open dataset: Amazon Berkeley Objects, DeepFashion, return defect datasets, synthetic defect injection (Raj 2026 approach)
- Train lightweight **multi-task CNN** (grade + category + defect localization) — can run on SageMaker, fallback when Bedrock down
- Confidence score gates Bedrock escalation

**Output schema — Condition Passport (JSON):**
```json
{
  "unit_id": "...",
  "grade": "B+",
  "disposition_recommendation": "p2p_resale",
  "defects": [{"type": "scuff", "severity": "minor", "bbox": [...]}],
  "confidence": 0.94,
  "media_hash": "...",
  "graded_at": "...",
  "model_tier_used": "T1"
}
```

This passport **is the trust artifact** shown to next buyer — not marketing copy.

---

### 4.3 Gamification & Trust (beyond points)

**Insight from research:** Gamification works for pro-environmental motivation via **instrumental + hedonic affordances**, but **warm glow → moral licensing → overconsumption** (Xianyu/C2C study, 613 users). Eco-points only work when they **build platform trust** (Frontiers 2026).

#### Trust mechanisms (prioritize these)
| Mechanism | What it does | Reference |
|---|---|---|
| **Condition Passport** | Immutable graded record with photos | Our core artifact |
| **Lifecycle timeline** | Return → grade → match → deliver chain | TRUCE / DPP concept (MDPI 2025) |
| **Verified seller/buyer badges** | Acceptance rate on renewed, not gamified noise | Amazon trust layer |
| **Video grade certificate** | "AI-inspected · 6 angles · Grade B" | Differentiator vs text-only used listings |
| **Impact Wallet** | CO₂ saved, landfill diverted, water saved — cumulative | Tentree Impact Wallet |
| **Worn Wear narrative** | Repair/reuse story, not discount chasing | Patagonia |

#### Gamification that doesn't backfire
- **Streaks for verified green actions** (return via exchange not ship-back, choose slower eco shipping, buy renewed) — verified via API, not self-report
- **Rescue hero badge** — claimed a Return Rescue item (real impact)
- **Fit improvement score** — "Your return rate dropped 20% since using Fit Insights" (competence, not vanity points)
- **Community proof** — "847 users in your city rescued items this month"
- **Avoid:** leaderboard that rewards volume of buying renewed (drives overconsumption)

#### Green credits (verified actions only)
Earn for: completing video grade, choosing exchange, buying renewed, successful P2P sale, Rescue claim.
Redeem for: Renewed discount, free priority on Rescue listings, donate-to-charity multiplier.
**Must be substantiated** — no greenwashing (Brandmovers sustainability loyalty guide).

---

### 4.4 What does "Easy P2P Resale inside Amazon's trusted ecosystem" mean?

**Plain English:** Let a regular customer sell their returned/unused item **directly to another customer** on Amazon — with Amazon handling trust, payments, shipping labels, and dispute resolution — instead of only professional refurbishers (Renewed) or Amazon itself selling returns (Resale/Warehouse).

#### What Amazon has TODAY
| Program | Who sells | Who buys | Trust layer |
|---|---|---|---|
| **Amazon Renewed** | Certified refurbishers only | Customers | Renewed Guarantee, pro inspection |
| **Amazon Resale** (ex-Warehouse) | Amazon sells returns | Customers | Condition grades, Amazon fulfillment |
| **Amazon Trade-In** | Customer → Amazon | N/A (gift card) | Amazon inspects, refurb/recycle |
| **"Used" third-party listings** | Any seller | Customers | Generic, low trust |
| **P2P like Mercari/Poshmark** | ❌ Not native | — | — |

#### The GAP (our opportunity)
Amazon has **B2C resale** (Renewed, Resale, Trade-In) but NOT **C2C resale with AI grading + Amazon escrow**.

**Ciclo** (competitor reference) explicitly routes to **"Peer-to-Peer Resale"** as a disposition channel for fit complaints and quality issues — lower ops cost, no warehousing.

**Our P2P flow (concept):**
1. Return graded → disposition engine says P2P viable
2. One-click list: AI pre-fills title, condition, price suggestion
3. Amazon holds payment in escrow
4. Buyer sees Condition Passport + seller return reason (optional)
5. Amazon shipping label OR local pickup (Rescue mode)
6. Dispute → re-grade with video

**Why Amazon would want this:** Keeps GMV inside ecosystem vs eBay/Meesho; Trade-In gift cards are less liquid than peer cash/credits.

---

### 4.5 Predictive Return Prevention (reframed — NOT Returnformer clone)

**Saturated:** Generic "return probability before checkout" — Returnformer (MDPI 2026), Returnalyze, True Fit, Zalando size AI.

**Our angle — "Fit Intelligence + Purchase Guardrails":**

#### User-level insights (UI mockup ideas)
- **Fit Profile:** "You return 72% of Size M in brand X — we recommend L"
- **Bracketing detector (P0/T1 — promoted Session 6):** "You have 3 sizes of same item in cart — keep the one that fits (we suggest L)." Active interceptor at checkout, the single most citable prevention signal (~40% of fashion returns). Advisory, never blocks.
- **Category risk:** "Electronics returns are rare for you; fashion is your friction point"
- **Exchange nudge:** Myntra already offers extra discount if you **exchange instead of return** — we formalize this with AI

#### Article-level insights (SizeFlags / MultiFlags — Zalando research)
- Bayesian flags: "This article runs large — size down"
- `too-big` / `too-small` / `true-to-size` / `critical-fit` from aggregate return reasons
- **Bhavya:** can implement simplified MultiFlags on synthetic/historical data

#### What we show at checkout (not just a score)
Instead of "23% return risk" ( scary, generic):
> "⚠️ Size alert: Based on your history + this article's fit data, Size M has high mismatch. Try L. **Or exchange free if it doesn't fit.**"

**Differentiation:** Prevention tied to **actionable fit + exchange path**, not fear-based scoring.

---

## 5. Industry Landscape (competitive / inspiration)

### Global reverse logistics AI
| Player | Focus |
|---|---|
| **Optoro** | ML disposition routing, max recovery |
| **ReturnPro** | Multi-marketplace disposition + VIP Outlet |
| **Ciclo** | AI routing incl. P2P, 95% image grading claim |
| **G2RL DecisionAI** | Autonomous tech asset disposition |
| **UPS** | AI disposition engine (Dec 2024) |

### India e-commerce circular initiatives
| Platform | Initiative |
|---|---|
| **Flipkart Reset** | Refurb electronics; Swap on Jeans textile recovery; AI diagnostics |
| **Myntra** | Return fees for high-return users; exchange nudges; Cupboard of Care / Project Restyle (CSR) |
| **Zomato** | Food Rescue — hyperlocal canceled order matching ⭐ |

### Amazon programs (baseline to extend, not rebuild)
- Renewed, Resale, Trade-In, FBA Grade and Resell (seller-side)

---

## 6. Research Paper & Reference Bank

### Must-read for Bhavya
| Paper / Source | Why |
|---|---|
| **Returnformer** (MDPI 2026) | Know the baseline; don't replicate as hero |
| **SizeFlags** (arXiv 2106.03532) | Article-level fit flags — production-tested at Zalando |
| **MultiFlags** (SCITEPRESS 2025) | Extension with priors + confidence gating |
| **Edge CNN + DRL reverse logistics** (Raj 2026, IJCA) | Architecture: vision → disposition → routing |
| **Green RL reverse logistics** (ScienceDirect 2024) | Multi-objective optimization framing |
| **Agentic AI reverse logistics** (Springer 2025) | Uncertainty + multi-objective |
| **When Volatility Reigns** (SIGIR eCom 2022) | Second-hand recsys challenges |
| **Gamification in C2C marketplaces** (CentAUR) | Pitfalls of points/warm glow |
| **TRUCE circular platform** (MDPI 2025) | Trust + gamified feedback + XR visualization |
| **McKinsey reverse logistics AI** (2025) | Industry decision engine framing |

### AWS / engineering refs
- Nova Pro Visual Inspection sample
- Smart Product Onboarding (Bedrock tier costs)
- Retail GenAI Style Classifier (batch inference)
- Bedrock batch = ~50% cost savings

---

## 7. Creative Additions BEYOND the Problem Statement

Ideas that could win judges without being in the brief:

| # | Idea | Why it's strong |
|---|---|---|
| 1 | **Return Rescue** (Zomato-style hyperlocal) | Concrete, visual demo, carbon story, no one else will show this |
| 2 | **Condition Passport** | Trust moat; portable across Renewed/P2P/Resale |
| 3 | **Exchange-first routing** | Skips full reverse logistics when swap suffices |
| 4 | **Impact Wallet** | Personal CO₂/landfill dashboard — emotional hook |
| 5 | **Fit Profile** | Actionable prevention, not Returnformer clone |
| 6 | **Rescue TTL UI** | Countdown creates urgency — great hackathon demo moment |
| 7 | **Bracketing interceptor** | Catch cart behavior before order |
| 8 | **Donation routing** | Low-value items → NGO matching by category + geo |
| 9 | **Bundle matching** | "Someone near you returned the matching shoe — complete the pair" |
| 10 | **Seller auto-list** | Zero-effort P2P from return flow — "easy" P2P made real |

---

## 8. Proposed System Architecture (brainstorm level)

### High-level services (Shikher owns)
```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Web/Mobile  │────▶│   API Gateway   │────▶│  Core Services   │
│  (React/Next)│     │  (FastAPI/Node) │     │                  │
└──────────────┘     └─────────────────┘     │ · Return Intake  │
                                               │ · Disposition    │
                                               │ · Matching       │
                                               │ · Credits        │
                                               │ · Fit Insights   │
                                               └────────┬─────────┘
                                                        │
        ┌───────────────────────────────────────────────┼────────────────────────┐
        ▼                       ▼                       ▼                        ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Bhavya ML Svc │    │ Amazon Bedrock  │    │ PostgreSQL +    │    │ Redis / SQS     │
│ · CNN grade   │    │ · Tiered vision │    │ pgvector        │    │ Rescue TTL jobs │
│ · Video kf    │    │ · Batch jobs    │    │ · item units    │    │                 │
└───────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data model sketch (key entities)
- **ProductUnit** — one physical item instance (serial, condition, disposition state)
- **ConditionPassport** — graded artifact linked to ProductUnit
- **ReturnEvent** — trigger with reason code, pickup geo
- **RescueListing** — TTL, geo radius, discount
- **MatchCandidate** — buyer ↔ unit score
- **FitProfile** — user size/return patterns
- **GreenCreditLedger** — verified action → credits

### Hackathon scope cut (for later session)
**MVP demo loop (recommended):**
1. User with Fit Profile sees checkout insight
2. Initiates return → uploads photos/video
3. Grading pipeline produces Condition Passport
4. Disposition engine routes to P2P or Rescue
5. Nearby buyer gets Rescue notification → claims
6. Green credits issued to both parties

**Defer:** Full RL optimizer, blockchain DPP, live Amazon integration.

---

## 9. Work Split — Parallel Tracks

### Shikher
- [ ] System architecture doc (this file evolves)
- [ ] API design for disposition + matching
- [ ] Frontend: checkout insights, return flow, Rescue feed, Passport viewer
- [ ] Disposition scoring engine (rules + ML hook)
- [ ] Matching service (geo + embedding retrieval)
- [ ] Green credits ledger
- [ ] Integration layer for Bhavya's model endpoints
- [ ] Bedrock orchestration (tier routing, batch vs realtime)
- [ ] Demo data / simulation

### Bhavya
- [ ] Literature review (papers in §6)
- [ ] Dataset plan: defect images, return reasons, fit data (synthetic OK for hackathon)
- [ ] Train lightweight grading CNN (MobileNet-style multi-task)
- [ ] Video keyframe pipeline
- [ ] Bedrock prompt templates for T2/T3 escalation
- [ ] Expose `/grade`, `/grade-video`, `/fit-flags` endpoints
- [ ] Confidence calibration for tier gating
- [ ] (Stretch) Simplified SizeFlags / MultiFlags prototype

### Integration contract (draft)
```
POST /ml/grade-image     → ConditionPassport partial
POST /ml/grade-video     → ConditionPassport full
POST /ml/fit-flags       → article flags for SKU
GET  /ml/health
```
Shikher's disposition engine consumes passport JSON; never raw images in business logic.

---

## 10. Open Questions

| # | Question | Status |
|---|---|---|
| 1 | Product name final? | **Relay** (working title) — see §15 |
| 2 | Primary demo category? | ✅ **Both** fashion + electronics |
| 3 | Rescue vs P2P? | ✅ **Both** — Rescue first in demo flow, P2P as parallel path |
| 4 | Bhavya: custom CNN vs Bedrock-only? | ✅ **Hybrid** |
| 5 | Blockchain for passport? | ✅ **Yes** — LifeLedger on-chain (see §16) |
| 6 | Mobile-first or web? | ✅ **Web priority** — no mobile app for now |
| 7 | Tech stack? | ⏳ Session 4 (next) |
| 8 | MVP screen flow wireframes? | ⏳ Session 4 |
| 9 | Feature finalization + risk audit? | ✅ Session 3 |

---

## 11. Decision Log

| Date | Decision | Rationale | Status |
|---|---|---|---|
| 2026-06-13 | Reframe hero as **Routing + Matching**, not return prediction | Crowded market; problem statement emphasizes second life | ✅ Accepted |
| 2026-06-13 | Use **tiered Bedrock** + custom CNN, not LLM-on-every-image | Cost, speed, engineering narrative | ✅ Accepted |
| 2026-06-13 | Trust via **Condition Passport**, not points alone | Research + problem statement trust gap | ✅ Accepted |
| 2026-06-13 | Add **Return Rescue** inspired by Zomato | Unique, demo-able, carbon story | ✅ Proposed |
| 2026-06-13 | Prevention via **Fit Intelligence**, not Returnformer clone | Differentiated, actionable UI | ✅ Proposed |
| 2026-06-13 | Product name → **Relay** (working) | Routing + handoff to next owner; not generic "circulate" | ✅ Accepted |
| 2026-06-13 | Demo covers **fashion + electronics** | Different return pain points; shows platform generality | ✅ Accepted |
| 2026-06-13 | Build **both Rescue + P2P** in MVP | Rescue = demo hook; P2P = problem-statement completeness | ✅ Accepted |
| 2026-06-13 | **Blockchain LifeLedger** for Condition Passport | EU DPP trend; tamper-proof trust; real product not hackathon gimmick | ✅ Accepted |
| 2026-06-13 | **Web-only** for now | Judge demo on laptop; responsive OK, no native app | ✅ Accepted |
| 2026-06-13 | Position Fit Intelligence as **VTO alternative** | Amazon killed Try Before You Buy (2025); VTO doesn't predict fit at scale | ✅ Accepted |
| 2026-06-13 | MVP features locked: **Reverse Wishlist, Exchange-first, Warranty chain** | High-impact differentiators from §19 | ✅ Accepted |
| 2026-06-13 | **Risk & guardrails** documented for all major features | Avoid return chains, rebound, greenwashing | ✅ Accepted |
| 2026-06-13 | HackOn winner pattern research complete | Validate approach vs past seasons | ✅ Accepted |
| 2026-06-13 | **Ready for tech stack** (Session 4) | Scope + risks finalized | ✅ Accepted |
| 2026-06-13 | **Iterative Lego tiers** (T0–T3) replace "out of scope" | Always demo-able; stretch features additive | ✅ Accepted |
| 2026-06-13 | Tech stack: **Python (FastAPI+Celery) + Go (relay-engine) + Next/shadcn** | User constraint; no Java/Node | ✅ Accepted |
| 2026-06-13 | Deploy: **AWS primary, Railway backup**; GitHub monorepo | Demo video safety + credits | ✅ Accepted |
| 2026-06-13 | UI: **Own Relay brand**, not Amazon clone | Winner pattern (Odyssey, GreenCart) | ✅ Accepted |
| 2026-06-13 | Datasets locked for Bhavya + seed scripts | HF defects + Kaggle fit + synthetic demo | ✅ Accepted |
| 2026-06-13 | **Multi-repo (4+contracts)**, not monorepo | Parallel work; Bhavya owns relay-ml exclusively | ✅ Accepted |
| 2026-06-14 | **Bracketing interceptor → P0/T1** (was optional) | ~40% of fashion returns; most citable, data-rich prevention; active not passive | ✅ Accepted |
| 2026-06-14 | **Ops/seller dashboard** as 2nd persona (T2) | PS says "ecosystem"; two-perspective demos win; cheap over existing data | ✅ Accepted |
| 2026-06-14 | **Hard-coded carbon constants** (rescue=2.4 kg) | "Simple formula" too vague for judges; anchor to ~15M t US-returns CO₂ stat | ✅ Accepted |
| 2026-06-14 | **pgvector matching → T1** (was optional T2) | Matching is a hero of the pitch; real vector search > geo-only; Shikher prod experience | ✅ Accepted |
| 2026-06-14 | **`GRADING_MODE=bedrock_only` escape hatch** | Real grades without trained CNN; demo-safe; distinct from Shikher's mock client | ✅ Accepted |
| 2026-06-14 | relay-ml T0 reviewed — good to go | Clean FastAPI skeleton + reproducible datasets; minor passport contract drift to fix | ✅ Accepted |
| 2026-06-14 | Bracketing threshold = **≥3** (strict) | Avoid false positives on legit 2-item buys; matches "3 sizes" narrative | ✅ Accepted |
| 2026-06-14 | **Embeddings owned by Bhavya** (relay-ml `/embed`) | Even work distribution; keeps relay-api lean; ML depth on his side | ✅ Accepted |
| 2026-06-14 | **Demand-weighted disposition** (wishes as routing input) | Turns disposition into real optimization, not static lookup | ✅ Accepted |
| 2026-06-14 | **Wish confidence scoring** (Bhavya logreg) | Non-trivial matching; ranks by buyer intent | ✅ Accepted |
| 2026-06-14 | **Pair Rescue promoted T3 → T2** | Most genuinely circular flow; memorable 20s; bipartite match, seedable in ~3h | ✅ Accepted |
| 2026-06-14 | **Seller-side return-signal aggregation** | Reactive → proactive ("fix your photos"); infrastructure framing | ✅ Accepted |
| 2026-06-14 | **Rescue decay pricing** (TTL → discount) | Recovery-value optimization; price-clock demo visual; one Go formula | ✅ Accepted |
| 2026-06-14 | **Build order: backend-first, UI last** | Schema → endpoints → flow → wire logic → UI; frontend wired only once backend is ready | ✅ Accepted |
| 2026-06-14 | **Track B — Second Life (resell + republish)** as 2nd marketplace surface | Closes the circular loop on the buyer side; reuses passport/ledger/pricer; two lanes (buyer resell `p2p` + seller republish `certified`) → one catalogue | ✅ Accepted |
| 2026-06-14 | New relay-ml **`POST /grade-and-price`** — resale grade + price **RANGE** | Resale needs a different grading lens + a trustworthy price; return a range and list the mean (absolute price is over-confident/harsh); Bhavya owns the algorithm inside the range | ✅ Accepted |
| 2026-06-14 | **Unified pricing** across rescue + resale; **`price_fit`** matching flag | One pricer, two surfaces — rescue `list_price` = mean(range); surface price-matched wishes in Genie/reverse-wishlist | ✅ Accepted |
| 2026-06-14 | **Resell gated on expired return window**; **payments STUBBED** | Honest demo without real payments; reuses rescue "claim locally" pattern (escrow none→held→released, ownership transfer, `P2P_SOLD` ledger); `return_window_days`=7 | ✅ Accepted |
| 2026-06-14 | **All-real seeding** via `seed_assets/` + canonical `/demo/reset` | Real DB + LifeLedger data only (no client mocks); populated buyer + seller personas; remove stale reset cruft + hardcoded mock fallbacks | ✅ Accepted |

---

## 12. Progress Log

| Date | Done | Not done |
|---|---|---|
| 2026-06-13 | Session 1 brainstorm; industry + research scan; context.md created | Implementation |
| 2026-06-13 | Session 2: locked name, categories, Rescue+P2P, blockchain, web; P2P/VTO/blockchain explained | Tech stack; wireframes; API schema |
| 2026-06-13 | Session 3: MVP features locked, risk audit, HackOn winner research, approach validated | Tech stack; implementation |
| 2026-06-13 | Session 4: tech stack locked, HLD, datasets, demo UI, Lego tiers; pre-plan.md | plan.md; repo init |
| 2026-06-13 | Session 5: **`plan.md` created** — full technical plan for Shikher + Bhavya + agents | GitHub repos; implementation |
| 2026-06-14 | 5 repos initialized + pushed; contracts v1 (schemas + OpenAPI) merged; relay-dev compose | Shikher T1 implementation |
| 2026-06-14 | Bhavya relay-ml T0 done (FastAPI skeleton, /health, fit-flags rules, dataset tooling) — reviewed | Passport contract align; CNN/Bedrock grading |
| 2026-06-14 | Session 6: plan updated — bracketing P0, ops persona, carbon constants, pgvector T1, Bedrock-only grading | Build T1 |
| 2026-06-14 | Session 6b: + demand-weighted disposition, wish-score (Bhavya), Pair Rescue (T2), seller signals, rescue decay pricing; bracketing ≥3; embeddings → Bhavya | Build T1 |
| 2026-06-14 | Session 7: **Track B (Second Life) specced** in plan.md §19 — `grade-and-price` contract, `resale_listings`/orders data model, all-real `seed_assets/` seeding, seller/buyer UX; ML(Bedrock)+backend+frontend+seeding flipped to done on task board | Deploy (AWS/Railway/CI) + demo video + submission |
| 2026-06-15 | Session 8: **Track C — Return-grading decisions built** (plan.md §20): size/fit return = pristine asset (Grade-A boost + minimal-discount Path-A listing); next-owner size-match gate (size eq OR fit confidence > 0.7); cheap prompt-only expected-context `verification` (additive `expected_size/color/title` → locked `verification` block on ConditionPassport + ResaleListing, **relay-ml prompt change flagged for Bhavya**, relay-api fallback); `wrong_item` fully gated (flagged return-to-seller, no grade/anchor/listing) + pick-pack seller signal; in-window `POST /orders/items/{id}/exchange` (no ML grade, replacement line + pristine returned unit → Path-A rescue + `EXCHANGED`). Additive migration 0005; seed + smoke extended → SMOKE_OK | Deploy (AWS/Railway/CI) + demo video + submission |

---

## 13. Session 1 Takeaways (for both teammates)

1. **You're not wrong about auto-matching** — it's real, but it's **disposition routing + next-owner matching**, not Amazon-style "customers who bought X."
2. **Zomato Food Rescue is gold** — adapt to physical goods as **Return Rescue** for hyperlocal second life.
3. **P2P in the brief** means consumer-to-consumer resale **with Amazon trust** — the gap Amazon hasn't filled natively.
4. **Return prediction is saturated** — win on **fit insights + exchange routing + Rescue matching + Condition Passport**.
5. **Bedrock story** = tiered pipeline + confidence gating + batch; Bhavya's CNN handles the 80% case cheaply.
6. **Gamification** = trust artifacts + verified impact, not leaderboards that drive overconsumption.

---

## 14. Next Session Agenda

1. Finalize product name (Relay vs shortlist in §15)
2. MVP screen flow wireframes (dual vertical: fashion path + electronics path)
3. Tech stack decision (FastAPI vs Node, Next vs plain React, blockchain layer)
4. Bhavya: dataset sources + model architecture sign-off
5. Shikher: API schema + DB schema v1 + LifeLedger smart contract design
6. Demo script (judge walkthrough: prevention → return → grade → Rescue claim → P2P list)

---

## 15. Product Naming (Session 2)

**Working title: Relay**

Why Relay works:
- **Verb + noun** — you relay an item to its next owner (matching + handoff)
- Covers Rescue (instant relay nearby) and P2P (relay to matched buyer)
- Sounds like infrastructure, not a coupon app
- Tagline-ready: *"Relay — every product finds its next owner"*

**Shortlist if Relay feels off:**

| Name | Vibe | Risk |
|---|---|---|
| **Relay** | Routing, handoff, system | Could echo Amazon Relay ( trucking ) — check branding |
| **Handoff** | P2P trust, explicit transfer | Very consumer; less "AI engine" |
| **LifeLedger** | Blockchain + lifecycle | Strong for passport story; weaker for Rescue |
| **ReRoute** | Reverse logistics literal | Slightly logistics-boring |
| **Kinship** | Item finds its person | Emotional; less tech |
| **Arc** | Circular, minimal | Maybe too abstract |
| **StillGood** | Trust in refurbished | Great UX copy; weak as platform name |

**Recommendation:** **Relay** for platform; **LifeLedger** as the blockchain sub-brand (*"Every unit gets a LifeLedger entry"*).

---

## 16. Blockchain — LifeLedger (how it works, why it's real)

### What problem blockchain actually solves here

Without blockchain, a seller can Photoshop condition photos or edit grade history. A Condition Passport stored only in your Postgres DB is **trust-me bro**.

Blockchain gives you:
- **Tamper-proof audit trail** — each grade, ownership transfer, and disposition event is hashed and chained
- **Portable trust** — buyer verifies passport on-chain without trusting your server alone
- **Regulatory alignment** — EU **Digital Product Passport (DPP)** under ESPR (textiles mandatory from 2026); Bain/eBay report: DPP can **double lifetime value** of fashion items via resale trust

This is NOT "put everything on chain." It's **hash anchoring + event log**.

### Architecture (practical, not crypto hype)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ AI grades item  │────▶│ Condition        │────▶│ LifeLedger (chain)  │
│ (Bhavya +       │     │ Passport JSON    │     │ stores:             │
│  Bedrock)       │     │ in S3/DB         │     │ · passport_hash     │
└─────────────────┘     └──────────────────┘     │ · grade + timestamp │
                                                  │ · grader_signature  │
                                                  │ · disposition       │
                                                  │ · owner_transfer    │
                                                  └─────────────────────┘
```

**What goes ON chain (small):**
- `passport_hash` — SHA-256 of full Condition Passport JSON
- Event type: `GRADED` | `RESCUED` | `P2P_LISTED` | `P2P_SOLD` | `DONATED` | `RECYCLED`
- `unit_id`, timestamp, actor (Amazon system / seller wallet id)
- Previous event hash (chain linkage)

**What stays OFF chain (big):**
- Images, video keyframes, full defect JSON → S3/IPFS optional
- Buyer PII, payment details

**Verification flow for buyer:**
1. Scan QR on listing → fetch passport from API
2. Recompute hash → compare to on-chain `passport_hash`
3. View event timeline: *Graded B+ on June 13 → Listed P2P June 14 → No edits*

### Tech choices (for Shikher)

| Option | Pros | Cons |
|---|---|---|
| **Amazon Managed Blockchain** (Hyperledger Fabric) | AWS-native, enterprise story | Heavier setup |
| **Polygon / Base L2** | Cheap txs, fast demo, public verify | Less "Amazon" |
| **Simple anchoring** (OpenTimestamps-style + your DB) | Minimal | Weaker "blockchain" demo |

**Hackathon → production path:** Start with **Polygon Amoy testnet** or **Hyperledger on AWS**; same ABI/logic either way.

**Oracle problem (who writes truth?):** Only your **grading service** (signed by backend key) can write `GRADED` events. Sellers cannot self-upgrade grade. Disputes create new `REGRADE_REQUESTED` event, not overwrite.

### Bhavya's role
- Grading output includes `passport_hash` field
- No direct chain interaction needed — Shikher's backend submits after grade

---

## 17. Amazon & Virtual Try-On (VTO)

### What Amazon HAS done
- **AR try-on for shoes and eyewear** in the mobile app (structured geometry — easier problem)
- **Personal Shopper / StyleSnap** — photo search, not fit prediction
- **Try Before You Buy** (clothing) — **shut down in 2025** (expensive, logistics-heavy)
- **AWS Nova Canvas** advertises virtual try-on as a *use case* — but **Amazon.com has NOT rolled out clothing VTO at catalog scale**

### Why Amazon hasn't scaled clothing VTO

| Barrier | Detail |
|---|---|
| **Fit ≠ look** | Industry reviews: VTO tools score ~1/5 on *dimensional fit*; they look okay but don't predict shoulder seam, drape, waist |
| **SKU explosion** | Millions of fashion SKUs, seasonal turnover — 3D asset pipeline doesn't scale |
| **Body diversity** | AI defaults to narrow body types → trust breaks → *more* returns |
| **Brand liability** | Wrong visual expectation = returns + complaints |
| **Cheaper alternative** | Size recommendation (True Fit style) + kill Try Before You Buy |

**Strategic insight for Relay:** Don't compete on **virtual try-on visuals**. Compete on **Fit Intelligence** (SizeFlags-style article flags + user fit profile + exchange-first). Position as: *"Amazon doesn't need a fake mirror — it needs a fit oracle."* Relay's prevention layer IS the pragmatic Amazon-scale answer VTO failed to be.

Optional stretch: Bedrock/Nova **styling** try-on as inspiration-only (with disclaimer) — not as core.

---

## 18. P2P Explained Simply

### The confusion
> "When I buy on Amazon from a third-party seller, isn't that already P2P?"

**Almost — but not what the problem statement means.**

### Analogy: Apartment marketplace

| Model | Real-world analog | Amazon equivalent |
|---|---|---|
| **Landlord model** | Professional property company rents units | **Amazon Retail** — Amazon owns inventory |
| **Marketplace model** | Small businesses list on platform | **Amazon Marketplace** — shops/brands/resellers list *new* inventory at scale |
| **Garage sale model** | You sell your own used couch to a neighbor | **What the brief wants** — *your* returned phone / *your* jacket, one item, zero business setup |

### Amazon today when YOU want to sell YOUR stuff

| Path | Effort | Trust | Problem |
|---|---|---|---|
| List as "Used" on Marketplace | High — you are a "seller", listing hell, pricing guess | Low — buyer scared | No AI grade, no passport, feels like eBay buried in Amazon |
| Trade-In | Low | High | Amazon keeps item — you get gift card, not cash; not peer sale |
| Renewed / Resale | N/A | High | Amazon or pro refurbisher sells — not you |
| **Relay P2P (our vision)** | **One-click from return flow** | **High — LifeLedger passport** | **You sell to another customer; Amazon escrow + shipping** |

### One sentence
**Amazon Marketplace = businesses selling inventory. Relay P2P = ordinary customers flipping *their specific returned unit* to another customer with verified AI grading and chain-of-custody.**

Ciclo (competitor) literally routes fit-complaint returns to **"Peer-to-Peer Resale"** as a disposition channel — industry validates this gap.

---

## 19. Off-Angle Ideas (Session 2 — don't miss these)

High-impact additions not fully explored in Session 1:

| # | Idea | Why it's killer |
|---|---|---|
| 1 | **Reverse Wishlist** | Buyers post "I want Size M navy hoodie under ₹800" *before* returns exist → return flow matches to waiting demand (demand-led, not supply-led) |
| 2 | **Pre-pickup Rescue** | Claim triggers *before* return reaches warehouse — max carbon save (Zomato timing) |
| 3 | **Exchange-first auto-route** | Return reason = "too small" → skip warehouse, offer instant exchange SKU (Myntra nudge + AI) |
| 4 | **Pair Rescue** | "Someone returned the left shoe M9 — you have the right" (long-tail inventory magic) |
| 5 | **Embodied carbon on LifeLedger** | Each event shows CO₂ saved vs new purchase — Impact Wallet fuel |
| 6 | **Grade dispute jury** | Buyer disputes B+ grade → secondary AI re-grade + human optional — trust moat |
| 7 | **Warranty chain (electronics)** | Passport carries remaining warranty + repair history — huge for refurbished trust |
| 8 | **Bracketing interceptor** | Cart has S/M/L same item → UI blocks with fit profile suggestion |
| 9 | **Donation match** | Low-value fashion → NGO need list by size (geo + category) |
| 10 | **Relay as Try-Before-You-Buy replacement** | Amazon killed TBYB — Relay prevention + exchange IS the scalable substitute |

**Top 3 to add to MVP demo:**
1. **Reverse Wishlist** (shows intelligence, not just routing) ✅ LOCKED
2. **Exchange-first auto-route** (fashion) ✅ LOCKED
3. **Warranty chain on LifeLedger** (electronics) ✅ LOCKED

**Session 6b — promoted/added to the build (see plan.md §7):**
- **Pair Rescue** (#4 above) → **T2**, was T3. Bipartite A↔B swap, the most circular flow in the system.
- **Demand-weighted disposition** — Reverse Wishlist bids become an *input* to routing, not just a post-match alert.
- **Wish confidence scoring** — rank matches by buyer intent (Bhavya logreg).
- **Seller-side return-signal aggregation** — "this SKU has 34% returns, reason: color mismatch → fix photos." Reactive → proactive.
- **Rescue decay pricing** — discount rises as TTL drops; countdown becomes a price clock.

---

## 21. Risk Audit — Cons, Failure Modes & Guardrails

> Every feature has downsides. Judges respect teams who acknowledge tradeoffs and engineer around them. This is a competitive advantage over "generic AI garbage."

### 21.1 Return Rescue / Pre-pickup Rescue — THE RETURN CHAIN PROBLEM

**Con (your insight is correct):** Rescue buyer re-returns → item ping-pongs → **more legs than warehouse path** → worse carbon, not better. Yale 2025 + Nature 2025: secondhand can expand footprint via rebound and displacement failure.

**Failure modes:**
- Serial rescuers treating Rescue as "try before you buy free"
- Wrong-size rescue of fashion → guaranteed second return
- Discount hunting without intent to keep
- **Relay chain:** A → B → C → D with 4 delivery emissions

**Guardrails (build these into product, mention in pitch):**

| Guardrail | Rule |
|---|---|
| **Rescue eligibility score** | Block users with return rate > threshold; require Fit Profile for fashion |
| **One active Rescue per user** | Can't claim another until current Rescue is kept 14 days or purchased |
| **Chain depth cap** | LifeLedger `transfer_count ≥ 3` → force refurb, donate, or recycle (no more Rescue/P2P) |
| **Net carbon gate** | Only show Rescue if `saved_warehouse_leg > delivery_to_new_buyer` (geo + routing math) |
| **Category blocklist** | Intimate apparel, personalized items — no Rescue |
| **Match quality threshold** | Fashion Rescue only if Reverse Wishlist size match OR fit profile ≥ confidence |
| **Keep-it credit** | Green credits **only after 14-day keep**, not at claim — reduces try-and-return |

**Pitch line:** *"We don't optimize for resales. We optimize for **final placement** — Rescue is blocked when it would create a return chain."*

---

### 21.2 Reverse Wishlist

**Cons:**
- Cold start — no wishes, no matches
- Privacy — buyers reveal intent
- Gaming — fake wishes to block competitors

**Guardrails:** Seed demo with synthetic wishes; expire wishes after 30 days; one wish per SKU variant per user.

---

### 21.3 Exchange-first

**Cons:**
- Inventory sync complexity (exchange SKU OOS)
- Seller/franchise cost absorption
- Can still fail if user wrong twice

**Guardrails:** Only trigger when exchange SKU in stock within 50km FC; cap 1 exchange per order; fall back to Rescue/P2P after failed exchange.

---

### 21.4 P2P Resale

**Cons:**
- Fraud (misgraded items) despite passport
- Race to bottom pricing
- **Moral licensing** — "I sold used, now I buy new" (Yale rebound research)
- Listing friction still too high if not truly one-click

**Guardrails:** Escrow until delivery confirm; LifeLedger regrade on dispute; price floor from AI; green credits for **net lifecycle extension** not listing volume.

---

### 21.5 LifeLedger / Blockchain

**Cons:**
- Over-engineering for hackathon if chain breaks during demo
- Gas costs, wallet UX friction
- "Blockchain for blockchain's sake" skepticism from judges
- Oracle trust — who writes grade truth?

**Guardrails:** Testnet + fallback cached verify; backend-signed events only; pitch EU DPP alignment; demo QR verify live.

---

### 21.6 Fit Intelligence / Prevention

**Cons:**
- Wrong advice → liability feel
- Needs history — cold start for new users
- Users ignore nudges

**Guardrails:** Article-level flags (SizeFlags) work without personal data; show confidence %; always offer exchange path not just warning.

---

### 21.7 Green Credits / Gamification

**Cons:**
- **Rebound effect** — credits for buying renewed/rescued → user buys MORE new stuff (documented 1:1.23 substitution failure in secondhand clothing research)
- Greenwashing if credits aren't tied to verified outcomes

**Guardrails:** Credits for **kept** rescues, exchanges (avoiding return trip), and **net CO₂ reduction** — never for purchase volume. Show Impact Wallet as *reduction vs baseline*, not badges for consumption.

**Decision (Session 6i) — credits buy ACCESS, not discounts.** Redeeming credits as a discount is cashback with a green skin (a tired 2019 loyalty trope, and it feeds the rebound effect above). Instead, lifetime credits define a **participation tier**: clearing the threshold unlocks **early access to the Rescue feed** (a ~10-min embargo window before listings go public). Circular (rescue → credits → better access to rescue more), scarce (a real head start on decay-priced listings), and near-zero cost (a feed filter). Keep the 2.4 kg CO₂ number + locked/spendable balance; only the *spend* changed. This avoids the rebound effect entirely — the reward is deeper participation in the loop, not consumption. Spec: plan.md §7 "Impact Wallet — credits buy ACCESS".

**Concrete carbon numbers (locked for demo, see plan.md §7):** anchor to ~**15M metric tons CO₂** from US returns/yr (Optoro / reverse-logistics research). Per-channel saved (kg CO₂e): rescue **2.4**, exchange 1.8, p2p 3.1, refurb 2.0, donate 1.5, recycle 0.6. Net formula subtracts `delivery_km × 0.12`. These are hard-coded, shown on the passport/Impact Wallet, and power the Rescue net-carbon gate (only show rescue when net > 0).

---

### 21.8 Warranty Chain (Electronics)

**Cons:**
- OEM may not honor transferred warranty
- Refurbished warranty ≠ original
- Complex legal per brand

**Guardrails:** Track *remaining Amazon/Renewed warranty period* + repair events on LifeLedger; label as "Amazon-backed coverage" not manufacturer; demo with simulated warranty data.

---

### 21.9 Tiered Bedrock Grading

**Cons:**
- Inconsistent grades across models
- Latency at scale
- Cost if tier gating fails open

**Guardrails:** Confidence threshold gates escalation; Bhavya CNN as cheap default; batch for backlog.

---

### 21.10 Dual Vertical (Fashion + Electronics)

**Cons:**
- 48-hour scope explosion
- Demo confusion if two full flows

**Guardrails:** One unified dashboard; demo script picks **one primary path live** (fashion Rescue) + **60-second electronics P2P+warranty screen**; same backend, different disposition rules.

---

## 22. HackOn Winner Research — Are We on the Right Track?

### 22.1 What HackOn actually is (Season 4–6)

| Season | Scale | Format |
|---|---|---|
| S4 | 38,000+ registrations, 110+ ideas, 60+ prototypes | Multi-round: coding → idea → prototype → mentorship → finale |
| S5 | Similar; 4 themes in idea round | Sustainable Shopping, Trust & Safety, Fire TV, Smart Payments |
| S6 (2026) | PPI + ₹2.25L prizes | **48-hour build** after kickoff PS reveal; submission = code + video + PPT |

**Judges:** AWS, Alexa, Amazon Pay, Amazon leaders. They evaluate **problem fit, working prototype, scale story, AWS usage, GenAI depth, submission quality.**

---

### 22.2 Documented winners & strong submissions

| Team / Project | Season / Event | Problem theme | What they did | Why it stood out |
|---|---|---|---|---|
| **Want2Win** (MIT Manipal) | S4 🥇 | Fraud Detection & Prevention | Counterfeit detection across **full product lifecycle** | Narrow PS, end-to-end trust, lifecycle framing — mirrors our approach |
| **IIIT Bangalore** | S4 🥈 | (Finale theme TBD) | Finalist — strong prototype | Execution quality |
| **BITS Pilani** | S4 🥉 | (Finale theme TBD) | Finalist | — |
| **GreenCart** | S5 participant (claims sustainability track) | Sustainable Shopping | EarthScore ratings, DBSCAN group buying, carbon gamification, Gemini chatbot | Hits same theme — **we must differentiate from this** |
| **S4 finale themes** | — | Fraud, Payments, Visual AI | Top 9 presented across 3 tracks | Winners pick **one PS deeply**, not all three |

**S5 winner project names** are not fully public; podcast confirms Alexa-adjacent winning team focused on **shipping a working project** after nearly dropping out.

---

### 22.3 What judges reward (Devpost, corporate hackathon research)

1. **Problem fit** — solution maps clearly to the PS, not shoehorned
2. **Working demo** — 3 features that work > 10 half-broken
3. **GenAI is core** — not a chatbot wrapper; AI drives the value
4. **AWS ecosystem** — Bedrock, Lambda, S3 used with purpose
5. **Scale narrative** — "designed for 10M users," architecture thinking
6. **Clean submission** — README, <3 min video showing product not slides, crisp PPT
7. **Differentiation** — fresh angle on the problem
8. **Commercial reasoning** — 2026 trend: business case beats polish alone
9. **Mentorship feedback** — top teams iterate after Amazon engineer review

---

### 22.4 Our approach vs winners — honest assessment

#### ✅ Where we're STRONG (right track)

| Our choice | Why it aligns with winners |
|---|---|
| **Lifecycle / routing engine** (like Want2Win's lifecycle fraud) | End-to-end story, not a single ML trick |
| **Trust + verification** (LifeLedger, Condition Passport) | S4/S5 both had trust/safety themes |
| **Tiered Bedrock + CNN** | GenAI core to value, engineering discipline |
| **Reverse Wishlist + Rescue** | Genuinely novel — not another EarthScore clone |
| **Risk awareness** (return chains, rebound) | Maturity signal — most teams won't mention this |
| **Dual vertical with shared engine** | Platform thinking, Amazon scale language |
| **EU DPP / blockchain** | Regulatory tailwind, real beyond hackathon |

#### ⚠️ Where we're AT RISK

| Risk | Mitigation |
|---|---|
| **Too many features for 48h** | Demo 1.5 flows max; backend stubs OK if demo path works |
| **GreenCart overlap** (sustainability + gamification) | Lead pitch with **routing + matching**, not green points |
| **Generic "AI returns"** | Never say "predict returns" — say "final placement" |
| **Blockchain demo failure** | Testnet + offline verify fallback |
| **Complex ML pipeline** | Bhavya CNN + Bedrock Lite for demo; defer full tier system |

#### Verdict: **Yes, we're on the right track** — closer to **Want2Win (lifecycle + trust)** than **GreenCart (gamified green shopping)**. The differentiation is **Reverse Logistics Routing + LifeLedger**, not sustainability ratings.

---

### 22.5 What would make us stand out vs other PS#2 submissions

Most teams will build: return predictor + green badges + refurb recommender.

**We should pitch as:**
> *"Relay is Amazon's disposition brain — every returned unit gets a Condition Passport on LifeLedger, routes to exchange, rescue, or P2P, and matches to a Reverse Wishlist buyer. We measure **net carbon**, block return chains, and replace Try-Before-You-Buy with Fit Intelligence."*

That's a **different category** from GreenCart-style eco-shopping.

---

## 23. Finalized MVP Scope (Pre–Tech Stack)

### Platform
- **Name:** Relay (platform) + LifeLedger (blockchain layer)
- **UI:** Web-first responsive
- **Categories:** Fashion + Electronics (shared engine, different rules)

### Core features (IN)

| # | Feature | Demo priority |
|---|---|---|
| 1 | Fit Intelligence + checkout insight | P0 — fashion prevention |
| 2 | **Bracketing interceptor** (≥3 sizes same item at checkout, strict) | P0 — most citable prevention (~40% returns) |
| 3 | Return intake + photo/video grade → Condition Passport (CNN or `bedrock_only`) | P0 |
| 4 | Disposition engine (exchange / rescue / P2P / refurb / donate) | P0 |
| 5 | **Return Rescue** (geo + TTL + guardrails) | P0 — hero demo moment |
| 6 | **Reverse Wishlist** → pgvector match alert | P0 |
| 7 | **Exchange-first** routing (fashion) | P0 |
| 8 | **Ops/seller dashboard** (flagged SKUs + rescue TTL + chain depth) | P1 — 2nd persona |
| 9 | **P2P one-click list** + escrow flow | P1 — second demo tab |
| 10 | **Warranty chain** on LifeLedger (electronics) | P1 |
| 11 | LifeLedger on-chain verify (QR) | P1 |
| 12 | Green credits (keep-based, not volume) | P2 — supporting |
| 13 | Impact Wallet (net CO₂, hard-coded constants) | P2 |

### Build philosophy: Iterative Lego (NOT permanent exclusions)

Features previously labeled "out of scope" are **Phase 2/3 add-ons** — stacked on a working core. If a layer fails, lower tiers still demo.

| Tier | When | What ships | If it breaks… |
|---|---|---|---|
| **T0 — Shell** | Hours 0–12 | Next UI, auth stub, browse/return flows, mock grade API | Still have navigable product |
| **T1 — Core** | Hours 12–30 | Real CNN+Bedrock grade, rule-based disposition, Rescue feed, exchange-first | Full fashion demo path works |
| **T2 — Differentiators** | Hours 30–42 | Reverse Wishlist match, demand-weighted disposition, Pair Rescue, rescue decay pricing, seller signals/ops, P2P list, LifeLedger QR verify, warranty chain | T1 demo unchanged |
| **T3 — Stretch** | Hours 42–48+ | RL optimizer hook, donation routing, return-reason NLP clustering, ClickHouse analytics | Ignore for pitch; T2 is the win |

**Previously "out of scope" → now phased:**

| Feature | Tier | Notes |
|---|---|---|
| Full RL disposition optimizer | T3 | Start with rule engine + weights; swap in RL later via same interface |
| Live Amazon APIs | Never in hackathon | Seed data + "integration-ready" adapter pattern |
| Mobile native app | Post-hackathon | Web responsive covers demo |
| Pair Rescue | **T2** (Session 6b) | Bipartite A↔B swap; extends Reverse Wishlist matching |
| Donation routing | T3 | Disposition enum already includes `DONATE` |
| Full SizeFlags model | T1 stub → T2+ | Rules + ModCloth data first; ML flags second |

**Agentic AI accelerates T2/T3** — but T1 must work without it.

### Demo script (3 min video)

1. **0:00–0:30** — Problem: returns cost + trust gap; rebound/chain awareness (10 sec)
2. **0:30–1:30** — Fashion: fit insight → return → grade → exchange OR rescue with wishlist match
3. **1:30–2:15** — Rescue guardrails flash (eligibility, chain cap) — show we're not naive
4. **2:15–2:45** — Electronics: P2P list + warranty on LifeLedger + QR verify
5. **2:45–3:00** — Scale + AWS architecture teaser

---

## 24. Tech Stack — LOCKED (Session 4)

### Language constraint
**Python + Go only.** No Java, no Node.js backend.

### Stack summary

| Layer | Choice | Owner | Why |
|---|---|---|---|
| **Frontend** | Next.js 14 (App Router) + TypeScript + Zustand + shadcn/ui + Tailwind | Shikher | Fast polish; winner projects (GreenCart, Odyssey) ship real UIs |
| **Primary API** | **FastAPI** (Python) | Shikher | ML integration, Celery, Bedrock SDK, rapid iteration |
| **Relay Engine** | **Go** service (chi/fiber) | Shikher | Disposition scoring, geo Rescue TTL, matching — performance + scale story |
| **ML service** | FastAPI (Python) — Bhavya's models | Bhavya | `/grade`, `/grade-video`, `/fit-flags` |
| **Workers** | **Celery** + Redis broker | Shikher | Grading jobs, wishlist match, LifeLedger writes, Rescue expiry |
| **Queue** | **AWS SQS** (prod path) + Redis (dev/local) | Shikher | SQS integrates free tier; Redis for local Lego builds |
| **Primary DB** | **PostgreSQL** (RDS or Railway) | Shikher | ACID, JSONB for passports, relational orders |
| **Vector search** | **pgvector** extension on Postgres | Shikher | P2P / wishlist similarity without extra service |
| **Cache / TTL** | **Redis** (ElastiCache or Railway Redis) | Shikher | Rescue TTL, session, rate limits |
| **Object storage** | **AWS S3** | Both | Grade images, demo assets, static frontend backup |
| **Blockchain** | **Polygon Amoy testnet** + simple Solidity event log | Shikher | LifeLedger; Railway fallback uses cached verify |
| **AI — primary** | **Amazon Bedrock** (Nova Lite/Pro, Claude Haiku) | Bhavya | Hackathon alignment; $200 AWS credits |
| **AI — fallback** | **OpenAI API** (both have keys) | Bhavya | Tier escalation, fit flags prose, dev fallback |
| **AI — optional** | **Gemini API** (if paid key acquired) | Bhavya | A/B on grading cost |
| **Deploy primary** | **AWS** (see HLD §25) | Shikher | Free tier credits |
| **Deploy backup** | **Railway** (full stack) | Shikher | Pre-recorded demo video safety net |
| **Source control** | **GitHub multi-repo** (see §24.1) | Both | Parallel ownership; shared contracts |

### Deferred (scale path, not 48h requirement)
- Kafka / RabbitMQ → SQS is enough; Kafka in HLD diagram as scale path
- MongoDB → Postgres JSONB covers document needs
- Cassandra / DynamoDB → mention in HLD for Rescue feed at 10M scale
- ClickHouse → T3 analytics; not blocking demo
- Kubernetes / EKS → scale story in HLD; **ship on ECS Fargate or Railway first**

### Repo strategy — multi-repo (LOCKED)

**Decision:** Split repos for parallel work. **Not a single monorepo.**

Bhavya should rarely touch Go or frontend. Shikher integrates Bhavya's work via **HTTP contract only**.

#### Recommended: 4 repos (+ 1 contracts)

| Repo | Primary owner | Contents | Bhavya touches? |
|---|---|---|---|
| **`relay-web`** | Shikher | Next.js + Zustand + shadcn | No |
| **`relay-engine`** | Shikher | Go — disposition, matching, Rescue TTL | No |
| **`relay-api`** | Shikher | FastAPI BFF, Celery workers, seed scripts, LifeLedger client, DB migrations | Rarely (integration PRs only) |
| **`relay-ml`** | **Bhavya** | ML FastAPI, training notebooks, models, Bedrock prompts, datasets | **Yes — full ownership** |
| **`relay-contracts`** | Both (PR review) | OpenAPI specs, shared JSON schemas (Condition Passport), env examples | Both read; small PRs |

**GitHub setup:** One org or Shikher's account with Bhavya as collaborator on all repos. Same for Railway/AWS deploy secrets per repo.

#### Why 4 repos beats 3 (python lumped together)

If Go + Python + ML live in one "backend" repo:
- Bhavya and Shikher both commit to same repo → merge noise, shared CI failures
- Bhavya's `torch`/heavy deps slow Shikher's API docker builds

**`relay-ml` isolated** = Bhavya ships Docker image with GPU/heavy deps; Shikher's `relay-api` stays lean.

#### Alternative: 3 repos (acceptable if 4 feels heavy)

| Repo | Owner | Note |
|---|---|---|
| `relay-web` | Shikher | Frontend |
| `relay-engine` | Shikher | Go |
| `relay-python` | Split by folder + **CODEOWNERS** | `ml-service/` → Bhavya; `api/` + `workers/` → Shikher |

Use only if you refuse a 4th repo — add `.github/CODEOWNERS`:
```
/ml-service/     @bhavya
/training/       @bhavya
/api/            @shikher
/workers/        @shikher
```

**Verdict: prefer 4 repos** for zero-conflict parallel work in 48h.

#### Integration boundary (how repos talk)

```
relay-web  ──HTTP──►  relay-api  ──HTTP──►  relay-ml
                           │
                           ├──HTTP──►  relay-engine (Go)
                           └──Celery──►  workers (in relay-api repo)
```

**Contract-first workflow:**
1. Define `ConditionPassport`, `/grade`, `/fit-flags` in **`relay-contracts`** (OpenAPI YAML)
2. Bhavya implements against spec in `relay-ml`
3. Shikher mocks `relay-ml` in `relay-api` until Bhavya deploys
4. Neither needs the other's repo checked out for daily work

#### Parallel work map

| Shikher (simultaneous) | Bhavya (simultaneous) |
|---|---|
| `relay-web` — UI shells, Rescue feed | `relay-ml` — dataset download, CNN train |
| `relay-api` — auth, returns, seed data | `relay-ml` — Bedrock tier prompts |
| `relay-engine` — disposition rules | `relay-ml` — `/grade` endpoint |
| `relay-api` — Celery + LifeLedger | `relay-ml` — `/fit-flags` stub |
| Integration: wire API → ML URL env var | Publish Docker image / Railway service URL |

**Zero file-level conflicts** if boundaries respected.

#### Local dev orchestration

**Option A — `relay-dev` meta repo (thin, optional):**
```
relay-dev/
├── docker-compose.yml    # pulls images / builds from sibling dirs
├── .env.example
└── README.md             # clone all 4 repos sibling folders
```

**Option B — docker-compose lives in `relay-api`** referencing sibling paths:
```yaml
services:
  ml:
    build: ../relay-ml
  engine:
    build: ../relay-engine
  web:
    build: ../relay-web
```

Clone layout on each machine:
```
~/relay/
├── relay-web/
├── relay-engine/
├── relay-api/
├── relay-ml/
├── relay-contracts/
└── relay-dev/          # optional compose only
```

#### CI per repo (minimal 48h)

| Repo | CI |
|---|---|
| relay-web | `npm run build` |
| relay-engine | `go test ./...` |
| relay-api | `pytest` + docker build |
| relay-ml | `pytest` + model smoke test |
| relay-contracts | validate OpenAPI |

#### What lives where (no ambiguity)

| Concern | Repo |
|---|---|
| Condition Passport JSON schema | relay-contracts |
| Grading CNN weights | relay-ml (`/models`) |
| Bedrock orchestration in workers | relay-api (calls relay-ml) OR relay-ml (Bhavya owns all ML paths) |
| Postgres migrations | relay-api |
| Seed/demo data scripts | relay-api |
| LifeLedger Solidity | relay-api `/contracts` or relay-contracts |
| Frontend env `NEXT_PUBLIC_API_URL` | relay-web |

**Rule:** If it touches tensors, Bedrock prompts, or training data → **`relay-ml`**. Everything else Shikher's repos.

### Inter-service contract
- Frontend → Python API (REST)
- Python API → Go Relay Engine (gRPC or REST)
- Python API → Bhavya ML service (REST)
- Python API → Celery → SQS/Redis → workers → Bedrock / S3 / LifeLedger

---

## 25. High-Level Design (HLD)

### Architecture diagram (logical)

```
                    ┌─────────────────────────────────────┐
                    │         Next.js (Relay UI)          │
                    │   Zustand · shadcn · demo + live    │
                    └─────────────────┬───────────────────┘
                                      │ HTTPS
                    ┌─────────────────▼───────────────────┐
                    │     FastAPI Gateway (Python)        │
                    │  auth · orders · returns · credits  │
                    └─┬─────────┬──────────┬──────────────┘
                      │         │          │
         ┌────────────▼──┐  ┌───▼────┐  ┌──▼─────────────┐
         │ Go Relay      │  │ ML Svc │  │ Celery Workers │
         │ Engine        │  │ (Py)   │  │ (Python)       │
         │ disposition   │  │ grade  │  │ grade jobs     │
         │ match · rescue│  │ fit    │  │ ledger · TTL   │
         └───────┬───────┘  └───┬────┘  └──┬─────────────┘
                 │              │           │
    ┌────────────▼──────────────▼───────────▼────────────┐
    │ PostgreSQL (+ pgvector) │ Redis │ S3 │ SQS         │
    └─────────────────────────┬──────────────────────────┘
                              │
              ┌───────────────▼───────────────┐
              │ Bedrock │ OpenAI │ LifeLedger │
              │ (AI)    │ (fallback) │ (chain)│
              └───────────────────────────────┘
```

### AWS deployment (primary)

| Component | 48h choice | Scale path (pitch) |
|---|---|---|
| Frontend | S3 + CloudFront **or** Vercel → S3 fallback | CloudFront global |
| API | **ECS Fargate** (Docker) | EKS when >N pods |
| Go engine | ECS Fargate sidecar or separate service | Horizontal pod autoscaler |
| ML service | ECS Fargate (GPU optional later) | SageMaker endpoint |
| Workers | ECS Fargate + Celery | Lambda for event triggers + SQS |
| DB | **RDS PostgreSQL** | Read replicas |
| Cache | ElastiCache Redis | Cluster mode |
| Queue | SQS | Kafka at enterprise scale |
| AI | Bedrock (on-demand + batch) | Provisioned throughput |
| IaC | Docker Compose local → minimal CDK/Terraform | Full CDK |

**Lambda note:** Use for **LifeLedger webhook**, **Rescue TTL expiry**, **S3 grade upload trigger** — good "we use Lambda" story without rewriting core in Lambda.

### Railway deployment (backup)
- Single `docker-compose.railway.yml`: web + api + go-engine + ml + worker + postgres + redis
- Pre-seed demo data on deploy
- Record demo video from Railway URL if AWS fails mid-finale

### Scale talking points (for judges)
- Go engine: sub-ms disposition for 10K returns/min (theoretical)
- SQS decouples grade backlog from API latency
- pgvector ANN for wishlist match at catalog scale
- Stateless services → horizontal scale
- LifeLedger hash anchoring O(1) on-chain regardless of SKU count

---

## 26. Demo UI Strategy

### Do NOT build a pixel-perfect Amazon clone
- Trademark / brand risk in presentation
- Judges compare to real Amazon and you lose
- Winners use **own brand, Amazon-adjacent patterns**

### What winners actually did

| Project | HackOn | UI approach |
|---|---|---|
| **Odyssey** | S3 Top 50 | Own brand "SmartShop Alexa"; deployed S3 website; goal-based recommender — **not amazon.com copy** |
| **GreenCart** | S5 sustainability | Own "GreenCart" brand; page titled "Amazon Landing Page" as **inspiration**; Material UI dashboard |
| **Want2Win** | S4 🥇 | Internal fraud/lifecycle tool aesthetic (likely dashboard, not storefront) |

### Relay UI direction (locked)

**Brand:** Relay — clean commerce + ops dashboard hybrid

| Surface | Design |
|---|---|
| **Shopper view** | shadcn commerce: product PDP, cart, checkout with **Fit Insight** banner — modern D2C aesthetic (think Everlane/Shopify), subtle Amazon-*familiar* layout (search top, grid) without logo/copy infringement |
| **Returns view** | Step wizard: reason → photo upload → grade result → disposition outcome |
| **Rescue feed** | Card feed with countdown TTL, distance badge, "Claim" CTA — Zomato-inspired urgency |
| **Ops / LifeLedger** | Dashboard tab: passport timeline, chain depth, QR verify, warranty chain |
| **Admin seed** | Hidden `/demo/reset` to replay judge walkthrough |

**Color:** Own palette (e.g. deep teal + amber accent) — **not Amazon orange**.

**Demo modes:**
1. **Live** — AWS/Railway, real API
2. **Video backup** — Railway recording, same UI
3. **Offline fallback** — pre-loaded Zustand state if network dies mid-pitch

---

## 27. Datasets — Bhavya (training) + Demo (Shikher)

### Bhavya — model training (priority order)

| Dataset | Source | Use | Size |
|---|---|---|---|
| **AI E-commerce defect images** | [HuggingFace](https://huggingface.co/datasets/prajwalkothwal/ai-generated-ecommerce-images) | Grade CNN + Bedrock prompts; 12 defect categories incl. damaged electronics, phone screen, quality_issue | 6,031 images |
| **Clothing fit dataset** | [Kaggle: rmisra/clothing-fit-dataset](https://www.kaggle.com/rmisra/clothing-fit-dataset-for-size-recommendation) | ModCloth + RentTheRunWay; fit labels small/fit/large | ~82K transactions |
| **ASOS GraphReturns** | [OSF](https://osf.io/c793h/) (not Kaggle) | Return prediction / fit flags research; 1.4M purchase events | Large |
| **Retail product categorization** | Kaggle (Mercari challenge) | Category head for CNN | 75K+ |
| **Amazon Berkeley Objects** | Berkeley / HuggingFace | Clean product images for grade baseline | 147K objects |
| **DeepFashion** | CUHK | Fashion category + landmark (optional) | Large |
| **MVTec AD** | Official | Anomaly detection pretrain (electronics defects) | 15 categories |
| **Kaputt** | Research (2025) | Retail logistics defects at scale — if access | 238K images |

**Bhavya minimum for 48h:** HuggingFace e-commerce defects + Kaggle fit dataset + fine-tune MobileNet/EfficientNet multi-head.

### Shikher — demo seed data (synthetic + derived)

| Data | Source | Use |
|---|---|---|
| Users + fit profiles | `scripts/seed.py` generated | Checkout insights |
| Orders + returns | Synthetic JSON | Return flow |
| Reverse Wishlists | Seed 20–50 wishes | Match demo |
| Rescue listings | Generated from return events + geo coords | Rescue feed |
| LifeLedger events | Written on grade (testnet) | QR verify |
| Product catalog | Mix: ABO subset + Unsplash placeholders + HF defect images as "returned units" | Browse + grade |
| Warranty records | Synthetic for 10 electronics SKUs | Warranty chain tab |

**No live Amazon API needed** — adapter interface `AmazonCatalogProvider` stubbed; real integration is post-hackathon.

### Kaggle — yes, but not only Kaggle
- **Kaggle** for fit + categorization
- **HuggingFace** for defect images (best match for our use case)
- **OSF** for ASOS returns graph (Bhavya research)
- **Synthetic** for Rescue geo + wishlist (Shikher)

---

## 28. AI & Cost Budget ($200 AWS credits)

| Service | Est. demo cost | Notes |
|---|---|---|
| Bedrock Nova Lite | ~$5–15 | Bulk grading in dev |
| Bedrock Haiku/Pro | ~$10–30 | Escalation only |
| RDS db.t3.micro | Free tier | |
| ECS Fargate | ~$20–40 | Minimal tasks |
| S3 + CloudFront | ~$1–5 | |
| ElastiCache / skip | Use Redis on Railway locally | |
| OpenAI fallback | Existing keys | When Bedrock throttles |
| Polygon testnet | Free | |

**Cost guardrails:** Bhavya CNN handles 80%; Bedrock batch for bulk; OpenAI only on fallback path.

---

## 29. Pre–plan.md Checklist

| Item | Status |
|---|---|
| Problem framing + differentiation | ✅ |
| MVP features + guardrails | ✅ |
| Iterative Lego tiers | ✅ |
| Tech stack (Python + Go) | ✅ |
| HLD + AWS/Railway deploy | ✅ |
| Demo UI direction | ✅ |
| Dataset plan | ✅ |
| **plan.md** | ✅ Created — technical build plan |
| Wireframes | ⏳ |
| API OpenAPI schema | ⏳ In relay-contracts (Shikher T0) |
| GitHub repo init | ⏳ Next — Shikher sets up 5 repos |

---

## 30. Document index

| File | Role |
|---|---|
| [`context.md`](./context.md) | Brainstorm, decisions, research, risk audit — *why* |
| [`plan.md`](./plan.md) | Technical build plan, tasks, contracts, schedules — *how* |
| [`hil-plan.md`](./hil-plan.md) | Reference format only (internship HIL project) |

**Next:** Shikher initializes 5 GitHub repos → Bhavya branches `relay-ml` → parallel M0/M1 per plan.md sequencing.

---

*End of Session 5. plan.md is the implementation source of truth.*
