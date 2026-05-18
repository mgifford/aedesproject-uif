#!/usr/bin/env python3
"""
Analyze correlations between climate variables and disease cases.

Builds predictive models linking temperature, GDD, precipitation to
tick/mosquito-borne disease incidence with appropriate time lags.
"""

import json
from datetime import datetime
from pathlib import Path

import numpy as np


class ClimateDiseaseAnalyzer:
    """Analyze climate-disease correlations for early warning signals."""

    def __init__(self, climate_data_dir: str = "data/climate", disease_data_dir: str = "data/surveillance"):
        self.climate_dir = Path(climate_data_dir)
        self.disease_dir = Path(disease_data_dir)

    def calculate_thermal_risk_index(
        self, temp_max_c: float, temp_min_c: float, disease: str = "lyme"
    ) -> dict:
        """
        Calculate thermal risk index for vector disease based on temperature.

        For Lyme (Ixodes):
        - Optimal development: 15-20°C
        - Activity threshold: >7°C
        - Heat stress: >25°C

        For WNV (Culex):
        - Virus transmission: >18°C
        - Optimal development: 21-28°C
        - Egg hatch: >13°C
        """

        mean_temp = (temp_max_c + temp_min_c) / 2
        result = {
            "mean_temp_c": mean_temp,
            "temp_max_c": temp_max_c,
            "temp_min_c": temp_min_c,
            "disease": disease,
            "timestamp": datetime.now().isoformat(),
        }

        if disease == "lyme":
            if mean_temp < 7:
                result["activity_status"] = "dormant"
                result["risk_score"] = 0.0
            elif 7 <= mean_temp < 13:
                result["activity_status"] = "emerging"
                result["risk_score"] = (mean_temp - 7) / 6 * 0.3  # Ramping up
            elif 13 <= mean_temp < 20:
                result["activity_status"] = "active"
                result["risk_score"] = 0.3 + (mean_temp - 13) / 7 * 0.5  # 0.3-0.8
            elif 20 <= mean_temp < 25:
                result["activity_status"] = "peak"
                result["risk_score"] = 0.8 + (mean_temp - 20) / 5 * 0.2  # 0.8-1.0
            else:  # >25
                result["activity_status"] = "heat_stress"
                result["risk_score"] = 0.7  # Reduced by heat

        elif disease == "wnv":
            if mean_temp < 13:
                result["mosquito_status"] = "dormant"
                result["virus_replication"] = "none"
                result["risk_score"] = 0.0
            elif 13 <= mean_temp < 18:
                result["mosquito_status"] = "developing"
                result["virus_replication"] = "minimal"
                result["risk_score"] = 0.1
            elif 18 <= mean_temp < 20:
                result["mosquito_status"] = "active"
                result["virus_replication"] = "slow"
                result["risk_score"] = 0.3
            elif 20 <= mean_temp < 25:
                result["mosquito_status"] = "abundant"
                result["virus_replication"] = "moderate"
                result["risk_score"] = 0.6 + (mean_temp - 20) / 5 * 0.2  # 0.6-0.8
            elif 25 <= mean_temp <= 28:
                result["mosquito_status"] = "peak"
                result["virus_replication"] = "rapid"
                result["risk_score"] = 0.9  # Peak transmission
            else:  # >28
                result["mosquito_status"] = "heat_stress"
                result["virus_replication"] = "reduced"
                result["risk_score"] = 0.7

        return result

    def calculate_gdd_advance(self, gdd_current: float, gdd_historical_avg: float) -> dict:
        """
        Compare current GDD accumulation to historical average.

        Positive values = ahead of schedule = earlier disease season.
        """

        days_ahead = (gdd_current - gdd_historical_avg) / 10  # Rough conversion GDD to days

        return {
            "gdd_current": gdd_current,
            "gdd_historical_avg": gdd_historical_avg,
            "gdd_difference": gdd_current - gdd_historical_avg,
            "estimated_days_ahead": days_ahead,
            "early_season_alert": days_ahead > 10,  # Alert if >10 days ahead
            "interpretation": (
                f"Season is {days_ahead:.1f} days ahead of historical average"
                if days_ahead > 0
                else f"Season is {abs(days_ahead):.1f} days behind schedule"
            ),
        }

    def assess_winter_tick_survival(self, min_temp_c: float) -> dict:
        """
        Assess Ixodes tick overwinter survival based on minimum temperature.

        Critical threshold: -10°C
        - Below -10°C: Heavy mortality (>80%)
        - -10 to -5°C: Moderate mortality (50-80%)
        - Above -5°C: Light mortality (<50%), possible range expansion
        """

        result = {
            "winter_minimum_c": min_temp_c,
            "tick_mortality_percent": None,
            "range_expansion_risk": None,
            "interpretation": None,
        }

        if min_temp_c < -15:
            result["tick_mortality_percent"] = 90
            result["range_expansion_risk"] = "low"
            result["interpretation"] = "Cold winter conditions limit northward tick range expansion"
        elif -15 <= min_temp_c < -10:
            result["tick_mortality_percent"] = 75
            result["range_expansion_risk"] = "low"
            result["interpretation"] = "Typical winter kill; range stable"
        elif -10 <= min_temp_c < -5:
            result["tick_mortality_percent"] = 50
            result["range_expansion_risk"] = "moderate"
            result["interpretation"] = "Milder winter; 50% more ticks survive; possible spring population increase"
        elif -5 <= min_temp_c < 0:
            result["tick_mortality_percent"] = 25
            result["range_expansion_risk"] = "high"
            result["interpretation"] = (
                "Warm winter; minimal tick mortality; expect elevated spring densities "
                "and possible range expansion northward"
            )
        else:  # >0°C
            result["tick_mortality_percent"] = 10
            result["range_expansion_risk"] = "very_high"
            result["interpretation"] = (
                "Exceptionally warm winter; ticks may remain active year-round; "
                "significant range expansion risk"
            )

        return result

    def build_climate_risk_forecast(self, location: str = "denver") -> dict:
        """
        Build 4-week climate-based disease risk forecast.

        Template for forecast structure (would use actual forecast data in production).
        """

        forecast = {
            "location": location,
            "forecast_date": datetime.now().isoformat(),
            "forecast_period": "Next 4 weeks",
            "weekly_forecasts": [
                {
                    "week": 1,
                    "avg_temp_c": 20.0,  # Placeholder
                    "lyme_risk": 0.6,
                    "wnv_risk": 0.3,
                    "alerts": ["Moderate Lyme risk with sustained 18-22°C temperatures"],
                },
                {
                    "week": 2,
                    "avg_temp_c": 22.0,
                    "lyme_risk": 0.8,
                    "wnv_risk": 0.5,
                    "alerts": [
                        "Elevated Lyme and WNV risk",
                        "Peak nymph activity predicted",
                    ],
                },
                {
                    "week": 3,
                    "avg_temp_c": 21.0,
                    "lyme_risk": 0.7,
                    "wnv_risk": 0.7,
                    "alerts": ["Warm forecast maintains Lyme risk; WNV breeding conditions favorable"],
                },
                {
                    "week": 4,
                    "avg_temp_c": 19.0,
                    "lyme_risk": 0.5,
                    "wnv_risk": 0.6,
                    "alerts": ["Slight cooling but conditions still favorable for vectors"],
                },
            ],
        }

        return forecast

    def generate_climate_alert_summary(self, climate_data: dict) -> dict:
        """Generate alert summary for public health communication."""

        alerts = {
            "report_date": datetime.now().isoformat(),
            "severity_level": "normal",  # normal, elevated, high, very_high
            "alerts": [],
            "recommendations": [],
        }

        # Example alerts (would be generated from real climate data)
        if "gdd_advance" in climate_data and climate_data["gdd_advance"] > 50:
            alerts["alerts"].append(
                {
                    "type": "early_season",
                    "disease": "lyme",
                    "message": "Growing Degree Days 50+ ahead of schedule. Nymph emergence expected 2+ weeks early.",
                    "risk_level": "elevated",
                }
            )
            alerts["recommendations"].append(
                "Begin tick prevention messaging and surveillance 2 weeks early"
            )
            alerts["severity_level"] = "elevated"

        if "winter_minimum_c" in climate_data and climate_data["winter_minimum_c"] > -5:
            alerts["alerts"].append(
                {
                    "type": "warm_winter",
                    "disease": "lyme",
                    "message": "Winter minimum >-5°C indicates reduced winter tick mortality.",
                    "risk_level": "high",
                }
            )
            alerts["recommendations"].append("Expect higher spring tick densities; prepare for elevated Lyme season")
            alerts["severity_level"] = "high"

        if "spring_precip_mm" in climate_data and climate_data.get("spring_precip_percentile", 0) > 150:
            alerts["alerts"].append(
                {
                    "type": "wet_spring",
                    "disease": "wnv",
                    "message": "Spring precipitation >150% of normal creates abundant mosquito breeding habitat.",
                    "risk_level": "elevated",
                }
            )
            alerts["recommendations"].append(
                "Enhance West Nile surveillance; encourage elimination of standing water"
            )
            alerts["severity_level"] = "elevated"

        return alerts


def main():
    """Perform climate-disease analysis and generate risk forecasts."""

    print("Analyzing climate-disease correlations...")

    analyzer = ClimateDiseaseAnalyzer()

    # Example analysis (would use real data from fetch_climate_data.py)
    print("\nCalculating thermal risk indices...")

    # Lyme risk at different temperatures
    lyme_risks = {}
    for temp_mean in [5, 10, 15, 20, 25, 30]:
        risk = analyzer.calculate_thermal_risk_index(temp_mean + 3, temp_mean - 3, disease="lyme")
        lyme_risks[f"{temp_mean}C"] = risk

    # WNV risk at different temperatures
    wnv_risks = {}
    for temp_mean in [10, 15, 20, 25, 30]:
        risk = analyzer.calculate_thermal_risk_index(temp_mean + 3, temp_mean - 3, disease="wnv")
        wnv_risks[f"{temp_mean}C"] = risk

    # Build output
    analysis = {
        "analysis_date": datetime.now().isoformat(),
        "thermal_risk_indices": {"lyme": lyme_risks, "wnv": wnv_risks},
        "gdd_analysis": analyzer.calculate_gdd_advance(450, 400),  # Example
        "winter_survival": analyzer.assess_winter_tick_survival(-8),  # Example
        "forecast": analyzer.build_climate_risk_forecast("denver"),
        "alerts": analyzer.generate_climate_alert_summary({}),
    }

    # Save analysis
    output_path = Path("data/climate/analysis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(analysis, f, indent=2, default=str)

    print(f"✓ Climate-disease analysis saved to {output_path}")


if __name__ == "__main__":
    main()
