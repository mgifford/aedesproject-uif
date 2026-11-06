"""Checks for config/data-sources.yaml, the data source registry."""
import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import fetch_surveillance_data as fsd  # noqa: E402

REGISTRY = yaml.safe_load((REPO_ROOT / "config" / "data-sources.yaml").read_text())["sources"]

REQUIRED_FIELDS = {
    "id", "artifact", "kind", "provider", "dataset", "url", "geography",
    "spatial_resolution", "temporal_resolution", "update_frequency", "observation_type",
    "data_type", "license", "status", "last_checked", "missing_data", "limitations",
}


def test_registry_lists_every_reliability_source_in_order():
    assert [e["id"] for e in REGISTRY] == [sid for sid, _ in fsd.RELIABILITY_SOURCES]


@pytest.mark.parametrize("entry", REGISTRY, ids=lambda e: e["id"])
def test_entry_has_required_fields_and_allowed_values(entry):
    missing = REQUIRED_FIELDS - set(entry)
    assert not missing, f"{entry['id']}: missing {sorted(missing)}"
    assert entry["kind"] in {"fetched", "static"}
    assert entry["observation_type"] in {"observed", "opportunistic", "modelled", "index", "unknown"}
    assert entry["status"] in {"verified", "unverified", "failing"}
    assert entry["limitations"], f"{entry['id']}: state at least one limitation"


@pytest.mark.parametrize("entry", REGISTRY, ids=lambda e: e["id"])
def test_artifact_path_matches_reliability_report(entry):
    artifacts = dict(fsd.RELIABILITY_SOURCES)
    assert entry["artifact"] == f"data/surveillance/{artifacts[entry['id']]}"


def test_verified_entries_record_when_they_were_checked():
    for entry in REGISTRY:
        if entry["status"] == "verified":
            assert entry["last_checked"], f"{entry['id']}: verified entries need last_checked"


def test_static_entries_match_committed_files():
    for entry in REGISTRY:
        path = REPO_ROOT / entry["artifact"]
        if entry["kind"] == "static" and path.exists():
            assert json.loads(path.read_text()).get("static") is True, entry["id"]
