"""Self-check for the two bits of pull_contributions.py that can silently go wrong:
streak arithmetic and the HTML/tooltip parse. Run: python tools/test_pull.py"""

from pull_contributions import Calendar, streaks


def days(*counts):
    return [{"count": c} for c in counts]


def test_streaks():
    assert streaks(days()) == (0, 0)
    assert streaks(days(0, 0, 0)) == (0, 0)
    assert streaks(days(1, 1, 1)) == (3, 3)
    assert streaks(days(1, 1, 0, 1, 1, 1)) == (3, 3)
    assert streaks(days(0, 1, 0, 1)) == (1, 1)
    # an empty today must not zero a live streak...
    assert streaks(days(1, 1, 0)) == (2, 2)
    # ...but two idle days genuinely breaks it
    assert streaks(days(1, 1, 0, 0)) == (0, 2)
    # longest survives even when the current run is dead
    assert streaks(days(1, 1, 1, 1, 0, 0)) == (0, 4)


def test_parse():
    html = """
    <td data-date="2026-01-01" data-level="0" data-ix="0" id="c-0-0"></td>
    <td data-date="2026-01-02" data-level="3" data-ix="0" id="c-1-0"></td>
    <tool-tip for="c-0-0">No contributions on January 1st.</tool-tip>
    <tool-tip for="c-1-0">12 contributions on January 2nd.</tool-tip>
    """
    cal = Calendar()
    cal.feed(html)
    assert len(cal.days) == 2, cal.days
    assert cal.days[1]["level"] == 3
    assert cal.tips["c-1-0"].startswith("12 contributions")
    assert "No contributions" in cal.tips["c-0-0"]


if __name__ == "__main__":
    test_streaks()
    test_parse()
    print("ok")
