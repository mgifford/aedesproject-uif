"""
Configuration management for AEDES project.

This module provides centralized configuration handling for path management,
API endpoints, and other project-wide settings.
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Project configuration management."""

    # Base paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    PROCESSED_DIR = PROJECT_ROOT / "processed"
    MODEL_DIR = PROJECT_ROOT / "model"

    # Data subdirectories
    DENGUE_DATA_DIR = DATA_DIR / "Dengue"
    GEOJSON_DATA_DIR = DATA_DIR / "GeoJSON"
    GOOGLE_TRENDS_DATA_DIR = DATA_DIR / "Google Trends"
    NASA_POWER_DATA_DIR = DATA_DIR / "NASA Power"
    OPENSTREETMAP_DATA_DIR = DATA_DIR / "OpenStreetMap"
    WORLDVIEW_DATA_DIR = DATA_DIR / "Worldview"

    # Processed subdirectories
    PROCESSED_INFORM_DIR = PROCESSED_DIR / "INFORM"
    PROCESSED_FORECASTING_DIR = PROCESSED_DIR / "Forecasting"
    PROCESSED_HOTSPOT_DIR = PROCESSED_DIR / "Hotspot Detection"

    # API configuration
    NASA_EARTHDATA_URL = "https://api.earthdata.nasa.gov"
    OSM_TIMEOUT = 60  # seconds
    PYTRENDS_TIMEOUT = (10, 50)
    PYTRENDS_RETRIES = 3

    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary project directories if they don't exist."""
        directories = [
            cls.DATA_DIR,
            cls.PROCESSED_DIR,
            cls.MODEL_DIR,
            cls.PROCESSED_INFORM_DIR,
            cls.PROCESSED_FORECASTING_DIR,
            cls.PROCESSED_HOTSPOT_DIR,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_data_dir(cls, country_code: str, data_type: str) -> Path:
        """
        Get the data directory for a specific country and data type.

        Args:
            country_code: ISO country code (e.g., 'PHL')
            data_type: Type of data (e.g., 'Dengue', 'NASA Power')

        Returns:
            Path to the data directory

        Raises:
            ValueError: If data_type is not recognized
        """
        data_type_map = {
            "dengue": cls.DENGUE_DATA_DIR,
            "geojson": cls.GEOJSON_DATA_DIR,
            "google_trends": cls.GOOGLE_TRENDS_DATA_DIR,
            "nasa_power": cls.NASA_POWER_DATA_DIR,
            "osm": cls.OPENSTREETMAP_DATA_DIR,
            "worldview": cls.WORLDVIEW_DATA_DIR,
        }

        if data_type.lower() not in data_type_map:
            raise ValueError(
                f"Unknown data type: {data_type}. "
                f"Choose from: {', '.join(data_type_map.keys())}"
            )

        data_dir = data_type_map[data_type.lower()] / country_code
        return data_dir

    @classmethod
    def get_processed_dir(cls, country_code: str, output_type: str) -> Path:
        """
        Get the processed output directory for a specific country and output type.

        Args:
            country_code: ISO country code (e.g., 'PHL')
            output_type: Type of output (e.g., 'INFORM', 'Forecasting')

        Returns:
            Path to the output directory

        Raises:
            ValueError: If output_type is not recognized
        """
        output_type_map = {
            "inform": cls.PROCESSED_INFORM_DIR,
            "forecasting": cls.PROCESSED_FORECASTING_DIR,
            "hotspot": cls.PROCESSED_HOTSPOT_DIR,
        }

        if output_type.lower() not in output_type_map:
            raise ValueError(
                f"Unknown output type: {output_type}. "
                f"Choose from: {', '.join(output_type_map.keys())}"
            )

        output_dir = output_type_map[output_type.lower()] / country_code
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
