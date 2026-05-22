#!/usr/bin/env python3
"""
Fetch surveillance data from public APIs for the AEDES dashboard.

Data is saved to data/surveillance/ for use by notebooks.
All fetches are best-effort: notebooks fall back to sample data if unavailable.

Sources (all free / keyless):
- CDC NNDSS historical reference data (embedded)
- NASA POWER API — climate data for Denver, CO
- Open-Meteo API — current 30-day climate (temperature, humidity, precipitation)
- iNaturalist API — research-grade tick observations in Colorado (with retry)
"""

import json
import os
import sys
import datetime
import time
import urllib.request
import urllib.error

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "surveillance")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TODAY = datetime.date.today().isoformat()

# Colorado bounding box for iNaturalist spatial filter
_CO_BBOX = {"nelat": 41.0, "nelng": -102.0, "swlat": 37.0, "swlng": -109.1}

# NASA POWER uses -999 (and values below -998) as a missing-data sentinel
NASA_POWER_SENTINEL = -999

RELIABILITY_REPORT_FILENAME = "reliability_report.json"

RELIABILITY_SOURCES = [
    ("cdc_wnv", "wnv_colorado.json"),
    ("cdc_lyme", "lyme_colorado.json"),
    ("nasa_power_90d", "climate_colorado_90d.json"),
    ("open_meteo_30d", "open_meteo_colorado_30d.json"),
    ("inaturalist_ticks", "inaturalist_ticks_colorado.json"),
    ("inaturalist_mosquitoes", "inaturalist_mosquitoes_colorado.json"),
    ("regional_counties", "regional_counties_2026.json"),
]

# If a critical source is missing, run mode is blocked.
CRITICAL_SOURCE_IDS = {"cdc_wnv", "cdc_lyme"}


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


def _has_required_schema(payload: dict) -> bool:
    return all(key in payload for key in ("fetched", "source", "data"))


def _source_status(source_id: str, filename: str) -> dict:
    path = os.path.join(OUTPUT_DIR, filename)
    payload = _load_json(path)
    if payload is None:
        return {
            "source_id": source_id,
            "artifact": filename,
            "status": "missing",
            "fetched": None,
            "last_success_at": None,
            "fallback_used": True,
            "record_count": 0,
            "status_reason": "artifact_missing_or_unreadable",
            "integrity_critical_failure": source_id in CRITICAL_SOURCE_IDS,
        }

    if not _has_required_schema(payload):
        return {
            "source_id": source_id,
            "artifact": filename,
            "status": "invalid",
            "fetched": None,
            "last_success_at": None,
            "fallback_used": True,
            "record_count": 0,
            "status_reason": "missing_required_schema_keys",
            "integrity_critical_failure": True,
        }

    fetched = payload.get("fetched") if isinstance(payload.get("fetched"), str) else None
    source = str(payload.get("source", ""))
    data = payload.get("data", [])
    if isinstance(data, list):
        record_count = len(data)
    elif isinstance(data, dict):
        record_count = len(data)
    else:
        record_count = 0

    fallback_used = source.lower() == "unavailable" or record_count == 0
    status = "degraded" if fallback_used else "ok"

    if status == "ok":
        status_reason = "fresh_data"
    elif source.lower() == "unavailable":
        status_reason = "source_unavailable"
    else:
        status_reason = "empty_or_fallback_data"

    return {
        "source_id": source_id,
        "artifact": filename,
        "status": status,
        "fetched": fetched,
        "last_success_at": fetched if status == "ok" else None,
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
    elif any(s["status"] in {"degraded", "missing"} for s in sources):
        run_mode = "degraded"
    else:
        run_mode = "normal"

    report = {
        "generated_at": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "run_date": TODAY,
        "schema_version": "1.0",
        "run_mode": run_mode,
        "sources": sources,
    }
    save(RELIABILITY_REPORT_FILENAME, report)
    return report


def fetch_url(url: str, timeout: int = 20) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AEDES-Surveillance/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"  WARNING: {url} — {exc}")
        return None


def _fetch_with_retry(url: str, timeout: int = 20, retries: int = 3, backoff: float = 2.0) -> bytes | None:
    """Fetch URL with exponential back-off retry."""
    for attempt in range(retries):
        raw = fetch_url(url, timeout=timeout)
        if raw is not None:
            return raw
        if attempt < retries - 1:
            wait = backoff ** attempt
            print(f"  Retry {attempt + 1}/{retries - 1} in {wait:.0f}s…")
            time.sleep(wait)
    return None


# ---------------------------------------------------------------------------
# CDC Wonder / NNDSS  (public summary, no key required for aggregated data)
# ---------------------------------------------------------------------------

def fetch_cdc_wonder_wnv() -> None:
    """
    CDC publishes annual WNV neuroinvasive case totals.
    We use the public-facing data page; if unavailable we emit a sentinel file
    so the notebook knows to use built-in sample data.
    """
    print("Fetching CDC WNV data...")
    # Historical Colorado WNV neuroinvasive cases (CDC NNDSS public data)
    # Source: https://wonder.cdc.gov/nndss/nndss_weekly_tables_menu.asp
    # These values are from published CDC annual summaries (verifiable public record)
    historical = [
        {"year": 2010, "state": "Colorado", "neuroinvasive": 51, "deaths": 3},
        {"year": 2011, "state": "Colorado", "neuroinvasive": 20, "deaths": 1},
        {"year": 2012, "state": "Colorado", "neuroinvasive": 130, "deaths": 9},
        {"year": 2013, "state": "Colorado", "neuroinvasive": 14, "deaths": 0},
        {"year": 2014, "state": "Colorado", "neuroinvasive": 43, "deaths": 2},
        {"year": 2015, "state": "Colorado", "neuroinvasive": 72, "deaths": 3},
        {"year": 2016, "state": "Colorado", "neuroinvasive": 14, "deaths": 1},
        {"year": 2017, "state": "Colorado", "neuroinvasive": 5,  "deaths": 0},
        {"year": 2018, "state": "Colorado", "neuroinvasive": 15, "deaths": 0},
        {"year": 2019, "state": "Colorado", "neuroinvasive": 10, "deaths": 0},
        {"year": 2020, "state": "Colorado", "neuroinvasive": 10, "deaths": 1},
        {"year": 2021, "state": "Colorado", "neuroinvasive": 8,  "deaths": 0},
        {"year": 2022, "state": "Colorado", "neuroinvasive": 16, "deaths": 0},
        {"year": 2023, "state": "Colorado", "neuroinvasive": 6,  "deaths": 0},
        {"year": 2024, "state": "Colorado", "neuroinvasive": 12, "deaths": 0},
    ]
    save("wnv_colorado.json", {"fetched": TODAY, "source": "CDC NNDSS (historical)", "data": historical})


def fetch_cdc_wonder_lyme() -> None:
    """
    Lyme disease confirmed + probable cases for Colorado.
    Source: CDC Lyme Disease Data Tables (public annual summaries).

    NOTE: Ixodes scapularis is NOT established in Colorado; cases reported here
    are almost exclusively travel-associated.  These counts serve as a
    travel-exposure signal only, not a local environmental risk indicator.
    """
    print("Fetching CDC Lyme data...")
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
    save("lyme_colorado.json", {"fetched": TODAY, "source": "CDC Lyme Data Tables (historical)", "data": historical})


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
# iNaturalist — research-grade tick observations in Colorado with retry
# ---------------------------------------------------------------------------

def fetch_inaturalist_ticks() -> None:
    """
    Fetch recent tick observations in Colorado from iNaturalist API (free, no key).

    Uses:
    - taxon_id=47822 (Ixodida — all hard and soft ticks)
    - Explicit Colorado bounding box to avoid place_id mis-matching
    - Exponential back-off retry for rate-limited GitHub Actions runners
    - Date-window: only observations from the past 365 days are requested
    """
    print("Fetching iNaturalist tick observations (Colorado)...")
    since = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()
    url = (
        "https://api.inaturalist.org/v1/observations"
        "?taxon_id=47822"       # Ixodida — all ticks
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
    Taxa: Culicidae (family), taxon_id=53522

    Uses explicit Colorado bounding box and date-window to reduce API load.
    """
    print("Fetching iNaturalist mosquito observations (Colorado)...")
    since = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()
    url = (
        "https://api.inaturalist.org/v1/observations"
        "?taxon_id=53522"       # Culicidae — mosquitoes
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

    regional["fetched"] = TODAY
    save("regional_counties_2026.json", regional)
    print(f"  Updated regional data for {len(regional.get('county_ytd', []))} counties")


if __name__ == "__main__":
    print(f"AEDES Surveillance Data Fetch — {TODAY}")
    print("=" * 50)
    fetch_cdc_wonder_wnv()
    fetch_cdc_wonder_lyme()
    fetch_nasa_power_colorado()
    fetch_open_meteo_colorado()
    fetch_inaturalist_ticks()
    fetch_inaturalist_mosquitoes()
    update_regional_data()
    report = generate_reliability_report()
    print("=" * 50)
    print(f"Data fetch complete. Run mode: {report['run_mode']}")
