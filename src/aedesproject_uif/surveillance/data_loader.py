"""
Unified surveillance data loader.

Handles standardized ingestion from CDC ArboNET, NOAA, NASA, USGS, iNaturalist,
and other public data sources.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import pandas as pd
from datetime import datetime, timedelta


class SurveillanceDataLoader:
    """
    Standardized data loader for surveillance data from multiple sources.
    
    Provides unified methods for loading CDC, NOAA, NASA, USGS, and citizen-science data
    with data validation, harmonization, and metadata tracking.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the data loader.
        
        Args:
            data_dir: Path to surveillance data directory. If None, defaults to
                     PROJECT_ROOT/data/surveillance
        """
        if data_dir is None:
            # Default to project structure
            from ..config import Config
            data_dir = Config.DATA_DIR / "surveillance"
        
        self.data_dir = Path(data_dir)
        self.metadata: Dict[str, Any] = {}
    
    def load_cdc_arbonet_cases(
        self, 
        disease: str, 
        region: str,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load CDC ArboNET human case data.
        
        Args:
            disease: Disease code (e.g., 'wnv', 'lyme', 'rmsf')
            region: Geographic region (e.g., 'colorado', 'western_us')
            year_start: Start year (inclusive)
            year_end: End year (inclusive)
        
        Returns:
            DataFrame with columns: date, county, disease, cases, deaths
        """
        # Try multiple file paths
        candidates = [
            self.data_dir / f"{disease}_{region}_cases.json",
            self.data_dir / f"cdc_arbonet_{disease}_{region}.csv",
            self.data_dir / f"{disease}_{region}.json",
        ]
        
        df = None
        for path in candidates:
            if path.exists():
                if path.suffix == ".json":
                    with open(path) as f:
                        data = json.load(f)
                    if isinstance(data, dict) and "data" in data:
                        df = pd.DataFrame(data["data"])
                    else:
                        df = pd.DataFrame(data)
                else:
                    df = pd.read_csv(path)
                break
        
        if df is None or df.empty:
            return pd.DataFrame(columns=["date", "county", "disease", "cases", "deaths"])
        
        # Standardize columns
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        
        # Filter by year range if specified
        if year_start is not None and "date" in df.columns:
            df = df[df["date"].dt.year >= year_start]
        if year_end is not None and "date" in df.columns:
            df = df[df["date"].dt.year <= year_end]
        
        # Track metadata
        self.metadata[f"cdc_arbonet_{disease}"] = {
            "source": "CDC ArboNET",
            "disease": disease,
            "region": region,
            "records": len(df),
            "date_range": (df["date"].min(), df["date"].max()) if "date" in df.columns else None,
        }
        
        return df
    
    def load_mosquito_pool_data(
        self,
        region: str,
        species: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load mosquito pool test data (entomological surveillance).
        
        Args:
            region: Geographic region
            species: Optional mosquito species filter (e.g., 'culex_tarsalis')
        
        Returns:
            DataFrame with columns: date, location, species, pool_size, positive_pools
        """
        candidates = [
            self.data_dir / f"mosquito_pools_{region}.json",
            self.data_dir / f"entomological_surveillance_{region}.csv",
        ]
        
        df = None
        for path in candidates:
            if path.exists():
                if path.suffix == ".json":
                    with open(path) as f:
                        data = json.load(f)
                    df = pd.DataFrame(data.get("data", []))
                else:
                    df = pd.read_csv(path)
                break
        
        if df is None or df.empty:
            return pd.DataFrame(columns=["date", "location", "species", "pool_size", "positive_pools"])
        
        if species is not None and "species" in df.columns:
            df = df[df["species"] == species]
        
        self.metadata[f"mosquito_pools_{region}"] = {
            "source": "Local/State Vector Surveillance",
            "region": region,
            "records": len(df),
        }
        
        return df
    
    def load_noaa_climate_data(
        self,
        region: str,
        days_back: int = 90
    ) -> pd.DataFrame:
        """
        Load NOAA/NASA POWER climate data.
        
        Args:
            region: Geographic region (e.g., 'colorado_denver')
            days_back: Days of historical data to load
        
        Returns:
            DataFrame with columns: date, temp_c, temp_f, precip_mm, humidity_percent
        """
        candidates = [
            self.data_dir / f"climate_{region}_90d.json",
            self.data_dir / f"climate_{region}.csv",
            self.data_dir / f"nasa_power_{region}.csv",
        ]
        
        df = None
        for path in candidates:
            if path.exists():
                if path.suffix == ".json":
                    with open(path) as f:
                        data = json.load(f)
                    df = pd.DataFrame(data.get("data", []))
                else:
                    df = pd.read_csv(path)
                break
        
        if df is None or df.empty:
            return pd.DataFrame(columns=["date", "temp_c", "temp_f", "precip_mm", "humidity_percent"])
        
        # Parse date
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
        
        # Filter invalid temperature values (NASA POWER uses -999 for missing)
        if "temp_c" in df.columns:
            df = df[df["temp_c"] > -80]
        
        self.metadata[f"climate_{region}"] = {
            "source": "NASA POWER / NOAA",
            "region": region,
            "records": len(df),
            "date_range": (df["date"].min(), df["date"].max()) if "date" in df.columns else None,
        }
        
        return df
    
    def load_inaturalist_vector_observations(
        self,
        vector_type: str,
        region: str
    ) -> pd.DataFrame:
        """
        Load iNaturalist citizen-science vector observations.
        
        Args:
            vector_type: Type of vector ('mosquitoes', 'ticks', 'rodents')
            region: Geographic region
        
        Returns:
            DataFrame with columns: date, location, species, latitude, longitude
        """
        candidates = [
            self.data_dir / f"inaturalist_{vector_type}_{region}.json",
            self.data_dir / f"inat_{vector_type}_{region}.csv",
        ]
        
        df = None
        for path in candidates:
            if path.exists():
                if path.suffix == ".json":
                    with open(path) as f:
                        data = json.load(f)
                    df = pd.DataFrame(data.get("data", []))
                else:
                    df = pd.read_csv(path)
                break
        
        if df is None or df.empty:
            return pd.DataFrame(columns=["date", "location", "species", "latitude", "longitude"])
        
        # Parse observation date
        if "observed_on" in df.columns:
            df["date"] = pd.to_datetime(df["observed_on"], errors="coerce")
        elif "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        
        self.metadata[f"inat_{vector_type}_{region}"] = {
            "source": "iNaturalist",
            "vector_type": vector_type,
            "region": region,
            "records": len(df),
            "date_range": (df["date"].min(), df["date"].max()) if "date" in df.columns else None,
        }
        
        return df
    
    def load_tick_surveillance_data(
        self,
        region: str
    ) -> pd.DataFrame:
        """
        Load local/state tick surveillance data (collection counts, pool testing).
        
        Args:
            region: Geographic region
        
        Returns:
            DataFrame with tick surveillance metrics
        """
        candidates = [
            self.data_dir / f"tick_surveillance_{region}.json",
            self.data_dir / f"tick_traps_{region}.csv",
        ]
        
        df = None
        for path in candidates:
            if path.exists():
                if path.suffix == ".json":
                    with open(path) as f:
                        data = json.load(f)
                    df = pd.DataFrame(data.get("data", []))
                else:
                    df = pd.read_csv(path)
                break
        
        if df is None or df.empty:
            return pd.DataFrame()
        
        self.metadata[f"tick_surveillance_{region}"] = {
            "source": "State Vector Control / Public Health",
            "region": region,
            "records": len(df),
        }
        
        return df
    
    def load_usgs_ecological_data(
        self,
        region: str,
        data_type: str = "habitat_suitability"
    ) -> pd.DataFrame:
        """
        Load USGS ecological and habitat data.
        
        Args:
            region: Geographic region
            data_type: Type of data ('habitat_suitability', 'water_bodies', 'elevation', etc.)
        
        Returns:
            DataFrame with ecological data
        """
        path = self.data_dir / f"usgs_{data_type}_{region}.geojson"
        
        if not path.exists():
            return pd.DataFrame()
        
        with open(path) as f:
            geojson = json.load(f)
        
        features = geojson.get("features", [])
        df = pd.DataFrame([f.get("properties", {}) for f in features])
        
        self.metadata[f"usgs_{data_type}_{region}"] = {
            "source": "USGS",
            "data_type": data_type,
            "region": region,
            "records": len(df),
        }
        
        return df
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata for all loaded datasets."""
        return self.metadata
