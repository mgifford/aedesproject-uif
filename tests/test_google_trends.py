"""
Unit tests for the Google Trends data extraction module.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pandas as pd
import pytest

from aedesproject_uif.data_extraction.google_trends import (
    GoogleTrendsError,
    fetch_google_trends,
    save_google_trends,
)


class TestValidation:
    """Tests for input validation functions."""

    def test_fetch_google_trends_invalid_country_code(self):
        """Test that invalid country codes raise ValueError."""
        with pytest.raises(ValueError, match="Invalid country code"):
            fetch_google_trends("INVALID", "2016-01-01", "2021-01-01")

    def test_fetch_google_trends_invalid_start_date(self):
        """Test that invalid date format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            fetch_google_trends("PHL", "2016/01/01", "2021-01-01")

    def test_fetch_google_trends_invalid_end_date(self):
        """Test that invalid date format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            fetch_google_trends("PHL", "2016-01-01", "2021/01/01")


class TestFetchGoogleTrends:
    """Tests for fetch_google_trends function."""

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    @patch("aedesproject_uif.data_extraction.google_trends.TrendReq")
    def test_fetch_google_trends_success(self, mock_trends_class, mock_read_csv, mock_exists):
        """Test successful fetch of Google Trends data."""
        # Mock the CSV reading
        mock_df = pd.DataFrame({
            "ISO 3166-2": ["PH-00"],
            "Region": ["Metro Manila"]
        })
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True

        # Mock TrendReq
        mock_trends = MagicMock()
        mock_trends_class.return_value = mock_trends

        # Mock related_queries response
        interest_data = pd.DataFrame({
            "2016-01-01": [50],
            "isPartial": [False]
        }, index=["dengue"])
        interest_data.index.name = "date"

        mock_trends.related_queries.return_value = {
            "dengue": {
                "rising": pd.DataFrame({"query": ["dengue fever", "dengue symptoms"]}),
                "top": pd.DataFrame({"query": ["dengue treatment"]})
            }
        }
        mock_trends.interest_over_time.return_value = interest_data

        result = fetch_google_trends("PHL", "2016-01-01", "2021-01-01")
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    def test_fetch_google_trends_missing_subdivision_data(self, mock_read_csv, mock_exists):
        """Test handling of missing subdivision data."""
        mock_exists.return_value = False

        with pytest.raises(GoogleTrendsError, match="Subdivision data not found"):
            fetch_google_trends("PHL", "2016-01-01", "2021-01-01")

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    def test_fetch_google_trends_corrupted_csv(self, mock_read_csv, mock_exists):
        """Test handling of corrupted CSV data."""
        mock_exists.return_value = True
        mock_read_csv.side_effect = pd.errors.ParserError("Error tokenizing data")

        with pytest.raises(GoogleTrendsError, match="Failed to parse subdivision data"):
            fetch_google_trends("PHL", "2016-01-01", "2021-01-01")

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    @patch("aedesproject_uif.data_extraction.google_trends.TrendReq")
    def test_fetch_google_trends_api_error(self, mock_trends_class, mock_read_csv, mock_exists):
        """Test handling of API errors."""
        mock_df = pd.DataFrame({
            "ISO 3166-2": ["PH-00"],
            "Region": ["Metro Manila"]
        })
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True

        mock_trends = MagicMock()
        mock_trends_class.return_value = mock_trends
        mock_trends.related_queries.side_effect = Exception("API Error")
        mock_trends.interest_over_time.return_value = pd.DataFrame()

        # Should raise error when no data is retrieved
        with pytest.raises(GoogleTrendsError, match="No Google Trends data was retrieved"):
            fetch_google_trends("PHL", "2016-01-01", "2021-01-01")


class TestSaveGoogleTrends:
    """Tests for save_google_trends function."""

    @patch("pathlib.Path.mkdir")
    @patch("pandas.DataFrame.to_csv")
    def test_save_google_trends_success(self, mock_to_csv, mock_mkdir):
        """Test successful saving of Google Trends data."""
        df = pd.DataFrame({
            "date": ["2016-01-01"],
            "keyword": ["dengue"],
            "value": [50],
            "geo": ["PH-00"],
            "region": ["Metro Manila"]
        })

        with patch("pathlib.Path.exists", return_value=False):
            path = save_google_trends(df, "PHL")
            assert "PHL.csv" in str(path)

    @patch("pathlib.Path.mkdir")
    @patch("pandas.DataFrame.to_csv")
    def test_save_google_trends_write_error(self, mock_to_csv, mock_mkdir):
        """Test handling of write errors."""
        df = pd.DataFrame({
            "date": ["2016-01-01"],
            "keyword": ["dengue"],
            "value": [50]
        })
        mock_to_csv.side_effect = IOError("Cannot write file")

        with pytest.raises(IOError, match="Failed to save Google Trends data"):
            save_google_trends(df, "PHL")

    def test_save_google_trends_custom_output_dir(self):
        """Test saving with custom output directory."""
        df = pd.DataFrame({
            "date": ["2016-01-01"],
            "keyword": ["dengue"],
            "value": [50]
        })

        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            path = save_google_trends(df, "PHL", output_dir)
            assert path.parent == output_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


