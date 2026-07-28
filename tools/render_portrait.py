"""Stage 2: map pixels to glyphs, draw the rows in top to bottom, then hold.

Single fill colour on purpose -- multi-colour ASCII reads as clutter, not a portrait.
Density maps to LIGHT (dark plate, light glyphs), so the black background falls at
the empty end of the ramp.
"""

from pathlib import Path

from PIL import Image
from theme import ACCENT, BG, DIM, MONO, PHOSPHOR, RULE, frame, label, scanlines

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "photo-ready.png"
OUT = ROOT / "portrait.svg"

GLYPHS = " '.,:;~+*xXO#"  # left = empty/dark, right = dense/lit
COLS = 80
CW, CH = 7, 12
PAD, HEAD, FOOT = 18, 30, 24
STEP, DUR = 0.035, 0.28  # per-row stagger and wipe duration -- linear, no easing


def main():
    img = Image.open(SRC).convert("L")
    rows = max(1, round(COLS * (img.height / img.width) * (CW / CH)))
    img = img.resize((COLS, rows), Image.LANCZOS)
    px = img.load()

    grid_w, grid_h = COLS * CW, rows * CH
    gx, gy = PAD, PAD + HEAD
    W, H = grid_w + PAD * 2, gy + grid_h + FOOT + PAD

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="ASCII portrait">',
        f"<defs>{scanlines('sl3')}",
    ]

    lines = []
    for r in range(rows):
        line = "".join(GLYPHS[px[c, r] * (len(GLYPHS) - 1) // 255] for c in range(COLS))
        lines.append(line.rstrip())

    # one clip per row, width driven 0 -> full
    for r, line in enumerate(lines):
        if not line:
            continue
        s.append(
            f'<clipPath id="r{r}"><rect x="{gx}" y="{gy + r * CH}" width="0" height="{CH}">'
            f'<animate attributeName="width" from="0" to="{len(line) * CW}" '
            f'begin="{r * STEP:.3f}s" dur="{DUR}s" fill="freeze"/></rect></clipPath>'
        )
    s.append("</defs>")

    s += [
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        frame(0.5, 0.5, W - 1, H - 1),
        label(PAD, PAD + 14, "[ ./portrait --ascii ]", 11, PHOSPHOR),
        label(W - PAD, PAD + 14, f"{COLS}x{rows} glyph", 9, DIM, anchor="end"),
        f'<line x1="{PAD}" y1="{PAD + 22}" x2="{W - PAD}" y2="{PAD + 22}" stroke="{RULE}"/>',
    ]

    for r, line in enumerate(lines):
        if not line:
            continue
        s.append(
            f'<text x="{gx}" y="{gy + r * CH + CH - 3}" clip-path="url(#r{r})" '
            f'font-family="{MONO}" font-size="11" fill="{PHOSPHOR}" xml:space="preserve" '
            f'textLength="{len(line) * CW}" lengthAdjust="spacingAndGlyphs">{line}</text>'
        )

    fy = H - PAD - 6
    s.append(f'<line x1="{PAD}" y1="{fy - 14}" x2="{W - PAD}" y2="{fy - 14}" stroke="{RULE}"/>')
    s.append(label(PAD, fy, f"ramp / {len(GLYPHS)} step mono", 9, DIM))
    s.append(label(W - PAD, fy, "///", 9, ACCENT, anchor="end"))
    s.append(f'<rect width="{W}" height="{H}" fill="url(#sl3)" style="pointer-events:none"/>')
    s.append("</svg>")

    OUT.write_text("".join(s))
    print(f"{OUT.name}: {COLS}x{rows} glyphs, {W}x{H}, draw {rows * STEP + DUR:.1f}s")


if __name__ == "__main__":
    main()
