"""Compare this season's reported cases with earlier seasons at the same week.

Works on the weekly rows written by scripts/fetch_surveillance_data.py
(data/surveillance/wnv_colorado_weekly.json): one row per year and MMWR week, where
"cumulative" is the year-to-date count as CDC published it that week. None means the
value is not available; 0 means CDC reported no cases.

This is a comparison of reported counts, not a risk estimate or forecast. Reporting
can arrive in batches (Colorado's 2024 count stayed at 0 until week 38), so a season
can look "below range" because reports have not arrived yet.
"""

from __future__ import annotations

from statistics import median
from typing import Iterable

STATUS_LABELS = {
    "no_data": "No in-season data",
    "no_baseline": "No earlier seasons to compare",
    "below_recent_range": "Below all recent seasons at this week",
    "within_recent_range": "Within the range of recent seasons",
    "above_recent_range": "Above all recent seasons at this week",
}


def cumulative_at_week(rows: Iterable[dict], year: int, week: int) -> int | None:
    """Return the latest available cumulative count for `year` at or before `week`."""
    best_week, best_value = None, None
    for row in rows:
        if row["year"] == year and row["week"] <= week and row.get("cumulative") is not None:
            if best_week is None or row["week"] > best_week:
                best_week, best_value = row["week"], row["cumulative"]
    return best_value


def season_pace(rows: Iterable[dict], year: int, week: int | None = None) -> dict:
    """Compare `year` with every earlier year in `rows` at the same MMWR week.

    If `week` is None, the latest week with a value in `year` is used.
    """
    rows = list(rows)
    current = [r for r in rows if r["year"] == year and r.get("cumulative") is not None]
    result = {"year": year, "week": week, "ytd": None, "prior": {},
              "prior_min": None, "prior_median": None, "prior_max": None}
    if not current:
        return {**result, "status": "no_data", "label": STATUS_LABELS["no_data"]}

    if week is None:
        week = max(r["week"] for r in current)
    ytd = cumulative_at_week(rows, year, week)
    if ytd is None:
        return {**result, "week": week, "status": "no_data", "label": STATUS_LABELS["no_data"]}

    earlier_years = sorted({r["year"] for r in rows if r["year"] < year})
    prior = {}
    for y in earlier_years:
        value = cumulative_at_week(rows, y, week)
        if value is not None:
            prior[y] = value
    result.update(week=week, ytd=ytd, prior=prior)
    if not prior:
        return {**result, "status": "no_baseline", "label": STATUS_LABELS["no_baseline"]}

    low, high = min(prior.values()), max(prior.values())
    if ytd < low:
        status = "below_recent_range"
    elif ytd > high:
        status = "above_recent_range"
    else:
        status = "within_recent_range"
    return {**result, "prior_min": low, "prior_median": median(prior.values()), "prior_max": high,
            "status": status, "label": STATUS_LABELS[status]}


def as_alert_metrics(pace: dict) -> dict:
    """Express a season_pace() result in the keys notebook 06 uses for its alert table.

    Values that cannot be computed are None rather than 0.
    """
    ytd, expected = pace.get("ytd"), pace.get("prior_median")
    deviation = None if ytd is None or not expected else (ytd - expected) / expected * 100
    return {
        "ytd_cases": ytd,
        "expected_at_week": expected,
        "deviation_pct": deviation,
        "alert_level": pace["label"],
        "data_week": pace.get("week"),
        "recent_range": (pace.get("prior_min"), pace.get("prior_max")),
        "recent_years": sorted(pace.get("prior", {})),
    }
