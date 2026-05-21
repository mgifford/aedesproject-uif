"""
Unified surveillance data loader.

Handles standardized ingestion from CDC ArboNET (via Socrata API), Open-Meteo,
NASA POWER, iNaturalist, and other public data sources.

Features:
- CDC Socrata API with dynamic schema-mapping to handle column name drift
- Compressed-CSV (gzip) local cache so a single API outage never crashes a run
- Open-Meteo free climate API (no key required) for current 30-day weather
- iNaturalist with exponential-backoff retries and incremental date-window fetching
"""

import gzip
import io
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.request

import pandas as pd


# ---------------------------------------------------------------------------
# CDC Socrata schema mapping — handles column-name drift across years
# ---------------------------------------------------------------------------

# Each key maps a canonical column name to the list of names it may appear as
# in the Socrata response (ordered by preference, newest first).
_CDC_COLUMN_ALIASES: Dict[str, List[str]] = {
    "year":    ["mmwr_year", "year", "report_year", "Year"],
    "state":   ["reporting_area", "state", "statename", "State"],
    "disease": ["disease", "condition", "Condition", "disease_name"],
    "cases":   ["cum_cases", "cases", "count", "total_cases", "Cases"],
    "deaths":  ["deaths", "total_deaths", "Deaths"],
}


def _apply_schema_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns in *df* to canonical names using `_CDC_COLUMN_ALIASES`."""
    rename_map: Dict[str, str] = {}
    for canonical, aliases in _CDC_COLUMN_ALIASES.items():
        if canonical in df.columns:
            continue  # Already present
        for alias in aliases:
            if alias in df.columns:
                rename_map[alias] = canonical
                break
    return df.rename(columns=rename_map)


class SurveillanceDataLoader:
    """
    Standardized data loader for surveillance data from multiple sources.

    Provides unified methods for loading CDC, Open-Meteo, NASA, and
    citizen-science data with validation, harmonization, and metadata tracking.
    """

    # Socrata dataset IDs for CDC public data (no API key required for public datasets)
    _CDC_SOCRATA_DATASETS = {
        "nndss_weekly": "x9gk-5huc",   # NNDSS weekly data (2014-present)
        "nndss_annual": "4m7b-pz77",   # ArboNET annual summary
    }

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the data loader.

        Args:
            data_dir: Path to surveillance data directory. If None, defaults to
                     PROJECT_ROOT/data/surveillance
        """
        if data_dir is None:
            from ..config import Config
            data_dir = Config.DATA_DIR / "surveillance"

        self.data_dir = Path(data_dir)
        self.cache_dir = self.data_dir.parent / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_url(self, url: str, timeout: int = 20,
                   retries: int = 3, backoff: float = 2.0) -> Optional[bytes]:
        """Fetch *url* with retry/back-off.  Returns raw bytes or None."""
        headers = {"User-Agent": "AEDES-Surveillance/2.0 (github.com/mgifford/aedesproject-uif)"}
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return resp.read()
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
                if attempt < retries - 1:
                    time.sleep(backoff ** attempt)
        return None

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.csv.gz"

    def _write_cache(self, key: str, df: pd.DataFrame) -> None:
        path = self._cache_path(key)
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            df.to_csv(io.TextIOWrapper(gz, encoding="utf-8"), index=False)
        path.write_bytes(buf.getvalue())

    def _read_cache(self, key: str) -> Optional[pd.DataFrame]:
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            with gzip.open(path, "rt", encoding="utf-8") as gz:
                return pd.read_csv(gz)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # CDC — Socrata API + local JSON + cache fallback
    # ------------------------------------------------------------------

    def _fetch_cdc_socrata(self, disease: str, state: str = "Colorado") -> Optional[pd.DataFrame]:
        """
        Query the CDC Socrata NNDSS API for annual case counts.

        Uses the public endpoint (no API key required).  Applies dynamic
        schema mapping so column renames don't break the pipeline.
        """
        disease_filter = urllib.request.quote(disease.replace("_", " ").title())
        state_filter = urllib.request.quote(state)
        dataset_id = self._CDC_SOCRATA_DATASETS["nndss_weekly"]
        url = (
            f"https://data.cdc.gov/resource/{dataset_id}.json"
            f"?$where=lower(reporting_area)='{state.lower()}'"
            f"&$limit=2000"
            f"&$order=mmwr_year%20DESC"
        )
        raw = self._fetch_url(url, timeout=25)
        if raw is None:
            return None
        try:
            records = json.loads(raw)
            if not isinstance(records, list) or not records:
                return None
            df = pd.DataFrame(records)
            df = _apply_schema_mapping(df)
            # Filter to disease of interest (case-insensitive substring match)
            if "disease" in df.columns:
                mask = df["disease"].str.lower().str.contains(
                    disease.lower().replace("_", " "), na=False
                )
                df = df[mask]
            return df if not df.empty else None
        except (json.JSONDecodeError, Exception):
            return None

    def load_cdc_arbonet_cases(
        self,
        disease: str,
        region: str,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Load CDC ArboNET/NNDSS human case data with multi-layer fallback.

        Resolution order:
        1. CDC Socrata API (live, with schema mapping)
        2. Local JSON file in data/surveillance/
        3. Compressed CSV cache in data/cache/

        Args:
            disease: Disease code (e.g., 'wnv', 'lyme', 'rmsf')
            region: Geographic region (e.g., 'colorado')
            year_start: Start year (inclusive)
            year_end: End year (inclusive)

        Returns:
            DataFrame with columns: date, county, disease, cases, deaths
        """
        cache_key = f"cdc_{disease}_{region}"
        df: Optional[pd.DataFrame] = None

        # Layer 1: live Socrata API
        state_map = {
            "colorado": "Colorado",
            "western_us": "Colorado",
        }
        state = state_map.get(region.lower(), region.replace("_", " ").title())
        df = self._fetch_cdc_socrata(disease, state)
        if df is not None and not df.empty:
            self._write_cache(cache_key, df)

        # Layer 2: local JSON files
        if df is None or df.empty:
            candidates = [
                self.data_dir / f"{disease}_{region}_cases.json",
                self.data_dir / f"cdc_arbonet_{disease}_{region}.csv",
                self.data_dir / f"{disease}_{region}.json",
            ]
            for path in candidates:
                if path.exists():
                    if path.suffix == ".json":
                        with open(path) as f:
                            data = json.load(f)
                        if isinstance(data, dict) and "data" in data:
                            df = pd.DataFrame(data["data"])
                        else:
                            df = pd.DataFrame(data)
                    else:
                        df = pd.read_csv(path)
                    if not df.empty:
                        break

        # Layer 3: compressed CSV cache
        if df is None or df.empty:
            df = self._read_cache(cache_key)

        if df is None or df.empty:
            return pd.DataFrame(columns=["date", "county", "disease", "cases", "deaths"])

        # Standardize date column
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        elif "year" in df.columns:
            df["date"] = pd.to_datetime(df["year"].astype(str) + "-01-01", errors="coerce")

        # Filter by year range
        if year_start is not None and "date" in df.columns:
            df = df[df["date"].dt.year >= year_start]
        if year_end is not None and "date" in df.columns:
            df = df[df["date"].dt.year <= year_end]

        self.metadata[f"cdc_arbonet_{disease}"] = {
            "source": "CDC Socrata / ArboNET",
            "disease": disease,
            "region": region,
            "records": len(df),
            "date_range": (df["date"].min(), df["date"].max()) if "date" in df.columns else None,
        }
        return df

    # ------------------------------------------------------------------
    # Open-Meteo — free, keyless climate API
    # ------------------------------------------------------------------

    def load_open_meteo_climate(
        self,
        latitude: float = 39.74,
        longitude: float = -104.99,
        past_days: int = 30,
    ) -> pd.DataFrame:
        """
        Fetch recent climate data from the Open-Meteo Historical/Forecast API.

        Free, keyless public API.  Returns daily temperature, humidity,
        and precipitation for use in GDD and habitat-suitability calculations.

        Args:
            latitude: Location latitude (default: Denver, CO)
            longitude: Location longitude (default: Denver, CO)
            past_days: Number of past days to retrieve (default: 30)

        Returns:
            DataFrame with columns: date, temp_max_c, temp_min_c, temp_mean_c,
                                    humidity_mean_pct, precip_mm
        """
        end_date = datetime.now(timezone.utc).date()
        start_date = end_date - timedelta(days=past_days)

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            "&daily=temperature_2m_max,temperature_2m_min,"
            "precipitation_sum,relative_humidity_2m_max,relative_humidity_2m_min"
            f"&start_date={start_date}&end_date={end_date}"
            "&timezone=America%2FDenver"
            "&temperature_unit=celsius"
        )

        raw = self._fetch_url(url, timeout=20, retries=3, backoff=2.0)
        if raw is not None:
            try:
                payload = json.loads(raw)
                daily = payload.get("daily", {})
                dates = daily.get("time", [])
                if dates:
                    temp_max = daily.get("temperature_2m_max", [None] * len(dates))
                    temp_min = daily.get("temperature_2m_min", [None] * len(dates))
                    precip = daily.get("precipitation_sum", [None] * len(dates))
                    rh_max = daily.get("relative_humidity_2m_max", [None] * len(dates))
                    rh_min = daily.get("relative_humidity_2m_min", [None] * len(dates))

                    df = pd.DataFrame({
                        "date": pd.to_datetime(dates),
                        "temp_max_c": pd.to_numeric(temp_max, errors="coerce"),
                        "temp_min_c": pd.to_numeric(temp_min, errors="coerce"),
                        "precip_mm": pd.to_numeric(precip, errors="coerce"),
                        "humidity_max_pct": pd.to_numeric(rh_max, errors="coerce"),
                        "humidity_min_pct": pd.to_numeric(rh_min, errors="coerce"),
                    })
                    df["temp_mean_c"] = (df["temp_max_c"] + df["temp_min_c"]) / 2
                    df["humidity_mean_pct"] = (df["humidity_max_pct"] + df["humidity_min_pct"]) / 2

                    self.metadata["open_meteo_climate"] = {
                        "source": "Open-Meteo API",
                        "location": f"{latitude},{longitude}",
                        "records": len(df),
                        "date_range": (df["date"].min(), df["date"].max()),
                    }
                    return df
            except (json.JSONDecodeError, KeyError, Exception):
                pass

        # Fallback to NASA POWER cache
        return self.load_noaa_climate_data("colorado_denver", days_back=past_days)

    # ------------------------------------------------------------------
    # NOAA / NASA POWER
    # ------------------------------------------------------------------

    def load_mosquito_pool_data(
        self,
        region: str,
        species: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load mosquito pool test data (entomological surveillance).

        Args:
            region: Geographic region
            species: Optional mosquito species filter (e.g., 'culex_tarsalis')

        Returns:
            DataFrame with columns: date, location, species, pool_size, positive_pools
        """
        candidates = [
            self.data_dir / f"mosquito_pools_{region}.json",
            self.data_dir / f"entomological_surveillance_{region}.csv",
        ]

        df = None
        for path in candidates:
            if path.exists():
                if path.suffix == ".json":
                    with open(path) as f:
                        data = json.load(f)
                    df = pd.DataFrame(data.get("data", []))
                else:
                    df = pd.read_csv(path)
                break

        if df is None or df.empty:
            return pd.DataFrame(columns=["date", "location", "species", "pool_size", "positive_pools"])

        if species is not None and "species" in df.columns:
            df = df[df["species"] == species]

        self.metadata[f"mosquito_pools_{region}"] = {
            "source": "Local/State Vector Surveillance",
            "region": region,
            "records": len(df),
        }

        return df

    def load_noaa_climate_data(
        self,
        region: str,
        days_back: int = 90
    ) -> pd.DataFrame:
        """
        Load NOAA/NASA POWER climate data from local cache files.

        Args:
            region: Geographic region (e.g., 'colorado_denver')
            days_back: Days of historical data to load

        Returns:
            DataFrame with columns: date, temp_c, temp_f, precip_mm, humidity_percent
        """
        candidates = [
            self.data_dir / f"climate_{region}_90d.json",
            self.data_dir / f"climate_{region}.csv",
            self.data_dir / f"nasa_power_{region}.csv",
        ]

        df = None
        for path in candidates:
            if path.exists():
                if path.suffix == ".json":
                    with open(path) as f:
                        data = json.load(f)
                    df = pd.DataFrame(data.get("data", []))
                else:
                    df = pd.read_csv(path)
                break

        if df is None or df.empty:
            return pd.DataFrame(columns=["date", "temp_c", "temp_f", "precip_mm", "humidity_percent"])

        # Parse date (NASA POWER uses YYYYMMDD integers)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"].astype(str), format="%Y%m%d", errors="coerce")
            if df["date"].isna().all():
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Filter invalid temperature values (NASA POWER uses -999 for missing)
        if "temp_c" in df.columns:
            df = df[df["temp_c"] > -80]

        self.metadata[f"climate_{region}"] = {
            "source": "NASA POWER / NOAA",
            "region": region,
            "records": len(df),
            "date_range": (df["date"].min(), df["date"].max()) if "date" in df.columns else None,
        }

        return df

    # ------------------------------------------------------------------
    # iNaturalist — with retry/back-off and incremental date-window
    # ------------------------------------------------------------------

    def load_inaturalist_vector_observations(
        self,
        vector_type: str,
        region: str,
        since_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Load iNaturalist citizen-science vector observations.

        Reads from local cache files produced by fetch_surveillance_data.py.
        Supports incremental loading via `since_date`.

        Args:
            vector_type: Type of vector ('mosquitoes', 'ticks', 'rodents')
            region: Geographic region
            since_date: Optional ISO-8601 date string to filter observations (e.g., '2026-01-01')

        Returns:
            DataFrame with columns: date, location, species, latitude, longitude
        """
        # Support both singular and plural file name conventions
        candidates = [
            self.data_dir / f"inaturalist_{vector_type}s_{region}.json",   # plural (ticks)
            self.data_dir / f"inaturalist_{vector_type}_{region}.json",    # singular (tick)
            self.data_dir / f"inat_{vector_type}_{region}.csv",
        ]

        df = None
        for path in candidates:
            if path.exists():
                if path.suffix == ".json":
                    with open(path) as f:
                        data = json.load(f)
                    df = pd.DataFrame(data.get("data", []))
                else:
                    df = pd.read_csv(path)
                if not df.empty:
                    break

        if df is None or df.empty:
            return pd.DataFrame(columns=["date", "location", "species", "latitude", "longitude"])

        # Normalise date column
        if "observed_on" in df.columns:
            df["date"] = pd.to_datetime(df["observed_on"], errors="coerce")
        elif "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Incremental filter
        if since_date is not None and "date" in df.columns:
            cutoff = pd.to_datetime(since_date, errors="coerce")
            if cutoff is not pd.NaT:
                df = df[df["date"] >= cutoff]

        # Normalise lat/lon column names
        for lat_col in ("lat", "latitude"):
            if lat_col in df.columns and "latitude" not in df.columns:
                df["latitude"] = pd.to_numeric(df[lat_col], errors="coerce")
        for lon_col in ("lon", "longitude"):
            if lon_col in df.columns and "longitude" not in df.columns:
                df["longitude"] = pd.to_numeric(df[lon_col], errors="coerce")

        # Normalise species column
        for sp_col in ("taxon", "taxon_name", "species_guess"):
            if sp_col in df.columns and "species" not in df.columns:
                df["species"] = df[sp_col]
                break

        self.metadata[f"inat_{vector_type}_{region}"] = {
            "source": "iNaturalist",
            "vector_type": vector_type,
            "region": region,
            "records": len(df),
            "date_range": (df["date"].min(), df["date"].max()) if "date" in df.columns else None,
        }

        return df

    # ------------------------------------------------------------------
    # Remaining loaders (tick, USGS)
    # ------------------------------------------------------------------

    def load_tick_surveillance_data(self, region: str) -> pd.DataFrame:
        """
        Load local/state tick surveillance data (collection counts, pool testing).

        Args:
            region: Geographic region

        Returns:
            DataFrame with tick surveillance metrics
        """
        candidates = [
            self.data_dir / f"tick_surveillance_{region}.json",
            self.data_dir / f"tick_traps_{region}.csv",
        ]

        df = None
        for path in candidates:
            if path.exists():
                if path.suffix == ".json":
                    with open(path) as f:
                        data = json.load(f)
                    df = pd.DataFrame(data.get("data", []))
                else:
                    df = pd.read_csv(path)
                break

        if df is None or df.empty:
            return pd.DataFrame()

        self.metadata[f"tick_surveillance_{region}"] = {
            "source": "State Vector Control / Public Health",
            "region": region,
            "records": len(df),
        }

        return df

    def load_usgs_ecological_data(
        self,
        region: str,
        data_type: str = "habitat_suitability"
    ) -> pd.DataFrame:
        """
        Load USGS ecological and habitat data.

        Args:
            region: Geographic region
            data_type: Type of data ('habitat_suitability', 'water_bodies', 'elevation', etc.)

        Returns:
            DataFrame with ecological data
        """
        path = self.data_dir / f"usgs_{data_type}_{region}.geojson"

        if not path.exists():
            return pd.DataFrame()

        with open(path) as f:
            geojson = json.load(f)

        features = geojson.get("features", [])
        df = pd.DataFrame([f.get("properties", {}) for f in features])

        self.metadata[f"usgs_{data_type}_{region}"] = {
            "source": "USGS",
            "data_type": data_type,
            "region": region,
            "records": len(df),
        }

        return df

    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata for all loaded datasets."""
        return self.metadata
