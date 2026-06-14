"""Real end-to-end check through relay-api -> relay-ml(bedrock) -> passport -> LifeLedger.

Run INSIDE the relay-ml container (it has Pillow + httpx and network access to
relay-api at http://relay-api:8010). Synthesizes a REAL JPEG with Pillow so
Bedrock (Nova Lite / Titan) accepts the bytes.
"""

import io
import sys

import httpx
from PIL import Image, ImageDraw

API = "http://relay-api:8010"
USER = "00000000-0000-0000-0000-000000000001"
HDR = {"X-User-Id": USER}


def make_jpeg(seed: int = 0) -> bytes:
    img = Image.new("RGB", (512, 512), (28, 48, 92))
    d = ImageDraw.Draw(img)
    for y in range(0, 512, 16):
        d.line([(0, y), (512, y)], fill=(58, 88, 138), width=2)
    d.rectangle([180, 26, 330, 68], outline=(205, 185, 120), width=4)
    d.line([(40, 80), (40, 480)], fill=(222, 202, 150), width=3)
    d.line([(472, 80), (472, 480)], fill=(222, 202, 150), width=3)
    d.ellipse([300 + seed, 360, 360 + seed, 420], outline=(180, 160, 110), width=2)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return buf.getvalue()


def main() -> int:
    with httpx.Client(base_url=API, timeout=180.0) as c:
        print("== reset (this triggers ~40 Titan embeds, may take 10-30s) ==")
        r = c.post("/demo/reset")
        print("reset:", r.status_code, str(r.json())[:200] if r.status_code == 200 else r.text[:300])
        if r.status_code != 200:
            print("FAIL: reset failed")
            return 1

        orders = c.get("/orders", headers=HDR)
        print("orders:", orders.status_code)
        if orders.status_code != 200:
            print("FAIL: orders", orders.text[:300])
            return 1
        ojson = orders.json()

        item = None
        for o in ojson:
            for it in o.get("items", []):
                if it.get("returnable") and not it.get("returned") and it.get("unit_id"):
                    item = it
                    break
            if item:
                break
        if not item:
            print("FAIL: no returnable order item found")
            return 1
        print(f"picked item: id={item['id']} title={item.get('title')} "
              f"category={item.get('category')} unit_id={item.get('unit_id')}")

        ret = c.post("/returns", headers=HDR, json={
            "order_item_id": item["id"],
            "reason_code": "changed_mind",
            "pickup_slot": "2026-06-16 10:00-12:00",
        })
        print("create return:", ret.status_code)
        if ret.status_code != 201:
            print("FAIL: create return", ret.text[:400])
            return 1
        rj = ret.json()
        return_id = rj["id"]
        unit_id = rj["unit_id"]
        print(f"   return_id={return_id} unit_id={unit_id} status={rj['status']}")

        jpeg = make_jpeg()
        media = c.post(f"/returns/{return_id}/media", headers=HDR,
                       files={"files": ("return.jpg", jpeg, "image/jpeg")})
        print("upload media (synchronous grade via Bedrock):", media.status_code)
        if media.status_code != 202:
            print("FAIL: media upload", media.text[:600])
            return 1
        mj = media.json()
        print(f"   job={mj.get('job_id')} status={mj.get('status')} "
              f"passport_id={mj.get('passport_id')} media_hashes={len(mj.get('media_hashes', []))}")

        pp = c.get(f"/returns/{return_id}/passport", headers=HDR)
        print("passport:", pp.status_code)
        if pp.status_code != 200:
            print("FAIL: passport", pp.text[:400])
            return 1
        p = pp.json()
        tier = p.get("model_tier_used")
        print(f"   grade={p.get('grade')} grade_numeric={p.get('grade_numeric')} "
              f"tier={tier} confidence={p.get('confidence')} "
              f"defects={len(p.get('defects', []))} passport_hash={p.get('passport_hash')}")
        if not tier or "mock" in str(tier).lower():
            print(f"FAIL: model_tier_used is not a Bedrock tier (got {tier!r})")
            return 1

        disp = c.post(f"/returns/{return_id}/disposition", headers=HDR)
        print("disposition:", disp.status_code)
        if disp.status_code != 200:
            print("FAIL: disposition", disp.text[:400])
            return 1
        dj = disp.json()
        print(f"   channel={dj.get('channel')} score={dj.get('score')} "
              f"reasons={dj.get('reasons')} net_co2_saved_kg={dj.get('net_co2_saved_kg')}")

        ver = c.get(f"/lifeledger/{unit_id}/verify")
        print("lifeledger verify:", ver.status_code)
        if ver.status_code != 200:
            print("FAIL: verify", ver.text[:400])
            return 1
        vj = ver.json()
        print(f"   verified={vj.get('verified')} passport_hash={vj.get('passport_hash')} "
              f"on_chain_hash={vj.get('on_chain_hash')} tx_hash={vj.get('tx_hash')} "
              f"events={[e.get('event_type') for e in vj.get('events', [])]}")
        if not vj.get("verified"):
            print("FAIL: lifeledger not verified")
            return 1

        print("\nE2E_OK  (real Bedrock grade anchored + verified on LifeLedger)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
