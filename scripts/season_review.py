#!/usr/bin/env python3
"""Reproduce the numbers in docs/2026-SEASON-REVIEW.md.

Compares what the dashboard published during a season with what CDC reported,
and computes the historical base rates used for the next season's reference
expectation.

Inputs:
- the gh-pages branch history (each daily deploy of the published notebooks);
  run `git fetch origin gh-pages` first
- data/surveillance/wnv_colorado.json (CDC ArboNET annual counts)
- data/surveillance/wnv_colorado_weekly.json (CDC NNDSS provisional weekly counts)
- NASA POWER daily temperature and precipitation at the dashboard's Denver point

Usage:
    python scripts/season_review.py --year 2026 --out docs/season-review-2026
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
from aedesproject_uif.surveillance.season import season_pace  # noqa: E402

POWER_URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR"
    "&community=AG&longitude=-104.99&latitude=39.74&start={start}&end={end}&format=JSON"
)
PUBLISHED = {
    "wnv": "notebooks/01_west_nile_virus_surveillance.html",
    "tick": "notebooks/02_tick_disease_surveillance.html",
    "season": "notebooks/06_current_season_monitoring.html",
}


# ---------------------------------------------------------------------------
# What the dashboard published
# ---------------------------------------------------------------------------

def output_text(page_html: str) -> str:
    """Visible output text of an nbconvert page (code cells excluded)."""
    blocks = re.findall(r'<div class="jp-RenderedText[^"]*"[^>]*>(.*?)</div>', page_html, re.S)
    text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", b)) for b in blocks)
    return re.sub(r"\s+", " ", text)


def index_value(text: str) -> tuple[str | None, float | None]:
    """Read the composite index label and value in either published format.

    Before 2026-11-05 the pages said "Integrated risk: LOW (47.6%)"; afterwards
    "Experimental composite index: LOW (0.48 on a 0-1 scale ...)".
    """
    m = re.search(r"(?:Integrated risk|Experimental composite index):\s*([A-Z ]+?)\s*\(([\d.]+)(%| on a 0-1)", text)
    if not m:
        return None, None
    value = float(m.group(2))
    return m.group(1).strip(), value / 100 if m.group(3) == "%" else value


def _first(pattern: str, text: str, cast=str):
    m = re.search(pattern, text)
    return cast(m.group(1)) if m else None


def published_values(ref: str = "origin/gh-pages") -> pd.DataFrame:
    """One row per day: the last dashboard deploy of that day."""
    def git(*args):
        return subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, check=True).stdout

    def show(sha, path):
        # Some early deploys lack a page; treat it as "no value", not an error.
        result = subprocess.run(["git", "-C", str(REPO_ROOT), "show", f"{sha}:{path}"], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else ""

    rows = []
    for line in git("log", ref, "--format=%h %aI %s").splitlines():
        sha, when, subject = line.split(" ", 2)
        if "dashboard: automated update" not in subject:
            continue
        pages = {k: output_text(show(sha, path)) for k, path in PUBLISHED.items()}
        wnv_label, wnv_index = index_value(pages["wnv"])
        tick_label, tick_index = index_value(pages["tick"])
        rows.append({
            "date": when[:10], "deployed_at": when, "commit": sha,
            "wnv_label": wnv_label, "wnv_index": wnv_index,
            "temp14_c": _first(r"14-day mean temperature:\s*([\d.\-]+)", pages["wnv"], float),
            "season_alert_wnv": _first(r"West Nile Virus: YTD Cases: \d+ .*?Alert Level: \S+ (\w+)", pages["season"]),
            "season_ytd_wnv": _first(r"West Nile Virus: YTD Cases: (\d+)", pages["season"], int),
            "tick_label": tick_label, "tick_index": tick_index,
            "inat_tick_obs": _first(r"iNaturalist tick observations:\s*(\d+)", pages["tick"], int),
        })
    df = pd.DataFrame(rows)
    df = df.assign(_t=pd.to_datetime(df["deployed_at"], utc=True)).sort_values("_t").drop(columns="_t")
    # Keep the whole last deploy of each day (groupby().last() would mix columns from different deploys).
    return df.drop_duplicates(subset="date", keep="last").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Climate at the dashboard's Denver point
# ---------------------------------------------------------------------------

def climate_by_year(daily: pd.DataFrame, first_year: int, last_year: int) -> pd.DataFrame:
    """Yearly summaries from daily T2M (deg C) and PRECTOTCORR (mm), indexed by date."""
    daily = daily.sort_index()
    t14 = daily["T2M"].rolling(14).mean()
    rows = []
    for year in range(first_year, last_year + 1):
        in_year = daily.index.year == year
        months = daily.index.month
        winter = (daily.index >= f"{year - 1}-12-01") & (daily.index < f"{year}-03-01")
        rows.append({
            "year": year,
            "summer_mean_c": daily.loc[in_year & months.isin([6, 7, 8]), "T2M"].mean(),
            "july_mean_c": daily.loc[in_year & (months == 7), "T2M"].mean(),
            "max_14day_mean_c": t14[in_year].max(),
            "days_14day_mean_over_18c": int((t14[in_year & (months <= 9)] > 18).sum()),
            "winter_mean_c": daily.loc[winter, "T2M"].mean(),
            "spring_precip_mm": daily.loc[in_year & months.isin([3, 4, 5]), "PRECTOTCORR"].sum(),
            "summer_precip_mm": daily.loc[in_year & months.isin([6, 7, 8]), "PRECTOTCORR"].sum(),
        })
    return pd.DataFrame(rows).set_index("year")


def fetch_power(first_year: int, last_day: datetime.date) -> pd.DataFrame:
    url = POWER_URL.format(start=f"{first_year - 1}1201", end=last_day.strftime("%Y%m%d"))
    with urllib.request.urlopen(url, timeout=120) as resp:
        params = json.load(resp)["properties"]["parameter"]
    daily = pd.DataFrame(params)
    daily.index = pd.to_datetime(daily.index, format="%Y%m%d")
    return daily.where(daily > -999)


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

def _counts(series: pd.Series) -> dict:
    return {str(k): int(v) for k, v in series.value_counts().items()}


def review(year: int, out: Path) -> dict:
    from scipy import stats  # only needed here

    out.mkdir(parents=True, exist_ok=True)
    data_dir = REPO_ROOT / "data" / "surveillance"
    annual_payload = json.loads((data_dir / "wnv_colorado.json").read_text())
    weekly_payload = json.loads((data_dir / "wnv_colorado_weekly.json").read_text())
    annual = pd.DataFrame(annual_payload["data"]).set_index("year")
    weekly = weekly_payload["data"]
    hist_years = [y for y in annual.index if y < year]

    # 1. what was published
    pub = published_values()
    pub = pub[pub["date"].str.startswith(str(year))].copy()
    pub.to_csv(out / "published_values.csv", index=False)
    both = pub.dropna(subset=["wnv_index", "temp14_c"])
    pub["month"] = pub["date"].str[:7]
    monthly = pub.groupby("month").agg(
        wnv_index_min=("wnv_index", "min"), wnv_index_max=("wnv_index", "max"),
        wnv_labels=("wnv_label", _counts),
        tick_index_min=("tick_index", "min"), tick_index_max=("tick_index", "max"),
    ).reset_index()

    # 2. climate and cases by year
    daily = fetch_power(min(hist_years), datetime.date.today() - datetime.timedelta(days=7))
    clim = climate_by_year(daily, min(hist_years), year).join(annual[["neuroinvasive", "total_cases"]])
    clim.to_csv(out / "climate_and_cases_by_year.csv", float_format="%.2f")
    fit = clim.loc[min(hist_years):year - 1]
    correlations = {}
    for col in [c for c in clim.columns if c not in ("neuroinvasive", "total_cases")]:
        rho = stats.spearmanr(fit[col], fit["neuroinvasive"])
        correlations[col] = {"rho": round(float(rho.statistic), 2), "p": round(float(rho.pvalue), 2)}

    # 3. base rates and persistence (CDC ArboNET, all reported cases)
    totals = annual.loc[hist_years, "total_cases"]
    lag = stats.spearmanr(totals.iloc[:-1].values, totals.iloc[1:].values)

    # simple baselines for the season just ended (CDC ArboNET totals)
    baselines = {
        "last_year": int(totals.iloc[-1]),
        "median": float(totals.median()),
        "mean": round(float(totals.mean()), 1),
        "median_last_5_years": float(totals.iloc[-5:].median()),
    }
    peak = both.loc[both["wnv_index"].idxmax()]

    # share of each earlier season's cases reported after a given week (reporting tail)
    def share_after(week):
        out = {}
        for y in sorted({r["year"] for r in weekly if r["year"] < year}):
            final = max((r["cumulative"] for r in weekly if r["year"] == y and r["cumulative"] is not None), default=None)
            at = season_pace(weekly, y, week)["ytd"] if final else None
            if final and at is not None:
                out[str(y)] = round(1 - at / final, 3)
        return out

    # 4. this season against earlier seasons by CDC week
    pace = {w: season_pace(weekly, year, w) for w in (30, 34, 38)}
    pace["latest"] = season_pace(weekly, year)

    summary = {
        "generated_at": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat(),
        "season": year,
        "inputs": {
            "arbonet_retrieved": annual_payload.get("fetched"),
            "nndss_retrieved": weekly_payload.get("fetched"),
            "nndss_latest_week": weekly_payload.get("latest_observation"),
            "published_days": len(pub),
            "published_first": pub["date"].min(), "published_last": pub["date"].max(),
        },
        "published": {
            "wnv_index_vs_temp14_pearson_r": round(float(stats.pearsonr(both["temp14_c"], both["wnv_index"]).statistic), 3),
            "wnv_index_days": len(both),
            "wnv_index_peak": {"date": peak["date"], "value": round(float(peak["wnv_index"]), 3)},
            "wnv_labels": _counts(pub["wnv_label"]),
            "season_alert_wnv": _counts(pub["season_alert_wnv"]),
            "tick_labels": _counts(pub["tick_label"]),
            "monthly": monthly.round(3).to_dict(orient="records"),
        },
        "climate_vs_neuroinvasive_spearman": {"years": f"{min(hist_years)}-{year - 1}", **correlations},
        "season_climate": clim.loc[year].drop(["neuroinvasive", "total_cases"]).round(2).to_dict(),
        "base_rates_total_cases": {
            "years": f"{min(hist_years)}-{year - 1}",
            "median": float(totals.median()),
            "quartiles": [float(totals.quantile(0.25)), float(totals.quantile(0.75))],
            "min": int(totals.min()), "max": int(totals.max()),
            "years_over_200": [int(y) for y in totals[totals > 200].index],
        },
        "year_to_year_spearman": {"rho": round(float(lag.statistic), 2), "p": round(float(lag.pvalue), 2),
                                  "n": len(totals) - 1},
        "pace": {str(k): {kk: v[kk] for kk in ("week", "ytd", "prior", "prior_median", "status")}
                 for k, v in pace.items()},
        "baselines_vs_season": baselines,
        "share_reported_after_latest_week": share_after(pace["latest"]["week"]) if pace["latest"]["week"] else {},
        "share_reported_after_week_34": share_after(34),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = review(args.year, args.out)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
