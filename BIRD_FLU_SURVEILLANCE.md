# AEDES for Avian Influenza: Bird Flu Surveillance Framework

## Executive Summary

Avian Influenza (bird flu) surveillance in Colorado represents a critical emerging threat that leverages AEDES's multi-source data integration capabilities in a novel way—monitoring wildlife disease spillover risk and occupational exposure to humans. This guide extends the Colorado context to include H5N1 and other novel influenza strains.

---

## Part 1: Why Bird Flu Matters in Colorado

### Geographic & Ecological Factors

**Colorado's Position on Migration Routes:**
- Located on the **Central Flyway** - major north-south bird migration corridor
- Millions of waterfowl, raptors, and shorebirds pass through annually
- Spring (March-May) and Fall (August-October) peak migration periods
- Colorado's diverse ecosystems support year-round bird populations

**Key Habitats for Surveillance:**
```
High-Risk Areas:
├── Wetlands (Denver Metro Area parks, wetland refuges)
├── Reservoir/Lake margins (Colorado River, reservoirs)
├── Agricultural areas (grain fields, livestock farms)
├── Wildlife rehabilitation centers
└── Raptor centers and zoos
```

### Disease Characteristics

#### H5N1 Avian Influenza
**Recent Concern (2021-2024):**
- Highly pathogenic avian influenza (HPAI)
- Detection in wild birds across North America
- Spillover to poultry farms causing massive culling
- Limited but concerning human cases (mostly occupational)
- High mortality in birds (can be 90-100%)

**Colorado-Specific Risk:**
- First Colorado wild bird detections: 2024
- Commercial poultry operations in eastern Colorado
- High human-bird contact (recreation, agriculture, wildlife management)
- Climate suitable for influenza transmission in wild birds

### Public Health Significance

| Level | Impact | Colorado Risk |
|-------|--------|---------------|
| **Wildlife** | Massive wild bird mortality | HIGH - on migration route |
| **Poultry** | Economic impact, supply chain | MEDIUM - smaller poultry industry |
| **Occupational** | Farm workers, wildlife handlers | MEDIUM - outdoor-oriented population |
| **Human Pandemic** | Low current risk | LOW (but rapidly changing) |

---

## Part 2: Data Sources for Bird Flu Surveillance

### A. Official Surveillance Programs

#### 1. **USGS National Wildlife Health Center (NWHC)**
```
Live HPAI Detection Dashboard:
URL: https://www.usgs.gov/avian-influenza/maps-current-us-detections

Data Available:
- Wild bird detections (species, location, date)
- Testing results (positive/negative)
- Geographic clusters
- Temporal trends
- Historical data (searchable)

Frequency: Real-time (updated daily)
Format: Interactive map + downloadable data
Access: Free, public
```

**Implementation:**
```python
# Fetch USGS bird flu data
import requests
import json
from datetime import datetime

def fetch_usgs_hpai_detections():
    """
    Fetch HPAI detections from USGS
    
    Note: USGS dashboard may require web scraping
    or they may provide an API endpoint
    """
    
    # USGS provides data via various formats
    # Check: https://www.usgs.gov/avian-influenza/data-downloads
    
    # Example structure for Colorado data
    url = "https://www.usgs.gov/avian-influenza/api/detections"  # hypothetical
    
    params = {
        "state": "Colorado",
        "days_back": 30  # Last 30 days
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        return {
            "source": "USGS NWHC",
            "total_detections": len(data['detections']),
            "detections": data['detections'],
            "timestamp": datetime.now().isoformat()
        }
    except:
        # Fallback: scrape the public dashboard
        return scrape_usgs_dashboard()
```

#### 2. **CDC Avian Influenza Program**
```
URL: https://www.cdc.gov/bird-flu/situation-summary/index.html

Data Available:
- Human cases in US (rare but critical)
- Risk assessment updates
- Guidance for healthcare providers
- Testing data
- Outbreak summaries

Frequency: Weekly updates + incident-driven
Format: Web pages + downloadable reports
```

#### 3. **Colorado Parks & Wildlife (CPW) - Wildlife Health**
```
URL: https://cpw.state.co.us/

Data Available:
- Colorado-specific wild bird surveillance
- Dead bird reports/submissions
- Wildlife rehabilitation center alerts
- Regional bird population surveys
- Partnership data from universities

Access: Contact directly or state data portal
```

#### 4. **APHIS (Animal & Plant Health Inspection Service)**
```
URL: https://www.aphis.usda.gov/aphis/activities/animal-health/avian/avian-influenza

Data Available:
- Poultry farm detections
- Commercial flock impacts
- Biosecurity status
- Culling events
- Economic impact data

Focus: Domestic poultry, not wild birds
Frequency: Weekly reports
```

### B. Wild Bird Surveillance Networks

#### 1. **eBird Dataset (Cornell Lab of Ornithology)**
```
URL: https://ebird.org

Data Available:
- Bird sightings and observations
- Species distribution changes
- Population presence/absence
- Seasonal patterns
- Geographic coverage

Colorado Usage:
- Monitor waterfowl presence
- Track raptor movements
- Detect unusual bird mortality events
- Seasonal migration patterns

API: https://documenter.getpostman.com/view/664302/S1nxP47V2
```

**Implementation:**
```python
import requests
import json

def fetch_ebird_hotspot_data(location_code: str, days: int = 7):
    """
    Fetch recent observations from eBird for Colorado hotspots
    
    Args:
        location_code: eBird location code (e.g., "US-CO" for Colorado)
        days: Number of days to look back
    """
    
    ebird_api_url = "https://api.ebird.org/v2/data/obs"
    
    params = {
        "loc": location_code,
        "back": days,
        "fmt": "json",
        "key": "YOUR_EBIRD_API_KEY"  # Get from https://ebird.org/api/keygen
    }
    
    response = requests.get(ebird_api_url, params=params)
    observations = response.json()
    
    # Filter for waterfowl and raptors (high-risk for HPAI)
    high_risk_species = [
        "Mallard", "Canada Goose", "Northern Pintail",
        "Great Blue Heron", "Bald Eagle", "Golden Eagle"
    ]
    
    relevant_obs = [
        obs for obs in observations 
        if obs['comName'] in high_risk_species
    ]
    
    return {
        "location": location_code,
        "observations": relevant_obs,
        "high_risk_count": len(relevant_obs),
        "timestamp": datetime.now().isoformat()
    }

# Colorado hotspot codes
colorado_hotspots = {
    "denver_metro": "L123456",      # Example
    "western_slope": "L789012",     # Example
    "arkansas_river": "L345678",    # Example
}

for hotspot_name, code in colorado_hotspots.items():
    data = fetch_ebird_hotspot_data(code)
    print(f"{hotspot_name}: {data['high_risk_count']} high-risk birds")
```

#### 2. **iNaturalist Bird Observations**
```
URL: https://www.inaturalist.org

Data Available:
- Geotagged bird photos
- Identifies unusual bird behavior
- Dead/sick bird reports
- Distribution data

Colorado API Usage:
- Query for "sick bird" observations
- Track raptor sightings
- Identify potential surveillance sites
```

### C. Occupational & Poultry Surveillance

#### 1. **Colorado Department of Agriculture - Poultry Health**
```
URL: https://ag.colorado.gov/

Data Available:
- Registered poultry farms
- Commercial flock status
- Biosecurity compliance
- Disease reports
- Feed/supply chain data

Contact: Colorado State Veterinarian's Office
```

#### 2. **Occupational Safety (OSHA + State)**
```
Key Data:
- Poultry worker health records
- Farm worker illness reports
- Biosecurity training programs
- Exposure incident reports

Sources:
- Colorado Department of Labor
- Regional OSHA offices
- Occupational health clinics
```

#### 3. **Sentinel Surveillance in At-Risk Workers**
```
Potential Programs:
- Poultry facility workers
- Veterinarians and animal handlers
- Wildlife rehabilitation workers
- Raptor center staff

Monitoring:
- Respiratory illness surveillance
- Serology (antibody) testing
- Risk factor assessment
```

### D. Environmental & Climate Data

#### 1. **Temperature & Moisture (Critical for Virus Survival)**
```
Why It Matters:
- Influenza survives longer in cold water
- Migratory birds carry virus during spring/fall (peak migration)
- Water body conditions affect bird congregation

Data Sources:
- NOAA weather (temperature, humidity)
- USGS water quality data
- Precipitation patterns
- Water body temperatures
```

#### 2. **Bird Migration Phenology**
```
Data Sources:
- eBird migration maps
- USGS Phenology project
- Radar ornithology (bird migration intensity)
- Historical migration patterns

Application:
- Predict peak arrival/departure times
- Identify high-risk periods
- Forecast surveillance intensity
```

### E. Social & News Data

#### 1. **Google Trends - Bird Flu Related**
```
Search Terms:
- "bird flu Colorado"
- "dead bird Colorado"
- "avian influenza"
- "H5N1"
- "sick birds"

Use:
- Detect public awareness spikes
- Identify reporting patterns
- Early warning of community notices
```

#### 2. **News & Media Monitoring**
```
Sources:
- Local Colorado news outlets
- Agricultural/poultry news
- Wildlife rehabilitation alerts
- CDC news releases

Tools:
- NewsAPI.com
- Google News Alerts
- Social media monitoring
```

---

## Part 3: Bird Flu Specific Data Model

### Context Extension

```python
# Add to contexts.yaml

bird_flu:
  name: "Avian Influenza (Bird Flu)"
  diseases:
    - h5n1
    - h7n9
    - novel_influenza
  
  vectors:
    - wild_birds
    - poultry
    - environmental_contamination
  
  target_populations:
    - wild_birds
    - poultry_workers
    - wildlife_handlers
    - veterinarians
  
  surveillance_types:
    - wildlife_surveillance
    - occupational_health
    - poultry_biosecurity
    - environmental_monitoring
  
  data_sources:
    usgs_nwhc:
      provider: "USGS National Wildlife Health Center"
      url: "https://www.usgs.gov/avian-influenza"
      frequency: "daily"
      format: "geospatial data, interactive map"
    
    cdc_avian_flu:
      provider: "CDC"
      url: "https://www.cdc.gov/bird-flu"
      frequency: "weekly"
      format: "news, reports, case summaries"
    
    ebird:
      provider: "Cornell Lab of Ornithology"
      url: "https://ebird.org"
      api: "https://documenter.getpostman.com/view/664302/S1nxP47V2"
      frequency: "real-time"
      format: "JSON API"
    
    cpw_wildlife:
      provider: "Colorado Parks & Wildlife"
      url: "https://cpw.state.co.us"
      frequency: "real-time"
      format: "database, reports"
    
    poultry_farms:
      provider: "Colorado Department of Agriculture"
      url: "https://ag.colorado.gov"
      frequency: "weekly"
      format: "registry, reports"
  
  seasonal_pattern:
    peak_risk_months: [3, 4, 5, 8, 9, 10]  # Spring and fall migration
    high_transmission_season: "March-May, August-October"
    mitigating_factors: "Summer breeding, reduced migration"
```

### Data Integration Pipeline

```python
# src/aedesproject_uif/data_extraction/bird_flu.py

from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta

class BirdFluSurveillance:
    """
    Integrated bird flu surveillance system for Colorado
    """
    
    def __init__(self):
        self.context = "colorado_bird_flu"
        self.data = {}
    
    def collect_all_data(self) -> Dict:
        """
        Collect from all bird flu data sources
        """
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "wild_bird_detections": self.get_usgs_detections(),
            "bird_observations": self.get_ebird_data(),
            "poultry_status": self.get_poultry_data(),
            "occupational_health": self.get_occupational_data(),
            "environmental": self.get_environmental_data(),
            "news_signals": self.get_news_signals()
        }
        
        return results
    
    def get_usgs_detections(self) -> List[Dict]:
        """
        Fetch USGS HPAI detections for Colorado
        """
        # Implementation to fetch from USGS
        pass
    
    def get_ebird_data(self) -> Dict:
        """
        Get waterfowl/raptor observations from eBird
        """
        # High-risk species for HPAI
        species = ["Mallard", "Canada Goose", "Bald Eagle", "Golden Eagle"]
        
        # Query eBird API
        observations = []
        for species_name in species:
            # Fetch observations
            pass
        
        return {
            "species_tracked": species,
            "recent_observations": observations,
            "population_trend": self.analyze_population_trend(observations)
        }
    
    def get_poultry_data(self) -> Dict:
        """
        Get Colorado poultry farm biosecurity status
        """
        return {
            "registered_farms": self.get_farm_count(),
            "birds_in_production": self.get_bird_count(),
            "biosecurity_status": self.get_biosecurity_alerts(),
            "recent_incidents": self.get_culling_events()
        }
    
    def get_occupational_data(self) -> Dict:
        """
        Get occupational health surveillance data
        """
        return {
            "at_risk_workers": self.estimate_at_risk_population(),
            "sentinel_sites": self.list_sentinel_clinics(),
            "respiratory_illness_reports": self.get_rir_data(),
            "serology_testing": self.get_serology_data()
        }
    
    def get_environmental_data(self) -> Dict:
        """
        Environmental factors affecting transmission
        """
        return {
            "temperature_trend": self.get_temperature_data(),
            "water_body_conditions": self.get_water_conditions(),
            "bird_migration_stage": self.assess_migration_period(),
            "transmission_risk": self.calculate_environmental_risk()
        }
    
    def get_news_signals(self) -> Dict:
        """
        Monitor news and social signals
        """
        return {
            "google_trends": self.get_google_trends("bird flu Colorado"),
            "news_mentions": self.get_news_articles(),
            "public_concern": self.analyze_sentiment()
        }
    
    def calculate_risk_score(self) -> Dict:
        """
        Integrated risk assessment
        """
        data = self.collect_all_data()
        
        risk_score = {
            "wildlife_spillover_risk": self.score_wildlife_risk(data),
            "poultry_outbreak_risk": self.score_poultry_risk(data),
            "occupational_exposure_risk": self.score_occupational_risk(data),
            "human_pandemic_risk": self.score_pandemic_risk(data),
            "overall_risk_level": self.combine_scores(data),
            "risk_trajectory": self.assess_trajectory(data),
            "key_drivers": self.identify_key_drivers(data),
            "recommended_actions": self.recommend_actions(data)
        }
        
        return risk_score
```

---

## Part 4: Unique Aspects of Bird Flu Surveillance

### Key Differences from Lyme/WNV

| Aspect | Lyme/WNV | Bird Flu |
|--------|----------|----------|
| **Primary Data** | Human health cases | Wildlife deaths + human exposure |
| **Lag Time** | 1-3 weeks (humans) | Real-time (wildlife) or days (occupational) |
| **Seasonality** | Summer peak | Spring & fall migration peaks |
| **Geographic Scale** | Regional/county | Flyway-wide, global |
| **Main Indicator** | Disease cases | Detections in wildlife |
| **Lead Indicator** | Google Trends, weather | Bird migration, wild bird detections |
| **Risk Focus** | Patient outcomes | Spillover prevention, occupational safety |
| **Intervention Points** | Personal protection | Biosecurity, occupational PPE, surveillance |

### Forecasting Approach for Bird Flu

```python
def forecast_bird_flu_risk(self, weeks_ahead: int = 4) -> pd.DataFrame:
    """
    Forecast bird flu risk 4 weeks in advance
    
    Key factors:
    - Bird migration intensity
    - Wild bird detections
    - Temperature trends
    - Historical patterns
    """
    
    forecast_data = pd.DataFrame()
    
    # Factor 1: Migration intensity (most important)
    migration_risk = self.predict_migration_intensity(weeks_ahead)
    
    # Factor 2: Detection rate
    detection_trend = self.project_detections(weeks_ahead)
    
    # Factor 3: Environmental conditions
    env_risk = self.project_environmental_risk(weeks_ahead)
    
    # Factor 4: Occupational exposure (based on activity)
    occ_exposure = self.project_occupational_exposure(weeks_ahead)
    
    # Combine factors
    forecast_data['date'] = pd.date_range(start='today', periods=weeks_ahead*7, freq='D')
    forecast_data['migration_risk'] = migration_risk
    forecast_data['detection_risk'] = detection_trend
    forecast_data['environmental_risk'] = env_risk
    forecast_data['occupational_risk'] = occ_exposure
    forecast_data['combined_risk'] = (
        0.4 * migration_risk + 
        0.3 * detection_trend + 
        0.2 * env_risk + 
        0.1 * occ_exposure
    )
    
    return forecast_data
```

---

## Part 5: Dashboard Design for Bird Flu

### Key Metrics to Display

```html
<!-- Real-time monitoring dashboard -->

<div class="bird-flu-dashboard">
  <div class="metrics">
    <metric>
      <label>USGS Detections (Last 30 days)</label>
      <value id="usgs-detections">0</value>
      <spark-chart id="detection-trend"></spark-chart>
    </metric>
    
    <metric>
      <label>High-Risk Bird Sightings</label>
      <value id="ebird-count">0</value>
      <location-list id="locations"></location-list>
    </metric>
    
    <metric>
      <label>Poultry Farm Alerts</label>
      <value id="farm-alerts">0</value>
      <status-indicator id="biosecurity"></status-indicator>
    </metric>
    
    <metric>
      <label>Migration Intensity</label>
      <value id="migration-index">0%</value>
      <gauge id="migration-gauge"></gauge>
    </metric>
  </div>
  
  <charts>
    <chart id="detections-map">
      <!-- Map of USGS detections -->
    </chart>
    
    <chart id="risk-timeline">
      <!-- Risk progression over time -->
    </chart>
    
    <chart id="species-distribution">
      <!-- Bird species at risk -->
    </chart>
    
    <chart id="migration-forecast">
      <!-- Predicted migration intensity -->
    </chart>
  </charts>
  
  <alerts>
    <!-- Real-time alerts for elevated risk -->
  </alerts>
</div>
```

### GitHub Pages Data Updates

```python
# scripts/bird_flu_data_update.py

def generate_bird_flu_dashboard_data():
    """
    Generate JSON files for bird flu dashboard
    """
    
    surveillance = BirdFluSurveillance()
    data = surveillance.collect_all_data()
    risk_score = surveillance.calculate_risk_score()
    forecast = surveillance.forecast_bird_flu_risk(weeks_ahead=4)
    
    # Save to docs/data
    json_files = {
        "bird-flu-detections.json": data['wild_bird_detections'],
        "bird-observations.json": data['bird_observations'],
        "poultry-status.json": data['poultry_status'],
        "occupational-health.json": data['occupational_health'],
        "risk-assessment.json": risk_score,
        "forecast.json": forecast.to_dict()
    }
    
    for filename, content in json_files.items():
        save_json(f"docs/data/{filename}", content)
```

---

## Part 6: Implementation Priorities

### Phase 1: Wild Bird Surveillance (Weeks 1-2)
- [ ] Set up USGS NWHC data integration
- [ ] Implement eBird API connections
- [ ] Create detection tracking dashboard
- [ ] Set up daily data updates

### Phase 2: Poultry & Occupational (Weeks 3-4)
- [ ] Contact Colorado Department of Agriculture for farm data
- [ ] Establish occupational health partnerships
- [ ] Create poultry farm monitoring dashboard
- [ ] Develop biosecurity alert system

### Phase 3: Risk Assessment & Forecasting (Weeks 5-6)
- [ ] Implement migration-based risk model
- [ ] Add environmental factor analysis
- [ ] Create 4-week forecast module
- [ ] Deploy to GitHub Pages

### Phase 4: Integration & Response (Weeks 7-8)
- [ ] Integrate with Colorado Department of Health
- [ ] Set up automated alerts
- [ ] Create response protocols
- [ ] Launch public-facing dashboard

---

## Part 7: Why Bird Flu for Colorado?

### Strategic Importance

1. **Geographic Location**: Central Flyway position = early detection opportunity
2. **Economic Interests**: Poultry industry + outdoor recreation
3. **Public Health**: Low current risk but rapidly changing threat landscape
4. **Data Availability**: Excellent wildlife surveillance infrastructure
5. **Occupational Health**: Significant outdoor worker population
6. **Innovation Opportunity**: First-to-market early warning system

### Global Relevance

The bird flu surveillance framework developed for Colorado could be rapidly adapted to:
- Other major flyways (Atlantic, Mississippi)
- Other countries with poultry industries
- Zoonotic disease spillover early warning globally

---

## Conclusion

Bird flu surveillance demonstrates AEDES's ability to pivot from human health cases (dengue) to wildlife disease spillover risk. The modular architecture enables seamless integration of new diseases, data sources, and risk models across different geographic contexts.

**Key Innovation**: AEDES becomes a **unified surveillance platform** for different epidemiological patterns:
- ✅ Dengue: Human cases with environmental co-factors
- ✅ Lyme: Tick exposure with environmental risks
- ✅ Bird Flu: Wildlife spillover with occupational exposure

This adaptability makes AEDES valuable for global disease surveillance networks.
