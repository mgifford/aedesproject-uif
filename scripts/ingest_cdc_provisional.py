#!/usr/bin/env python3
"""
CDC Provisional Data Weekly Ingestion

Fetches the latest CDC provisional disease data and updates 2026_season_ytd.json
with new weekly data. This script is designed to run weekly (e.g., via GitHub Actions).

Supported diseases:
- West Nile Virus (WNV)
- Lyme Disease
- Rocky Mountain Spotted Fever (RMSF)

Data source: CDC NNDSS Provisional Reports
(https://www.cdc.gov/nndss/downloads.html)
"""

import json
import os
import sys
import datetime
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
import urllib.request
import urllib.error

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "surveillance"
SEASON_YTD_FILE = DATA_DIR / "2026_season_ytd.json"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


class CDCProvisionalDataFetcher:
    """Fetches and validates CDC provisional disease data."""

    # CDC NNDSS provisional report endpoints (simplified for demo)
    # In production, these would use CDC's actual API or parse their HTML reports
    CDC_NNDSS_BASE = "https://www.cdc.gov/nndss/downloads"
    
    DISEASES = {
        "west_nile_virus": {"code": "WNV", "short": "wnv"},
        "lyme": {"code": "LYM", "short": "lyme"},
        "rocky_mountain_spotted_fever": {"code": "RMS", "short": "rmsf"},
    }

    def __init__(self, timeout: int = 30):
        """Initialize fetcher with timeout."""
        self.timeout = timeout

    def fetch_url(self, url: str) -> Optional[bytes]:
        """Fetch URL with error handling."""
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AEDES-CDC-Ingestion/1.0"}
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            logger.warning(f"Failed to fetch {url}: {exc}")
            return None

    def get_current_week(self) -> int:
        """Calculate ISO week number for today."""
        today = datetime.date.today()
        return today.isocalendar()[1]

    def get_week_start_date(self, week: int, year: int = 2026) -> datetime.date:
        """Get the Monday of the given week."""
        jan1 = datetime.date(year, 1, 1)
        target_week = jan1 + datetime.timedelta(weeks=week - 1)
        # Find the Monday of this week
        monday = target_week - datetime.timedelta(days=target_week.weekday())
        return monday

    def fetch_provisional_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch provisional disease data from CDC.
        
        In a production system, this would:
        1. Parse CDC's HTML reports or use their API
        2. Extract disease counts by state
        3. Return structured data
        
        For now, we return None to trigger fallback to manual update.
        """
        logger.info("Attempting to fetch CDC provisional data...")
        
        # Try to fetch latest report (simplified)
        url = f"{self.CDC_NNDSS_BASE}/Diseases.html"
        data = self.fetch_url(url)
        
        if not data:
            logger.warning("Could not fetch CDC data; will use manual input")
            return None
        
        # In production: parse HTML/JSON and extract Colorado case counts
        # For now, return None to indicate API unavailable
        logger.info("CDC API currently unavailable; ready for manual update")
        return None


class SeasonYTDManager:
    """Manages the 2026 season YTD JSON file."""

    def __init__(self, filepath: Path = SEASON_YTD_FILE):
        """Initialize with path to season YTD file."""
        self.filepath = filepath
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load JSON file or create with defaults."""
        if self.filepath.exists():
            try:
                with open(self.filepath) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as exc:
                logger.error(f"Failed to load {self.filepath}: {exc}")
                return self._create_default()
        else:
            logger.warning(f"{self.filepath} not found; creating new")
            return self._create_default()

    def _create_default(self) -> Dict[str, Any]:
        """Create default season structure."""
        return {
            "season": "2026",
            "fetched": datetime.date.today().isoformat(),
            "status": "preliminary",
            "note": "CDC preliminary data. Official 2026 annual summary available end of year.",
            "data": [],
            "historical_baseline_2024": {
                "wnv_cases_full_year": 12,
                "lyme_cases_full_year": 119,
                "peak_wnv_month": "August",
                "peak_lyme_month": "July",
                "ytd_through_may": {"wnv": 0, "lyme": 3}
            },
            "update_frequency": "weekly",
            "next_update": self._calculate_next_update()
        }

    def _calculate_next_update(self) -> str:
        """Calculate next Monday for update."""
        today = datetime.date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_monday = today + datetime.timedelta(days=days_until_monday)
        return next_monday.isoformat()

    def get_current_week(self) -> int:
        """Get the most recent week in the data."""
        if not self.data.get("data"):
            return 0
        return max(entry.get("week", 0) for entry in self.data["data"])

    def add_week(
        self,
        week: int,
        wnv_cases: int,
        lyme_cases: int,
        rmsf_cases: int,
        notes: str = ""
    ) -> bool:
        """
        Add or update a week's data.
        
        Returns True if added, False if duplicate/error.
        """
        # Validate inputs
        if not isinstance(week, int) or week < 1 or week > 53:
            logger.error(f"Invalid week: {week}")
            return False

        if not all(isinstance(c, int) and c >= 0 for c in [wnv_cases, lyme_cases, rmsf_cases]):
            logger.error(f"Invalid case counts: WNV={wnv_cases}, Lyme={lyme_cases}, RMSF={rmsf_cases}")
            return False

        # Check for duplicate week
        existing = [e for e in self.data["data"] if e.get("week") == week]
        if existing:
            logger.warning(f"Week {week} already exists; updating")
            # Update existing
            for entry in existing:
                entry["wnv_cases"] = wnv_cases
                entry["lyme_cases"] = lyme_cases
                entry["rmsf_cases"] = rmsf_cases
                entry["notes"] = notes
                entry["updated"] = datetime.date.today().isoformat()
        else:
            # Add new week
            fetcher = CDCProvisionalDataFetcher()
            week_date = fetcher.get_week_start_date(week)
            
            new_entry = {
                "week": week,
                "date": week_date.isoformat(),
                "wnv_cases": wnv_cases,
                "lyme_cases": lyme_cases,
                "rmsf_cases": rmsf_cases,
                "source": "CDC provisional",
                "notes": notes or "Weekly update"
            }
            
            self.data["data"].append(new_entry)
            # Keep data sorted by week
            self.data["data"].sort(key=lambda x: x.get("week", 0))

        self.data["fetched"] = datetime.date.today().isoformat()
        self.data["next_update"] = self._calculate_next_update()
        
        logger.info(f"Added week {week}: WNV={wnv_cases}, Lyme={lyme_cases}, RMSF={rmsf_cases}")
        return True

    def save(self) -> bool:
        """Save to file."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=2)
            logger.info(f"Saved {self.filepath}")
            return True
        except IOError as exc:
            logger.error(f"Failed to save {self.filepath}: {exc}")
            return False

    def validate(self) -> bool:
        """Validate data integrity."""
        required_keys = {"season", "data", "fetched"}
        if not all(k in self.data for k in required_keys):
            logger.error(f"Missing required keys: {required_keys - set(self.data.keys())}")
            return False

        for entry in self.data["data"]:
            required_entry_keys = {"week", "date", "wnv_cases", "lyme_cases", "rmsf_cases"}
            if not all(k in entry for k in required_entry_keys):
                logger.error(f"Week {entry.get('week')}: missing keys")
                return False

        logger.info("Validation passed")
        return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update CDC provisional surveillance data for 2026 season"
    )
    parser.add_argument(
        "--week",
        type=int,
        help="Week number (1-53) to update"
    )
    parser.add_argument(
        "--wnv",
        type=int,
        default=0,
        help="West Nile Virus cases"
    )
    parser.add_argument(
        "--lyme",
        type=int,
        default=0,
        help="Lyme disease cases"
    )
    parser.add_argument(
        "--rmsf",
        type=int,
        default=0,
        help="Rocky Mountain Spotted Fever cases"
    )
    parser.add_argument(
        "--notes",
        type=str,
        default="",
        help="Notes for this week"
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Attempt to fetch from CDC (auto-mode)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing data without updating"
    )

    args = parser.parse_args()

    # Initialize manager
    manager = SeasonYTDManager()

    # Validate mode
    if args.validate:
        logger.info("Validation mode")
        if manager.validate():
            print("✅ Data valid")
            return 0
        else:
            print("❌ Data invalid")
            return 1

    # Fetch mode
    if args.fetch:
        logger.info("Fetch mode")
        fetcher = CDCProvisionalDataFetcher()
        provisional = fetcher.fetch_provisional_data()
        if provisional:
            # Update with fetched data (implementation depends on API)
            logger.info("Fetched data available (not yet implemented)")
        else:
            logger.info("CDC data unavailable; ready for manual weekly update")
            logger.info(f"Current week in database: {manager.get_current_week()}")
        return 0

    # Manual update mode
    if args.week:
        if manager.add_week(
            week=args.week,
            wnv_cases=args.wnv,
            lyme_cases=args.lyme,
            rmsf_cases=args.rmsf,
            notes=args.notes
        ):
            if manager.save():
                if manager.validate():
                    print(f"✅ Week {args.week} updated successfully")
                    return 0

        print("❌ Failed to update week")
        return 1

    # No action specified
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
