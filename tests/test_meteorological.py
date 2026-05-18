import os
import json
from unittest.mock import patch, MagicMock
import pytest

from tests.src.data_extraction.meteorological import (
    get_lat_lon,
    get_weather,
    fetch_weather_data,
)


class TestGetLatLon:
    def test_returns_query_unchanged(self):
        """Stub passes query through; real impl should return (lat, lon) tuple."""
        assert get_lat_lon("Manila") == "Manila"

    def test_returns_none_for_none(self):
        assert get_lat_lon(None) is None


class TestGetWeather:
    def test_returns_combination_of_inputs(self):
        """Stub adds its arguments; verifies the function is callable."""
        result = get_weather("PHL", "14.6,121.0", "2016-01-01", "2021-12-31", "T2M")
        assert result is not None

    def test_accepts_expected_parameter_types(self):
        result = get_weather("PHL", "latlong", "start", "end", "params")
        assert isinstance(result, str)


class TestFetchWeatherData:
    def test_returns_combination_of_inputs(self):
        """Stub concatenates iso_country_code + start + end."""
        result = fetch_weather_data("PHL", "start", "end")
        assert result == "PHLstartend"

    def test_accepts_string_parameters(self):
        result = fetch_weather_data("USA", "2020-01-01", "2020-12-31")
        assert isinstance(result, str)
        assert "USA" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])