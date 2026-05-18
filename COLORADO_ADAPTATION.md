# AEDES Adaptation: Colorado Vector-Borne Disease Surveillance

## Executive Summary

The AEDES framework, originally developed for dengue surveillance in the Philippines, can be effectively adapted to monitor vector-borne diseases in Colorado. This document outlines:

1. **Relevant Diseases**: Lyme Disease, West Nile Virus, Rocky Mountain Spotted Fever
2. **Data Sources**: Colorado-specific health, environmental, and surveillance data
3. **Architecture Changes**: Modular configuration to support multiple contexts
4. **GitHub Pages Setup**: Real-time monitoring dashboard and visualization

---

## Part 1: Vector-Borne Diseases in Colorado

### Primary Diseases of Concern

#### 1. **Lyme Disease** 🔴 (HIGHEST PRIORITY)
**Why It's Important:**
- Fastest-growing vector-borne disease in the US
- Colorado is in the tick endemic zone (especially Western Slope)
- Serious health consequences if untreated
- Seasonal pattern (spring-fall, peak summer)

**Epidemiology:**
- Agent: Borrelia burgdorferi (spirochete bacteria)
- Vector: Ixodes scapularis (black-legged tick), Ixodes pacificus (Western tick)
- Geographic Range: Expanding (particularly Western Colorado)
- Cases: ~300,000 annually in US (likely underestimated)
- Colorado Case Trend: Increasing over past decade

**Risk Factors in Colorado:**
- High altitude forests (tick habitat)
- Outdoor recreation (hiking, camping, hunting)
- Wildlife: White-tailed deer, black bears, mountain lions
- Elevation effect: Some areas have higher tick populations

**Surveillance Indicators:**
- Laboratory-confirmed cases reported to CDPHE
- Seasonal patterns (April-October)
- Geographic clusters (county-level)
- Age groups (outdoor workers, recreationalists)

#### 2. **West Nile Virus** 🟡 (MEDIUM PRIORITY)
**Why It's Important:**
- Mosquito-borne (not tick)
- Seasonal epidemic pattern
- Can cause severe neurological complications
- Colorado had significant outbreaks (2002-2003, 2018)

**Epidemiology:**
- Agent: West Nile Virus (flavivirus)
- Vector: Culex mosquitoes (night-feeding)
- Geographic Range: Throughout Colorado
- Cases: Varies by year (2018: 80+ cases in Colorado)
- Severity: ~80% asymptomatic, ~20% symptomatic, <1% severe

**Risk Factors in Colorado:**
- Summer/early fall transmission (June-October)
- Standing water (breeding grounds for Culex)
- Urban/suburban areas with irrigation
- Elderly and immunocompromised higher risk

**Surveillance Indicators:**
- Human cases
- Mosquito surveillance/trapping data
- Dead bird surveillance (early warning)
- Water body stagnation

#### 3. **Rocky Mountain Spotted Fever** 🟡 (MEDIUM PRIORITY)
**Why It's Important:**
- Named after the Rocky Mountain region
- High case fatality rate if untreated (5-10%)
- Requires early antibiotic intervention
- Less common but more severe than Lyme

**Epidemiology:**
- Agent: Rickettsia rickettsii (bacterium)
- Vector: Dermacentor ticks (wood ticks)
- Geographic Range: Western Colorado especially
- Cases: ~30-50 annually in Colorado
- Severity: Higher mortality if untreated

**Risk Factors in Colorado:**
- Spring (April-June): peak tick activity
- Wood/oak brush habitat
- Outdoor recreation in endemic areas
- Early season tick exposure (April-May)

#### 4. **Colorado Tick Fever** 🟢 (EMERGING)
**Why It's Important:**
- Endemic to Colorado region
- Under-recognized/under-reported
- Distinct from Rocky Mountain Spotted Fever

**Epidemiology:**
- Agent: Colorado Tick Fever Virus (orbivirus)
- Vector: Dermacentor ticks
- Geographic Range: Western slope mountains
- Cases: ~40-50 annually in Colorado

#### 5. **Babesiosis** 🟢 (EMERGING)
**Why It's Important:**
- Emerging threat in Colorado
- Tick-borne
- Can be severe in immunocompromised

**Epidemiology:**
- Agent: Babesia parasite
- Vector: Ixodes scapularis tick
- Geographic Range: Expanding eastward into Colorado
- Cases: Still rare in Colorado but increasing

---

## Part 2: Data Sources for Colorado Context

### A. Official Health Surveillance Data

#### 1. **Colorado Department of Public Health & Environment (CDPHE)**
**Data Available:**
- Confirmed case reports (Lyme, West Nile, RMSF)
- Weekly disease surveillance reports
- County-level case distributions
- Testing/laboratory data

**Access:**
```
https://cdphe.colorado.gov/disease-reports-and-data
Database: Colorado Disease Reporting System (CDRS)
```

**API/Data Format:**
- Weekly reports (PDF/web)
- County-level data (HTML tables)
- May need FOIA request for detailed data

**Availability:**
- Historical: 5+ years
- Frequency: Weekly/Monthly
- Lag: 1-2 weeks

#### 2. **CDC Disease Surveillance (NNDSS/FluView)**
**Data Available:**
- National case counts
- State-level aggregates
- Provisional estimates
- Mortality data

**Access:**
```
https://wonder.cdc.gov/
https://www.cdc.gov/lyme/index.html
https://www.cdc.gov/westnile/
```

**API:**
```bash
# CDC Wonder API documentation
https://wonder.cdc.gov/api/
```

#### 3. **Hospital Emergency Department Data**
**Data Available:**
- Chief complaint surveillance (tick bites, rashes)
- Syndromic surveillance
- Real-time trend data

**Access:**
- Colorado Hospital Association may have aggregated data
- CMS has de-identified ED data
- State health department may have partnerships

### B. Environmental & Climate Data

#### 1. **Temperature & Precipitation**
**Why It Matters:**
- Drives tick/mosquito population dynamics
- Affects vector activity season
- Key predictor of disease transmission

**Sources:**
```
1. NOAA National Weather Service
   - Daily/hourly climate data
   - County-level summaries
   API: https://www.weather.gov/documentation/services-web-api

2. PRISM Climate Data (Oregon State University)
   - Daily precipitation & temperature
   - High spatial resolution (4km grid)
   URL: https://prism.oregonstate.edu/

3. NASA POWER (Already in AEDES!)
   - Meteorological data for any location
   - Solar radiation, temperature, humidity
   API: https://power.larc.nasa.gov/api/v1/
```

#### 2. **Elevation & Topography**
**Why It Matters:**
- Colorado's elevation variation (3,000-14,000 ft)
- Affects temperature, climate, tick populations
- Influences hiking/exposure patterns

**Sources:**
```
USGS Digital Elevation Model (DEM)
- 30m resolution
- Free download
URL: https://www.usgs.gov/3dep

Use with AEDES to create elevation-stratified analysis
```

#### 3. **Vegetation & Land Use**
**Why It Matters:**
- Indicates tick/mosquito habitat
- Oak/scrub brush = tick habitat
- Agricultural areas = mosquito breeding
- Urban areas = West Nile risk

**Sources:**
```
USGS Landsat
- Multi-spectral imagery
- NDVI (vegetation index)
- Land cover classification
API: https://earthexplorer.usgs.gov/

NOAA Land Cover Database
- 30m resolution
- Classes: forest, shrub, grass, developed, water
URL: https://www.mrlc.gov/

Sentinal-2 (ESA)
- Similar to Landsat
- 10m resolution in some bands
- Free access
```

#### 4. **Phenology Data**
**Why It Matters:**
- When spring arrives (affects tick emergence)
- Growing season length
- Predictive for disease season

**Sources:**
```
USGS Phenology Project
- Spring indices
- Leaf-out dates
- Bloom predictions
URL: https://www.usgs.gov/faqs/what-leaf-out-index

NASA SMAP/Sentinel phenology products
- Remote sensing based phenology
```

### C. Vector & Wildlife Data

#### 1. **Tick Surveillance Programs**
**Colorado-Specific:**
```
Colorado Parks & Wildlife
- Tick surveys
- Disease prevalence in ticks
- Population estimates
Contact: colorado.gov/parks-wildlife

University of Colorado Tick Lab
- Active tick surveillance
- Pathogen testing
- Research partnerships
```

**Citizen Science:**
```
iNaturalist
- Tick observations (with photos)
- Geographic distribution
- Seasonal patterns
API: https://api.inaturalist.org/v1/

TickReport/TickEncounter
- Crowd-sourced tick reports
- Location data
- Species identification
URL: https://www.tickencounter.org/
```

#### 2. **Mosquito Surveillance**
**Colorado Data:**
```
Colorado Department of Agriculture
- West Nile Virus surveillance
- Mosquito trapping data
- County-level programs

Local Public Health Agencies
- County-level mosquito control
- Trapping data
- Treatment reports

CDC/USGS Arbovirus Surveillance
- National mosquito surveillance
- West Nile positive sites
```

#### 3. **Wildlife Population Data**
**Why It Matters:**
- Deer populations affect tick abundance
- Wildlife behavior affects human exposure
- Useful for forecasting

**Sources:**
```
Colorado Parks & Wildlife
- Deer population surveys
- Habitat assessments
- Population trends
URL: https://cpw.state.co.us/

USGS Wildlife Data
- Regional wildlife estimates

iNaturalist
- Large mammal observations
```

### D. Population & Exposure Data

#### 1. **Demographic Data**
**Sources:**
```
US Census Bureau
- Population density by county/block
- Age distribution
- Socioeconomic data
API: https://api.census.gov/

CDC Social Vulnerability Index
- Combines demographic and socioeconomic data
- County-level
```

#### 2. **Activity/Exposure Data**
**Hiking & Recreation (Proxy for Exposure):**
```
AllTrails.com
- Trail popularity data
- Hiking season patterns
- Traffic by location
Possible scraping with permission

Google Trends
- "Hiking Colorado"
- "Lyme disease Colorado"
- "Tick bite prevention"
API: pytrends library (already in AEDES)

Google Maps
- Park visits
- Popular trails
- Seasonal patterns
```

#### 3. **Occupational Risk Data**
**Sources:**
```
Colorado Labor Statistics
- Outdoor workers by county
- Agricultural workers
- Construction workers

Forestry/Land Management
- Worker populations
- Land management schedules
```

### E. Social Data & Digital Signals

#### 1. **Google Trends**
**Relevant Searches:**
```
Disease-related:
- "Lyme disease"
- "Lyme disease Colorado"
- "West Nile Virus"
- "Rocky Mountain Spotted Fever"

Symptom-related:
- "Tick bite"
- "Rash"
- "Joint pain"

Prevention-related:
- "Tick prevention"
- "DEET"
- "Permethrin"
```

**Why It's Useful:**
- Early warning of disease awareness
- Seasonal pattern detection
- Lag time: peaks may lead cases

#### 2. **News & Media Analysis**
**Sources:**
```
NewsAPI
- Colorado health news
- Disease outbreak coverage
- Travel warnings

Reddit/Social Media
- Community reports
- Personal experiences
- Geographic tags
```

#### 3. **Search Engine Optimization Data**
```
SEMrush/Ahrefs (if budget allows)
- Health-related search volume
- Geographic variations
```

---

## Part 3: Architecture for Multi-Context AEDES

### Current State (Philippines/Dengue)
```
src/aedesproject_uif/
├── data_extraction/
│   ├── demographics.py
│   ├── google_trends.py
│   ├── nasa_power.py
│   └── ... (Philippines-specific)
├── data_preparation/
├── ml/
└── predict/
```

### Proposed Multi-Context Architecture

```
src/aedesproject_uif/
├── config/
│   ├── contexts.py          # (NEW) Context configurations
│   ├── colorado/
│   │   ├── disease_config.py
│   │   ├── data_sources.py
│   │   └── parameters.py
│   └── philippines/
│       ├── disease_config.py
│       └── parameters.py
│
├── data_extraction/
│   ├── __init__.py
│   ├── demographics.py
│   ├── google_trends.py
│   ├── nasa_power.py
│   ├── colorado/           # (NEW)
│   │   ├── cdphe_surveillance.py
│   │   ├── weather_data.py
│   │   ├── tick_surveillance.py
│   │   ├── inat_ticks.py
│   │   └── mosquito_data.py
│   └── philippines/
│
├── data_preparation/
│   ├── disease_data.py      # (UPDATED) Generic disease data handler
│   └── colorado/            # (NEW)
│       ├── lyme_disease.py
│       ├── west_nile.py
│       └── rmsf.py
│
├── ml/
│   └── disease_forecasting.py # (UPDATED) Generic forecasting
│
└── predict/
    └── risk_assessment.py    # (UPDATED) Generic risk scoring
```

### Configuration Strategy

```python
# contexts.py (NEW)
class Context:
    """Base context class for disease surveillance"""
    
    CONTEXT_NAME: str
    REGION: str
    DISEASES: List[str]
    DATA_SOURCES: Dict[str, str]
    PRIMARY_VECTOR: str
    SEASONAL_PATTERN: str

class PhilippinesContext(Context):
    CONTEXT_NAME = "philippines"
    DISEASES = ["dengue"]
    PRIMARY_VECTOR = "mosquito"

class ColoradoContext(Context):
    CONTEXT_NAME = "colorado"
    DISEASES = ["lyme_disease", "west_nile_virus", "rmsf"]
    PRIMARY_VECTOR = ["tick", "mosquito"]
```

### Data Source Integration

```python
# Data sources for Colorado
COLORADO_DATA_SOURCES = {
    "case_surveillance": {
        "provider": "CDPHE",
        "api": "https://cdphe.colorado.gov/",
        "frequency": "weekly",
        "format": "json/csv"
    },
    "weather": {
        "provider": "NOAA",
        "api": "https://api.weather.gov/",
        "frequency": "hourly"
    },
    "tick_surveillance": {
        "provider": "iNaturalist",
        "api": "https://api.inaturalist.org/v1/",
        "frequency": "daily"
    },
    "google_trends": {
        "provider": "Google Trends",
        "frequency": "weekly"
    }
}
```

---

## Part 4: GitHub Pages Setup for Real-Time Monitoring

### Architecture Overview

```
aedesproject-uif/
├── .github/
│   └── workflows/
│       ├── data-update.yml      # (NEW) Daily data fetch
│       ├── analysis.yml          # (NEW) Weekly analysis
│       └── deploy-pages.yml      # (NEW) Deploy to GitHub Pages
│
├── docs/                         # (NEW) GitHub Pages content
│   ├── index.html               # Dashboard
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── dashboard.js
│   │   ├── charts.js
│   │   └── data-loader.js
│   ├── data/                     # (NEW) Generated data files
│   │   ├── lyme-trend.json
│   │   ├── weather-trend.json
│   │   └── forecasts.json
│   └── assets/
│
└── data-pipeline/               # (NEW) Data processing scripts
    ├── fetch_data.py
    ├── process_data.py
    └── generate_report.py
```

### Step 1: Enable GitHub Pages

```yaml
# Repository Settings -> Pages
Source: Deploy from a branch
Branch: main
Folder: /docs
```

### Step 2: Automated Data Pipeline (GitHub Actions)

#### Daily Data Fetch Workflow

```yaml
# .github/workflows/data-update.yml
name: Daily Data Update

on:
  schedule:
    # Run every day at 9 AM UTC (2 AM Mountain Time)
    - cron: '0 9 * * *'
  workflow_dispatch:  # Manual trigger

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Fetch CDPHE data
        env:
          CDPHE_API_KEY: ${{ secrets.CDPHE_API_KEY }}
        run: python data-pipeline/fetch_data.py
      
      - name: Fetch weather data
        run: python data-pipeline/fetch_weather.py
      
      - name: Fetch Google Trends
        run: python data-pipeline/fetch_trends.py
      
      - name: Fetch iNaturalist ticks
        run: python data-pipeline/fetch_inat.py
      
      - name: Process data
        run: python data-pipeline/process_data.py
      
      - name: Generate reports
        run: python data-pipeline/generate_report.py
      
      - name: Commit & push updates
        run: |
          git config user.name "Data Bot"
          git config user.email "bot@aedes.project"
          git add docs/data/*
          git commit -m "Update data: $(date)" || echo "No changes"
          git push

      - name: Deploy to Pages
        uses: actions/deploy-pages@v1
```

#### Weekly Analysis Workflow

```yaml
# .github/workflows/analysis.yml
name: Weekly Analysis

on:
  schedule:
    - cron: '0 10 * * MON'  # Every Monday 10 AM UTC

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run forecasting models
        run: python src/aedesproject_uif/predict/generate_forecasts.py
      - name: Generate insights
        run: python data-pipeline/generate_insights.py
      - name: Commit & push
        run: |
          git config user.name "Data Bot"
          git config user.email "bot@aedes.project"
          git add docs/data/* docs/reports/*
          git commit -m "Weekly analysis: $(date)" || echo "No changes"
          git push
```

### Step 3: Dashboard HTML

```html
<!-- docs/index.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AEDES: Colorado Vector-Borne Disease Surveillance</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="header">
        <h1>🦠 AEDES Colorado: Vector-Borne Disease Surveillance</h1>
        <p>Real-time monitoring of Lyme Disease, West Nile Virus, and Rocky Mountain Spotted Fever</p>
        <p class="last-update">Last updated: <span id="last-update"></span></p>
    </div>

    <div class="container">
        <div class="tabs">
            <button class="tab-button active" data-tab="lyme">Lyme Disease</button>
            <button class="tab-button" data-tab="wnv">West Nile Virus</button>
            <button class="tab-button" data-tab="rmsf">Rocky Mountain Spotted Fever</button>
        </div>

        <div id="lyme" class="tab-content active">
            <h2>Lyme Disease Surveillance</h2>
            <div class="dashboard-grid">
                <div class="card">
                    <h3>Confirmed Cases (This Year)</h3>
                    <div id="lyme-cases-chart" class="chart"></div>
                </div>
                <div class="card">
                    <h3>Tick Activity Index</h3>
                    <div id="tick-activity-chart" class="chart"></div>
                </div>
                <div class="card">
                    <h3>Google Trends Interest</h3>
                    <div id="lyme-trends-chart" class="chart"></div>
                </div>
                <div class="card">
                    <h3>Weather Indicators</h3>
                    <div id="weather-chart" class="chart"></div>
                </div>
            </div>
            <div class="card">
                <h3>County-Level Distribution</h3>
                <div id="lyme-map" class="map"></div>
            </div>
            <div class="card">
                <h3>Forecast (Next 4 Weeks)</h3>
                <div id="lyme-forecast" class="chart"></div>
            </div>
        </div>

        <div id="wnv" class="tab-content">
            <h2>West Nile Virus Surveillance</h2>
            <div class="dashboard-grid">
                <div class="card">
                    <h3>Confirmed Cases</h3>
                    <div id="wnv-cases-chart" class="chart"></div>
                </div>
                <div class="card">
                    <h3>Mosquito Activity</h3>
                    <div id="mosquito-activity-chart" class="chart"></div>
                </div>
                <div class="card">
                    <h3>Positive Mosquito Pools</h3>
                    <div id="positive-pools-chart" class="chart"></div>
                </div>
                <div class="card">
                    <h3>Dead Bird Reports</h3>
                    <div id="dead-birds-chart" class="chart"></div>
                </div>
            </div>
        </div>

        <div id="rmsf" class="tab-content">
            <h2>Rocky Mountain Spotted Fever Surveillance</h2>
            <!-- Similar structure -->
        </div>
    </div>

    <footer>
        <p>Data sources: CDPHE, CDC, iNaturalist, NOAA, Google Trends</p>
        <p>Last updated: <span id="footer-date"></span></p>
    </footer>

    <script src="js/data-loader.js"></script>
    <script src="js/dashboard.js"></script>
    <script src="js/charts.js"></script>
</body>
</html>
```

### Step 4: Data Loading Script

```javascript
// docs/js/data-loader.js
class DataLoader {
    constructor() {
        this.data = {};
        this.loadData();
    }

    async loadData() {
        try {
            // Load all data files
            this.data.lymeCases = await this.fetchJSON('data/lyme-cases.json');
            this.data.tickActivity = await this.fetchJSON('data/tick-activity.json');
            this.data.googleTrends = await this.fetchJSON('data/google-trends.json');
            this.data.weather = await this.fetchJSON('data/weather.json');
            this.data.forecast = await this.fetchJSON('data/forecast.json');
            
            this.updateDashboard();
            this.updateTimestamp();
        } catch (error) {
            console.error('Error loading data:', error);
        }
    }

    async fetchJSON(url) {
        const response = await fetch(url + '?t=' + new Date().getTime());
        return response.json();
    }

    updateTimestamp() {
        const now = new Date().toLocaleString();
        document.getElementById('last-update').textContent = now;
        document.getElementById('footer-date').textContent = now;
    }

    updateDashboard() {
        this.createLymeChart();
        this.createWeatherChart();
        this.createForecastChart();
        // ... other charts
    }

    createLymeChart() {
        const data = this.data.lymeCases;
        Plotly.newPlot('lyme-cases-chart', [
            {
                x: data.dates,
                y: data.cases,
                type: 'scatter',
                mode: 'lines+markers'
            }
        ], {
            title: 'Lyme Disease Cases Over Time',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Cases' }
        });
    }

    createWeatherChart() {
        const data = this.data.weather;
        Plotly.newPlot('weather-chart', [
            {
                x: data.dates,
                y: data.temperature,
                name: 'Temperature (°F)',
                yaxis: 'y'
            },
            {
                x: data.dates,
                y: data.precipitation,
                name: 'Precipitation (in)',
                yaxis: 'y2'
            }
        ], {
            title: 'Weather Conditions',
            yaxis: { title: 'Temperature (°F)' },
            yaxis2: { title: 'Precipitation (in)', overlaying: 'y', side: 'right' }
        });
    }

    createForecastChart() {
        const data = this.data.forecast;
        Plotly.newPlot('lyme-forecast', [
            {
                x: data.dates,
                y: data.forecast,
                name: 'Forecast',
                line: { dash: 'dash' }
            },
            {
                x: data.dates,
                y: data.upper_bound,
                fill: 'tonexty',
                name: 'Upper Bound',
                line: { color: 'rgba(0,0,0,0)' }
            },
            {
                x: data.dates,
                y: data.lower_bound,
                fill: 'toself',
                name: 'Lower Bound',
                line: { color: 'rgba(0,0,0,0)' }
            }
        ]);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new DataLoader();
});
```

### Step 5: Data Generation Script

```python
# data-pipeline/generate_report.py
import json
from datetime import datetime
from pathlib import Path

class DataReportGenerator:
    def __init__(self):
        self.output_dir = Path('docs/data')
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_lyme_data(self, cases_df, trends_df, weather_df):
        """Generate Lyme disease JSON for dashboard"""
        data = {
            'dates': cases_df['date'].astype(str).tolist(),
            'cases': cases_df['cases'].tolist(),
            'cumulative': cases_df['cases'].cumsum().tolist(),
            'counties': cases_df.groupby('county')['cases'].sum().to_dict(),
            'updated': datetime.now().isoformat()
        }
        
        with open(self.output_dir / 'lyme-cases.json', 'w') as f:
            json.dump(data, f)
    
    def generate_weather_data(self, weather_df):
        """Generate weather trends JSON"""
        data = {
            'dates': weather_df['date'].astype(str).tolist(),
            'temperature': weather_df['temp'].tolist(),
            'precipitation': weather_df['precip'].tolist(),
            'humidity': weather_df['humidity'].tolist(),
            'updated': datetime.now().isoformat()
        }
        
        with open(self.output_dir / 'weather.json', 'w') as f:
            json.dump(data, f)
    
    def generate_forecast(self, forecast_df):
        """Generate 4-week forecast"""
        data = {
            'dates': forecast_df['date'].astype(str).tolist(),
            'forecast': forecast_df['forecast'].tolist(),
            'upper_bound': forecast_df['upper_ci'].tolist(),
            'lower_bound': forecast_df['lower_ci'].tolist(),
            'updated': datetime.now().isoformat()
        }
        
        with open(self.output_dir / 'forecast.json', 'w') as f:
            json.dump(data, f)
```

### Step 6: GitHub Pages Domain Setup

```markdown
# DNS Configuration (if using custom domain)

1. In repository Settings > Pages:
   - Custom domain: aedes-colorado.io (example)

2. Update DNS records:
   CNAME aedes-colorado.io -> cirrolytix.github.io

3. Let GitHub handle HTTPS (automatic with custom domain)
```

---

## Part 5: Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Create Colorado context configuration
- [ ] Set up GitHub Pages repository
- [ ] Implement CDPHE data extraction
- [ ] Create basic dashboard HTML

### Phase 2: Data Integration (Weeks 3-4)
- [ ] Add weather data integration
- [ ] Add Google Trends integration
- [ ] Add iNaturalist tick data
- [ ] Create data processing pipeline

### Phase 3: Automation (Weeks 5-6)
- [ ] Set up GitHub Actions workflows
- [ ] Implement automated data updates
- [ ] Create monitoring alerts
- [ ] Deploy initial dashboard

### Phase 4: Analysis & Forecasting (Weeks 7-8)
- [ ] Adapt ML models for Colorado context
- [ ] Implement disease forecasting
- [ ] Add risk assessment models
- [ ] Create predictive visualizations

### Phase 5: Enhancement (Ongoing)
- [ ] Add county-level mapping
- [ ] Implement user feedback
- [ ] Add additional data sources
- [ ] Expand to other diseases/regions

---

## Part 6: Data Integration Challenges & Solutions

### Challenge 1: Real-Time vs. Delayed Data
**Problem**: CDPHE data may have 1-2 week lag

**Solution**:
- Use nowcasting techniques
- Supplement with leading indicators (Google Trends, weather)
- Show confidence intervals in forecasts

### Challenge 2: Data Privacy
**Problem**: Case-level data may be restricted

**Solution**:
- Use aggregated county-level data
- Implement anonymization for small numbers
- Focus on trends rather than individual cases

### Challenge 3: Seasonal Variation
**Problem**: Colorado has strong seasonality

**Solution**:
- Use seasonal decomposition in forecasting
- Show historical comparisons
- Adjust models by season

### Challenge 4: Multiple Vectors
**Problem**: Different diseases have different vectors and patterns

**Solution**:
- Create disease-specific models
- Use vector-appropriate climate variables
- Separate dashboards per disease

---

## Part 7: Key Differences from Philippines Context

| Aspect | Philippines (Dengue) | Colorado (Lyme/WNV/RMSF) |
|--------|----------------------|--------------------------|
| **Primary Vector** | Aedes mosquito | Ixodes tick, Culex mosquito |
| **Climate** | Tropical, year-round | Temperate, strong seasonality |
| **Season** | Year-round (peaks rainy) | Spring-fall (Lyme), Summer (WNV) |
| **Key Predictor** | Rainfall, temperature | Temperature, snow, elevation |
| **Case Lag** | Days-weeks | 1-3 weeks (reporting) |
| **Scale** | Provincial-national | County-regional |
| **Main Risk Factor** | Urban-periurban proximity | Outdoor recreation, occupational |

---

## Part 8: Resources & APIs

### Colorado-Specific APIs
```
CDPHE Data Portal: https://cdphe.colorado.gov/
CDC Wonder: https://wonder.cdc.gov/
USGS Water Data: https://waterdata.usgs.gov/
NOAA Weather: https://api.weather.gov/
iNaturalist: https://www.inaturalist.org/pages/developers
```

### Python Libraries for Colorado Data
```python
# Already in AEDES requirements:
- requests (API calls)
- pandas (data processing)
- numpy (analysis)
- scikit-learn (ML)

# Add for Colorado:
- geopandas (geospatial - Colorado counties)
- folium (mapping)
- plotly (interactive dashboards)
- prophet (time series forecasting)
```

---

## Conclusion

The AEDES framework is highly adaptable to Colorado's vector-borne disease surveillance context. The key advantages:

✅ **Modular Architecture**: Easy to swap regions and diseases  
✅ **Multiple Data Sources**: Flexible integration of different data types  
✅ **Automated Workflows**: GitHub Actions handles data updates  
✅ **Open Science**: GitHub Pages makes findings publicly accessible  
✅ **Real-Time Monitoring**: Dashboard updates with latest data  

This approach transforms AEDES from a Philippines-specific tool into a flexible epidemiological surveillance platform applicable to different contexts globally.
