"""
Ecological feature engineering for vector-borne disease surveillance.

Computes vector habitat suitability, phenology, climate indices, and
environmental features for risk modeling.
"""

from typing import Optional, Tuple
import numpy as np
import pandas as pd

from .registry import VectorType, DiseaseVectorRegistry


class EcologicalFeatureEngine:
    """
    Feature engineering for ecological and environmental surveillance features.
    
    Computes:
    - Vector habitat suitability indices
    - Phenology and seasonal timing
    - Climate anomalies and thermal indices
    - Environmental condition features
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
        base_temp: float = 10.0
    ) -> pd.Series:
        """
        Compute accumulated growing degree days (GDD).
        
        Used for phenology prediction (tick/mosquito development timing).
        
        Args:
            temp_series: Series of daily mean temperatures (°C)
            base_temp: Base temperature threshold for development
        
        Returns:
            Series with cumulative GDD
        """
        daily_gdd = (temp_series - base_temp).clip(lower=0)
        cumulative_gdd = daily_gdd.cumsum()
        return cumulative_gdd
    
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
        
        Args:
            climate_df: DataFrame with columns: date, temp_c, humidity_percent (optional)
            weights: Optional dict with weights for each component:
                    {'thermal': 0.6, 'humidity': 0.3, 'season': 0.1}
        
        Returns:
            Series with combined habitat suitability (0-1)
        """
        if weights is None:
            weights = {'thermal': 0.6, 'humidity': 0.3, 'season': 0.1}
        
        combined = pd.Series(0, index=climate_df.index, dtype=float)
        
        # Thermal component
        if 'temp_c' in climate_df.columns:
            thermal = self.compute_thermal_suitability(climate_df['temp_c'])
            combined += weights.get('thermal', 0) * thermal
        
        # Humidity component
        if 'humidity_percent' in climate_df.columns:
            humidity = self.compute_humidity_suitability(climate_df['humidity_percent'])
            combined += weights.get('humidity', 0) * humidity
        else:
            # If humidity not available, use proxy from precipitation/vegetation
            combined += weights.get('humidity', 0) * 0.5  # Neutral proxy
        
        # Seasonal component
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
            climate_df: DataFrame with 'temp_c' column
            historical_mean: Historical mean temperature (°C)
            historical_std: Historical standard deviation
        
        Returns:
            Series with standardized anomaly (z-score like)
        """
        if historical_std == 0:
            return pd.Series(0, index=climate_df.index)
        
        anomaly = (climate_df['temp_c'] - historical_mean) / historical_std
        return anomaly
