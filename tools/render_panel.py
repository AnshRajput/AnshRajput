"""Terminal system-info plate. Rows snap in one at a time, mechanically.

PREVIEW=1 renders a static frame for viewing in a normal image viewer.
"""

import os
from pathlib import Path

from theme import ACCENT, BG, DIM, GREEN, MONO, PHOSPHOR, RULE, TRACK, esc, frame, label, scanlines

OUT = Path(__file__).resolve().parent.parent / "sysinfo.svg"

HANDLE = "ANSHRAJPUT"
TAGLINE = "software engineer / ships product"

# --- edit these ------------------------------------------------------------
ROWS = [
    ("focus", "on-device ai, systems"),
    ("stack", "python, typescript, flutter"),
    ("building", "dhruva - local llm on mobile"),
    ("shipped", "pawpilot, mantra infotech"),
    ("locale", "in / utc+05:30"),
    ("status", "operational"),
]
# ---------------------------------------------------------------------------

# H tracks portrait.svg's aspect so the two plates render the same height
# side by side in the README (360w portrait and 460w panel both land ~395 tall).
W, H = 460, 396
PAD = 18
ROW_Y, ROW_PITCH, VAL_X = 152, 30, 128
STEP = 0.09  # seconds between rows
PREVIEW = os.environ.get("PREVIEW") == "1"


def snap(inner, begin):
    if PREVIEW:
        return f"<g>{inner}</g>"
    return (
        f'<g opacity="0">{inner}<animate attributeName="opacity" values="0;1" '
        f'dur="0.01s" begin="{begin:.2f}s" calcMode="discrete" fill="freeze"/></g>'
    )


def main():
    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="System info panel for {esc(HANDLE)}">',
        f"<defs>{scanlines('sl2')}</defs>",
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        frame(0.5, 0.5, W - 1, H - 1),
    ]

    # header
    s.append(label(PAD, PAD + 14, "[ whoami --verbose ]", 11, PHOSPHOR))
    s.append(label(W - PAD, PAD + 14, "unit / d-01", 9, DIM, anchor="end"))
    s.append(f'<line x1="{PAD}" y1="{PAD + 26}" x2="{W - PAD}" y2="{PAD + 26}" stroke="{RULE}"/>')

    # macro type -- the scale contrast against 9px metadata
    s.append(
        f'<text x="{PAD}" y="{92}" font-family="{MONO}" font-size="30" font-weight="700" '
        f'fill="{PHOSPHOR}" letter-spacing="-0.02em">{esc(HANDLE)}</text>'
    )
    s.append(f'<rect x="{PAD}" y="{102}" width="34" height="3" fill="{ACCENT}"/>')
    s.append(label(PAD + 42, 105, TAGLINE, 9, DIM))
    s.append(f'<line x1="{PAD}" y1="{126}" x2="{W - PAD}" y2="{126}" stroke="{RULE}"/>')

    # data rows
    for i, (k, v) in enumerate(ROWS):
        y = ROW_Y + i * ROW_PITCH
        row = [
            label(PAD, y, k, 10, DIM),
            f'<text x="{VAL_X}" y="{y}" font-family="{MONO}" font-size="11" '
            f'fill="{PHOSPHOR}" letter-spacing="{TRACK}">{esc(v.upper())}</text>',
        ]
        if k == "status":
            # the single green element in the entire system
            row.append(f'<rect x="{VAL_X - 16}" y="{y - 8}" width="7" height="7" fill="{GREEN}"/>')
        s.append(snap("".join(row), 0.25 + i * STEP))

    # footer
    fy = H - PAD - 10
    s.append(f'<line x1="{PAD}" y1="{fy - 16}" x2="{W - PAD}" y2="{fy - 16}" stroke="{RULE}"/>')
    s.append(label(PAD, fy, "no recruiters (c) rev 2.6", 9, DIM))
    s.append(label(W - PAD, fy, ">>>", 9, ACCENT, anchor="end"))

    s.append(f'<rect width="{W}" height="{H}" fill="url(#sl2)" style="pointer-events:none"/>')
    s.append("</svg>")

    OUT.write_text("".join(s))
    print(f"{OUT.name}: {W}x{H}, {len(ROWS)} rows{' (static preview)' if PREVIEW else ''}")


if __name__ == "__main__":
    main()
