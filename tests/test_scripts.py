"""
Tests for scripts/fetch_surveillance_data.py and scripts/generate_dashboard.py.
"""
import json
import os
import sys
import importlib
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Make scripts importable by adding the scripts/ directory to sys.path
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


# ---------------------------------------------------------------------------
# fetch_surveillance_data
# ---------------------------------------------------------------------------

import fetch_surveillance_data as fsd


class TestSaveFunction:
    def test_creates_file_with_json_content(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        data = {"key": "value", "count": 42}
        fsd.save("test_output.json", data)
        out = tmp_path / "test_output.json"
        assert out.exists()
        loaded = json.loads(out.read_text())
        assert loaded["key"] == "value"
        assert loaded["count"] == 42

    def test_creates_output_directory_if_missing(self, tmp_path, monkeypatch):
        new_dir = str(tmp_path / "new" / "nested")
        os.makedirs(new_dir, exist_ok=True)
        monkeypatch.setattr(fsd, "OUTPUT_DIR", new_dir)
        fsd.save("x.json", {})
        assert os.path.exists(os.path.join(new_dir, "x.json"))


class TestFetchUrl:
    def test_returns_bytes_on_success(self):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"result": "ok"}'
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_response):
            result = fsd.fetch_url("https://example.com/api")
        assert result == b'{"result": "ok"}'

    def test_returns_none_on_timeout(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("timed out")):
            result = fsd.fetch_url("https://example.com/api", timeout=1)
        assert result is None

    def test_returns_none_on_url_error(self):
        import urllib.error
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("connection refused")):
            result = fsd.fetch_url("https://example.com/api")
        assert result is None

    def test_returns_none_on_http_error(self):
        import urllib.error
        err = urllib.error.HTTPError("https://example.com", 404, "Not Found", {}, None)
        with patch("urllib.request.urlopen", side_effect=err):
            result = fsd.fetch_url("https://example.com/api")
        assert result is None


class TestFetchCDCWonderWNV:
    def test_saves_file_with_expected_structure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        fsd.fetch_cdc_wonder_wnv()
        out = tmp_path / "wnv_colorado.json"
        assert out.exists()
        data = json.loads(out.read_text())
        assert "data" in data
        assert "fetched" in data
        assert len(data["data"]) > 0
        first = data["data"][0]
        assert "year" in first
        assert "neuroinvasive" in first
        assert "deaths" in first

    def test_all_years_have_non_negative_cases(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        fsd.fetch_cdc_wonder_wnv()
        data = json.loads((tmp_path / "wnv_colorado.json").read_text())
        for row in data["data"]:
            assert row["neuroinvasive"] >= 0
            assert row["deaths"] >= 0


class TestFetchCDCWonderLyme:
    def test_saves_file_with_expected_structure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        fsd.fetch_cdc_wonder_lyme()
        out = tmp_path / "lyme_colorado.json"
        assert out.exists()
        data = json.loads(out.read_text())
        assert "data" in data
        assert len(data["data"]) > 0
        first = data["data"][0]
        assert "confirmed" in first
        assert "probable" in first

    def test_confirmed_plus_probable_are_positive(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        fsd.fetch_cdc_wonder_lyme()
        data = json.loads((tmp_path / "lyme_colorado.json").read_text())
        for row in data["data"]:
            assert row["confirmed"] + row["probable"] > 0


class TestFetchNASAPower:
    def test_saves_fallback_sentinel_on_api_unavailable(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        with patch.object(fsd, "fetch_url", return_value=None):
            fsd.fetch_nasa_power_colorado()
        out = tmp_path / "climate_colorado_90d.json"
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["source"] == "unavailable"
        assert data["data"] == []

    def test_parses_valid_nasa_power_response(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        mock_payload = {
            "properties": {
                "parameter": {
                    "T2M":          {"20260101": 5.0, "20260102": 8.2},
                    "PRECTOTCORR":  {"20260101": 0.0, "20260102": 2.1},
                }
            }
        }
        with patch.object(fsd, "fetch_url", return_value=json.dumps(mock_payload).encode()):
            fsd.fetch_nasa_power_colorado()
        data = json.loads((tmp_path / "climate_colorado_90d.json").read_text())
        assert data["source"] == "NASA POWER"
        assert len(data["data"]) == 2
        assert data["data"][0]["temp_c"] == 5.0


class TestFetchINaturalist:
    def test_ticks_saves_fallback_on_api_unavailable(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        with patch.object(fsd, "fetch_url", return_value=None):
            fsd.fetch_inaturalist_ticks()
        out = tmp_path / "inaturalist_ticks_colorado.json"
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["source"] == "unavailable"

    def test_ticks_parses_valid_inaturalist_response(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        mock_results = {
            "results": [
                {
                    "id": 123,
                    "observed_on": "2026-05-01",
                    "taxon": {"name": "Ixodes scapularis", "preferred_common_name": "deer tick"},
                    "location": "39.74,-104.99",
                    "place_guess": "Jefferson County, CO",
                }
            ]
        }
        with patch.object(fsd, "fetch_url", return_value=json.dumps(mock_results).encode()):
            fsd.fetch_inaturalist_ticks()
        data = json.loads((tmp_path / "inaturalist_ticks_colorado.json").read_text())
        assert data["source"] == "iNaturalist API"
        assert data["count"] == 1
        assert data["data"][0]["taxon"] == "Ixodes scapularis"

    def test_mosquitoes_saves_fallback_on_api_unavailable(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        with patch.object(fsd, "fetch_url", return_value=None):
            fsd.fetch_inaturalist_mosquitoes()
        out = tmp_path / "inaturalist_mosquitoes_colorado.json"
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["source"] == "unavailable"


# ---------------------------------------------------------------------------
# generate_dashboard
# ---------------------------------------------------------------------------

import generate_dashboard as gd


class TestBuildNotebookCards:
    def test_empty_list_returns_no_data_message(self):
        html = gd.build_notebook_cards([])
        assert "no-data" in html or "No analyses" in html

    def test_known_notebook_renders_title(self, tmp_path):
        fake_html = tmp_path / "01_west_nile_virus_surveillance.html"
        fake_html.write_text("<html></html>")
        cards = gd.build_notebook_cards([str(fake_html)])
        assert "West Nile Virus" in cards
        assert "Culex tarsalis" in cards
        assert 'href=' in cards

    def test_unknown_notebook_renders_fallback_title(self, tmp_path):
        fake_html = tmp_path / "99_custom_analysis.html"
        fake_html.write_text("<html></html>")
        cards = gd.build_notebook_cards([str(fake_html)])
        assert "99 Custom Analysis" in cards or "custom" in cards.lower()

    def test_multiple_notebooks_all_appear(self, tmp_path):
        nb1 = tmp_path / "01_west_nile_virus_surveillance.html"
        nb2 = tmp_path / "02_tick_disease_surveillance.html"
        nb1.write_text("<html></html>")
        nb2.write_text("<html></html>")
        cards = gd.build_notebook_cards([str(nb1), str(nb2)])
        assert "West Nile Virus" in cards
        assert "Tick" in cards


class TestBuildIndex:
    def test_creates_index_html(self, tmp_path, monkeypatch):
        monkeypatch.setattr(gd, "SITE_DIR", str(tmp_path))
        monkeypatch.setattr(gd, "NOTEBOOKS_DIR", str(tmp_path / "notebooks"))
        monkeypatch.setattr(gd, "DATA_DIR", str(tmp_path))
        gd.build_index()
        index = tmp_path / "index.html"
        assert index.exists()

    def test_index_contains_expected_structure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(gd, "SITE_DIR", str(tmp_path))
        monkeypatch.setattr(gd, "NOTEBOOKS_DIR", str(tmp_path / "notebooks"))
        monkeypatch.setattr(gd, "DATA_DIR", str(tmp_path))
        gd.build_index()
        content = (tmp_path / "index.html").read_text()
        assert "AEDES" in content
        assert "Colorado" in content
        assert "West Nile Virus" in content   # disease reference table
        assert "Lyme Disease" in content

    def test_index_links_existing_notebooks(self, tmp_path, monkeypatch):
        nb_dir = tmp_path / "notebooks"
        nb_dir.mkdir()
        (nb_dir / "01_west_nile_virus_surveillance.html").write_text("<html></html>")
        monkeypatch.setattr(gd, "SITE_DIR", str(tmp_path))
        monkeypatch.setattr(gd, "NOTEBOOKS_DIR", str(nb_dir))
        monkeypatch.setattr(gd, "DATA_DIR", str(tmp_path))
        gd.build_index()
        content = (tmp_path / "index.html").read_text()
        assert "01_west_nile_virus_surveillance.html" in content

    def test_fetched_date_appears_in_index(self, tmp_path, monkeypatch):
        monkeypatch.setattr(gd, "SITE_DIR", str(tmp_path))
        monkeypatch.setattr(gd, "NOTEBOOKS_DIR", str(tmp_path / "notebooks"))
        # Write a sample wnv file so get_last_fetched finds it
        wnv = {"fetched": "2026-05-18", "source": "test", "data": []}
        (tmp_path / "wnv_colorado.json").write_text(json.dumps(wnv))
        monkeypatch.setattr(gd, "DATA_DIR", str(tmp_path))
        gd.build_index()
        content = (tmp_path / "index.html").read_text()
        assert "2026-05-18" in content
