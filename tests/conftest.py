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
    }
    for name, payload in files.items():
        with open(os.path.join(temp_dir, name), "w") as f:
            json.dump(payload, f)
    return temp_dir
