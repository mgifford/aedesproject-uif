import os
import warnings
from unittest.mock import patch, MagicMock
import pytest

warnings.filterwarnings("ignore")

# Skip entire module if heavy geo dependencies are not installed
gpd = pytest.importorskip("geopandas", reason="geopandas not installed")
pytest.importorskip("fiona", reason="fiona not installed")

from tests.src.data_extraction.admin_boundaries import (
    fetch_geoboundaries,
    save_admin_regions,
)


class TestFetchGeoboundaries:
    def test_returns_combination_of_inputs(self):
        """Stub concatenates country code + admin level."""
        result = fetch_geoboundaries("PHL", "2")
        assert result == "PHL2"

    def test_accepts_expected_parameters(self):
        result = fetch_geoboundaries("USA", "1")
        assert isinstance(result, str)
        assert "USA" in result


class TestSaveAdminRegions:
    def test_returns_combination_of_inputs(self):
        result = save_admin_regions("PHL", "2")
        assert result == "PHL2"

    def test_accepts_expected_parameters(self):
        result = save_admin_regions("USA", "1")
        assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
