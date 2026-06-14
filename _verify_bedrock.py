"""Real-Bedrock end-to-end check for relay-ml (run INSIDE the relay-ml container).

Synthesizes real JPEG bytes with Pillow and hits the live service so we exercise
Titan embeddings + Nova Lite grading (single + multi-angle) with actual AWS calls.
"""

import io
import httpx
from PIL import Image, ImageDraw

BASE = "http://localhost:8001"


def make_jpeg(kind: str, seed: int = 0) -> bytes:
    img = Image.new("RGB", (512, 512), (28, 48, 92) if kind == "jeans" else (38, 38, 42))
    d = ImageDraw.Draw(img)
    if kind == "jeans":
        for y in range(0, 512, 16):
            d.line([(0, y), (512, y)], fill=(58, 88, 138), width=2)
        d.rectangle([180, 26, 330, 68], outline=(205, 185, 120), width=4)  # leather label
        d.line([(40, 80), (40, 480)], fill=(222, 202, 150), width=3)  # contrast stitch
        d.line([(472, 80), (472, 480)], fill=(222, 202, 150), width=3)
        d.ellipse([300 + seed, 360, 360 + seed, 420], outline=(180, 160, 110), width=2)
    else:
        d.ellipse([120, 110, 392, 382], outline=(190, 190, 190), width=12)  # earcup ring
        d.rectangle([60, 230, 120, 300], fill=(18, 18, 18))
        d.arc([150, 40, 362, 260], start=200, end=340, fill=(170, 170, 170), width=10)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return buf.getvalue()


def main() -> None:
    with httpx.Client(base_url=BASE, timeout=90.0) as c:
        print("health:", c.get("/health").json())

        emb = c.post("/embed", json={"category": "jeans", "vertical": "fashion", "size": "32"})
        if emb.status_code == 200:
            ej = emb.json()
            print(f"embed (Titan): dim={len(ej['vector'])} model={ej.get('model')}")
        else:
            print("embed ERR", emb.status_code, emb.text[:300])

        jeans = make_jpeg("jeans")
        r1 = c.post("/grade-image", data={"unit_id": "verify-1", "category": "jeans"},
                    files={"image": ("jeans.jpg", jeans, "image/jpeg")})
        print("grade-image:", r1.status_code)
        if r1.status_code == 200:
            p = r1.json()
            print(f"   grade={p['grade']} num={p.get('grade_numeric')} "
                  f"tier={p.get('model_tier_used')} conf={p.get('confidence')} "
                  f"defects={len(p.get('defects', []))}")
        else:
            print("   ERR", r1.text[:400])

        r2 = c.post("/grade-images", data={"unit_id": "verify-2", "category": "jeans"},
                    files=[("images", ("a.jpg", jeans, "image/jpeg")),
                           ("images", ("b.jpg", make_jpeg("jeans", seed=20), "image/jpeg")),
                           ("images", ("c.jpg", make_jpeg("jeans", seed=40), "image/jpeg"))])
        print("grade-images (3 angles):", r2.status_code)
        if r2.status_code == 200:
            p = r2.json()
            print(f"   grade={p['grade']} tier={p.get('model_tier_used')} "
                  f"media_hashes={len(p.get('media_hashes', []))}")
        else:
            print("   ERR", r2.text[:400])

        hp = make_jpeg("headphones")
        r3 = c.post("/grade-image", data={"unit_id": "verify-3", "category": "headphones"},
                    files={"image": ("hp.jpg", hp, "image/jpeg")})
        print("grade-image (electronics):", r3.status_code,
              r3.json().get("grade") if r3.status_code == 200 else r3.text[:200])

        print("\nBEDROCK_OK")


if __name__ == "__main__":
    main()
