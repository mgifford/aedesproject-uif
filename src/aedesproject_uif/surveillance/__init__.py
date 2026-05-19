"""
Unified vector-borne disease surveillance module.

This package provides a modular, multi-disease, multi-vector framework for:
- Data ingestion from standardized sources (CDC ArboNET, NOAA, NASA, USGS, iNaturalist, etc.)
- Data harmonization and validation
- Ecological feature engineering (vector habitat suitability, phenology, climate anomalies)
- Probabilistic risk scoring and uncertainty quantification
- Multi-layer validation (ecological, entomological, epidemiological, operational)

Supports:
- Multiple vectors: mosquitoes (Culex, Aedes), ticks (Ixodes, Dermacentor), rodents
- Multiple diseases: WNV, Lyme, RMSF, Lyme disease, tularemia, plague, hantavirus
- Multiple geographies: counties, regions, ecological zones in Colorado and western US
- Multiple epidemiological and environmental datasets
"""

from .registry import DiseaseVectorRegistry, VectorType, DiseaseType
from .data_loader import SurveillanceDataLoader
from .feature_engine import EcologicalFeatureEngine
from .risk_scorer import ProbabilisticRiskScorer
from .validator import MultiLayerValidator

__all__ = [
    "DiseaseVectorRegistry",
    "VectorType",
    "DiseaseType",
    "SurveillanceDataLoader",
    "EcologicalFeatureEngine",
    "ProbabilisticRiskScorer",
    "MultiLayerValidator",
]
