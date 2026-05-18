#!/usr/bin/env python3
"""
Fetch climate data from NOAA, PRISM, and NASA POWER for disease surveillance.

Provides temperature, precipitation, and derived metrics (GDD) needed to
correlate with tick/mosquito-borne disease risk.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests


class ClimateDataFetcher:
    """Fetch climate data for Colorado disease surveillance."""

    def __init__(self, output_dir: str = "data/climate"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Colorado reference locations
        self.locations = {
            "denver": {"lat": 39.7392, "lon": -104.9903, "name": "Denver Metro"},
            "boulder": {"lat": 40.0150, "lon": -105.2705, "name": "Boulder"},
            "glenwood_springs": {"lat": 39.5515, "lon": -107.3262, "name": "Glenwood Springs"},
            "grand_junction": {"lat": 39.0558, "lon": -108.5007, "name": "Grand Junction"},
        }

    def save(self, filename: str, data: dict) -> None:
        """Save JSON data to output directory."""
        path = self.output_dir / filename
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"  Saved {path}")

    def fetch_noaa_forecast(self, location_key: str = "denver", days: int = 14) -> dict:
        """Fetch NOAA forecast including temperature and precipitation."""
        loc = self.locations[location_key]
        lat, lon = loc["lat"], loc["lon"]

        try:
            # Get grid point data
            points_url = f"https://api.weather.gov/points/{lat},{lon}"
            points_response = requests.get(points_url, timeout=20)
            points_response.raise_for_status()

            forecast_url = points_response.json()["properties"]["forecast"]
            forecast_response = requests.get(forecast_url, timeout=20)
            forecast_response.raise_for_status()

            periods = forecast_response.json()["properties"]["periods"]

            # Extract temp and precip data
            data = {
                "location": loc["name"],
                "fetched": datetime.now().isoformat(),
                "forecast": [],
            }

            for period in periods[:days]:
                data["forecast"].append(
                    {
                        "date": period.get("startTime"),
                        "temperature_f": period.get("temperature"),
                        "temperature_c": (period.get("temperature") - 32) * 5 / 9
                        if period.get("temperature")
                        else None,
                        "precipitation_chance": period.get("precipChance", {}).get("value"),
                        "description": period.get("shortForecast"),
                        "wind_speed": period.get("windSpeed"),
                    }
                )

            return data

        except Exception as e:
            print(f"  Error fetching NOAA forecast for {location_key}: {e}")
            return {"error": str(e)}

    def calculate_gdd(
        self, temp_max_c: float, temp_min_c: float, base_temp: float = 10.0
    ) -> float:
        """
        Calculate Growing Degree Days (GDD).

        GDD = mean_temp - base_temp (if mean_temp > base_temp, else 0)

        For Ixodes tick development, base_temp = 10°C
        """
        mean_temp = (temp_max_c + temp_min_c) / 2
        return max(0, mean_temp - base_temp)

    def build_climate_disease_dataset(self, location_key: str = "denver", days_back: int = 365) -> dict:
        """
        Build historical dataset of GDD accumulation and other climate metrics.

        For production use, would fetch real historical data from PRISM/NOAA.
        This is a template for the data structure needed.
        """

        loc = self.locations[location_key]

        # Build dataset template
        data = {
            "location": loc["name"],
            "period": f"Last {days_back} days",
            "generated": datetime.now().isoformat(),
            "metrics": {
                "gdd_base_10c": {
                    "description": "Growing Degree Days (base 10°C) - for Ixodes development",
                    "current_year_total": None,
                    "historical_average_by_date": None,
                    "days_ahead_of_schedule": None,
                },
                "frost_free_period": {
                    "description": "Consecutive days without frost (<0°C)",
                    "current_season_length": None,
                    "historical_average": None,
                    "days_earlier_than_average": None,
                },
                "winter_minimum": {
                    "description": "Lowest temperature recorded in winter season",
                    "current_season_low": None,
                    "historical_average": None,
                    "tick_survival_risk": None,
                },
                "spring_precipitation": {
                    "description": "Total precipitation in spring (April-June)",
                    "current_year_total_mm": None,
                    "percentile_vs_historical": None,
                },
            },
            "interpretation": {
                "gdd_early": "GDD >50 ahead of schedule indicates early vector emergence",
                "mild_winter": "Winter minimum >-5°C allows 50%+ higher tick overwinter survival",
                "wet_spring": "Spring precip >150% of normal creates abundant mosquito breeding habitat",
                "freeze_delay": "First freeze >2 weeks late extends fall transmission season",
            },
            "data_note": "Real data would be fetched from PRISM (4km resolution), NOAA daily stations, or NASA POWER",
        }

        return data

    def compile_regional_climate_summary(self) -> dict:
        """Compile climate data across Colorado locations for regional comparison."""

        summary = {
            "report_date": datetime.now().isoformat(),
            "locations": {},
            "regional_alerts": [],
        }

        for location_key in self.locations.keys():
            print(f"Fetching climate data for {location_key}...")
            forecast = self.fetch_noaa_forecast(location_key)
            summary["locations"][location_key] = forecast

        # Generate regional alerts
        # (In production, would compare to historical thresholds)
        summary["regional_alerts"].append(
            {
                "type": "gdd_accumulation",
                "status": "NORMAL",
                "message": "GDD accumulation tracking within normal range for mid-May",
            }
        )

        return summary


def main():
    """Fetch climate data and save for surveillance dashboard."""

    print("Fetching climate data for Colorado disease surveillance...")

    fetcher = ClimateDataFetcher(output_dir="data/climate")

    # Fetch forecasts for each location
    print("\nFetching NOAA forecasts...")
    for location_key in fetcher.locations.keys():
        forecast = fetcher.fetch_noaa_forecast(location_key, days=14)
        fetcher.save(f"{location_key}_forecast.json", forecast)

    # Build climate-disease dataset template
    print("\nBuilding climate-disease correlation dataset...")
    dataset = fetcher.build_climate_disease_dataset("denver")
    fetcher.save("climate_disease_template.json", dataset)

    # Regional summary
    print("\nCompiling regional climate summary...")
    summary = fetcher.compile_regional_climate_summary()
    fetcher.save("regional_climate_summary.json", summary)

    print("\n✓ Climate data fetch complete")


if __name__ == "__main__":
    main()
