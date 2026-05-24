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


class TestFetchGoogleTrends:
    def test_saves_fallback_when_pytrends_unavailable(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        monkeypatch.setattr(fsd, "TrendReq", None)

        fsd.fetch_google_trends_colorado()

        out = tmp_path / "google_trends_colorado.json"
        assert out.exists()
        payload = json.loads(out.read_text())
        assert payload["source"] == "unavailable"
        assert payload["geo"] == "US-CO"
        assert payload["time_series"] == []

    def test_parses_google_trends_payload(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))

        class MockTrendReq:
            def __init__(self, *args, **kwargs):
                self._last_keywords = []

            def build_payload(self, keywords, timeframe, geo, gprop):
                self._last_keywords = keywords

            def interest_over_time(self):
                import pandas as pd

                return pd.DataFrame(
                    {"west nile virus": [42], "lyme disease": [31], "isPartial": [False]},
                    index=pd.to_datetime(["2026-05-01"]),
                )

            def interest_by_region(self, resolution, inc_low_vol=True, inc_geo_code=False):
                import pandas as pd

                if resolution == "DMA":
                    return pd.DataFrame(
                        {"west nile virus": [55], "lyme disease": [40]},
                        index=["Denver CO"],
                    )
                if resolution == "CITY":
                    return pd.DataFrame(
                        {"west nile virus": [60], "lyme disease": [33]},
                        index=["Denver"],
                    )
                return pd.DataFrame()

        monkeypatch.setattr(fsd, "TrendReq", MockTrendReq)
        monkeypatch.setattr(fsd, "GOOGLE_TRENDS_KEYWORDS", ["west nile virus", "lyme disease"])
        monkeypatch.setattr(fsd.random, "randint", lambda *_: 0)
        monkeypatch.setattr(fsd.time, "sleep", lambda *_: None)

        fsd.fetch_google_trends_colorado()

        out = tmp_path / "google_trends_colorado.json"
        payload = json.loads(out.read_text())
        assert payload["source"] == "Google Trends API"
        assert payload["geo"] == "US-CO"
        assert len(payload["time_series"]) == 2
        assert len(payload["by_dma"]) == 2
        assert len(payload["by_city"]) == 2


class TestReliabilityReport:
    @staticmethod
    def _write_all_sources_ok() -> None:
        fsd.save("wnv_colorado.json", {"fetched": "2026-05-22", "source": "CDC", "data": [{"year": 2024}]})
        fsd.save("lyme_colorado.json", {"fetched": "2026-05-22", "source": "CDC", "data": [{"year": 2024}]})
        fsd.save(
            "climate_colorado_90d.json",
            {"fetched": "2026-05-22", "source": "NASA POWER", "data": [{"date": "20260522"}]},
        )
        fsd.save(
            "open_meteo_colorado_30d.json",
            {"fetched": "2026-05-22", "source": "Open-Meteo API", "data": [{"date": "2026-05-22"}]},
        )
        fsd.save(
            "google_trends_colorado.json",
            {
                "fetched": "2026-05-22",
                "source": "Google Trends API",
                "data": [{"date": "2026-05-22", "keyword": "west nile virus", "value": 10}],
            },
        )
        fsd.save(
            "inaturalist_ticks_colorado.json",
            {"fetched": "2026-05-22", "source": "iNaturalist API", "data": [{"id": 1}]},
        )
        fsd.save(
            "inaturalist_mosquitoes_colorado.json",
            {"fetched": "2026-05-22", "source": "iNaturalist API", "data": [{"id": 2}]},
        )
        fsd.save("regional_counties_2026.json", {"fetched": "2026-05-22", "source": "generated", "data": [{"county": "Adams"}]})

    def test_generates_reliability_report_with_required_fields(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))

        # Create representative successful source artifacts.
        self._write_all_sources_ok()

        report = fsd.generate_reliability_report()
        out = tmp_path / fsd.RELIABILITY_REPORT_FILENAME
        assert out.exists()

        data = json.loads(out.read_text())
        assert data["schema_version"] == "1.0"
        assert data["run_mode"] in {"normal", "degraded", "blocked"}
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) == len(fsd.RELIABILITY_SOURCES)

        for source in data["sources"]:
            assert "source_id" in source
            assert "status" in source
            assert "last_success_at" in source
            assert "fallback_used" in source
            assert "status_reason" in source
            assert "integrity_critical_failure" in source

        assert report["run_mode"] == "normal"

    def test_degraded_when_non_critical_source_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        self._write_all_sources_ok()

        # Remove a non-critical source artifact.
        os.remove(tmp_path / "open_meteo_colorado_30d.json")

        report = fsd.generate_reliability_report()
        open_meteo = next(s for s in report["sources"] if s["source_id"] == "open_meteo_30d")
        assert open_meteo["status"] == "missing"
        assert open_meteo["integrity_critical_failure"] is False
        assert report["run_mode"] == "degraded"

    def test_blocked_when_critical_source_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        self._write_all_sources_ok()

        os.remove(tmp_path / "lyme_colorado.json")

        report = fsd.generate_reliability_report()
        lyme = next(s for s in report["sources"] if s["source_id"] == "cdc_lyme")
        assert lyme["status"] == "missing"
        assert lyme["integrity_critical_failure"] is True
        assert report["run_mode"] == "blocked"

    def test_blocked_when_source_schema_invalid(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))
        self._write_all_sources_ok()

        # Corrupt required schema keys for one source.
        fsd.save("climate_colorado_90d.json", {"fetched": "2026-05-22", "data": []})

        report = fsd.generate_reliability_report()
        climate = next(s for s in report["sources"] if s["source_id"] == "nasa_power_90d")
        assert climate["status"] == "invalid"
        assert climate["integrity_critical_failure"] is True
        assert report["run_mode"] == "blocked"

    def test_marks_unavailable_source_as_degraded(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fsd, "OUTPUT_DIR", str(tmp_path))

        # Only one source file exists and is unavailable; others are missing.
        fsd.save("wnv_colorado.json", {"fetched": "2026-05-22", "source": "unavailable", "data": []})
        report = fsd.generate_reliability_report()

        wnv = next(s for s in report["sources"] if s["source_id"] == "cdc_wnv")
        assert wnv["status"] == "degraded"
        assert wnv["fallback_used"] is True
        assert wnv["last_success_at"] is None
        assert report["run_mode"] == "blocked"

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
import postprocess_notebook_html as pnh


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

    def test_index_shows_reliability_section_from_report(self, tmp_path, monkeypatch):
        monkeypatch.setattr(gd, "SITE_DIR", str(tmp_path))
        monkeypatch.setattr(gd, "NOTEBOOKS_DIR", str(tmp_path / "notebooks"))
        monkeypatch.setattr(gd, "DATA_DIR", str(tmp_path))

        report = {
            "generated_at": "2026-05-22T10:00:00Z",
            "run_date": "2026-05-22",
            "schema_version": "1.0",
            "run_mode": "degraded",
            "sources": [
                {
                    "source_id": "open_meteo_30d",
                    "status": "missing",
                    "fetched": None,
                    "last_success_at": None,
                    "fallback_used": True,
                    "record_count": 0,
                    "status_reason": "artifact_missing_or_unreadable",
                    "integrity_critical_failure": False,
                }
            ],
        }
        (tmp_path / "reliability_report.json").write_text(json.dumps(report))

        gd.build_index()
        content = (tmp_path / "index.html").read_text()

        assert "Pipeline Reliability Status" in content
        assert "Run mode:" in content
        assert "Degraded" in content
        assert "open_meteo_30d" in content
        assert "artifact_missing_or_unreadable" in content
