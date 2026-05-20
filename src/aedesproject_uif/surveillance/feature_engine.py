"""
Ecological feature engineering for vector-borne disease surveillance.

Computes vector habitat suitability, phenology, climate indices, and
environmental features for risk modeling.

Includes Open-Meteo integration for live 30-day climate indicators.
"""

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from .registry import VectorType, DiseaseVectorRegistry


# ---------------------------------------------------------------------------
# Colorado bounding box for spatial queries
# ---------------------------------------------------------------------------
COLORADO_BBOX = {
    "lat_min": 37.0, "lat_max": 41.0,
    "lon_min": -109.0, "lon_max": -102.0,
    "centroid_lat": 39.1, "centroid_lon": -105.4,   # geographic centre of CO
    "denver_lat": 39.74, "denver_lon": -104.99,
}


def fetch_open_meteo_climate(
    latitude: float = COLORADO_BBOX["denver_lat"],
    longitude: float = COLORADO_BBOX["denver_lon"],
    past_days: int = 30,
    retries: int = 3,
    backoff: float = 2.0,
) -> pd.DataFrame:
    """
    Fetch daily climate data from the Open-Meteo free, keyless API.

    Retrieves temperature (min/max), precipitation, and relative humidity
    for the past *past_days* days.  Falls back to an empty DataFrame if
    the API is unavailable.

    Args:
        latitude: Location latitude (default: Denver, CO centroid)
        longitude: Location longitude (default: Denver, CO centroid)
        past_days: Days of history to retrieve (max 92 for free tier)
        retries: Number of retry attempts on failure
        backoff: Exponential back-off base in seconds

    Returns:
        DataFrame with columns:
            date, temp_max_c, temp_min_c, temp_mean_c,
            humidity_mean_pct, precip_mm
    """
    end_date = datetime.utcnow().date()
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

    headers = {"User-Agent": "AEDES-Surveillance/2.0"}
    raw: Optional[bytes] = None

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read()
            break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            if attempt < retries - 1:
                time.sleep(backoff ** attempt)

    if raw is None:
        return pd.DataFrame(columns=[
            "date", "temp_max_c", "temp_min_c", "temp_mean_c",
            "humidity_mean_pct", "precip_mm",
        ])

    try:
        payload = json.loads(raw)
        daily = payload.get("daily", {})
        dates = daily.get("time", [])
        if not dates:
            raise ValueError("Empty daily data in Open-Meteo response")

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
        return df.dropna(subset=["date"]).reset_index(drop=True)

    except (json.JSONDecodeError, KeyError, ValueError):
        return pd.DataFrame(columns=[
            "date", "temp_max_c", "temp_min_c", "temp_mean_c",
            "humidity_mean_pct", "precip_mm",
        ])


class EcologicalFeatureEngine:
    """
    Feature engineering for ecological and environmental surveillance features.

    Computes:
    - Vector habitat suitability indices
    - Phenology and seasonal timing
    - Climate anomalies and thermal indices (GDD, precipitation anomaly)
    - Environmental condition features from Open-Meteo live data
    """

    def __init__(self, vector_type: VectorType):
        """
        Initialize feature engine for a specific vector type.

        Args:
            vector_type: Type of vector (mosquito, tick, rodent, etc.)
        """
        self.vector_type = vector_type
        self.ecology = DiseaseVectorRegistry.get_vector_ecology(vector_type)

    def compute_thermal_suitability(
        self,
        temp_series: pd.Series,
        window_days: int = 14
    ) -> pd.Series:
        """
        Compute thermal suitability index for the vector.

        Based on temperature thresholds and optimal ranges for vector activity.

        Args:
            temp_series: Series of daily temperatures (°C)
            window_days: Rolling window size for smoothing

        Returns:
            Series with values 0-1 indicating thermal suitability
        """
        min_temp = self.ecology.temperature_min_c
        max_temp = self.ecology.temperature_max_c
        peak_temp = self.ecology.temperature_peak_c

        # Piecewise linear suitability
        suitability = np.zeros_like(temp_series, dtype=float)

        # Below minimum: 0
        suitability = np.where(temp_series < min_temp, 0, suitability)

        # Min to peak: linear ramp up
        in_ramp_up = (temp_series >= min_temp) & (temp_series < peak_temp)
        suitability[in_ramp_up] = (temp_series[in_ramp_up] - min_temp) / (peak_temp - min_temp) * 0.8

        # Peak to max: linear ramp down
        in_ramp_down = (temp_series >= peak_temp) & (temp_series <= max_temp)
        suitability[in_ramp_down] = 0.8 - (temp_series[in_ramp_down] - peak_temp) / (max_temp - peak_temp) * 0.8

        # Above maximum: 0
        suitability = np.where(temp_series > max_temp, 0, suitability)

        suitability_series = pd.Series(suitability, index=temp_series.index)

        # Rolling average for smoothing
        if window_days > 1:
            suitability_series = suitability_series.rolling(window=window_days, center=True).mean()

        return suitability_series.clip(0, 1)

    def compute_growing_degree_days(
        self,
        temp_series: pd.Series,
        base_temp: float = 10.0,
    ) -> pd.Series:
        """
        Compute accumulated growing degree days (GDD).

        Used for phenology prediction (tick/mosquito development timing).
        For *Dermacentor andersoni* the published base temperature is ~10 °C.
        Accumulated GDD > ~200 correlates with peak nymphal activity in CO.

        Args:
            temp_series: Series of daily mean temperatures (°C)
            base_temp: Base temperature threshold for development

        Returns:
            Series with cumulative GDD
        """
        daily_gdd = (temp_series - base_temp).clip(lower=0)
        return daily_gdd.cumsum()

    def compute_gdd_activity_multiplier(
        self,
        cumulative_gdd: pd.Series,
        gdd_onset: float = 50.0,
        gdd_peak: float = 200.0,
        gdd_decline: float = 500.0,
    ) -> pd.Series:
        """
        Map cumulative GDD to a tick-questing activity multiplier (0–1).

        Replaces the static calendar month weight used in earlier versions.
        Default thresholds match *Dermacentor andersoni* phenology in Colorado:
        - GDD < onset : pre-emergence (multiplier → 0)
        - onset–peak  : rapid ramp-up
        - peak–decline: gradual decline (summer heat suppression)
        - > decline   : near-zero questing (heat quiescence)

        Args:
            cumulative_gdd: Series of accumulated GDD values
            gdd_onset: GDD threshold for activity onset
            gdd_peak: GDD at maximum activity
            gdd_decline: GDD at which activity declines to near-zero

        Returns:
            Series with activity multiplier (0–1)
        """
        multiplier = pd.Series(0.0, index=cumulative_gdd.index)

        ramp_up = (cumulative_gdd >= gdd_onset) & (cumulative_gdd < gdd_peak)
        multiplier[ramp_up] = (
            (cumulative_gdd[ramp_up] - gdd_onset) / (gdd_peak - gdd_onset)
        ).clip(0, 1)

        at_peak = (cumulative_gdd >= gdd_peak) & (cumulative_gdd < gdd_decline)
        multiplier[at_peak] = (
            1.0 - (cumulative_gdd[at_peak] - gdd_peak) / (gdd_decline - gdd_peak)
        ).clip(0, 1)

        return multiplier.clip(0, 1)

    def compute_humidity_suitability(
        self,
        humidity_series: pd.Series,
        window_days: int = 7
    ) -> pd.Series:
        """
        Compute humidity suitability for the vector.

        Args:
            humidity_series: Series of relative humidity (percent, 0-100)
            window_days: Rolling window for smoothing

        Returns:
            Series with values 0-1 indicating humidity suitability
        """
        min_humidity = self.ecology.humidity_min_percent

        # Suitability increases with humidity above minimum
        suitability = np.clip((humidity_series - min_humidity) / (100 - min_humidity), 0, 1)
        suitability_series = pd.Series(suitability, index=humidity_series.index)

        if window_days > 1:
            suitability_series = suitability_series.rolling(window=window_days, center=True).mean()

        return suitability_series.clip(0, 1)

    def compute_precipitation_anomaly(
        self,
        precip_series: pd.Series,
        historical_mean_mm: float = 1.5,
        historical_std_mm: float = 2.0,
        window_days: int = 14,
    ) -> pd.Series:
        """
        Compute rolling precipitation anomaly (z-score) vs. historical baseline.

        Positive values indicate anomalously wet conditions (may increase humidity-
        dependent tick survival); extreme negatives suggest drought stress.

        Args:
            precip_series: Daily precipitation in mm
            historical_mean_mm: Historical daily mean precipitation for the region/season
            historical_std_mm: Historical standard deviation
            window_days: Rolling sum window in days

        Returns:
            Series of z-score anomalies (rolling sum vs. long-term normal)
        """
        rolling_sum = precip_series.rolling(window=window_days, min_periods=1).sum()
        expected = historical_mean_mm * window_days
        std_sum = historical_std_mm * (window_days ** 0.5)
        if std_sum == 0:
            return pd.Series(0.0, index=precip_series.index)
        return (rolling_sum - expected) / std_sum

    def compute_activity_window(
        self,
        dates: pd.DatetimeIndex
    ) -> pd.Series:
        """
        Compute seasonal activity window (0 outside season, 1 during season).

        Args:
            dates: DatetimeIndex for activity window

        Returns:
            Series with values 0-1 indicating activity window
        """
        start_month = self.ecology.activity_season[0]
        end_month = self.ecology.activity_season[1]

        months = dates.month

        if start_month <= end_month:
            in_season = (months >= start_month) & (months <= end_month)
        else:
            # Wraps across year boundary (e.g., Oct-Feb)
            in_season = (months >= start_month) | (months <= end_month)

        return pd.Series(in_season.astype(int), index=dates)

    def compute_combined_habitat_suitability(
        self,
        climate_df: pd.DataFrame,
        weights: Optional[dict] = None
    ) -> pd.Series:
        """
        Compute combined habitat suitability index.

        Integrates thermal, humidity, seasonal, and other factors.
        If *climate_df* contains a ``gdd`` column the GDD activity multiplier
        replaces the flat seasonal binary.

        Args:
            climate_df: DataFrame with columns: date, temp_c or temp_mean_c,
                        humidity_percent or humidity_mean_pct (optional), gdd (optional)
            weights: Optional dict with weights for each component:
                    {'thermal': 0.6, 'humidity': 0.3, 'season': 0.1}

        Returns:
            Series with combined habitat suitability (0-1)
        """
        if weights is None:
            weights = {'thermal': 0.6, 'humidity': 0.3, 'season': 0.1}

        combined = pd.Series(0.0, index=climate_df.index)

        # Thermal component — prefer temp_mean_c, fall back to temp_c
        temp_col = next((c for c in ("temp_mean_c", "temp_c") if c in climate_df.columns), None)
        if temp_col:
            thermal = self.compute_thermal_suitability(climate_df[temp_col])
            combined += weights.get('thermal', 0) * thermal

        # Humidity component — prefer humidity_mean_pct, fall back to humidity_percent
        hum_col = next((c for c in ("humidity_mean_pct", "humidity_percent") if c in climate_df.columns), None)
        if hum_col:
            humidity = self.compute_humidity_suitability(climate_df[hum_col])
            combined += weights.get('humidity', 0) * humidity
        else:
            combined += weights.get('humidity', 0) * 0.5  # Neutral proxy

        # Seasonal / GDD component
        if "gdd" in climate_df.columns:
            gdd_mult = self.compute_gdd_activity_multiplier(climate_df["gdd"])
            combined += weights.get('season', 0) * gdd_mult
        elif isinstance(climate_df.index, pd.DatetimeIndex):
            season = self.compute_activity_window(climate_df.index)
            combined += weights.get('season', 0) * season

        return combined.clip(0, 1)

    def compute_climate_anomaly_index(
        self,
        climate_df: pd.DataFrame,
        historical_mean: float,
        historical_std: float
    ) -> pd.Series:
        """
        Compute climate anomaly index (deviation from historical baseline).

        Values > 1 indicate unusually warm; < -1 indicate unusually cold.

        Args:
            climate_df: DataFrame with 'temp_c' or 'temp_mean_c' column
            historical_mean: Historical mean temperature (°C)
            historical_std: Historical standard deviation

        Returns:
            Series with standardized anomaly (z-score like)
        """
        if historical_std == 0:
            return pd.Series(0, index=climate_df.index)

        temp_col = next((c for c in ("temp_mean_c", "temp_c") if c in climate_df.columns), None)
        if temp_col is None:
            return pd.Series(0, index=climate_df.index)

        return (climate_df[temp_col] - historical_mean) / historical_std
