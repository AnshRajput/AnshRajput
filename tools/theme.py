"""Shared design tokens. Tactical-telemetry palette: one accent, no gradients, 90-degree corners."""

BG = "#0A0A0A"        # deactivated CRT, never pure black
PANEL = "#101010"     # compartment fill
RULE = "#242424"      # hairline dividers
PHOSPHOR = "#EAEAEA"  # primary foreground
DIM = "#6E6E6E"       # labels, metadata
ACCENT = "#E61919"    # hazard red -- the ONLY accent
ACCENT_HI = "#FF2A2A"
GREEN = "#4AF626"     # exactly one element in the whole system (panel status dot)

# Contribution ramp: tints of the single accent, dark -> hot. Not a rainbow.
# L0 sits well above the plate on purpose -- if empty cells vanish, the calendar
# reads as scattered dots instead of a grid, and the shape of the year is lost.
LEVELS = ["#1F1F1F", "#5C1414", "#9B1A1A", "#D01F1F", "#FF3B3B"]

# No webfonts: GitHub serves these SVGs as proxied images, so @font-face never
# loads. Ride the platform monospace stack and lock geometry with textLength.
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

TRACK = "0.1em"  # generous mechanical tracking on all metadata


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def label(x, y, text, size=10, fill=DIM, anchor="start", extra=""):
    """Uppercase tracked metadata line."""
    return (
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
        f'fill="{fill}" letter-spacing="{TRACK}" text-anchor="{anchor}" {extra}>'
        # upper() BEFORE esc(), or "&gt;" becomes the undefined entity "&GT;"
        f"{esc(str(text).upper())}</text>"
    )


def frame(x, y, w, h, stroke=RULE, fill="none"):
    """Square-cornered compartment. No rx, ever."""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'


def scanlines(uid="sl"):
    """Simulated electron-beam sweep. Applied over the whole plate at low opacity."""
    return (
        f'<pattern id="{uid}" width="1" height="3" patternUnits="userSpaceOnUse">'
        f'<rect width="1" height="1" fill="#000" opacity="0.28"/></pattern>'
    )
