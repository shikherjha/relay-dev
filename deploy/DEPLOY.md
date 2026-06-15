# Relay — production deploy (single EC2 + Docker Compose)

Fastest reliable path: one EC2 box runs the whole stack via Docker Compose,
Caddy terminates HTTPS, and AWS access (S3 + Bedrock) comes from the instance
role — no static keys on the box.

```
Internet ──▶ Caddy :80/:443 ──┬─▶ relay-web  :3000   (app.yourdomain.com)
                              └─▶ relay-api  :8010   (api.yourdomain.com)
relay-api ─▶ relay-ml :8001 (Bedrock) · relay-engine :8002 · postgres · redis
AWS: S3 (relay-media) + Bedrock  ◀── EC2 instance role (RelayAppRole)
```

## 0. Prerequisites
- A domain you control (for `app.` and `api.` subdomains).
- AWS account with the `relay-media` S3 bucket created in your region.
- **Bedrock model access enabled** in that region (Console ▸ Bedrock ▸ Model
  access ▸ enable Amazon Nova Lite + Titan Embeddings). This is the usual cause
  of `/grade-image` 503s.

## 1. IAM role for the instance
1. Create a policy from [`iam-policy.json`](./iam-policy.json) (edit the bucket
   name / region if yours differ). Name it `RelayAppPolicy`.
2. Create an IAM **role** for EC2 (`RelayAppRole`), attach `RelayAppPolicy`.
3. You'll attach this role to the instance in step 2.

With the role attached, leave `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
**blank** in every `.env` — boto3 picks up the role automatically.

## 2. Launch EC2
- AMI: Ubuntu 22.04 LTS · Type: **t3.large** (Bedrock + ML want the RAM) · 30 GB gp3.
- IAM instance profile: `RelayAppRole`.
- Security group:
  - `22/tcp`  from **your IP only**
  - `80/tcp`  and `443/tcp` from `0.0.0.0/0`
- Allocate an Elastic IP and associate it.

## 3. DNS
Point both A records at the Elastic IP:
```
app.yourdomain.com  A  <elastic-ip>
api.yourdomain.com  A  <elastic-ip>
```

## 4. Install Docker
```bash
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER && newgrp docker
```

## 5. Clone the repos as siblings
```bash
mkdir -p ~/Hackon && cd ~/Hackon
for r in relay-dev relay-api relay-ml relay-engine relay-web; do
  git clone <your-remote>/$r.git
done
cd relay-dev
```

## 6. Configure env
`relay-dev/.env` (compose-level):
```ini
APP_DOMAIN=app.yourdomain.com
API_DOMAIN=api.yourdomain.com
PUBLIC_API_URL=https://api.yourdomain.com
POSTGRES_PASSWORD=<a strong password>
AWS_REGION=ap-south-1
GRADING_MODE=bedrock_only
```
`relay-api/.env` and `relay-ml/.env`: set `S3_BUCKET=relay-media`, `AWS_REGION`,
leave AWS keys blank. For real on-chain anchoring also set in `relay-api/.env`:
```ini
USE_REAL_LEDGER=true
LIFELEDGER_PRIVATE_KEY=<key funded with Amoy test-MATIC>   # faucet.polygon.technology
POLYGON_RPC_URL=https://rpc-amoy.polygon.technology         # or a dedicated Alchemy/Infura URL
```

## 7. Build + start
```bash
docker compose -f deploy/docker-compose.prod.yml up -d --build
```
Caddy auto-provisions TLS certs once DNS resolves. Check:
```bash
docker compose -f deploy/docker-compose.prod.yml ps
docker compose -f deploy/docker-compose.prod.yml logs -f caddy relay-api
```

## 8. Seed the demo (remote seeding)
The seed uploads product images to S3 from inside the container and populates
the catalogue + order/return/Second-Life/Rescue history — no separate image
step needed.
```bash
# Option A — run the seed module
docker compose -f deploy/docker-compose.prod.yml exec relay-api python -m scripts.seed
# Option B — hit the endpoint (same thing)
curl -X POST https://api.yourdomain.com/demo/reset
```

## 9. Verify
- App: `https://app.yourdomain.com`
- API health: `https://api.yourdomain.com/health`
- On-chain: open any product's LifeLedger page — live anchors show a
  **"Anchored on Polygon Amoy · view tx"** link to PolygonScan (only after
  `USE_REAL_LEDGER=true` and a new return/resale/checkout creates a real tx;
  the seed's historical events stay unlinked by design).

## Redeploy after a code change
```bash
cd ~/Hackon/relay-api && git pull        # (repeat per changed repo)
cd ~/Hackon/relay-dev
docker compose -f deploy/docker-compose.prod.yml up -d --build
```

## Troubleshooting
- **`/grade-image` 503** → Bedrock model access not enabled in the region, or
  the instance role lacks `bedrock:InvokeModel`. Check `docker logs relay-ml`.
- **CORS errors in the browser** → `CORS_ALLOW_ORIGINS` must equal the app
  origin; the compose sets it to `https://$APP_DOMAIN` automatically.
- **TLS not issued** → DNS must resolve to the box and 80/443 must be open
  before Caddy can complete the ACME challenge.
- **Blockchain** → confirm the key is funded (Amoy faucet) and `USE_REAL_LEDGER=true`;
  if the RPC is flaky the client falls back to a mock anchor so the demo never breaks.
