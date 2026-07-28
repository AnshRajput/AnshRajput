"""Stage 1 of the portrait: cut the background, even out lighting, flatten to a canvas.

Straight-out-of-camera photos convert to mush -- everything lands mid-gray. Three
fixes in order: kill the background, CLAHE the luminance, composite onto BLACK.

Black (not white) because the plate is a dark terminal: glyph density maps to
LIGHT, so the background has to sit at the empty end of the ramp.

    python tools/clean_photo.py [source.jpg]     # defaults to the GitHub avatar
"""

import sys
import urllib.request
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "photo-ready.png"
AVATAR = "https://github.com/AnshRajput.png"
SIZE = 900
# Calibration knob: square crop side as a fraction of the subject's short edge.
# Lower = tighter on the face. Depends entirely on how your photo is framed --
# retune this rather than the glyph ramp if the portrait reads as a blob.
ZOOM = 0.75


def load(src):
    if src:
        return Image.open(src).convert("RGBA")
    req = urllib.request.Request(AVATAR, headers={"User-Agent": "profile-readme"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"source: {AVATAR}")
        return Image.open(BytesIO(r.read())).convert("RGBA")


def cut_background(img):
    try:
        from rembg import remove
    except ImportError:
        # ponytail: rembg pulls ~180MB of onnx. Skip it rather than hard-fail --
        # a tightly cropped avatar barely needs it. pip install rembg to enable.
        print("rembg not installed -- keeping original background")
        return img
    return remove(img).convert("RGBA")


def equalize(rgb):
    """CLAHE on the L channel: pulls real shadow/highlight detail out of flat lighting."""
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    lab[:, :, 0] = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8)).apply(lab[:, :, 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)


def main():
    img = cut_background(load(sys.argv[1] if len(sys.argv) > 1 else None))
    img.thumbnail((SIZE, SIZE), Image.LANCZOS)

    arr = np.array(img)
    rgb, alpha = arr[:, :, :3], arr[:, :, 3:4].astype(np.float32) / 255.0
    rgb = equalize(rgb).astype(np.float32)

    flat = (rgb * alpha).astype(np.uint8)  # composite onto black
    out = Image.fromarray(flat).convert("L")

    # stretch to full range so the glyph ramp actually gets used end to end,
    # measuring only the subject so a cut-out background doesn't drag it down
    g = np.array(out)
    fg = g[g > 8]
    lo, hi = np.percentile(fg if fg.size else g, [2, 98])
    scaled = np.clip((g.astype(np.float32) - lo) * 255.0 / max(hi - lo, 1), 0, 255)

    # Crop to the subject, then tighten onto the head. Two reasons: a full-body
    # crop renders as a tower that won't sit beside the info panel, and a light
    # shirt out-brightens the face, so the torso saturates into a solid block and
    # eats the portrait. Less torso in frame = more glyph budget on the face.
    ys, xs = np.where(scaled > 24)
    if ys.size:
        m = 10
        y0, y1 = max(int(ys.min()) - m, 0), int(ys.max()) + m
        x0, x1 = max(int(xs.min()) - m, 0), int(xs.max()) + m

        side = int(min(x1 - x0, y1 - y0) * ZOOM)
        # centre on the head: brightness-weighted centroid of the top of the subject
        band = scaled[y0 : y0 + max((y1 - y0) // 4, 1), x0:x1].astype(np.float64)
        mass = band.sum(axis=0)
        cx = x0 + int((mass * np.arange(mass.size)).sum() / mass.sum()) if mass.sum() else (x0 + x1) // 2

        x0 = min(max(cx - side // 2, 0), max(scaled.shape[1] - side, 0))
        scaled = scaled[y0 : y0 + side, x0 : x0 + side]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    final = Image.fromarray(scaled.astype(np.uint8))
    final.save(OUT)
    print(f"{OUT.relative_to(ROOT)}: {final.width}x{final.height} grayscale, range {lo:.0f}-{hi:.0f}")


if __name__ == "__main__":
    main()
