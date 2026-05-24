"""
Tests for Jupyter notebook structure, execution, and data-flow contracts.

Test tiers
----------
1. Unit-style (fast, no kernel) — structure, JSON validity, cell ordering.
2. Output-contract (no kernel) — verify exported JSON files from previous runs.
3. Integration (requires kernel, marked ``@pytest.mark.integration``) — actually
   execute each notebook via nbclient and assert it completes without errors.

Run only the fast tests (default CI)::

    pytest tests/test_notebooks.py

Run everything including live notebook execution::

    pytest tests/test_notebooks.py -m integration --timeout=300
"""
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).parent.parent
NB_DIR = REPO_ROOT / "notebooks"
DATA_DIR = REPO_ROOT / "data" / "surveillance"
PROCESSED_DIR = REPO_ROOT / "processed"

# All notebooks expected to exist (stem names without .ipynb)
EXPECTED_NOTEBOOKS = [
    "01_west_nile_virus_surveillance",
    "02_tick_disease_surveillance",
    "03_multi_disease_dashboard",
    "04_climate_disease_correlation",
    "05_climate_change_impact_analysis",
    "06_current_season_monitoring",
    "07_regional_tracking",
    "08_comprehensive_surveillance_dashboard",
    "09_model_validation_report",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_nb(name: str) -> dict[str, Any]:
    path = NB_DIR / f"{name}.ipynb"
    with open(path) as f:
        return json.load(f)


def all_code_cells(nb: dict) -> list[dict]:
    return [c for c in nb["cells"] if c.get("cell_type") == "code"]


def source_of(cell: dict) -> str:
    src = cell.get("source", [])
    return "".join(src) if isinstance(src, list) else src


# ---------------------------------------------------------------------------
# 1. Structure tests — fast, no kernel
# ---------------------------------------------------------------------------


class TestNotebookInventory:
    """Check all expected notebooks are present and findable."""

    def test_notebooks_directory_exists(self):
        assert NB_DIR.is_dir(), "notebooks/ directory not found"

    @pytest.mark.parametrize("stem", EXPECTED_NOTEBOOKS)
    def test_expected_notebook_exists(self, stem):
        assert (NB_DIR / f"{stem}.ipynb").exists(), f"{stem}.ipynb not found"

    def test_no_unexpected_notebooks(self):
        """Notebooks not in EXPECTED_NOTEBOOKS should not silently appear."""
        found = {p.stem for p in NB_DIR.glob("*.ipynb")}
        unexpected = found - set(EXPECTED_NOTEBOOKS)
        assert not unexpected, (
            f"Unexpected notebooks found (add to EXPECTED_NOTEBOOKS or remove): {unexpected}"
        )


class TestNotebookJSON:
    """Validate notebook file format."""

    @pytest.mark.parametrize("stem", EXPECTED_NOTEBOOKS)
    def test_valid_json(self, stem):
        path = NB_DIR / f"{stem}.ipynb"
        try:
            with open(path) as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            pytest.fail(f"{stem}.ipynb is not valid JSON: {exc}")
        assert "cells" in data
        assert "metadata" in data
        assert "nbformat" in data

    @pytest.mark.parametrize("stem", EXPECTED_NOTEBOOKS)
    def test_python_kernelspec(self, stem):
        nb = load_nb(stem)
        ks = nb.get("metadata", {}).get("kernelspec", {})
        lang = ks.get("language", "") or nb.get("metadata", {}).get("language_info", {}).get("name", "")
        assert "python" in lang.lower(), f"{stem}.ipynb should declare a Python kernel"

    @pytest.mark.parametrize("stem", EXPECTED_NOTEBOOKS)
    def test_every_cell_has_source_and_type(self, stem):
        nb = load_nb(stem)
        for i, cell in enumerate(nb["cells"]):
            assert "cell_type" in cell, f"{stem} cell {i}: missing cell_type"
            assert "source" in cell, f"{stem} cell {i}: missing source"
            assert cell["cell_type"] in {"code", "markdown", "raw"}, (
                f"{stem} cell {i}: unknown cell_type '{cell['cell_type']}'"
            )


class TestNotebookOrdering:
    """Ensure notebooks open with documentation and imports first."""

    @pytest.mark.parametrize("stem", EXPECTED_NOTEBOOKS)
    def test_first_cell_is_markdown_title(self, stem):
        nb = load_nb(stem)
        first = nb["cells"][0]
        assert first["cell_type"] == "markdown", (
            f"{stem}: first cell should be a markdown title, not {first['cell_type']}"
        )
        src = source_of(first)
        assert src.lstrip().startswith("#"), f"{stem}: first markdown cell should start with a heading"

    @pytest.mark.parametrize("stem", EXPECTED_NOTEBOOKS)
    def test_imports_appear_before_data_loading(self, stem):
        """Imports must come before any open() or pd.read_ calls (in different cells)."""
        nb = load_nb(stem)
        import_cell_idx = None
        load_cell_idx = None

        for i, cell in enumerate(all_code_cells(nb)):
            src = source_of(cell)
            if "import " in src and import_cell_idx is None:
                import_cell_idx = i
            if ("open(" in src or "pd.read_" in src or "json.load" in src) and load_cell_idx is None:
                load_cell_idx = i

        # Only assert if they're in different cells
        if import_cell_idx is not None and load_cell_idx is not None and import_cell_idx != load_cell_idx:
            assert import_cell_idx < load_cell_idx, (
                f"{stem}: data loading (cell {load_cell_idx}) appears before imports (cell {import_cell_idx})"
            )

    @pytest.mark.parametrize("stem", EXPECTED_NOTEBOOKS)
    def test_no_hardcoded_workspace_paths(self, stem):
        """Notebooks must not hardcode /workspaces/ paths."""
        nb = load_nb(stem)
        for i, cell in enumerate(nb["cells"]):
            src = source_of(cell)
            assert "/workspaces/" not in src, (
                f"{stem} cell {i}: contains hardcoded /workspaces/ path — use os.getcwd() instead"
            )


class TestNotebookDocumentation:
    """Notebooks should be documented with section headers."""

    @pytest.mark.parametrize("stem", EXPECTED_NOTEBOOKS)
    def test_has_markdown_sections(self, stem):
        nb = load_nb(stem)
        md_cells = [c for c in nb["cells"] if c["cell_type"] == "markdown"]
        assert len(md_cells) >= 2, (
            f"{stem}: should have at least 2 markdown cells (title + ≥1 section)"
        )

    @pytest.mark.parametrize("stem", EXPECTED_NOTEBOOKS)
    def test_no_empty_code_cells(self, stem):
        nb = load_nb(stem)
        for i, cell in enumerate(all_code_cells(nb)):
            src = source_of(cell).strip()
            assert src, f"{stem} code cell {i}: is completely empty — remove or fill it"


# ---------------------------------------------------------------------------
# 2. Data-contract tests — verify surveillance data files + exports
# ---------------------------------------------------------------------------


class TestSurveillanceDataFiles:
    """Verify data/surveillance/ JSON files conform to the expected schema."""

    def _check_file(self, name: str, required_keys: list[str], check_data_list: bool = True):
        path = DATA_DIR / name
        if not path.exists():
            pytest.skip(f"{name} not present (run scripts/fetch_surveillance_data.py first)")
        with open(path) as f:
            payload = json.load(f)
        for key in required_keys:
            assert key in payload, f"{name}: missing top-level key '{key}'"
        if check_data_list:
            assert isinstance(payload["data"], list), f"{name}: 'data' should be a list"

    def test_wnv_colorado_schema(self):
        self._check_file("wnv_colorado.json", ["fetched", "source", "data"])

    def test_lyme_colorado_schema(self):
        self._check_file("lyme_colorado.json", ["fetched", "source", "data"])

    def test_climate_colorado_schema(self):
        self._check_file("climate_colorado_90d.json", ["fetched", "source", "data"])

    def test_season_ytd_schema(self):
        self._check_file(
            "2026_season_ytd.json",
            ["season", "fetched", "data", "historical_baseline_2024"],
        )

    def test_season_ytd_entry_schema(self):
        path = DATA_DIR / "2026_season_ytd.json"
        if not path.exists():
            pytest.skip("2026_season_ytd.json not present")
        with open(path) as f:
            ytd = json.load(f)
        for entry in ytd.get("data", []):
            for key in ("week", "date", "wnv_cases", "lyme_cases", "rmsf_cases"):
                assert key in entry, f"season YTD entry missing '{key}': {entry}"
            assert 1 <= entry["week"] <= 53, f"invalid week number: {entry['week']}"
            assert entry["wnv_cases"] >= 0
            assert entry["lyme_cases"] >= 0
            assert entry["rmsf_cases"] >= 0

    def test_regional_counties_schema(self):
        path = DATA_DIR / "regional_counties_2026.json"
        if not path.exists():
            pytest.skip("regional_counties_2026.json not present")
        with open(path) as f:
            reg = json.load(f)
        assert "county_ytd" in reg
        assert "regions" in reg
        for entry in reg["county_ytd"]:
            for key in ("county", "fips", "region", "wnv_cases", "lyme_cases", "rmsf_cases"):
                assert key in entry, f"county entry missing '{key}': {entry}"

    def test_inaturalist_ticks_schema(self):
        self._check_file("inaturalist_ticks_colorado.json", ["fetched", "source", "data"])

    def test_google_trends_schema(self):
        self._check_file("google_trends_colorado.json", ["fetched", "source", "geo", "data"])

    def test_no_negative_case_counts_in_season_ytd(self):
        path = DATA_DIR / "2026_season_ytd.json"
        if not path.exists():
            pytest.skip("2026_season_ytd.json not present")
        with open(path) as f:
            ytd = json.load(f)
        for entry in ytd.get("data", []):
            for disease in ("wnv_cases", "lyme_cases", "rmsf_cases"):
                assert entry.get(disease, 0) >= 0, (
                    f"Negative {disease} in week {entry.get('week')}"
                )

    def test_season_ytd_weeks_are_unique(self):
        path = DATA_DIR / "2026_season_ytd.json"
        if not path.exists():
            pytest.skip("2026_season_ytd.json not present")
        with open(path) as f:
            ytd = json.load(f)
        weeks = [e["week"] for e in ytd.get("data", [])]
        assert len(weeks) == len(set(weeks)), f"Duplicate week entries: {weeks}"


class TestNotebookExportedOutputs:
    """Verify JSON artefacts written by notebooks during CI."""

    def test_regional_summary_export_schema(self):
        path = PROCESSED_DIR / "Dashboard" / "current_season" / "regional_summary.json"
        if not path.exists():
            pytest.skip("regional_summary.json not produced yet (run notebook 07)")
        with open(path) as f:
            summary = json.load(f)
        for key in ("generated", "season", "regions", "statewide_totals"):
            assert key in summary, f"regional_summary.json missing '{key}'"
        totals = summary["statewide_totals"]
        for disease in ("wnv", "lyme", "rmsf"):
            assert disease in totals
            assert totals[disease] >= 0


# ---------------------------------------------------------------------------
# 3. Integration tests — actually execute notebooks via nbclient
# ---------------------------------------------------------------------------

try:
    import nbformat  # noqa: F401
    import nbclient  # noqa: F401
    _NBCLIENT_AVAILABLE = True
except ImportError:
    _NBCLIENT_AVAILABLE = False


def _execute_notebook(stem: str, timeout: int = 300) -> tuple[bool, str]:
    """
    Execute a notebook in-process using nbclient.

    Returns (success, error_message).
    Sets cwd to notebooks/ so relative data paths resolve correctly.
    """
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError

    nb_path = NB_DIR / f"{stem}.ipynb"
    with open(nb_path) as f:
        nb = nbformat.read(f, as_version=4)

    client = NotebookClient(
        nb,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(NB_DIR)}},
    )
    try:
        client.execute()
        return True, ""
    except CellExecutionError as exc:
        return False, str(exc)[-800:]


@pytest.mark.integration
@pytest.mark.skipif(not _NBCLIENT_AVAILABLE, reason="nbclient not installed")
class TestNotebookExecution:
    """Run each notebook end-to-end and assert no cell raises an exception."""

    @pytest.mark.parametrize("stem", EXPECTED_NOTEBOOKS)
    def test_notebook_executes_without_error(self, stem):
        ok, err = _execute_notebook(stem)
        assert ok, f"{stem}.ipynb raised a cell error:\n{err}"

    @pytest.mark.parametrize("stem", [
        "06_current_season_monitoring",
        "07_regional_tracking",
    ])
    def test_monitoring_notebooks_produce_no_exceptions(self, stem):
        """Season-monitoring notebooks must be fully resilient to empty data."""
        ok, err = _execute_notebook(stem)
        assert ok, f"{stem}.ipynb failed (check fallback data handling):\n{err}"


# ---------------------------------------------------------------------------
# 4. nbmake compatibility note
# ---------------------------------------------------------------------------
# If pytest-nbmake is installed (`pip install pytest-nbmake`), running:
#   pytest --nbmake notebooks/
# also executes all notebooks and is a simple alternative to the integration
# tests above.  Both approaches can coexist.
