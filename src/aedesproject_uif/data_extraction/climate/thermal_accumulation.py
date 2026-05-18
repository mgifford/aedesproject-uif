"""Thermal accumulation calculations for vector development models.

Growing Degree Days (GDD) is the primary metric for predicting when vectors
will reach developmentally significant life stages (nymph emergence, adult
emergence, etc.). This module calculates cumulative GDD and flags periods of
high disease risk based on thermal advancement.
"""

import pandas as pd
from datetime import datetime, date
from typing import Dict, Tuple, Optional


# Vector-specific thermal thresholds (base temperatures in °C)
THERMAL_THRESHOLDS = {
    "ixodes_scapularis": {
        "base_temp": 10,  # Developmental threshold
        "min_survival": 0,  # Below this, ticks die
        "activity_threshold": 7,  # Below this, minimal activity
        "optimal_range": (15, 20),  # Fastest development
        "stress_temperature": 25,  # Heat stress begins
        "milestones": {
            "nymph_emergence": 300,  # GDD to peak nymph activity
            "peak_nymph_activity": 500,  # May-June peak in Colorado
            "adult_emergence": 800,  # Fall adults
        }
    },
    "culex_mosquito": {
        "base_temp": 10,
        "min_survival": 5,
        "activity_threshold": 13,
        "optimal_range": (25, 30),
        "stress_temperature": 35,  # Heat stress for mosquitoes
        "milestones": {
            "egg_hatch": 100,
            "development_complete": 300,  # Egg to adult in summer
            "wnv_transmission": 18,  # Virus replicates above this
        }
    },
    "dermacentor_tick": {
        "base_temp": 10,
        "min_survival": -5,  # Slightly hardier than Ixodes
        "activity_threshold": 10,
        "optimal_range": (15, 22),
        "stress_temperature": 28,
        "milestones": {
            "spring_emergence": 200,
            "peak_activity": 400,  # Earlier than Ixodes
            "adult_peak": 700,
        }
    }
}


def calculate_gdd(
    min_temp_c: float,
    max_temp_c: float,
    base_temp_c: float = 10
) -> float:
    """Calculate Growing Degree Days for a single day.
    
    Args:
        min_temp_c: Daily minimum temperature in Celsius
        max_temp_c: Daily maximum temperature in Celsius
        base_temp_c: Base threshold temperature (default 10°C)
    
    Returns:
        GDD value for the day (0 if below threshold)
    
    Formula:
        GDD = ((T_max + T_min) / 2) - T_base
    """
    mean_temp = (max_temp_c + max_temp_c) / 2
    gdd = max(0, mean_temp - base_temp_c)
    return gdd


def cumulative_gdd_from_start_of_year(
    daily_temps_df: pd.DataFrame,
    base_temp_c: float = 10,
    start_month: int = 1,
    start_day: int = 1
) -> pd.DataFrame:
    """Calculate cumulative GDD from the start of the specified date.
    
    Args:
        daily_temps_df: DataFrame with columns ['date', 'min_temp_c', 'max_temp_c']
        base_temp_c: Base threshold temperature
        start_month: Month to start accumulation (1-12)
        start_day: Day to start accumulation (1-31)
    
    Returns:
        DataFrame with added columns: ['gdd_daily', 'gdd_cumulative']
    
    Example:
        >>> df = pd.DataFrame({
        ...     'date': pd.date_range('2026-01-01', periods=150),
        ...     'min_temp_c': 2,
        ...     'max_temp_c': 12
        ... })
        >>> result = cumulative_gdd_from_start_of_year(df, start_month=3)
        >>> print(result[result['date'] == '2026-05-20'].gdd_cumulative.values)
    """
    df = daily_temps_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate daily GDD
    df['gdd_daily'] = df.apply(
        lambda row: calculate_gdd(
            row['min_temp_c'],
            row['max_temp_c'],
            base_temp_c
        ),
        axis=1
    )
    
    # Filter to start date onwards
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['year'] = df['date'].dt.year
    
    # Reset cumulative at start of each year
    df['gdd_cumulative'] = 0.0
    
    for year in df['year'].unique():
        year_mask = df['year'] == year
        year_df = df[year_mask].copy()
        
        # Find start index within this year
        start_mask = (year_df['month'] >= start_month) & (year_df['day'] >= start_day)
        start_idx = year_df[start_mask].index.min()
        
        if pd.notna(start_idx):
            year_df_filtered = year_df[year_df.index >= start_idx].copy()
            year_df_filtered['gdd_cumulative'] = year_df_filtered['gdd_daily'].cumsum()
            df.loc[year_df_filtered.index, 'gdd_cumulative'] = year_df_filtered['gdd_cumulative']
    
    return df[['date', 'min_temp_c', 'max_temp_c', 'gdd_daily', 'gdd_cumulative']]


def days_to_gdd_milestone(
    cumulative_gdd: float,
    daily_gdd_forecast: list,
    target_gdd: float
) -> int:
    """Estimate days until a GDD milestone is reached.
    
    Args:
        cumulative_gdd: Current cumulative GDD
        daily_gdd_forecast: List of forecasted daily GDD values
        target_gdd: Target cumulative GDD (e.g., 500 for nymph emergence)
    
    Returns:
        Number of days until target is reached
    """
    if cumulative_gdd >= target_gdd:
        return 0
    
    remaining_gdd = target_gdd - cumulative_gdd
    days = 0
    
    for daily in daily_gdd_forecast:
        days += 1
        remaining_gdd -= daily
        if remaining_gdd <= 0:
            return days
    
    return len(daily_gdd_forecast)  # Won't reach within forecast window


def gdd_advancement_score(
    current_gdd: float,
    historical_gdd_avg: float,
    date_percentile: float = 0.5
) -> float:
    """Calculate disease risk score based on GDD advancement.
    
    Args:
        current_gdd: Current cumulative GDD for the date
        historical_gdd_avg: Historical average GDD for this date
        date_percentile: Position in year (0-1)
    
    Returns:
        Risk score (0-1), where:
        - 0.0: On schedule or behind
        - 0.5: 1-2 weeks early
        - 1.0: 2+ weeks early (high risk)
    """
    if current_gdd < historical_gdd_avg:
        return 0.0
    
    advancement = current_gdd - historical_gdd_avg
    
    # Estimate days advancement (assuming ~10 GDD per day in May)
    days_early = advancement / 15  # Conservative estimate
    
    # Score: 0 = on time, 14 days early = 1.0
    score = min(1.0, days_early / 14)
    
    return score


def winter_survival_score(
    min_winter_temp: float,
    min_consecutive_days: int = 7
) -> float:
    """Estimate tick survival through winter based on minimum temperature.
    
    Args:
        min_winter_temp: Coldest temperature recorded (°C)
        min_consecutive_days: Number of consecutive days at that temp
    
    Returns:
        Survival score (0-1):
        - 0.0: Severe winter (-25°C+), high mortality
        - 0.5: Moderate winter (-15 to -5°C)
        - 1.0: Mild winter (>-5°C), high survival
    
    Reference: Eisen et al. 2016 - Ixodes survival correlates with winter severity
    """
    # Harsh freeze mortality increases exponentially below -15°C
    if min_winter_temp < -20:
        base_survival = 0.1
    elif min_winter_temp < -15:
        base_survival = 0.3
    elif min_winter_temp < -10:
        base_survival = 0.5
    elif min_winter_temp < -5:
        base_survival = 0.7
    else:
        base_survival = 0.9
    
    # Duration factor: sustained cold increases mortality
    if min_consecutive_days >= 10:
        duration_factor = 1.0  # Full effect
    else:
        duration_factor = min_consecutive_days / 10
    
    return base_survival * duration_factor


if __name__ == "__main__":
    # Example: Calculate GDD for Denver 2026
    import numpy as np
    
    # Create sample data (150 days from Mar 1)
    dates = pd.date_range("2026-03-01", periods=150, freq="D")
    temps = pd.DataFrame({
        "date": dates,
        "min_temp_c": np.random.normal(8, 5, 150),  # Spring temps
        "max_temp_c": np.random.normal(15, 5, 150),
    })
    
    # Calculate GDD
    result = cumulative_gdd_from_start_of_year(temps, start_month=3, start_day=1)
    print(result.tail(20))
    print(f"\nCumulative GDD by May 28: {result[result['date'] == '2026-05-28'].gdd_cumulative.values}")
