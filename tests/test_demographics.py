"""
Unit tests for the demographics data extraction module.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest

from aedesproject_uif.data_extraction.demographics import (
    DemographicsDataError,
    download_popmap,
    download_rwi,
    fetch_population_density,
    fetch_relative_wealth_index,
)


class TestValidation:
    """Tests for input validation functions."""

    def test_fetch_relative_wealth_index_invalid_country_code(self):
        """Test that invalid country codes raise ValueError."""
        with pytest.raises(ValueError, match="Invalid country code"):
            fetch_relative_wealth_index("Test Country", "INVALID")

    def test_fetch_relative_wealth_index_empty_country_code(self):
        """Test that empty country code raises ValueError."""
        with pytest.raises(ValueError, match="Invalid country code"):
            fetch_relative_wealth_index("Test Country", "")

    def test_fetch_population_density_invalid_segment(self):
        """Test that invalid segment raises ValueError."""
        with pytest.raises(ValueError, match="Invalid segment"):
            fetch_population_density("Philippines", "PHL", "invalid_segment")

    def test_fetch_population_density_valid_segments(self):
        """Test that valid segments are accepted."""
        valid_segments = ["general", "children", "women", "youth"]
        for segment in valid_segments:
            with patch("requests.get") as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.text = f"https://example.com/download/phl_{segment}_test_geotiff.zip"
                mock_get.return_value = mock_response

                with patch("aedesproject_uif.data_extraction.demographics.download_popmap"):
                    try:
                        fetch_population_density("Philippines", "PHL", segment)
                    except DemographicsDataError:
                        pass  # Expected if download fails


class TestFetchRelativeWealthIndex:
    """Tests for fetch_relative_wealth_index function."""

    @patch("requests.get")
    def test_fetch_relative_wealth_index_success(self, mock_get):
        """Test successful fetch of relative wealth index."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "https://data.humdata.org/dataset/test/resource/123/download/phl_relative_wealth_index.csv"
        mock_get.return_value = mock_response

        with patch("aedesproject_uif.data_extraction.demographics.download_rwi") as mock_download:
            fetch_relative_wealth_index("Philippines", "PHL")
            mock_download.assert_called_once()

    @patch("requests.get")
    def test_fetch_relative_wealth_index_connection_error(self, mock_get):
        """Test handling of connection errors."""
        import requests
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        with pytest.raises(DemographicsDataError, match="Failed to access"):
            fetch_relative_wealth_index("Philippines", "PHL")

    @patch("requests.get")
    def test_fetch_relative_wealth_index_not_found(self, mock_get):
        """Test handling of missing data."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "No relevant data found"
        mock_get.return_value = mock_response

        with pytest.raises(DemographicsDataError, match="No relative wealth index data found"):
            fetch_relative_wealth_index("Philippines", "PHL")


class TestDownloadRWI:
    """Tests for download_rwi function."""

    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_rwi_success(self, mock_file, mock_get):
        """Test successful download of RWI file."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"test data"
        mock_get.return_value = mock_response

        with patch("pathlib.Path.mkdir"):
            path = download_rwi(
                "https://example.com/file.csv",
                "Philippines",
                "PHL"
            )
            assert path.name == "PHL_relative_wealth_index.csv"
            mock_file.assert_called_once()

    @patch("requests.get")
    def test_download_rwi_connection_error(self, mock_get):
        """Test handling of connection errors during download."""
        import requests
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        with pytest.raises(DemographicsDataError, match="Failed to download file"):
            download_rwi("https://example.com/file.csv", "Philippines", "PHL")

    @patch("requests.get")
    @patch("builtins.open")
    def test_download_rwi_write_error(self, mock_file, mock_get):
        """Test handling of file write errors."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"test data"
        mock_get.return_value = mock_response
        mock_file.side_effect = IOError("Cannot write file")

        with pytest.raises(DemographicsDataError, match="Failed to write file"):
            with patch("pathlib.Path.mkdir"):
                download_rwi(
                    "https://example.com/file.csv",
                    "Philippines",
                    "PHL"
                )


class TestFetchPopulationDensity:
    """Tests for fetch_population_density function."""

    @patch("requests.get")
    def test_fetch_population_density_success(self, mock_get):
        """Test successful fetch of population density."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "https://example.com/download/phl_general_test_geotiff.zip"
        mock_get.return_value = mock_response

        with patch("aedesproject_uif.data_extraction.demographics.download_popmap"):
            fetch_population_density("Philippines", "PHL", "general")
            mock_get.assert_called()

    @patch("requests.get")
    def test_fetch_population_density_segment_validation(self, mock_get):
        """Test that invalid segments are rejected."""
        with pytest.raises(ValueError, match="Invalid segment"):
            fetch_population_density("Philippines", "PHL", "invalid")


class TestDownloadPopmap:
    """Tests for download_popmap function."""

    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_popmap_success(self, mock_file, mock_get):
        """Test successful download of population density file."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content = lambda chunk_size: [b"test", b" ", b"data"]
        mock_get.return_value = mock_response

        with patch("pathlib.Path.mkdir"):
            path = download_popmap(
                "https://example.com/file.zip",
                "Philippines",
                "PHL",
                "general"
            )
            assert "population_density.zip" in str(path)

    @patch("requests.get")
    def test_download_popmap_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        import requests
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        with pytest.raises(DemographicsDataError, match="Failed to download file"):
            download_popmap(
                "https://example.com/file.zip",
                "Philippines",
                "PHL"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
