# Changelog

All notable changes to this project are documented here.
This file captures the evolution of the project at a feature/milestone level,
not commit-by-commit. For full commit history see `git log`.

---

## Upstream Versions (Cirrolytix / original AEDES project)

The upstream project went through four published versions before this fork.
See [docs/changelog.md](docs/changelog.md) for the upstream release notes.

| Version | Highlights |
|---------|-----------|
| 1.0.0 | NASA Space Apps 2019. Philippines dengue forecasting, admin-1 monthly cases, PAGASA weather, Google Trends, Sentinel-2. Stepwise regression. |
| 2.0.0 | Additional Philippine locations; ARIMA added as a comparison forecasting method. |
| 3.0.0 | Admin-2 weekly cases; Google Earth Engine remote sensing; OpenStreetMap POIs; PyPI package; HDX upload. |
| 4.0.0 | Automated pipeline (extraction → prep → ML → prediction). NASA AppEEARS, NASA Worldview, NASA POWER, geoboundaries.org, Meta Data for Good. Multidimensional INFORM-inspired risk scores for Zamboanga Peninsula. |

---

## Fork: Colorado Vector-Borne Disease Surveillance

This fork (github.com/mgifford/aedesproject-uif) adapts the framework for
**USA public-health surveillance**, focused on Colorado vector-borne disease risk.

---

### [v5.0] — Foundation: Colorado Pivot & Infrastructure (~early 2026)

**Scope change — Philippines dengue → Colorado multi-disease:**
- Renamed AEDES to *Advanced Early **Disease** Prediction and Exploration Service*
- README rewritten: Colorado vector-borne disease surveillance as primary purpose
- Added `TICK.md` and `MOSQUITO.md`: comprehensive disease reference files covering
  species, diseases, seasonality, surveillance methods, and data sources for
  *Ixodes scapularis*, *Culex tarsalis*, *Dermacentor andersoni*, and others
- Added `TICK.md` section on additional zoonotic diseases (Hantavirus, Plague,
  Leptospirosis, Rabies)
- Added validated article hyperlinks (13 peer-reviewed references) to both files

**Deployment infrastructure:**
- GitHub Actions surveillance dashboard (`surveillance-dashboard.yml`):
  daily 6 AM UTC trigger, push trigger, manual dispatch; publishes to GitHub Pages
- Weekly CDC data ingestion workflow (`weekly-data-ingestion.yml`):
  Fridays 5 PM UTC, auto-triggers dashboard rebuild
- `scripts/generate_dashboard.py`: index.html with 6 analysis cards
- `scripts/fetch_surveillance_data.py`: CDC / NASA POWER / iNaturalist data fetching
- `scripts/fetch_climate_data.py`: NOAA forecast fetching, GDD calculation
- `scripts/climate_disease_analysis.py`: thermal risk indices, alert generation

**Test suite:**
- Fixed 5 collection errors → 60 tests passing
- `tests/conftest.py` with shared fixtures
- `tests/test_scripts.py` with 24 surveillance pipeline tests
- `pytest.ini` with `integration` marker (slow nbclient tests opt-in)
- CI `test-coverage.yml` updated with correct invocation

---

### [v5.1] — Analysis Notebooks: Climate & Regional Tracking (~early 2026)

**New notebooks added:**
- **NB04** `04_climate_disease_correlation.ipynb` (19 cells): data ingestion,
  feature engineering (GDD, thermal indices, anomalies), correlation modelling
  with lag analysis, forecast export
- **NB05** `05_climate_change_impact_analysis.ipynb` (22 cells, "Option C"):
  dual-track output — documentation artifacts (DATA_DICTIONARY, QA_REPORT,
  METHODOLOGY, SUMMARY_REPORT) + analysis artifacts (merged CSV, Plotly HTML);
  2050 projections (50–100 % Lyme increase, WNV season doubled)
- **NB06** `06_current_season_monitoring.ipynb` (19 cells): 2026 real-time
  season monitoring with dynamic parameters and historical context
- **NB07** `07_regional_tracking.ipynb` (16 cells): county-level regional
  tracking across Colorado and neighbouring states

**Climate change documentation:**
- `CLIMATE_CHANGE_TRACKING.md` (~3,500 words, 8 parts): thermal biology,
  climate predictors, data sources, correlation framework, regional dynamics,
  interpretation examples, AEDES integration pathway, 2050 projections
- Climate sensitivity sections added to `TICK.md` (Lyme, RMSF, Anaplasmosis)
  and `MOSQUITO.md` (WNV, Dengue) — temperature thresholds, season extension,
  range expansion

---

### [v5.2] — Accessibility & Agent Skills Integration (~May 2026)

- `.agents/ACCESSIBILITY.md` (450+ lines): WCAG 2.1 AA visualization standards —
  colorblind-safe palettes, alt text patterns, data table exports, ARIA, plain language
- `.agents/README.md`: quick-start guide for developers using the agent skills
- `AGENTS.md` updated: Data Visualization Accessibility section, skill dependency diagram
- `skills-lock.json`: 6 accessibility skills added (charts-graphs, image-alt-text,
  tables, plain-language, color-contrast, svg)
- `tests/test_accessibility.py`: accessibility validation tests
- Notebooks 01–02 improved: anchor links, collapsible query cells, temperature
  sentinel-value handling, rolling snapshot history and trend charts in NB01
- 154 tests passing after colour-contrast test fix

---

### [v5.3] — One Health Reframing & Unified Surveillance Module (~May 2026)

**Conceptual shift — single-disease notebooks → One Health ecological framework:**
- NB01 (WNV) and NB02 (tick) refactored with One Health intro, ecological
  context, Colorado-specific data integration narrative, and risk framing

**New `aedesproject_uif.surveillance` module (1,347 lines, 6 files):**

| File | Purpose |
|------|---------|
| `registry.py` | Central registry: 12 diseases × 4 vector types (mosquito, tick, rodent, bird), `VectorEcology`, `DiseaseCharacteristics` |
| `data_loader.py` | `SurveillanceDataLoader`: CDC ArboNET, NOAA POWER, iNaturalist, USGS, pool positivity |
| `feature_engine.py` | `EcologicalFeatureEngine`: GDD, thermal suitability, habitat suitability, activity window, anomaly index |
| `risk_scorer.py` | `ProbabilisticRiskScorer`: vector presence probability, transmission risk, human exposure, outbreak risk, integrated score with 95 % CI |
| `validator.py` | `MultiLayerValidator`: ecological, entomological, epidemiological correlation checks |
| `README.md` | API documentation |

**Registry coverage:**
- 12 diseases: WNV, Lyme, RMSF, CTF, Anaplasmosis, Babesiosis, Powassan,
  TBRF, Tularemia, Plague, Hantavirus, CCHF
- 4 vector types with full ecology: Mosquito (*Culex tarsalis*), Tick
  (*Ixodes scapularis*, *Dermacentor andersoni*), Rodent (*Peromyscus maniculatus*,
  *Cynomys spp.*), Bird (*Corvus brachyrhynchos*)

**Notebook integration (Phase 1):**
- NB01, NB02, NB03 fully wired to the surveillance module — all cells clean,
  fallback data paths, probabilistic risk scoring with 95 % CI, snapshot history

---

### [v5.4] — Multi-Disease Dashboard & Comprehensive Panels (~May 2026)

**NB03** `03_multi_disease_dashboard.ipynb` (new in this version):
- Risk scoring loop over all 10 diseases
- Horizontal bar + pie risk comparison chart
- Habitat suitability timeline
- 12-month seasonal risk calendar heatmap
- Phase 2: conditional rendering guards added to all chart cells so empty
  data produces a debug note rather than an error

**NB08** `08_comprehensive_surveillance_dashboard.ipynb` (new):
- 10-panel Plotly/matplotlib One Health dashboard:
  1. Growing-Degree Days and phenology milestones
  2. Thermal suitability index vs. vector thresholds
  3. Mosquito vs. tick habitat suitability (90-day rolling)
  4. Mean temperature (daily)
  5. Temperature profile with 0 / 10 / 35 °C ecological thresholds
  6. Daily precipitation + 30-day cumulative drought indicator
  7. Rolling vector activity window
  8. Annual WNV + Lyme case totals (2010–2024)
  9. Current-year YTD cumulative cases by epi week
  10. Integrated risk score with 95 % uncertainty bands
- Viridis colorblind-safe palette throughout
- Alt-text descriptions printed below every figure
- All sections guarded against missing data

---

## Pending / Roadmap

- **Phase 4 (NB09)**: Baseline comparison and model validation — seasonal-average
  and persistence baselines, MAE/RMSE against module output
- **Accessibility — apply to NB01–07**: add alt-text prints + CSV/JSON data table
  exports to all existing notebooks (NB08 already compliant)
- **GitHub Pages accessibility**: ARIA labels, skip links, landmark structure
  on the generated `index.html` dashboard
- **CI accessibility tests**: automate alt-text presence, contrast, and table
  export checks in `tests/test_accessibility.py`
