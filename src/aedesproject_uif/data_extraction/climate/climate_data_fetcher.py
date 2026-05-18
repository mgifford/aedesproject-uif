"""Climate data fetching from multiple sources.

Integrates:
- NASA POWER (temperature, precipitation, wind)
- NOAA (HRRR model, local weather data)
- USGS Phenology Network (spring indices, leaf-out dates)
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import json


class NASAPowerClient:
    """Fetch climate data from NASA POWER API.
    
    Available parameters:
    - T2M: Temperature at 2m
    - T2M_MAX: Daily maximum temperature
    - T2M_MIN: Daily minimum temperature
    - PRECTOTCORR: Corrected precipitation
    - WS10M: Wind speed at 10m
    - RH2M: Relative humidity at 2m
    """
    
    BASE_URL = "https://power.larc.nasa.gov/api/v1/temporal/daily/point"
    
    def __init__(self, latitude: float, longitude: float, community: str = "AG"):
        """Initialize NASA POWER client.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            community: Data community ("AG" for agriculture, default)
        """
        self.latitude = latitude
        self.longitude = longitude
        self.community = community
    
    def fetch_temperature_data(
        self,
        start_date: str,
        end_date: str,
        format_type: str = "json"
    ) -> Optional[pd.DataFrame]:
        """Fetch daily min/max temperature data.
        
        Args:
            start_date: Start date as YYYYMMDD
            end_date: End date as YYYYMMDD
            format_type: Output format (json or csv)
        
        Returns:
            DataFrame with columns: date, t_min, t_max (in Celsius)
        """
        params = {
            "parameters": "T2M_MIN,T2M_MAX",
            "community": self.community,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "start": start_date,
            "end": end_date,
            "format": format_type
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            # Parse NASA POWER response format
            properties = data.get("properties", {}).get("sis_t2m_min_daily_2d", {})
            if not properties:
                # Try alternative key
                properties = data.get("properties", {})
            
            # Convert to DataFrame
            df_list = []
            for key, value in properties.items():
                if key not in ["T2M_MIN", "T2M_MAX"]:
                    continue
                
            return self._parse_nasa_power_response(data)
        
        except Exception as e:
            print(f"Error fetching NASA POWER data: {e}")
            return None
    
    def _parse_nasa_power_response(self, data: Dict) -> pd.DataFrame:
        """Parse NASA POWER JSON response into DataFrame."""
        try:
            header = data.get("header", {})
            properties = data.get("properties", {})
            
            dates = []
            t_mins = []
            t_maxs = []
            
            for date_str, value in properties.get("T2M_MIN", {}).items():
                dates.append(datetime.strptime(date_str, "%Y%m%d"))
                t_mins.append(value)
            
            for date_str, value in properties.get("T2M_MAX", {}).items():
                t_maxs.append(value)
            
            return pd.DataFrame({
                "date": dates,
                "t_min_c": t_mins,
                "t_max_c": t_maxs
            }).sort_values("date")
        
        except Exception as e:
            print(f"Error parsing NASA POWER response: {e}")
            return pd.DataFrame()


class NOAAWeatherClient:
    """Fetch weather data from NOAA APIs."""
    
    POINTS_URL = "https://api.weather.gov/points"
    FORECAST_URL = "{points_url}/forecast"
    
    def __init__(self, latitude: float, longitude: float):
        """Initialize NOAA client for a specific location."""
        self.latitude = latitude
        self.longitude = longitude
        self.points_data = None
        self._fetch_points_data()
    
    def _fetch_points_data(self):
        """Get forecast URL for this location."""
        try:
            url = f"{self.POINTS_URL}/{self.latitude},{self.longitude}"
            response = requests.get(url, timeout=10, headers={"User-Agent": "AEDES/1.0"})
            response.raise_for_status()
            self.points_data = response.json()
        except Exception as e:
            print(f"Error fetching NOAA points data: {e}")
    
    def fetch_forecast(self) -> Optional[List[Dict]]:
        """Fetch 7-day forecast."""
        if not self.points_data:
            return None
        
        try:
            forecast_url = self.points_data["properties"]["forecast"]
            response = requests.get(forecast_url, timeout=10, headers={"User-Agent": "AEDES/1.0"})
            response.raise_for_status()
            
            forecast_data = response.json()
            periods = forecast_data.get("properties", {}).get("periods", [])
            
            return periods
        except Exception as e:
            print(f"Error fetching NOAA forecast: {e}")
            return None


class USGSPhenologyClient:
    """Fetch spring phenology data from USGS USA-NPN.
    
    Spring indices predict leaf-out, bloom, and migration timing based on
    cumulative warmth. Used as early warning for vector activity.
    """
    
    BASE_URL = "https://data.usanpn.org/api/v0"
    
    @staticmethod
    def get_spring_index(latitude: float, longitude: float) -> Optional[Dict]:
        """Fetch spring index prediction for location.
        
        Returns SI-x values (days until leaf-out based on current warmth).
        """
        try:
            url = f"{USGSPhenologyClient.BASE_URL}/spring_indices"
            params = {
                "lat": latitude,
                "lon": longitude,
                "model": "si-x"  # Spring Index Extended model
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error fetching USGS phenology data: {e}")
            return None
    
    @staticmethod
    def interpret_spring_index(si_value: float) -> str:
        """Interpret SI-x value.
        
        SI-x = days remaining until key phenological event (e.g., leaf-out)
        """
        if si_value is None:
            return "Data unavailable"
        elif si_value < 0:
            return f"Event occurred {abs(si_value):.0f} days ago"
        elif si_value < 7:
            return f"Event expected within {si_value:.0f} days (IMMINENT)"
        elif si_value < 14:
            return f"Event expected in {si_value:.0f} days (1-2 weeks)"
        else:
            return f"Event expected in {si_value:.0f} days (2+ weeks)"


def fetch_colorado_climate_current_season(location_name: str = "Denver") -> Optional[Dict]:
    """Convenience function: fetch all climate data for current season.
    
    Args:
        location_name: Location (Denver, Boulder, Fort Collins, etc.)
    
    Returns:
        Dictionary with NASA POWER, NOAA, and phenology data
    """
    
    # Predefined Colorado locations
    locations = {
        "Denver": (39.7392, -104.9903),
        "Boulder": (40.0150, -105.2705),
        "Fort Collins": (40.5853, -105.0844),
        "Durango": (37.2809, -107.8757),
        "Grand Junction": (39.0639, -108.5506),
    }
    
    if location_name not in locations:
        print(f"Location {location_name} not recognized")
        return None
    
    lat, lon = locations[location_name]
    
    # Calculate date range (Jan 1 to today)
    today = datetime.now()
    start_date = datetime(today.year, 1, 1).strftime("%Y%m%d")
    end_date = today.strftime("%Y%m%d")
    
    # Fetch data
    nasa_client = NASAPowerClient(lat, lon)
    noaa_client = NOAAWeatherClient(lat, lon)
    
    result = {
        "location": location_name,
        "latitude": lat,
        "longitude": lon,
        "fetched_at": datetime.now().isoformat(),
        "nasa_power": nasa_client.fetch_temperature_data(start_date, end_date),
        "noaa_forecast": noaa_client.fetch_forecast(),
        "phenology": USGSPhenologyClient.get_spring_index(lat, lon),
    }
    
    return result


if __name__ == "__main__":
    # Example: Fetch Denver climate data
    print("Fetching Denver climate data...")
    data = fetch_colorado_climate_current_season("Denver")
    
    if data and data["nasa_power"] is not None:
        print("\nNASA POWER data (last 10 days):")
        print(data["nasa_power"].tail(10))
    
    if data and data["phenology"]:
        print("\nPhenology prediction:")
        print(json.dumps(data["phenology"], indent=2))
