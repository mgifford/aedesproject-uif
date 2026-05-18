# AEDES Colorado: Complete Multi-Disease Surveillance Platform

## Overview: From Single Disease to Multi-Disease Surveillance

The AEDES framework, originally built for dengue surveillance in the Philippines, can evolve into a **unified multi-disease surveillance platform** for Colorado and beyond. This document shows how different disease contexts fit together.

---

## Disease Contexts for Colorado

### Context 1: Tick-Borne Diseases (Spring-Fall Peak)

**Primary Disease**: Lyme Disease
- **Vectors**: Ixodes ticks (black-legged, western)
- **Season**: April-October (peak June-August)
- **Data Focus**: Cases, tick surveillance, Google Trends
- **Risk Factors**: Elevation, hiking activity, outdoor work

**Secondary Diseases**:
- Rocky Mountain Spotted Fever (April-June peak)
- Colorado Tick Fever (endemic, spring peak)
- Babesiosis (emerging, increasing)

**Key Data Sources**:
- CDPHE case surveillance
- iNaturalist tick observations
- Weather/temperature data
- Hiking/outdoor activity patterns

### Context 2: Mosquito-Borne Diseases (Summer-Fall Peak)

**Primary Disease**: West Nile Virus
- **Vector**: Culex mosquitoes (night-feeding)
- **Season**: June-October (peak August-September)
- **Data Focus**: Cases, mosquito trapping, dead birds
- **Risk Factors**: Standing water, urban irrigation

**Key Data Sources**:
- CDPHE WNV surveillance
- Colorado Parks & Wildlife mosquito data
- Dead bird reports (early warning)
- Weather/precipitation data

### Context 3: Wildlife Spillover Risk (Migration-Driven)

**Primary Disease**: Avian Influenza (H5N1, novel strains)
- **Vectors**: Wild birds (migratory), poultry
- **Seasons**: Spring (March-May) and Fall (August-October) migration peaks
- **Data Focus**: Wild bird detections, migration patterns, occupational exposure
- **Risk Factors**: Bird migration intensity, temperature, poultry density

**Secondary Concerns**:
- Other novel influenza strains
- Spillover to humans (occupational)
- Poultry farm economic impact

**Key Data Sources**:
- USGS National Wildlife Health Center
- eBird observations
- Colorado Parks & Wildlife
- Poultry farm biosecurity data
- Occupational health surveillance

---

## Unified Dashboard Architecture

### Dashboard Hub (Main Page)

```
AEDES Colorado: Vector-Borne & Zoonotic Disease Surveillance
================================================================

[Tabs/Navigation]
├── Lyme Disease
├── West Nile Virus  
├── Rocky Mountain Spotted Fever
├── Avian Influenza
├── Multi-Disease Risk Map
└── Integrated Forecasts
```

### Individual Disease Pages

#### Lyme Disease Tab
```
Key Metrics:
├── Cases This Year: 42
├── Cases This Week: 3
├── Trend: ↑ Increasing
├── Risk Level: MODERATE
└── Forecast (4 weeks): 45-55 cases

Real-Time Data:
├── CDPHE confirmed cases
├── Tick activity (iNaturalist)
├── Temperature correlation
├── Google Trends interest
└── County-level distribution

Charts:
├── Cases over time
├── Tick observations by location
├── Weather & case correlation
├── 4-week forecast with confidence
└── County risk heatmap

Alerts:
├── Cases increasing >20% week-over-week
├── Peak tick season approaching
├── Weather conditions favorable for transmission
└── Latest CDC guidance
```

#### West Nile Virus Tab
```
Key Metrics:
├── Cases This Year: 8
├── Cases This Week: 1
├── Mosquito Activity: MODERATE
├── Risk Level: MODERATE
└── Forecast (4 weeks): 10-15 cases

Real-Time Data:
├── CDPHE confirmed cases
├── CPW mosquito trapping results
├── Dead bird reports
├── Positive mosquito pools
└── Temperature/humidity index

Charts:
├── Cases over time
├── Mosquito activity trends
├── Dead bird reports (leading indicator)
├── Temperature conditions
└── Risk progression forecast
```

#### Avian Influenza Tab
```
Key Metrics:
├── Wild Bird Detections: 3 (last 30 days)
├── Poultry Farm Alerts: 0
├── Migration Intensity: MODERATE
├── Occupational Risk: LOW-MODERATE
└── Overall Risk Level: MODERATE

Real-Time Data:
├── USGS HPAI detections (Colorado)
├── High-risk bird sightings (eBird)
├── Migration intensity index
├── Poultry farm biosecurity status
├── Occupational health surveillance

Charts:
├── Detection locations map
├── Migration forecast
├── Risk timeline
├── Species at risk
└── Environmental conditions

Alerts:
├── New wild bird detections
├── Peak migration periods
├── Poultry farm biosecurity changes
└── CDC pandemic risk updates
```

#### Multi-Disease Risk Map
```
Interactive Map showing:
├── Current case locations (Lyme, WNV, RMSF)
├── High-risk bird sighting clusters
├── Poultry farm locations
├── Mosquito breeding habitats
├── Tick hotspots
├── Wildlife rehabilitation centers
└── Raptor centers/zoos

Color coding by disease type and risk level
Real-time updates
Clickable for detailed information
```

#### Integrated Forecasts
```
4-Week Forecast Table:
┌─────────────────────────────────────────┐
│ Week  │ Lyme │ WNV │ RMSF │ Bird Flu  │
├─────────────────────────────────────────┤
│ Week 1│ 10-12│ 2-3 │ 1-2  │ 2-4       │
│ Week 2│ 11-14│ 3-4 │ 0-1  │ 4-6       │
│ Week 3│ 12-15│ 4-6 │ 1-2  │ 6-8       │
│ Week 4│ 13-17│ 5-7 │ 1-3  │ 8-10      │
└─────────────────────────────────────────┘

Combined Risk Score:
├── Seasonal adjustment
├── Current case trends
├── Environmental factors
├── Occupational exposure risks
└── Migration/detection patterns
```

---

## Data Architecture for Multiple Diseases

### Modular Data Extraction

```
src/aedesproject_uif/
├── data_extraction/
│   ├── colorado/
│   │   ├── cdphe_surveillance.py      # All case data
│   │   ├── tick_surveillance.py       # Lyme/RMSF/CTF
│   │   ├── mosquito_surveillance.py   # WNV
│   │   ├── bird_flu_surveillance.py   # H5N1, etc.
│   │   ├── weather_data.py            # NOAA/PRISM
│   │   ├── inat_observations.py       # eBird, iNaturalist
│   │   ├── google_trends.py           # Disease searches
│   │   └── wildlife_data.py           # CPW, USGS
│   │
│   └── shared/
│       ├── base_extractor.py          # Common methods
│       ├── caching.py                 # Data caching
│       └── error_handling.py           # Unified error handling

├── data_preparation/
│   ├── colorado/
│   │   ├── lyme_data.py               # Tick-borne processing
│   │   ├── wnv_data.py                # Mosquito-borne processing
│   │   ├── bird_flu_data.py           # Spillover processing
│   │   └── integrated_data.py         # Multi-disease merging

├── ml/
│   ├── colorado/
│   │   ├── tick_forecasting.py        # Lyme + RMSF
│   │   ├── mosquito_forecasting.py    # WNV
│   │   ├── bird_flu_forecasting.py    # H5N1
│   │   ├── environmental_model.py     # Weather effects
│   │   └── combined_risk_model.py     # Integrated assessment

└── predict/
    └── colorado/
        ├── generate_lyme_forecast.py
        ├── generate_wnv_forecast.py
        ├── generate_bird_flu_forecast.py
        └── generate_integrated_report.py
```

### Data Flow

```
Real-time Data Sources
        ↓
    [Extract] (Daily automated)
        ├── CDPHE → Case data
        ├── iNaturalist → Observations
        ├── NOAA → Weather
        ├── USGS → Bird detections
        └── CPW → Wildlife data
        ↓
    [Validate & Cache]
        ├── Check data quality
        ├── Handle missing values
        ├── Normalize formats
        └── Store in docs/data/
        ↓
    [Analyze] (Weekly)
        ├── Disease-specific analysis
        ├── Environmental correlation
        ├── Trend detection
        └── Risk assessment
        ↓
    [Forecast] (Weekly)
        ├── Lyme prediction
        ├── WNV prediction
        ├── Bird flu risk
        └── Combined risk score
        ↓
    [Visualize] (Daily refresh)
        └── GitHub Pages dashboard
```

---

## GitHub Actions Workflow

### Unified Workflow for All Diseases

```yaml
# .github/workflows/colorado-surveillance.yml

name: Colorado Disease Surveillance Update

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC
  workflow_dispatch:

jobs:
  collect-data:
    runs-on: ubuntu-latest
    steps:
      # Case Surveillance
      - name: Fetch CDPHE cases
        run: python scripts/colorado/fetch_cdphe.py
      
      # Tick Surveillance
      - name: Fetch tick observations
        run: python scripts/colorado/fetch_ticks.py
      
      # Mosquito Surveillance
      - name: Fetch mosquito data
        run: python scripts/colorado/fetch_mosquitoes.py
      
      # Bird Flu Surveillance
      - name: Fetch USGS bird detections
        run: python scripts/colorado/fetch_bird_flu.py
      
      # Environmental Data
      - name: Fetch weather data
        run: python scripts/colorado/fetch_weather.py
      
      # Commit data updates
      - name: Commit data
        run: |
          git add docs/data/*
          git commit -m "Update surveillance data: $(date)" || true
          git push

  analyze-data:
    needs: collect-data
    runs-on: ubuntu-latest
    steps:
      - name: Run disease analyses
        run: python scripts/colorado/analyze_all_diseases.py
      
      - name: Generate forecasts
        run: python scripts/colorado/generate_forecasts.py
      
      - name: Create dashboard JSON
        run: python scripts/colorado/generate_dashboard.py
      
      - name: Commit analysis
        run: |
          git add docs/data/*
          git commit -m "Update analysis: $(date)" || true
          git push

  deploy:
    needs: analyze-data
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v1
```

---

## Colorado Context Configuration

```yaml
# config/contexts.yaml

colorado_tick_borne:
  name: "Colorado Tick-Borne Diseases"
  diseases:
    - lyme_disease
    - rmsf
    - colorado_tick_fever
  vectors: [tick]
  season: spring-fall
  data_sources:
    - cdphe_surveillance
    - tick_observations
    - weather_data
    - google_trends

colorado_mosquito_borne:
  name: "Colorado Mosquito-Borne Diseases"
  diseases:
    - west_nile_virus
  vectors: [mosquito]
  season: summer-fall
  data_sources:
    - cdphe_surveillance
    - mosquito_surveillance
    - dead_bird_reports
    - water_body_data

colorado_spillover_risk:
  name: "Colorado Wildlife Spillover Risk"
  diseases:
    - avian_influenza
  vectors: [wild_birds, poultry]
  seasons: [spring, fall]  # Migration peaks
  data_sources:
    - usgs_bird_detections
    - ebird_observations
    - migration_data
    - poultry_farm_status
    - occupational_health
    - weather_data

colorado_integrated:
  name: "Colorado Integrated Surveillance"
  diseases: [all]
  integration_method: risk_score_combination
  reporting_frequency: daily
  dashboard_url: https://cirrolytix.github.io/aedesproject-uif/colorado
```

---

## Summary: Disease Comparison for Colorado

| Aspect | Lyme Disease | West Nile | Bird Flu |
|--------|-------------|-----------|----------|
| **Vector** | Tick (Ixodes) | Mosquito (Culex) | Wild birds/Poultry |
| **Peak Season** | June-August | August-September | Mar-May, Aug-Oct |
| **Primary Data** | Human cases | Human cases | Wildlife detections |
| **Data Lag** | 1-3 weeks | 1-2 weeks | Real-time |
| **Leading Indicator** | Tick activity, weather | Dead birds, temperature | Migration intensity |
| **Scale** | Regional/county | Statewide | Flyway-wide |
| **Key Risk Factor** | Outdoor activity | Urban water bodies | Bird migration |
| **Surveillance** | Cases + environmental | Cases + vectors | Wildlife + occupational |

---

## Implementation Path

### Phase 1: Foundation (Months 1-2)
- ✅ Set up GitHub Pages
- ✅ Implement basic dashboard
- ✅ Integrate CDPHE case data
- [ ] Deploy initial GitHub Actions

### Phase 2: Tick-Borne Diseases (Months 2-3)
- [ ] Complete Lyme disease surveillance
- [ ] Add RMSF data
- [ ] Implement tick forecasting
- [ ] Integrate iNaturalist

### Phase 3: Mosquito-Borne Diseases (Months 3-4)
- [ ] Complete West Nile surveillance
- [ ] Add mosquito trapping data
- [ ] Integrate dead bird reporting
- [ ] Implement WNV forecasting

### Phase 4: Wildlife Spillover (Months 4-5)
- [ ] Implement bird flu surveillance
- [ ] Integrate USGS HPAI data
- [ ] Add occupational health monitoring
- [ ] Develop spillover risk models

### Phase 5: Integration & Operations (Months 5+)
- [ ] Multi-disease risk scoring
- [ ] Unified forecasting
- [ ] Stakeholder partnerships
- [ ] Public dashboard launch
- [ ] Automated alerting

---

## Key Innovation

**AEDES Colorado transforms from a single-disease tool into a multi-vector, multi-season surveillance platform**:

✅ **Modular Architecture**: Add diseases without redesigning the system  
✅ **Multiple Data Sources**: Integrate case data, environmental data, wildlife data, occupational data  
✅ **Flexible Seasonality**: Handles different transmission seasons simultaneously  
✅ **Real-Time + Predictive**: Combines current data with forecasts  
✅ **Public Access**: GitHub Pages makes data accessible to all stakeholders  
✅ **Automated Operations**: GitHub Actions keep data fresh without manual intervention  

---

## Next Steps

1. **Decide Priority**: Start with Lyme (highest burden) or Bird Flu (highest attention)?
2. **Data Partnerships**: Contact CDPHE, CPW, universities for data access
3. **Stakeholder Engagement**: Identify key users (public health, agriculture, wildlife)
4. **Set Up Infrastructure**: Deploy GitHub Pages and initial automation
5. **Build Iteratively**: Add diseases one at a time, learn from each
6. **Measure Impact**: Track adoption and outcomes

---

## Contact & Resources

**For AEDES Development:**
- GitHub: https://github.com/Cirrolytix/aedesproject-uif
- Documentation: See COLORADO_ADAPTATION.md, GITHUB_PAGES_SETUP.md, BIRD_FLU_SURVEILLANCE.md

**Colorado Data Sources:**
- CDPHE: https://cdphe.colorado.gov/disease-reports-and-data
- CPW: https://cpw.state.co.us/
- USGS: https://www.usgs.gov/avian-influenza
- NOAA: https://api.weather.gov/

**Potential Partners:**
- Colorado Department of Public Health & Environment
- Colorado Parks & Wildlife
- Colorado Department of Agriculture
- University of Colorado (Medical, Epidemiology)
- Colorado State University (Animal Health)

---

**Vision**: AEDES Colorado becomes the first unified, open-source surveillance platform monitoring vector-borne and zoonotic diseases using real-time data, environmental factors, and predictive modeling.
