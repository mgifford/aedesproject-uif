"""
Shared pytest fixtures for AEDES test suite.
"""
import json
import os
import tempfile
import pytest


@pytest.fixture
def temp_dir():
    """Provide a temporary directory that is cleaned up after the test."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_wnv_data():
    return {
        "fetched": "2026-01-01",
        "source": "CDC NNDSS (test fixture)",
        "data": [
            {"year": 2022, "state": "Colorado", "neuroinvasive": 16, "deaths": 0},
            {"year": 2023, "state": "Colorado", "neuroinvasive": 6,  "deaths": 0},
            {"year": 2024, "state": "Colorado", "neuroinvasive": 12, "deaths": 0},
        ],
    }


@pytest.fixture
def sample_lyme_data():
    return {
        "fetched": "2026-01-01",
        "source": "CDC Lyme Data Tables (test fixture)",
        "data": [
            {"year": 2022, "state": "Colorado", "confirmed": 57, "probable": 46},
            {"year": 2023, "state": "Colorado", "confirmed": 61, "probable": 49},
        ],
    }


@pytest.fixture
def sample_climate_data():
    return {
        "fetched": "2026-01-01",
        "source": "NASA POWER (test fixture)",
        "location": "Denver, CO",
        "data": [
            {"date": "20260101", "temp_c": -2.1, "precip_mm": 0.0},
            {"date": "20260102", "temp_c":  1.4, "precip_mm": 1.2},
            {"date": "20260103", "temp_c":  5.0, "precip_mm": 0.0},
        ],
    }


@pytest.fixture
def surveillance_data_dir(temp_dir, sample_wnv_data, sample_lyme_data, sample_climate_data):
    """Populate a temp directory with sample surveillance JSON files."""
    files = {
        "wnv_colorado.json": sample_wnv_data,
        "lyme_colorado.json": sample_lyme_data,
        "climate_colorado_90d.json": sample_climate_data,
        "inaturalist_ticks_colorado.json": {"fetched": "2026-01-01", "source": "iNaturalist", "data": []},
        "inaturalist_mosquitoes_colorado.json": {"fetched": "2026-01-01", "source": "iNaturalist", "data": []},
        "2026_season_ytd.json": {
            "season": "2026",
            "fetched": "2026-01-01",
            "status": "preliminary",
            "data": [
                {"week": 1,  "date": "2026-01-05", "wnv_cases": 0, "lyme_cases": 0, "rmsf_cases": 0,
                 "source": "CDC provisional", "notes": "Winter baseline"},
                {"week": 20, "date": "2026-05-18", "wnv_cases": 0, "lyme_cases": 2, "rmsf_cases": 0,
                 "source": "CDC provisional", "notes": "Early season"},
            ],
            "historical_baseline_2024": {
                "wnv_cases_full_year": 12, "lyme_cases_full_year": 119,
                "peak_wnv_month": "August", "peak_lyme_month": "July",
                "ytd_through_may": {"wnv": 0, "lyme": 3},
            },
            "update_frequency": "weekly",
            "next_update": "2026-05-25",
        },
        "regional_counties_2026.json": {
            "season": "2026",
            "fetched": "2026-01-01",
            "source": "CDC provisional",
            "regions": {
                "front_range": {"label": "Front Range", "counties": ["Denver", "Jefferson"]},
            },
            "county_ytd": [
                {"county": "Denver",    "fips": "08031", "region": "front_range",
                 "wnv_cases": 0, "lyme_cases": 1, "rmsf_cases": 0,
                 "population": 715522, "lat": 39.74, "lon": -104.99},
                {"county": "Jefferson", "fips": "08059", "region": "front_range",
                 "wnv_cases": 0, "lyme_cases": 0, "rmsf_cases": 0,
                 "population": 582910, "lat": 39.59, "lon": -105.21},
            ],
            "historical_county_peaks": {
                "wnv_hotspot_counties": ["Weld"],
                "lyme_hotspot_counties": ["Boulder"],
                "rmsf_hotspot_counties": ["El Paso"],
            },
        },
    }
    for name, payload in files.items():
        with open(os.path.join(temp_dir, name), "w") as f:
            json.dump(payload, f)
    return temp_dir
