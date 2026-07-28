"""Redraw the contribution calendar as a plotter-style grid that sweeps in by column."""

import json
from datetime import date
from pathlib import Path

from theme import ACCENT, BG, DIM, LEVELS, PHOSPHOR, RULE, esc, frame, label, scanlines

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "contributions.json"
OUT = ROOT / "graph.svg"

CELL, GAP = 11, 3
PITCH = CELL + GAP
PAD, GUTTER = 20, 32
HEAD, MONTHS_H, FOOT = 34, 16, 34

SWEEP = 0.024  # seconds between columns -- plotter head, not a fade
MONTH = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
DAY_ROWS = {1: "MON", 3: "WED", 5: "FRI"}  # Sun=0 grid rows, label every other


def main():
    d = json.loads(DATA.read_text())
    days = d["days"]
    weeks = max(x["week"] for x in days) + 1

    grid_w = weeks * PITCH - GAP
    grid_x = PAD + GUTTER
    grid_y = PAD + HEAD + MONTHS_H
    W = grid_x + grid_w + PAD
    H = grid_y + 7 * PITCH - GAP + FOOT + PAD

    cols = {}
    for x in days:
        cols.setdefault(x["week"], []).append(x)

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Contribution calendar for {esc(d["user"])}">',
        f"<defs>{scanlines()}</defs>",
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        frame(0.5, 0.5, W - 1, H - 1),
    ]

    # --- header compartment -------------------------------------------------
    s.append(label(PAD, PAD + 14, "[ contribution telemetry ]", 11, PHOSPHOR))
    s.append(label(W - PAD, PAD + 14, f"rev / {d['generated']}", 9, DIM, anchor="end"))
    s.append(f'<line x1="{PAD}" y1="{PAD + HEAD - 12}" x2="{W - PAD}" y2="{PAD + HEAD - 12}" stroke="{RULE}"/>')

    # --- month ticks --------------------------------------------------------
    seen = set()
    for w in sorted(cols):
        first = min(cols[w], key=lambda x: x["date"])
        m = date.fromisoformat(first["date"]).month
        if m not in seen and int(first["date"][8:10]) <= 7:
            seen.add(m)
            s.append(label(grid_x + w * PITCH, grid_y - 5, MONTH[m - 1], 9, DIM))

    # --- day-of-week gutter -------------------------------------------------
    for row, name in DAY_ROWS.items():
        s.append(label(PAD, grid_y + row * PITCH + CELL - 2, name, 9, DIM))

    # --- the grid: one animate per column, hard snap, no easing -------------
    for w in sorted(cols):
        cells = []
        for x in cols[w]:
            row = (date.fromisoformat(x["date"]).weekday() + 1) % 7
            cells.append(
                f'<rect x="{grid_x + w * PITCH}" y="{grid_y + row * PITCH}" '
                f'width="{CELL}" height="{CELL}" fill="{LEVELS[x["level"]]}"/>'
            )
        s.append(
            f'<g opacity="0">{"".join(cells)}'
            f'<animate attributeName="opacity" values="0;1" dur="0.01s" '
            f'begin="{w * SWEEP:.3f}s" calcMode="discrete" fill="freeze"/></g>'
        )

    # --- footer: stats left, legend right -----------------------------------
    fy = grid_y + 7 * PITCH - GAP + 22
    s.append(f'<line x1="{PAD}" y1="{fy - 14}" x2="{W - PAD}" y2="{fy - 14}" stroke="{RULE}"/>')
    stats = (
        f"total {d['total']}  //  streak {d['current_streak']}d  //  "
        f"best {d['longest_streak']}d  //  peak {d['busiest_dow']}"
    )
    s.append(label(PAD, fy + 4, stats, 10, PHOSPHOR))

    lx = W - PAD - (len(LEVELS) * 13) - 46
    s.append(label(lx - 6, fy + 4, "less", 9, DIM, anchor="end"))
    for i, c in enumerate(LEVELS):
        s.append(f'<rect x="{lx + i * 13}" y="{fy - 5}" width="9" height="9" fill="{c}"/>')
    s.append(label(lx + len(LEVELS) * 13 + 2, fy + 4, "more", 9, DIM))

    # accent tick: bottom-left corner marker, the one structural red on this plate
    s.append(f'<rect x="{PAD}" y="{H - PAD + 2}" width="18" height="2" fill="{ACCENT}"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#sl)" style="pointer-events:none"/>')
    s.append("</svg>")

    OUT.write_text("".join(s))
    print(f"{OUT.name}: {weeks}w x 7d, {W}x{H}, sweep {weeks * SWEEP:.1f}s")


if __name__ == "__main__":
    main()
