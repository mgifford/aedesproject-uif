#!/usr/bin/env python3
"""
Fetch surveillance data from public APIs for the AEDES dashboard.

Data is saved to data/surveillance/ for use by notebooks.
All fetches are best-effort: notebooks fall back to sample data if unavailable.

Sources (all free / keyless):
- CDC ArboNET — Colorado West Nile virus cases by year (state-level CSV)
- CDC NNDSS — Colorado provisional weekly West Nile virus cases (in season)
- Lyme disease — static table in this script (not fetched, origin unverified)
- NASA POWER API — climate data for Denver, CO
- Open-Meteo API — current 30-day climate (temperature, humidity, precipitation)
- Google Trends (pytrends) — Colorado search interest for vector-borne disease terms
- iNaturalist API — research-grade tick observations in Colorado (with retry)
"""

import csv
import io
import json
import os
import sys
import datetime
import time
import random
import urllib.parse
import urllib.request
import urllib.error

try:
    from pytrends.request import TrendReq
except ImportError:  # pragma: no cover - optional dependency in local runs
    TrendReq = None

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "surveillance")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TODAY = datetime.date.today().isoformat()

# Colorado bounding box for iNaturalist spatial filter
_CO_BBOX = {"nelat": 41.0, "nelng": -102.0, "swlat": 37.0, "swlng": -109.1}

# iNaturalist taxon IDs, checked against https://api.inaturalist.org/v1/taxa/<id>
# on 2026-11-05. The previous values (47822 = order Diptera, 53522 = genus
# Synbranchus) returned flies and no mosquitoes (see issue #13).
INAT_TAXON_TICKS = 51672       # order Ixodida (ticks)
INAT_TAXON_MOSQUITOES = 52134  # family Culicidae (mosquitoes)

# NASA POWER uses -999 (and values below -998) as a missing-data sentinel
NASA_POWER_SENTINEL = -999

GOOGLE_TRENDS_KEYWORDS = [
    "west nile virus",
    "lyme disease",
    "rocky mountain spotted fever",
    "tularemia",
    "plague symptoms",
    "hantavirus",
    "mosquito bite",
    "tick bite",
]

RELIABILITY_REPORT_FILENAME = "reliability_report.json"

RELIABILITY_SOURCES = [
    ("cdc_wnv", "wnv_colorado.json"),
    ("cdc_wnv_weekly", "wnv_colorado_weekly.json"),
    ("cdc_lyme", "lyme_colorado.json"),
    ("nasa_power_90d", "climate_colorado_90d.json"),
    ("open_meteo_30d", "open_meteo_colorado_30d.json"),
    ("google_trends_co", "google_trends_colorado.json"),
    ("inaturalist_ticks", "inaturalist_ticks_colorado.json"),
    ("inaturalist_mosquitoes", "inaturalist_mosquitoes_colorado.json"),
    ("regional_counties", "regional_counties_2026.json"),
]

# If a critical source is missing, run mode is blocked.
CRITICAL_SOURCE_IDS = {"cdc_wnv", "cdc_lyme"}

# Sources whose records are not under the "data" key.
SOURCE_DATA_KEYS = {"regional_counties": "county_ytd"}


def save(filename: str, data: object) -> None:
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved {path}")


def _load_json(path: str) -> dict | None:
    try:
        with open(path) as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            return payload
        return None
    except (OSError, json.JSONDecodeError):
        return None


def _has_required_schema(payload: dict, data_key: str = "data") -> bool:
    return all(key in payload for key in ("fetched", "source", data_key))


def _source_status(source_id: str, filename: str) -> dict:
    path = os.path.join(OUTPUT_DIR, filename)
    payload = _load_json(path)
    if payload is None:
        return {
            "source_id": source_id,
            "artifact": filename,
            "kind": None,
            "status": "missing",
            "fetched": None,
            "latest_observation": None,
            "last_success_at": None,
            "fallback_used": True,
            "record_count": 0,
            "status_reason": "artifact_missing_or_unreadable",
            "integrity_critical_failure": source_id in CRITICAL_SOURCE_IDS,
        }

    data_key = SOURCE_DATA_KEYS.get(source_id, "data")
    if not _has_required_schema(payload, data_key):
        return {
            "source_id": source_id,
            "artifact": filename,
            "kind": None,
            "status": "invalid",
            "fetched": None,
            "latest_observation": None,
            "last_success_at": None,
            "fallback_used": True,
            "record_count": 0,
            "status_reason": "missing_required_schema_keys",
            "integrity_critical_failure": True,
        }

    is_static = payload.get("static") is True
    latest_observation = payload.get("latest_observation")

    fetched = payload.get("fetched") if isinstance(payload.get("fetched"), str) else None
    source = str(payload.get("source", ""))
    data = payload.get(data_key, [])
    if isinstance(data, list):
        record_count = len(data)
    elif isinstance(data, dict):
        record_count = len(data)
    else:
        record_count = 0

    # Files that do not state their latest observation: use the newest record date.
    if latest_observation is None and isinstance(data, list):
        for field in ("date", "observed_on", "year"):
            values = [r[field] for r in data if isinstance(r, dict) and r.get(field) is not None]
            if values:
                latest_observation = max(values)
                break

    fallback_used = source.lower() == "unavailable" or record_count == 0

    # "static": values stored in the repo, never fetched. "stale": a fetched source
    # that was not updated in this run (the previous copy is kept).
    if fallback_used:
        status = "degraded"
        status_reason = "source_unavailable" if source.lower() == "unavailable" else "empty_or_fallback_data"
    elif is_static:
        status, status_reason = "static", "static_table_unverified"
    elif fetched != TODAY:
        status, status_reason = "stale", "not_updated_this_run"
    else:
        status, status_reason = "ok", "fresh_data"

    return {
        "source_id": source_id,
        "artifact": filename,
        "kind": "static" if is_static else "fetched",
        "status": status,
        "fetched": fetched,
        "latest_observation": latest_observation,
        "last_success_at": fetched if status in {"ok", "stale"} else None,
        "fallback_used": fallback_used,
        "record_count": record_count,
        "status_reason": status_reason,
        "integrity_critical_failure": False,
    }


def generate_reliability_report() -> dict:
    """Generate per-source reliability metadata for the latest fetch run."""
    sources = [_source_status(source_id, filename) for source_id, filename in RELIABILITY_SOURCES]

    if any(s.get("integrity_critical_failure", False) for s in sources):
        run_mode = "blocked"
    elif any(s["status"] in {"degraded", "missing", "stale", "static"} for s in sources):
        run_mode = "degraded"
    else:
        run_mode = "normal"

    report = {
        "generated_at": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "run_date": TODAY,
        "schema_version": "1.1",
        "run_mode": run_mode,
        "sources": sources,
    }
    save(RELIABILITY_REPORT_FILENAME, report)
    return report


def fetch_url(url: str, timeout: int = 20, user_agent: str | None = "AEDES-Surveillance/2.0") -> bytes | None:
    """Fetch a URL. Pass user_agent=None to send the standard Python client header."""
    try:
        headers = {"User-Agent": user_agent} if user_agent else {}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"  WARNING: {url} — {exc}")
        return None


def _fetch_with_retry(
    url: str, timeout: int = 20, retries: int = 3, backoff: float = 2.0, **fetch_kwargs
) -> bytes | None:
    """Fetch URL with exponential back-off retry."""
    for attempt in range(retries):
        raw = fetch_url(url, timeout=timeout, **fetch_kwargs)
        if raw is not None:
            return raw
        if attempt < retries - 1:
            wait = backoff ** attempt
            print(f"  Retry {attempt + 1}/{retries - 1} in {wait:.0f}s…")
            time.sleep(wait)
    return None


# ---------------------------------------------------------------------------
# CDC ArboNET — West Nile virus human cases by state and year
# ---------------------------------------------------------------------------

# CSV behind CDC's "Historic Data" page. On 2026-11-06 the page said "All data are
# finalized as of September 16, 2026". The file has no state-level deaths.
CDC_WNV_PAGE = "https://www.cdc.gov/west-nile-virus/data-maps/historic-data.html"
CDC_WNV_STATE_CSV = (
    "https://www.cdc.gov/wcms/vizdata/live/ncezid_dvbd/WNV/"
    "wnv_hum_historic%20-%20Historic%20Sta.csv"
)
WNV_FIRST_YEAR = 2010  # first year shown in the dashboard charts
_CDC_WNV_COLUMNS = {"Type", "Year", "State", "Reported Cases"}
_CDC_WNV_TYPES = {"Neuroinvasive disease cases": "neuroinvasive", "All disease cases": "total_cases"}


def parse_cdc_wnv_state_csv(
    text: str, state_code: str = "CO", state_name: str = "Colorado", first_year: int = WNV_FIRST_YEAR
) -> list[dict]:
    """Return annual WNV case counts for one state from CDC's state-level CSV.

    Raises ValueError when the file does not have the expected structure, so a
    format change is reported instead of producing wrong numbers. Deaths are
    recorded as None because CDC does not publish them at state level here.
    """
    reader = csv.DictReader(io.StringIO(text))
    missing = _CDC_WNV_COLUMNS - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"CDC CSV is missing columns {sorted(missing)}")

    by_year: dict[int, dict[str, int]] = {}
    for row in reader:
        if row["State"] != state_code or row["Type"] not in _CDC_WNV_TYPES:
            continue
        if not row["Year"].isdigit():  # cumulative rows such as "1999-2025"
            continue
        year = int(row["Year"])
        if year < first_year:
            continue
        count = int(row["Reported Cases"].replace(",", ""))
        if count < 0:
            raise ValueError(f"negative count for {year}")
        by_year.setdefault(year, {})[_CDC_WNV_TYPES[row["Type"]]] = count

    if not by_year:
        raise ValueError(f"no rows for state {state_code} from {first_year}")

    records = []
    for year in sorted(by_year):
        counts = by_year[year]
        if set(counts) != set(_CDC_WNV_TYPES.values()):
            raise ValueError(f"incomplete counts for {year}: {counts}")
        if counts["neuroinvasive"] > counts["total_cases"]:
            raise ValueError(f"neuroinvasive count exceeds total for {year}")
        records.append({"year": year, "state": state_name, **counts, "deaths": None})

    gaps = [y for y in range(records[0]["year"], records[-1]["year"] + 1) if y not in by_year]
    if gaps:
        # A year absent from the file is not the same as a year with zero cases.
        print(f"  NOTE: CDC file has no {state_code} rows for {gaps}; those years are left out")
    return records


def fetch_cdc_arbonet_wnv() -> None:
    """Fetch Colorado WNV human case counts (annual) from CDC ArboNET.

    If the download or validation fails, the existing file is kept as the last
    known good copy and the reliability report marks it stale. No built-in
    numbers are substituted.
    """
    print("Fetching CDC ArboNET WNV data (Colorado)...")
    # CDC answers 403 to the custom "AEDES-Surveillance/2.0" header but accepts the
    # standard Python client header (checked 2026-11-06), so this request uses that.
    raw = _fetch_with_retry(CDC_WNV_STATE_CSV, timeout=30, retries=3, backoff=3.0, user_agent=None)
    try:
        if raw is None:
            raise ValueError("download failed")
        records = parse_cdc_wnv_state_csv(raw.decode("utf-8-sig"))
    except (ValueError, KeyError, UnicodeDecodeError) as exc:
        print(f"  WARNING: CDC WNV data not updated ({exc})")
        if not os.path.exists(os.path.join(OUTPUT_DIR, "wnv_colorado.json")):
            save("wnv_colorado.json", {"fetched": TODAY, "source": "unavailable", "data": []})
        return

    save(
        "wnv_colorado.json",
        {
            "fetched": TODAY,
            "retrieved_at": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat(),
            "source": "CDC ArboNET",
            "source_url": CDC_WNV_STATE_CSV,
            "source_page": CDC_WNV_PAGE,
            "static": False,
            "latest_observation": records[-1]["year"],
            "notes": (
                "Annual human cases by state of residence, not place of exposure. "
                "Neuroinvasive cases are the comparable series; CDC advises against comparing "
                "non-neuroinvasive counts across places or years. Deaths are not published at "
                "state level in this file and are recorded as null."
            ),
            "data": records,
        },
    )
    print(f"  Got {len(records)} years ({records[0]['year']}-{records[-1]['year']})")


# ---------------------------------------------------------------------------
# CDC NNDSS — provisional weekly West Nile virus counts (in season)
# ---------------------------------------------------------------------------

NNDSS_WEEKLY_API = "https://data.cdc.gov/resource/x9gk-5huc.json"
NNDSS_WEEKLY_PAGE = "https://data.cdc.gov/NNDSS/NNDSS-Weekly-Data/x9gk-5huc"
NNDSS_WNV_LABEL = "Arboviral diseases, West Nile virus disease"
NNDSS_FIRST_YEAR = 2022  # first year of this dataset
# CDC's flag "-" means the state reported no cases, which is a true zero. Every other
# flag (U, N, NN, NP, NC) means the value is not available and is recorded as None.
_NNDSS_NO_CASES_FLAG = "-"


def _nndss_count(record: dict, field: str) -> int | None:
    raw = record.get(field)
    if raw not in (None, ""):
        value = float(raw)
        if value < 0 or value != int(value):
            raise ValueError(f"unexpected {field} value {raw!r}")
        return int(value)
    return 0 if record.get(f"{field}_flag") == _NNDSS_NO_CASES_FLAG else None


def parse_nndss_weekly(records: list) -> list[dict]:
    """Return one row per year and MMWR week from NNDSS weekly records.

    "cumulative" is the year-to-date count as CDC published it that week (m3);
    "week_cases" is the count reported that week (m1). Raises ValueError when the
    records do not have the expected structure.
    """
    if not isinstance(records, list) or not records:
        raise ValueError("no NNDSS records")
    rows = []
    for record in records:
        if not isinstance(record, dict) or "year" not in record or "week" not in record:
            raise ValueError(f"unexpected NNDSS record {record!r}")
        year, week = int(record["year"]), int(record["week"])
        if not 1 <= week <= 53:
            raise ValueError(f"week out of range: {year} week {week}")
        rows.append({
            "year": year,
            "week": week,
            "week_cases": _nndss_count(record, "m1"),
            "cumulative": _nndss_count(record, "m3"),
        })
    rows.sort(key=lambda r: (r["year"], r["week"]))
    return rows


def fetch_cdc_nndss_wnv_weekly() -> None:
    """Fetch Colorado's provisional weekly WNV counts from CDC NNDSS, 2022 to now.

    Earlier years are kept as published at the time, so the current season can be
    compared with them at the same reporting delay. On failure the previous file is
    kept and reported stale.
    """
    print("Fetching CDC NNDSS weekly WNV data (Colorado)...")
    years = ",".join(f"'{y}'" for y in range(NNDSS_FIRST_YEAR, datetime.date.today().year + 1))
    query = urllib.parse.urlencode({
        "$where": f"upper(states)='COLORADO' and label='{NNDSS_WNV_LABEL}' and year in ({years})",
        "$select": "year,week,m1,m1_flag,m3,m3_flag",
        "$limit": "1000",
    })
    raw = _fetch_with_retry(f"{NNDSS_WEEKLY_API}?{query}", timeout=30, retries=3, backoff=3.0)
    try:
        if raw is None:
            raise ValueError("download failed")
        rows = parse_nndss_weekly(json.loads(raw))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"  WARNING: NNDSS weekly WNV data not updated ({exc})")
        if not os.path.exists(os.path.join(OUTPUT_DIR, "wnv_colorado_weekly.json")):
            save("wnv_colorado_weekly.json", {"fetched": TODAY, "source": "unavailable", "data": []})
        return

    latest = rows[-1]
    save(
        "wnv_colorado_weekly.json",
        {
            "fetched": TODAY,
            "retrieved_at": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat(),
            "source": "CDC NNDSS (provisional weekly)",
            "source_url": NNDSS_WEEKLY_API,
            "source_page": NNDSS_WEEKLY_PAGE,
            "static": False,
            "latest_observation": f"{latest['year']}-W{latest['week']:02d}",
            "notes": (
                "Provisional West Nile virus disease cases (neuroinvasive and non-neuroinvasive) "
                "reported to CDC by Colorado, by MMWR week of report, not week of illness onset. "
                "Counts are revised as late reports arrive. cumulative is the year-to-date count "
                "as published that week; 0 means CDC reported no cases and null means not available."
            ),
            "data": rows,
        },
    )
    print(f"  Got {len(rows)} weeks; latest {latest['year']} week {latest['week']}")


# ---------------------------------------------------------------------------
# Lyme disease — static table (not fetched)
# ---------------------------------------------------------------------------

def write_lyme_static_table() -> None:
    """
    Write the Colorado Lyme disease table (confirmed + probable cases).

    These values are stored in this script and are NOT fetched. Their source has
    not been verified against CDC, and the national Lyme surveillance case
    definition changed in 2022, so the series is not comparable across that year.
    The file is marked static and is not stamped with the run date.

    NOTE: Ixodes scapularis is NOT established in Colorado; cases reported here
    are almost exclusively travel-associated.  These counts serve as a
    travel-exposure signal only, not a local environmental risk indicator.
    """
    print("Writing static Lyme table (not fetched)...")
    historical = [
        {"year": 2015, "state": "Colorado", "confirmed": 35,  "probable": 18},
        {"year": 2016, "state": "Colorado", "confirmed": 29,  "probable": 22},
        {"year": 2017, "state": "Colorado", "confirmed": 33,  "probable": 27},
        {"year": 2018, "state": "Colorado", "confirmed": 41,  "probable": 31},
        {"year": 2019, "state": "Colorado", "confirmed": 44,  "probable": 35},
        {"year": 2020, "state": "Colorado", "confirmed": 38,  "probable": 28},
        {"year": 2021, "state": "Colorado", "confirmed": 52,  "probable": 41},
        {"year": 2022, "state": "Colorado", "confirmed": 57,  "probable": 46},
        {"year": 2023, "state": "Colorado", "confirmed": 61,  "probable": 49},
        {"year": 2024, "state": "Colorado", "confirmed": 65,  "probable": 54},
    ]
    save(
        "lyme_colorado.json",
        {
            "fetched": None,
            "source": "Static table in scripts/fetch_surveillance_data.py (origin unverified)",
            "static": True,
            "latest_observation": historical[-1]["year"],
            "notes": (
                "Not fetched and not verified against CDC. The 2022 change to the national Lyme "
                "surveillance case definition makes years before and after 2022 not comparable. "
                "Colorado cases are travel-associated."
            ),
            "data": historical,
        },
    )


# ---------------------------------------------------------------------------
# NASA POWER — climate baseline (90-day rolling)
# ---------------------------------------------------------------------------

def fetch_nasa_power_colorado() -> None:
    """
    Fetch recent temperature and precipitation data for Colorado (Denver centroid)
    from NASA POWER API — free, no key required.
    """
    print("Fetching NASA POWER climate data for Colorado...")
    end = datetime.date.today()
    start = end - datetime.timedelta(days=90)

    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        "?parameters=T2M,PRECTOTCORR"
        "&community=RE"
        f"&longitude=-104.99&latitude=39.74"
        f"&start={start.strftime('%Y%m%d')}&end={end.strftime('%Y%m%d')}"
        "&format=JSON"
    )

    raw = fetch_url(url)
    if raw:
        try:
            payload = json.loads(raw)
            props = payload.get("properties", {}).get("parameter", {})
            t2m = props.get("T2M", {})
            precip = props.get("PRECTOTCORR", {})
            records = [
                {"date": d, "temp_c": t2m.get(d), "precip_mm": precip.get(d)}
                for d in sorted(t2m.keys())
                if t2m.get(d) is not None and float(t2m.get(d, NASA_POWER_SENTINEL)) > (NASA_POWER_SENTINEL + 1)
            ]
            save(
                "climate_colorado_90d.json",
                {"fetched": TODAY, "source": "NASA POWER", "location": "Denver, CO", "data": records},
            )
            print(f"  Got {len(records)} days of climate data")
            return
        except (KeyError, json.JSONDecodeError) as exc:
            print(f"  WARNING: could not parse NASA POWER response — {exc}")

    # Fallback: write a sentinel so notebooks know to use synthetic data
    save("climate_colorado_90d.json", {"fetched": TODAY, "source": "unavailable", "data": []})


# ---------------------------------------------------------------------------
# Open-Meteo — free, keyless current 30-day climate (replaces heuristic)
# ---------------------------------------------------------------------------

def fetch_open_meteo_colorado() -> None:
    """
    Fetch the past 30 days of daily climate data for Colorado (Denver centroid)
    from the Open-Meteo free API — no key required.

    Provides temperature (min/max), precipitation, and relative humidity for
    use in GDD computation and habitat-suitability risk scoring.
    """
    print("Fetching Open-Meteo 30-day climate data for Colorado...")
    end = datetime.date.today()
    start = end - datetime.timedelta(days=30)

    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=39.74&longitude=-104.99"
        "&daily=temperature_2m_max,temperature_2m_min,"
        "precipitation_sum,relative_humidity_2m_max,relative_humidity_2m_min"
        f"&start_date={start}&end_date={end}"
        "&timezone=America%2FDenver"
        "&temperature_unit=celsius"
    )

    raw = _fetch_with_retry(url, timeout=20, retries=3, backoff=2.0)
    if raw:
        try:
            payload = json.loads(raw)
            daily = payload.get("daily", {})
            dates = daily.get("time", [])
            if dates:
                records = []
                for i, d in enumerate(dates):
                    t_max = daily.get("temperature_2m_max", [None] * len(dates))[i]
                    t_min = daily.get("temperature_2m_min", [None] * len(dates))[i]
                    precip = daily.get("precipitation_sum", [None] * len(dates))[i]
                    rh_max = daily.get("relative_humidity_2m_max", [None] * len(dates))[i]
                    rh_min = daily.get("relative_humidity_2m_min", [None] * len(dates))[i]
                    records.append({
                        "date": d,
                        "temp_max_c": t_max,
                        "temp_min_c": t_min,
                        "temp_mean_c": round((t_max + t_min) / 2, 2) if t_max is not None and t_min is not None else None,
                        "precip_mm": precip,
                        "humidity_max_pct": rh_max,
                        "humidity_min_pct": rh_min,
                        "humidity_mean_pct": round((rh_max + rh_min) / 2, 1) if rh_max is not None and rh_min is not None else None,
                    })
                save(
                    "open_meteo_colorado_30d.json",
                    {"fetched": TODAY, "source": "Open-Meteo API", "location": "Denver, CO", "data": records},
                )
                print(f"  Got {len(records)} days of Open-Meteo climate data")
                return
        except (KeyError, json.JSONDecodeError) as exc:
            print(f"  WARNING: could not parse Open-Meteo response — {exc}")

    save("open_meteo_colorado_30d.json", {"fetched": TODAY, "source": "unavailable", "data": []})


# ---------------------------------------------------------------------------
# Google Trends — Colorado state-level search signals
# ---------------------------------------------------------------------------

def _chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def fetch_google_trends_colorado() -> None:
    """
    Fetch state-level Colorado Google Trends data for North American vector-borne terms.

    Captures:
    - Weekly interest-over-time in Colorado (`geo=US-CO`)
    - DMA and city breakdowns where available
    """
    print("Fetching Google Trends data for Colorado...")
    if TrendReq is None:
        save(
            "google_trends_colorado.json",
            {
                "fetched": TODAY,
                "source": "unavailable",
                "geo": "US-CO",
                "keywords": GOOGLE_TRENDS_KEYWORDS,
                "time_series": [],
                "by_dma": [],
                "by_city": [],
                "data": [],
            },
        )
        return

    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)
    timeframe = f"{start_date.isoformat()} {end_date.isoformat()}"

    try:
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 30), retries=2, backoff_factor=0.5)
        time_series_records: list[dict] = []
        by_dma_records: list[dict] = []
        by_city_records: list[dict] = []

        for keyword_group in _chunks(GOOGLE_TRENDS_KEYWORDS, 5):
            pytrends.build_payload(keyword_group, timeframe=timeframe, geo="US-CO", gprop="")

            interest_df = pytrends.interest_over_time()
            if interest_df is not None and not interest_df.empty:
                if "isPartial" in interest_df.columns:
                    interest_df = interest_df.drop(columns=["isPartial"])
                for date_value, row in interest_df.iterrows():
                    for keyword in keyword_group:
                        value = row.get(keyword)
                        if value is not None:
                            time_series_records.append(
                                {
                                    "date": date_value.date().isoformat(),
                                    "keyword": keyword,
                                    "value": int(value),
                                }
                            )

            dma_df = pytrends.interest_by_region(resolution="DMA", inc_low_vol=True, inc_geo_code=False)
            if dma_df is not None and not dma_df.empty:
                for region_name, row in dma_df.iterrows():
                    for keyword in keyword_group:
                        value = row.get(keyword)
                        if value is not None:
                            by_dma_records.append(
                                {
                                    "region": str(region_name),
                                    "keyword": keyword,
                                    "value": int(value),
                                }
                            )

            city_df = pytrends.interest_by_region(resolution="CITY", inc_low_vol=True, inc_geo_code=False)
            if city_df is not None and not city_df.empty:
                for region_name, row in city_df.iterrows():
                    for keyword in keyword_group:
                        value = row.get(keyword)
                        if value is not None:
                            by_city_records.append(
                                {
                                    "region": str(region_name),
                                    "keyword": keyword,
                                    "value": int(value),
                                }
                            )

            time.sleep(random.randint(2, 4))

        has_data = bool(time_series_records or by_dma_records or by_city_records)
        source = "Google Trends API" if has_data else "unavailable"
        payload = {
            "fetched": TODAY,
            "source": source,
            "geo": "US-CO",
            "timeframe": timeframe,
            "keywords": GOOGLE_TRENDS_KEYWORDS,
            "time_series": time_series_records,
            "by_dma": by_dma_records,
            "by_city": by_city_records,
            "data": time_series_records,
        }
        save("google_trends_colorado.json", payload)
        print(
            f"  Got {len(time_series_records)} time points, "
            f"{len(by_dma_records)} DMA rows, {len(by_city_records)} city rows"
        )
    except Exception as exc:
        print(f"  WARNING: Google Trends fetch failed — {exc}")
        save(
            "google_trends_colorado.json",
            {
                "fetched": TODAY,
                "source": "unavailable",
                "geo": "US-CO",
                "keywords": GOOGLE_TRENDS_KEYWORDS,
                "time_series": [],
                "by_dma": [],
                "by_city": [],
                "data": [],
            },
        )


# ---------------------------------------------------------------------------
# iNaturalist — research-grade tick observations in Colorado with retry
# ---------------------------------------------------------------------------

def fetch_inaturalist_ticks() -> None:
    """
    Fetch recent tick observations in Colorado from iNaturalist API (free, no key).

    Uses:
    - taxon_id=INAT_TAXON_TICKS (Ixodida — all hard and soft ticks)
    - Explicit Colorado bounding box to avoid place_id mis-matching
    - Exponential back-off retry for rate-limited GitHub Actions runners
    - Date-window: only observations from the past 365 days are requested
    """
    print("Fetching iNaturalist tick observations (Colorado)...")
    since = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()
    url = (
        "https://api.inaturalist.org/v1/observations"
        f"?taxon_id={INAT_TAXON_TICKS}"       # Ixodida — all ticks
        "&quality_grade=research"
        f"&nelat={_CO_BBOX['nelat']}&nelng={_CO_BBOX['nelng']}"
        f"&swlat={_CO_BBOX['swlat']}&swlng={_CO_BBOX['swlng']}"
        f"&d1={since}"
        "&per_page=200"
        "&order=desc&order_by=observed_on"
    )
    raw = _fetch_with_retry(url, timeout=25, retries=4, backoff=3.0)
    if raw:
        try:
            payload = json.loads(raw)
            obs = [
                {
                    "id": o["id"],
                    "observed_on": o.get("observed_on"),
                    "taxon": o.get("taxon", {}).get("name"),
                    "common_name": o.get("taxon", {}).get("preferred_common_name"),
                    "lat": o.get("location", "").split(",")[0] if o.get("location") else None,
                    "lon": o.get("location", "").split(",")[1] if o.get("location") else None,
                    "county": o.get("place_guess"),
                }
                for o in payload.get("results", [])
            ]
            save(
                "inaturalist_ticks_colorado.json",
                {"fetched": TODAY, "source": "iNaturalist API", "count": len(obs), "data": obs},
            )
            print(f"  Got {len(obs)} tick observations")
            return
        except (KeyError, json.JSONDecodeError) as exc:
            print(f"  WARNING: could not parse iNaturalist response — {exc}")

    save("inaturalist_ticks_colorado.json", {"fetched": TODAY, "source": "unavailable", "data": []})


def fetch_inaturalist_mosquitoes() -> None:
    """
    Fetch recent mosquito observations in Colorado from iNaturalist API.
    Taxa: Culicidae (family), taxon_id=INAT_TAXON_MOSQUITOES

    Uses explicit Colorado bounding box and date-window to reduce API load.
    """
    print("Fetching iNaturalist mosquito observations (Colorado)...")
    since = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()
    url = (
        "https://api.inaturalist.org/v1/observations"
        f"?taxon_id={INAT_TAXON_MOSQUITOES}"  # Culicidae — mosquitoes
        "&quality_grade=research"
        f"&nelat={_CO_BBOX['nelat']}&nelng={_CO_BBOX['nelng']}"
        f"&swlat={_CO_BBOX['swlat']}&swlng={_CO_BBOX['swlng']}"
        f"&d1={since}"
        "&per_page=200"
        "&order=desc&order_by=observed_on"
    )
    raw = _fetch_with_retry(url, timeout=25, retries=4, backoff=3.0)
    if raw:
        try:
            payload = json.loads(raw)
            obs = [
                {
                    "id": o["id"],
                    "observed_on": o.get("observed_on"),
                    "taxon": o.get("taxon", {}).get("name"),
                    "common_name": o.get("taxon", {}).get("preferred_common_name"),
                    "lat": o.get("location", "").split(",")[0] if o.get("location") else None,
                    "lon": o.get("location", "").split(",")[1] if o.get("location") else None,
                    "county": o.get("place_guess"),
                }
                for o in payload.get("results", [])
            ]
            save(
                "inaturalist_mosquitoes_colorado.json",
                {"fetched": TODAY, "source": "iNaturalist API", "count": len(obs), "data": obs},
            )
            print(f"  Got {len(obs)} mosquito observations")
            return
        except (KeyError, json.JSONDecodeError) as exc:
            print(f"  WARNING: could not parse iNaturalist response — {exc}")

    save("inaturalist_mosquitoes_colorado.json", {"fetched": TODAY, "source": "unavailable", "data": []})


def update_regional_data() -> None:
    """
    Refresh county-level YTD totals in regional_counties_2026.json.

    Merges iNaturalist observation county tags into the county registry and
    sets the `fetched` timestamp so notebooks know the file is current.
    If the file doesn't exist yet, the initial seed file is left in place.
    """
    print("Updating regional county data...")

    regional_path = os.path.join(OUTPUT_DIR, "regional_counties_2026.json")

    # Load existing regional data (created by seed file at install time)
    if not os.path.exists(regional_path):
        print("  ⚠ regional_counties_2026.json not found; skipping regional update")
        return

    with open(regional_path) as f:
        regional = json.load(f)

    # Count iNaturalist tick observations per county this season
    ticks_path = os.path.join(OUTPUT_DIR, "inaturalist_ticks_colorado.json")
    mosq_path = os.path.join(OUTPUT_DIR, "inaturalist_mosquitoes_colorado.json")

    county_tick_obs: dict[str, int] = {}
    county_mosq_obs: dict[str, int] = {}

    for path, counter in [(ticks_path, county_tick_obs), (mosq_path, county_mosq_obs)]:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    obs_data = json.load(f)
                for obs in obs_data.get("data", []):
                    county_guess = obs.get("county", "") or ""
                    # iNaturalist uses "County, CO" format
                    parts = [p.strip() for p in county_guess.split(",")]
                    if parts:
                        county_name = parts[0].replace(" County", "").strip()
                        counter[county_name] = counter.get(county_name, 0) + 1
            except (json.JSONDecodeError, IOError) as exc:
                print(f"  WARNING: could not load {path}: {exc}")

    # Annotate each county with observation counts
    for county_entry in regional.get("county_ytd", []):
        name = county_entry.get("county", "")
        county_entry["tick_observations_ytd"] = county_tick_obs.get(name, 0)
        county_entry["mosquito_observations_ytd"] = county_mosq_obs.get(name, 0)

    # Only the iNaturalist columns change here; the case columns are seed values,
    # so "fetched" is left alone rather than stamped with the run date.
    regional["inaturalist_counts_updated"] = TODAY
    save("regional_counties_2026.json", regional)
    print(f"  Updated regional data for {len(regional.get('county_ytd', []))} counties")


if __name__ == "__main__":
    print(f"AEDES Surveillance Data Fetch — {TODAY}")
    print("=" * 50)
    fetch_cdc_arbonet_wnv()
    fetch_cdc_nndss_wnv_weekly()
    write_lyme_static_table()
    fetch_nasa_power_colorado()
    fetch_open_meteo_colorado()
    fetch_google_trends_colorado()
    fetch_inaturalist_ticks()
    fetch_inaturalist_mosquitoes()
    update_regional_data()
    report = generate_reliability_report()
    print("=" * 50)
    print(f"Data fetch complete. Run mode: {report['run_mode']}")
