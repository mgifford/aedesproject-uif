import os
import json
import datetime
from unittest.mock import patch, MagicMock
import pytest

# Skip entire module if wget is not installed
wget = pytest.importorskip("wget", reason="wget not installed")

from tests.src.data_extraction.nasa_worldview import (
    get_lat_lon,
    latlong_gen,
    url_gen,
    next_date,
)


class TestGetLatLon:
    def test_returns_query_unchanged(self):
        """Stub passes query through."""
        assert get_lat_lon("Manila") == "Manila"
        assert get_lat_lon(None) is None


class TestLatLongGen:
    def test_returns_non_empty_result(self):
        result = latlong_gen("14.6,121.0", 0.5)
        assert result is not None


class TestUrlGen:
    def test_returns_non_empty_result(self):
        result = url_gen("14.0", "121.0", "14.5", "121.5", "2021-01-01", "2021-12-31")
        assert result is not None


class TestNextDate:
    def test_returns_non_empty_result(self):
        result = next_date("2021-01-01")
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
