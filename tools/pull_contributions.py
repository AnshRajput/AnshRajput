"""Pull the public contribution calendar. No token, no OAuth, no dependencies.

GitHub serves the same HTML fragment the profile page consumes at
/users/<name>/contributions. stdlib html.parser handles it fine.
"""

import json
import re
import urllib.request
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

USER = "AnshRajput"
URL = f"https://github.com/users/{USER}/contributions"
OUT = Path(__file__).resolve().parent.parent / "assets" / "contributions.json"

DOW = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = []
        self.tips = {}
        self._tip_for = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "td" and a.get("data-date"):
            self.days.append(
                {
                    "date": a["data-date"],
                    "level": int(a.get("data-level") or 0),
                    "week": int(a.get("data-ix") or 0),
                    "_id": a.get("id", ""),
                }
            )
        elif tag == "tool-tip":
            self._tip_for = a.get("for")

    def handle_data(self, data):
        if self._tip_for:
            self.tips[self._tip_for] = self.tips.get(self._tip_for, "") + data

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self._tip_for = None


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": f"{USER}-profile-readme"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def streaks(days):
    """current = run of active days ending now; today counts but does not break the run."""
    active = [d["count"] > 0 for d in days]

    longest = run = 0
    for a in active:
        run = run + 1 if a else 0
        longest = max(longest, run)

    tail = active[:]
    if tail and not tail[-1]:
        tail.pop()  # today isn't over yet -- don't let an empty today zero the streak
    current = 0
    for a in reversed(tail):
        if not a:
            break
        current += 1
    return current, longest


def main():
    cal = Calendar()
    cal.feed(fetch())
    if not cal.days:
        raise SystemExit("no contribution cells parsed -- GitHub markup may have changed")

    for d in cal.days:
        text = cal.tips.get(d.pop("_id"), "")
        m = re.search(r"([\d,]+)\s+contribution", text)
        d["count"] = int(m.group(1).replace(",", "")) if m else 0

    days = sorted(cal.days, key=lambda d: d["date"])
    current, longest = streaks(days)

    by_dow = Counter()
    for d in days:
        by_dow[date.fromisoformat(d["date"]).weekday()] += d["count"]

    payload = {
        "user": USER,
        "generated": days[-1]["date"],
        "range": [days[0]["date"], days[-1]["date"]],
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "busiest_dow": DOW[by_dow.most_common(1)[0][0]] if by_dow else "--",
        "dow_totals": {DOW[i]: by_dow.get(i, 0) for i in range(7)},
        "days": days,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, separators=(",", ":")))
    print(
        f"{OUT.name}: {len(days)} days, {payload['total']} contributions, "
        f"streak {current} (best {longest}), busiest {payload['busiest_dow']}"
    )


if __name__ == "__main__":
    main()
