"""Atmospheric transport and wind risk modeling.

Models disease vector displacement and long-distance transport via:
- Prevailing wind patterns
- Atmospheric circulation
- Bird migration corridors
"""

import math
from typing import Dict, Tuple, Optional
from enum import Enum


class WindDirection(Enum):
    """Cardinal and intercardinal wind directions."""
    N = 0
    NNE = 22.5
    NE = 45
    ENE = 67.5
    E = 90
    ESE = 112.5
    SE = 135
    SSE = 157.5
    S = 180
    SSW = 202.5
    SW = 225
    WSW = 247.5
    W = 270
    WNW = 292.5
    NW = 315
    NNW = 337.5


class AtmosphericTransportModel:
    """Model disease vector transport via wind and atmospheric circulation."""
    
    # Risk scores for wind direction (to Colorado)
    # Positive values indicate wind bringing potential disease FROM upstream
    WIND_DIRECTION_RISK_TO_COLORADO = {
        "SW": 0.95,   # From New Mexico/Arizona - WNV, tick hosts
        "S": 0.80,    # From Oklahoma/Texas
        "SSW": 0.85,  # Between S and SW
        "W": 0.60,    # From Utah/Nevada
        "WSW": 0.75,  # Between W and SW
        "NW": 0.30,   # From Wyoming - colder air
        "WNW": 0.40,
        "N": 0.20,    # From Canada/northern plains
        "NNW": 0.25,
        "NE": 0.10,   # Generally not favorable for disease import
        "E": 0.05,
        "SE": 0.15,
        "SSE": 0.40,
    }
    
    @staticmethod
    def wind_to_disease_risk(
        wind_direction_degrees: float,
        wind_speed_mph: float,
        disease: str = "wnv"
    ) -> float:
        """Calculate disease transport risk from wind patterns.
        
        Args:
            wind_direction_degrees: Wind direction in degrees (0-360, where 0=N, 90=E, etc.)
            wind_speed_mph: Wind speed in mph
            disease: Disease type ("wnv", "lyme", "rmsf")
        
        Returns:
            Risk score (0-1) where:
            - 0.0: No disease transport expected
            - 0.5: Moderate transport conditions
            - 1.0: High transport conditions
        
        Mechanism:
            - Wind <5 mph: Insufficient for mosquito displacement
            - Wind 5-15 mph: Optimal for Culex mosquito transport (~50-100 km)
            - Wind 15-20 mph: Good transport but disrupts vector behavior
            - Wind >20 mph: Disrupts vector activity; less transmission
        """
        
        # Normalize wind direction to nearest cardinal direction
        direction_name = AtmosphericTransportModel._wind_direction_name(wind_direction_degrees)
        
        # Get base risk for this direction
        base_direction_risk = AtmosphericTransportModel.WIND_DIRECTION_RISK_TO_COLORADO.get(
            direction_name, 0.1
        )
        
        # Score wind speed for vector transport
        if disease == "wnv":
            # Culex mosquitoes: optimal wind displacement at 5-15 mph
            if wind_speed_mph < 5:
                speed_score = 0.0  # Too calm
            elif wind_speed_mph < 15:
                # Linear increase from 0.5 to 1.0
                speed_score = 0.5 + (wind_speed_mph - 5) / 20
            elif wind_speed_mph < 20:
                # Slight decrease (wind disrupts behavior)
                speed_score = 1.0 - (wind_speed_mph - 15) / 10
            else:
                speed_score = 0.5  # Too windy
        
        elif disease == "lyme":
            # Tick transport via wildlife (especially deer):
            # Less wind-dependent; more about atmospheric rivers
            if wind_speed_mph < 3:
                speed_score = 0.0
            elif wind_speed_mph < 10:
                speed_score = 0.4 + (wind_speed_mph / 25)
            else:
                speed_score = 0.8  # Ticks move with animals
        
        else:  # rmsf (similar to lyme)
            speed_score = (
                0.0 if wind_speed_mph < 3
                else min(0.8, wind_speed_mph / 15)
            )
        
        # Combined risk: direction × speed
        combined_risk = base_direction_risk * speed_score
        
        return min(1.0, combined_risk)
    
    @staticmethod
    def _wind_direction_name(degrees: float) -> str:
        """Convert wind direction degrees to name."""
        degrees = degrees % 360
        
        # Cardinal directions
        if 11.25 <= degrees < 33.75:
            return "NNE"
        elif 33.75 <= degrees < 56.25:
            return "NE"
        elif 56.25 <= degrees < 78.75:
            return "ENE"
        elif 78.75 <= degrees < 101.25:
            return "E"
        elif 101.25 <= degrees < 123.75:
            return "ESE"
        elif 123.75 <= degrees < 146.25:
            return "SE"
        elif 146.25 <= degrees < 168.75:
            return "SSE"
        elif 168.75 <= degrees < 191.25:
            return "S"
        elif 191.25 <= degrees < 213.75:
            return "SSW"
        elif 213.75 <= degrees < 236.25:
            return "SW"
        elif 236.25 <= degrees < 258.75:
            return "WSW"
        elif 258.75 <= degrees < 281.25:
            return "W"
        elif 281.25 <= degrees < 303.75:
            return "WNW"
        elif 303.75 <= degrees < 326.25:
            return "NW"
        elif 326.25 <= degrees < 348.75:
            return "NNW"
        else:  # 348.75 to 11.25
            return "N"
    
    @staticmethod
    def prevailing_wind_season_score(
        spring_wind_direction: float,
        spring_wind_speed: float,
        summer_wind_direction: float,
        summer_wind_speed: float
    ) -> Dict[str, float]:
        """Calculate seasonal disease transport risk.
        
        Returns:
            Dictionary with spring_risk and summer_risk scores
        """
        return {
            "spring_risk": AtmosphericTransportModel.wind_to_disease_risk(
                spring_wind_direction, spring_wind_speed, "lyme"
            ),
            "summer_risk": AtmosphericTransportModel.wind_to_disease_risk(
                summer_wind_direction, summer_wind_speed, "wnv"
            ),
        }
    
    @staticmethod
    def distance_mosquito_can_travel(wind_speed_mph: float, hours: int = 24) -> float:
        """Estimate distance Culex mosquito can travel via wind.
        
        Args:
            wind_speed_mph: Sustained wind speed
            hours: Duration of wind event
        
        Returns:
            Approximate distance in miles
        
        Reference: Studies show Culex can drift 50-100 km in favorable conditions
        """
        
        # Base flight speed: 0.5-1 mph
        # Wind displacement: wind_speed * fraction of wind (assuming mosquito partially avoids wind)
        
        # Assume mosquito drifts with ~50% of wind speed
        effective_wind_mph = wind_speed_mph * 0.5
        
        # Total distance
        distance = (0.75 + effective_wind_mph) * hours  # 0.75 mph base flight
        
        return distance
    
    @staticmethod
    def day_range_between_outbreak_and_location(
        outbreak_location: Tuple[float, float],  # (lat, lon)
        target_location: Tuple[float, float],
        prevailing_wind_direction: float,
        wind_speed_mph: float
    ) -> Optional[int]:
        """Estimate days for disease to reach target location via wind transport.
        
        Args:
            outbreak_location: (latitude, longitude) of upstream outbreak
            target_location: (latitude, longitude) of concern
            prevailing_wind_direction: Average wind direction
            wind_speed_mph: Average wind speed
        
        Returns:
            Estimated days for vector/disease to reach target (None if wind opposes)
        """
        
        # Calculate bearing from outbreak to target
        bearing = AtmosphericTransportModel._calculate_bearing(
            outbreak_location, target_location
        )
        
        # Check if wind direction aligns with outbreak-to-target direction
        angle_diff = abs(prevailing_wind_direction - bearing)
        if angle_diff > 90 and angle_diff < 270:
            # Wind not favorable
            return None
        
        # Calculate distance
        distance_miles = AtmosphericTransportModel._haversine_distance(
            outbreak_location, target_location
        )
        
        # Calculate travel speed
        mosquito_travel_mph = 0.75 + (wind_speed_mph * 0.5)
        
        # Estimate days
        hours = distance_miles / mosquito_travel_mph
        days = hours / 24
        
        return int(math.ceil(days))
    
    @staticmethod
    def _calculate_bearing(
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """Calculate bearing between two lat/lon points (degrees)."""
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lon_diff = math.radians(lon2 - lon1)
        
        y = math.sin(lon_diff) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lon_diff))
        
        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360) % 360
    
    @staticmethod
    def _haversine_distance(
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """Calculate distance between two points in miles."""
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        R = 3959  # Earth's radius in miles
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c


if __name__ == "__main__":
    # Example: Calculate WNV transport risk from Albuquerque to Denver
    
    # SW wind, 8 mph (typical spring/summer in Colorado)
    risk = AtmosphericTransportModel.wind_to_disease_risk(225, 8, "wnv")
    print(f"WNV transport risk (SW 8mph): {risk:.2f}")
    
    # Calculate travel time
    albuquerque = (35.0844, -106.6504)
    denver = (39.7392, -104.9903)
    
    days = AtmosphericTransportModel.day_range_between_outbreak_and_location(
        albuquerque, denver, 225, 8
    )
    print(f"Days for WNV to reach Denver from Albuquerque: {days}")
