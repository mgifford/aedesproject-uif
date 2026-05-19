# Unified Surveillance Module: Multi-Disease, Multi-Vector Framework

## Overview

The `surveillance` module provides a modular, extensible framework for vector-borne disease surveillance across multiple vectors (mosquitoes, ticks, rodents), diseases (WNV, Lyme, RMSF, etc.), and geographies (Colorado counties, regions, ecological zones).

**Key Principles:**
- **Multi-disease/vector support** without code duplication
- **Standardized data ingestion** from CDC ArboNET, NOAA, NASA, USGS, iNaturalist
- **Ecological feature engineering** for vector habitat suitability, phenology, climate anomalies
- **Probabilistic risk scoring** with uncertainty quantification
- **Multi-layer validation** (ecological, entomological, epidemiological, operational)
- **One Health framing** integrating human, animal, vector, climate, and land-use factors

---

## Components

### 1. **Registry** (`registry.py`)

Defines disease-vector associations, ecological characteristics, and epidemiological data.

**Key Classes:**
- `VectorType`: Enum of supported vectors (MOSQUITO, TICK, RODENT, BIRD)
- `DiseaseType`: Enum of Colorado-relevant diseases (WNV, LYME, RMSF, TULAREMIA, PLAGUE, HANTAVIRUS, etc.)
- `VectorEcology`: Ecological parameters (activity season, temperature range, humidity, habitat, hosts)
- `DiseaseCharacteristics`: Epidemiological data (incubation, CFR, reportability, endemic status)
- `DiseaseVectorRegistry`: Central registry for querying associations, ecology, and disease data

**Usage Example:**
```python
from aedesproject_uif.surveillance import DiseaseVectorRegistry, DiseaseType, VectorType

# Get disease characteristics
lyme_chars = DiseaseVectorRegistry.get_disease_characteristics(DiseaseType.LYME_DISEASE)
print(f"Lyme CFR: {lyme_chars.case_fatality_rate}")

# Get vector ecology
ixodes_ecology = DiseaseVectorRegistry.get_vector_ecology(VectorType.TICK, "ixodes_scapularis")
print(f"Ixodes activity season: {ixodes_ecology.activity_season}")

# List all diseases for a vector
tick_diseases = DiseaseVectorRegistry.list_diseases(VectorType.TICK)
```

---

### 2. **Data Loader** (`data_loader.py`)

Standardized ingestion from multiple public data sources with validation and metadata tracking.

**Key Methods:**
- `load_cdc_arbonet_cases()`: Human case surveillance from CDC ArboNET
- `load_mosquito_pool_data()`: Entomological mosquito pool testing
- `load_noaa_climate_data()`: Temperature, precipitation, humidity from NASA POWER/NOAA
- `load_inaturalist_vector_observations()`: Citizen-science vector observations
- `load_tick_surveillance_data()`: Local tick trap/pool data
- `load_usgs_ecological_data()`: Habitat suitability, water bodies, elevation

**Features:**
- Handles multiple file formats (JSON, CSV, GeoJSON)
- Validates data schemas and filters invalid values
- Tracks metadata (source, record count, date range)
- Resolves missing values gracefully

**Usage Example:**
```python
from aedesproject_uif.surveillance import SurveillanceDataLoader

loader = SurveillanceDataLoader(data_dir="/path/to/surveillance")

# Load CDC data
wnv_cases = loader.load_cdc_arbonet_cases(disease="wnv", region="colorado", year_start=2020)

# Load climate data
climate = loader.load_noaa_climate_data(region="colorado_denver", days_back=90)

# Load iNaturalist tick observations
tick_obs = loader.load_inaturalist_vector_observations("ticks", "colorado")

# Get metadata
print(loader.get_metadata())
```

---

### 3. **Feature Engine** (`feature_engine.py`)

Ecological feature engineering for vector habitat suitability, phenology, and climate anomalies.

**Key Methods:**
- `compute_thermal_suitability()`: Temperature-based habitat suitability (0-1)
- `compute_growing_degree_days()`: Accumulated GDD for phenology prediction
- `compute_humidity_suitability()`: Humidity-based habitat suitability
- `compute_activity_window()`: Seasonal activity timing
- `compute_combined_habitat_suitability()`: Integrated habitat index
- `compute_climate_anomaly_index()`: Deviation from historical baseline

**Supports:**
- Vector-specific ecology (temperature ranges, humidity requirements, seasonality)
- Phenological modeling (development timing via GDD)
- Climate anomaly detection
- Multi-factor habitat suitability integration

**Usage Example:**
```python
from aedesproject_uif.surveillance import EcologicalFeatureEngine, VectorType

engine = EcologicalFeatureEngine(VectorType.TICK)

# Compute thermal suitability for Ixodes from temperature data
thermal = engine.compute_thermal_suitability(climate_df['temp_c'])

# Compute GDD for phenology
gdd = engine.compute_growing_degree_days(climate_df['temp_c'], base_temp=10)

# Combined habitat suitability
habitat = engine.compute_combined_habitat_suitability(
    climate_df,
    weights={'thermal': 0.6, 'humidity': 0.3, 'season': 0.1}
)
```

---

### 4. **Risk Scorer** (`risk_scorer.py`)

Probabilistic risk estimation with uncertainty quantification across multiple dimensions.

**Key Methods:**
- `compute_vector_presence_probability()`: P(vector present) with confidence intervals
- `compute_transmission_risk()`: P(pathogen transmission | vector)
- `compute_human_exposure_risk()`: P(human exposure to vector)
- `compute_outbreak_risk()`: P(outbreak | current conditions)
- `compute_integrated_risk_score()`: Composite score from multiple components
- `categorize_risk()`: Convert probability to LOW/MODERATE/HIGH

**Features:**
- Probabilistic outputs (point estimates + confidence intervals)
- Integrates multiple data streams (habitat, cases, climate)
- Adaptive uncertainty based on signal confidence
- Composite scoring with configurable weights

**Usage Example:**
```python
from aedesproject_uif.surveillance import ProbabilisticRiskScorer

scorer = ProbabilisticRiskScorer()

# Compute vector presence probability
vec_prob, vec_low_ci, vec_high_ci = scorer.compute_vector_presence_probability(
    habitat_suitability,
    recent_observations=5,
    observation_confidence=0.9
)

# Compute integrated risk
integrated_risk, low_risk, high_risk = scorer.compute_integrated_risk_score(
    vector_prob,
    transmission_prob,
    exposure_prob,
    outbreak_prob,
    weights={'vector': 0.2, 'transmission': 0.3, 'exposure': 0.3, 'outbreak': 0.2}
)

# Categorize
risk_category = scorer.categorize_risk(integrated_risk)
```

---

### 5. **Multi-Layer Validator** (`validator.py`)

Validates models across ecological, entomological, epidemiological, and operational layers.

**Validation Layers:**

1. **Ecological**: Vector habitat predictions vs. known distribution (sensitivity, specificity)
2. **Entomological**: Vector activity predictions vs. pool/trap data (correlation)
3. **Epidemiological**: Case forecasts vs. observed cases (lead time, false alert rate, outbreak detection)
4. **Operational**: Baseline comparison (seasonal average, persistence), geographic generalization, drift testing

**Key Methods:**
- `validate_ecological_accuracy()`: Confusion matrix vs. presence/absence data
- `validate_entomological_correlation()`: Spearman/Pearson correlation with pool/trap counts
- `validate_epidemiological_accuracy()`: Lead time, sensitivity to severe outbreaks, false alert rate
- `compare_to_baselines()`: Model performance vs. seasonal, persistence baselines
- `validate_geographic_generalization()`: Performance across urban/rural and geographic strata
- `validate_drift_testing()`: Performance stability across major events (pandemic, climate shifts)

**Usage Example:**
```python
from aedesproject_uif.surveillance import MultiLayerValidator

validator = MultiLayerValidator()

# Ecological validation
eco_results = validator.validate_ecological_accuracy(
    predicted_habitat,
    observed_presence,
    presence_threshold=0.5
)

# Epidemiological validation with lead-time analysis
epi_results = validator.validate_epidemiological_accuracy(
    predicted_risk,
    observed_cases,
    lead_time_days=14
)

# Baseline comparison
baseline_results = validator.compare_to_baselines(
    predicted_cases,
    observed_cases,
    historical_data=historical_cases
)

# Geographic generalization
geo_results = validator.validate_geographic_generalization(
    model_predictions={'denver': pred1, 'rural_county': pred2},
    observed_cases={'denver': obs1, 'rural_county': obs2},
    geography_types={'denver': 'urban', 'rural_county': 'rural'}
)

# Get full report
report = validator.get_validation_report()
```

---

## Workflow: Multi-Disease Surveillance

**Example: Building a unified WNV + Lyme + RMSF surveillance dashboard**

```python
from aedesproject_uif.surveillance import (
    DiseaseVectorRegistry, DiseaseType, VectorType,
    SurveillanceDataLoader, EcologicalFeatureEngine,
    ProbabilisticRiskScorer, MultiLayerValidator
)

# Configure diseases
diseases = [DiseaseType.WEST_NILE_VIRUS, DiseaseType.LYME_DISEASE, DiseaseType.ROCKY_MOUNTAIN_SPOTTED_FEVER]

# Load climate data (shared across all diseases)
loader = SurveillanceDataLoader()
climate_data = loader.load_noaa_climate_data("colorado_denver", days_back=90)

results = {}

for disease in diseases:
    print(f"\n=== {disease.value.upper()} ===")
    
    # Get disease info
    disease_chars = DiseaseVectorRegistry.get_disease_characteristics(disease)
    vectors = DiseaseVectorRegistry.get_vectors_for_disease(disease)
    
    print(f"Vectors: {[v.value for v in vectors]}")
    print(f"Case Fatality Rate: {disease_chars.case_fatality_rate * 100:.2f}%")
    
    # Integrate vectors
    all_risk = None
    for vector in vectors:
        # Get vector ecology
        ecology = DiseaseVectorRegistry.get_vector_ecology(vector)
        
        # Feature engineering
        engine = EcologicalFeatureEngine(vector)
        habitat = engine.compute_combined_habitat_suitability(climate_data)
        
        # Risk scoring
        scorer = ProbabilisticRiskScorer()
        vector_prob, _, _ = scorer.compute_vector_presence_probability(habitat)
        
        if all_risk is None:
            all_risk = vector_prob
        else:
            all_risk = all_risk.combine(vector_prob, max)  # Take max across vectors
    
    # Load epidemiological data
    cases = loader.load_cdc_arbonet_cases(disease.value, "colorado")
    
    # Compute integrated risk
    scorer = ProbabilisticRiskScorer()
    integrated_risk, low_ci, high_ci = scorer.compute_integrated_risk_score(
        all_risk, all_risk * 0.7, all_risk * 0.8, all_risk * 0.6
    )
    
    # Validation
    if len(cases) > 0:
        validator = MultiLayerValidator()
        validator.validate_epidemiological_accuracy(integrated_risk, cases)
        validator.compare_to_baselines(integrated_risk, cases)
        report = validator.get_validation_report()
        print(f"Validation: {report}")
    
    results[disease.value] = {
        'risk': integrated_risk,
        'low_ci': low_ci,
        'high_ci': high_ci,
    }
```

---

## Extending the Framework

### Adding a New Disease

1. Add to `DiseaseType` enum in `registry.py`
2. Add `DiseaseCharacteristics` to `DISEASE_CHARACTERISTICS` dict
3. Add vector association to `DISEASE_VECTORS` dict

```python
class DiseaseType(Enum):
    MY_NEW_DISEASE = "mynewd"  # Add here

DISEASE_CHARACTERISTICS = {
    DiseaseType.MY_NEW_DISEASE: DiseaseCharacteristics(
        disease_type=DiseaseType.MY_NEW_DISEASE,
        vector_types=[VectorType.TICK],
        incubation_days=(5, 21),
        case_fatality_rate=0.01,
        colorado_endemic=True,
        reportable=True,
        description="..."
    ),
}
```

### Adding a New Vector Species

```python
VECTOR_ECOLOGY = {
    VectorType.TICK: {
        "my_new_tick": VectorEcology(
            vector_type=VectorType.TICK,
            scientific_names=["My new tick"],
            primary_habitat="...",
            activity_season=(3, 10),
            temperature_min_c=8,
            temperature_max_c=28,
            temperature_peak_c=18,
            humidity_min_percent=65,
            primary_hosts=["deer", "humans"],
            phenology_description="..."
        ),
    },
}
```

### Adding a New Data Source

Extend `SurveillanceDataLoader` with a new method:

```python
def load_my_custom_data_source(self, region: str) -> pd.DataFrame:
    """Load custom data and return standardized DataFrame."""
    # Load, validate, harmonize
    df = pd.read_csv(f"my_data_{region}.csv")
    
    # Track metadata
    self.metadata[f"my_source_{region}"] = {...}
    
    return df
```

---

## Integration with Notebooks

The surveillance module is designed to be used in Jupyter notebooks for analysis and reporting.

**Example Notebook Structure:**

```python
# Cell 1: Import and configure
from aedesproject_uif.surveillance import (
    DiseaseVectorRegistry, DiseaseType,
    SurveillanceDataLoader, EcologicalFeatureEngine,
    ProbabilisticRiskScorer, MultiLayerValidator
)

disease = DiseaseType.WEST_NILE_VIRUS
region = "colorado"

# Cell 2: Load data
loader = SurveillanceDataLoader()
climate = loader.load_noaa_climate_data(f"{region}_denver")
cases = loader.load_cdc_arbonet_cases(disease.value, region)
pools = loader.load_mosquito_pool_data(region, species="culex_tarsalis")

# Cell 3: Feature engineering
engine = EcologicalFeatureEngine(VectorType.MOSQUITO)
habitat = engine.compute_combined_habitat_suitability(climate)

# Cell 4: Risk scoring
scorer = ProbabilisticRiskScorer()
risk, low_ci, high_ci = scorer.compute_integrated_risk_score(habitat, ...)

# Cell 5: Validation
validator = MultiLayerValidator()
validator.validate_epidemiological_accuracy(risk, cases)

# Cell 6: Visualization
import matplotlib.pyplot as plt
plt.plot(risk.index, risk, label='Risk')
plt.fill_between(low_ci.index, low_ci, high_ci, alpha=0.3)
plt.show()
```

---

## Configuration & Customization

**Disease/Vector Associations:**
Update `registry.py` `DISEASE_VECTORS`, `DISEASE_CHARACTERISTICS`, `VECTOR_ECOLOGY` dicts.

**Data Paths:**
`SurveillanceDataLoader` resolves paths from `PROJECT_ROOT/data/surveillance/`.

**Risk Scoring Weights:**
Pass custom `weights` dict to `compute_integrated_risk_score()`.

**Validation Thresholds:**
Adjust thresholds in `MultiLayerValidator` methods.

---

## Testing

Run the test suite to validate the surveillance module:

```bash
pytest tests/test_surveillance_registry.py
pytest tests/test_surveillance_data_loader.py
pytest tests/test_surveillance_feature_engine.py
pytest tests/test_surveillance_risk_scorer.py
pytest tests/test_surveillance_validator.py
```

---

## References

- CDC ArboNET: https://www.cdc.gov/vector-borne-diseases/php/arbonet/index.html
- NASA POWER: https://power.larc.nasa.gov/
- NOAA Climate: https://www.ncdc.noaa.gov/cdo-web/
- USGS Ecological: https://www.usgs.gov/
- iNaturalist: https://www.inaturalist.org/

---

**Last Updated:** May 19, 2026  
**Version:** 1.0.0  
**License:** CC BY-SA 4.0
