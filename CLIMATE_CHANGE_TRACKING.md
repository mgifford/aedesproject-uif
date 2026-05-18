# Climate Change Tracking for Vector-Borne Disease Surveillance

## Executive Summary

Climate change is fundamentally altering the geography and seasonality of vector-borne diseases in Colorado and neighboring regions. Warmer winters, earlier springs, wetter summers, and extended transmission seasons create conditions favorable for disease-carrying ticks and mosquitoes to thrive in new areas and for longer periods.

This document provides:
1. **Thermal biology thresholds** for disease vectors
2. **Climate variables most predictive** of disease expansion
3. **Data sources and integration methods**
4. **Interpretation framework** for early warning signals
5. **Projected future risk scenarios**

---

## Part 1: Thermal Biology of Colorado Vectors

### 1. Ixodes scapularis (Black-Legged Tick) — Lyme Disease & Co-infections

#### Temperature Thresholds

| Parameter | Value | Significance |
|-----------|-------|--------------|
| **Minimum survival** | 0°C | Ticks die if exposed to sustained <0°C |
| **Activity threshold** | >7-10°C | Ticks begin questing (searching for hosts) |
| **Development rate** | Accelerates >13°C | Each life stage takes fewer days per degree |
| **Optimal development** | 15-20°C | Fastest larva → nymph → adult development |
| **Heat stress** | >25°C | High mortality; reduced activity (estivation) |
| **Winter survival zone** | ≥-5°C avg winter temp | Critical: CO Western Slope is marginal; Front Range is warming into suitable range |

#### Growing Degree Days (GDD) Model

**Concept**: Accumulated heat above a threshold temperature predicts developmental timing.

```
GDD = Σ(T_max + T_min)/2 - T_base
where T_base = 10°C for Ixodes

Key milestones:
- 300-400 GDD: Spring nymph emergence (April-May in CO)
- 500 GDD: Peak nymph activity (May-June)
- 800-1000 GDD: Adult emergence (September-October)
- 1500+ GDD: Winter immobility onset
```

**Application to AEDES:**
- Track cumulative GDD from March 1st each year
- Compare to historical average
- Early GDD accumulation = early outbreak season
- Delayed freeze date = extended fall tick season

#### Lyme Transmission Window

```
Month       Nymph Activity    Risk Level    Notes
March       Emerging          LOW           First warm days
April       Active            MODERATE      Peak emergence
May         Peak              HIGH          Maximum nymph density
June        Peak              HIGH          Peak questing behavior
July        Declining         MODERATE      Heat stress (estivation)
August      Low               LOW           Adults replacing nymphs
September   Emerging          MODERATE      Adult emergence begins
October     Peak              HIGH          Fall feeding frenzy
November    Declining         MODERATE      First freezes
December    Minimal           LOW           Winter dormancy
```

**Climate Change Impact:**
- **Pre-1990**: Typical season = May-October (6 months)
- **2010s-2020s**: Extended season = April-November (7-8 months)
- **Projected 2050**: March-December (10 months) in Front Range

---

### 2. Culex pipiens & Cx. restuans (West Nile Virus Vectors)

#### Temperature Thresholds

| Parameter | Value | Significance |
|-----------|-------|--------------|
| **Egg hatch** | >13°C water temp | First eggs laid in spring |
| **Larval development** | 7-10 days at 20-25°C | Rapid in warm years |
| **Adult emergence** | 7-21 days depending on temp | Faster in hotter summers |
| **Adult activity** | >15-20°C | Active flight/feeding |
| **WNV transmission** | >18°C | Virus replicates in mosquito (extrinsic incubation period: 8-14 days at optimal temps) |
| **Diapause trigger** | <15°C photoperiod | Triggers winter dormancy |
| **Winter survival** | >-10°C extremes | Cold sensitive; die in extreme cold |

#### West Nile Virus Development Cycle

```
Water Temperature    Development Time    Risk
13-15°C              14-21 days          Low (slow emergence, cool hosts)
16-20°C              7-10 days           Moderate (building populations)
21-25°C              5-7 days            High (rapid population doubling)
26-28°C (optimal)    4-5 days            Very High (peak transmission)
>29°C                Stress; mortality   High (heat stress reduces feeding)
```

**Extrinsic Incubation Period (EIP)** = Time for WNV to replicate in mosquito:
```
Temperature    EIP          Implications
18°C          14+ days     Barely viable; rare transmission
20°C          10-12 days   Threshold for epidemic potential
25°C          4-6 days     Rapid transmission cycle
28°C          2-3 days     Explosive transmission risk
```

#### Seasonal WNV Window

```
Month       Mosquito Status   Virus Activity   Risk Level
June        Larvae emerging   Starting         LOW
July        Building pop      Increasing       MODERATE
August      Peak population   Peak circulation HIGH
September   Still abundant    Declining        MODERATE
October     Declining         Seasonal end     LOW
```

**Climate Change Impact:**
- **Pre-2000**: WNV season = July-September (3 months, peak in late August)
- **2010s-2020s**: Extended = June-October (5 months)
- **Projected 2050**: May-November (7 months); peak shifted to mid-August

---

### 3. Dermacentor variabilis (American Dog Tick) — RMSF

#### Temperature Thresholds

| Parameter | Value | Significance |
|-----------|-------|--------------|
| **Activity threshold** | >5-10°C | Earlier spring emergence than Ixodes |
| **Peak activity** | 15-25°C | Spring peak (April-June) |
| **Summer dormancy** | >27°C | Aestivate (hide in cool microhabitats) |
| **Fall reactivation** | <20°C | September-October feeding (pre-winter) |
| **Winter survival** | >-15°C avg | More cold-hardy than Ixodes |
| **Development speed** | Slower than Ixodes | Multi-year life cycle |

**RMSF Seasonality:**
- April-June: Primary spring transmission (adults)
- July-August: Minimal (summer dormancy)
- September-October: Secondary fall transmission

**Climate Change Impact:**
- Extended spring season = earlier cases
- Warmer winters = reduced winter kill
- Earlier tick emergence = earlier cases

---

## Part 2: Climate Variables Predictive of Disease Expansion

### Primary Climate Predictors

#### 1. **Winter Minimum Temperature** 🌡️
**Why it matters**: Determines tick survival

```
Scenario 1: Traditional Winter (current)
- Minimum: -15°C to -20°C
- Ixodes mortality: 80-90% of overwintering population
- Range: Limited by winter kill

Scenario 2: Mild Winter
- Minimum: -5°C to 0°C
- Ixodes mortality: 20-30%
- Range: Northward expansion possible

Scenario 3: Extreme Warm (rare but increasing)
- Minimum: >0°C
- Ixodes mortality: <10%
- Range: Explosive range expansion
```

**Data to track**:
- Number of days below -10°C
- Minimum temperature reached
- Duration of cold snaps
- Years without hard freeze

**NOAA Data Source**: Daily min/max from Weather Stations
- Boulder: 40.0150°N, 105.2705°W
- Denver: 39.7392°N, 104.9903°W
- Glenwood Springs: 39.5515°N, 107.3262°W

#### 2. **Growing Degree Days (GDD)** 📈
**Why it matters**: Predicts developmental timing of vectors

```
Formula: GDD = Σ[(T_max + T_min)/2 - T_base]
         where T_base = 10°C for Ixodes

Interpretation:
- GDD accumulated by June 1: Predicts peak nymph emergence date
- Early GDD = early season = more transmission time
- Late GDD = compressed season = lower transmission

Example (Colorado Front Range):
- Historical: 500 GDD by June 15
- 2020s average: 500 GDD by June 5 (10-day acceleration)
- Projected 2050: 500 GDD by May 25 (20-day acceleration)
```

**Integration into AEDES**:
- Calculate cumulative GDD from March 1
- Compare current year to historical baseline
- Alert if +50 GDD ahead of schedule

#### 3. **Frost-Free Period** ❄️→🌱
**Why it matters**: Expands transmission season

```
Traditional (1961-1990 baseline):
- Front Range: May 20 ± 5 days (last frost)
- Western Slope: June 10 ± 5 days
- Growing season: ~140 days

Current (2010-2023 average):
- Front Range: May 5 ± 5 days (15-day earlier)
- Western Slope: May 25 ± 5 days (16-day earlier)
- Growing season: ~155 days

Projected 2050:
- Front Range: April 20 (30-day earlier)
- Growing season: ~170 days
```

**Vector impact**:
- Longer season = more tick/mosquito generations
- Earlier spring = nymphs active before expected
- Later fall = adult ticks feeding in November

#### 4. **Spring/Summer Precipitation** 💧
**Why it matters**: Creates mosquito breeding habitat

```
Moderate Rain (normal):
- Creates seasonal ponds → Culex breeding
- 2-3 generations per summer
- Endemic WNV transmission

Heavy Rain (wet year):
- Abundant breeding habitat
- 4-5 generations possible
- Potential epidemic year

Drought:
- Reduced breeding sites
- Limited generations
- Lower WNV risk
```

**Data to track**:
- April-July precipitation total
- Frequency of rain events (>0.5 inch)
- Soil moisture index
- Snowpack (affects spring runoff)

#### 5. **Snowpack Timing** ❄️
**Why it matters**: Affects spring water availability and vector emergence

```
Early melt (climate change signal):
- Peak snowmelt: Earlier (March vs. May)
- Spring runoff earlier
- More stable spring breeding sites for mosquitoes

Late melt (cold years):
- Delayed spring
- Late tick emergence
- Compressed summer season
```

**Colorado-specific**:
- San Juan Mountains snowpack affects NM/CO border
- Front Range snowpack affects metro area
- USGS operates Snow Telemetry (SNOTEL) network

---

## Part 3: Data Sources and APIs

### A. Temperature & Precipitation Data

#### 1. **NOAA National Weather Service**
```
Endpoint: https://api.weather.gov/points/{lat},{lon}
Format: JSON, daily/hourly
Lag: Real-time to 1 hour
Historical: 7 days online; archive available
Coverage: Colorado-wide

Colorado reference points:
- Boulder: 40.0150, -105.2705
- Denver: 39.7392, -104.9903
- Grand Junction: 39.0558, -108.5007
- Glenwood Springs: 39.5515, -107.3262
```

**Python implementation**:
```python
import requests
from datetime import datetime, timedelta

class NOAAWeatherClient:
    def __init__(self):
        self.base_url = "https://api.weather.gov"
    
    def get_daily_forecast(self, lat, lon, days=7):
        """Fetch daily forecast with temps"""
        points_url = f"{self.base_url}/points/{lat},{lon}"
        response = requests.get(points_url)
        forecast_url = response.json()["properties"]["forecast"]
        
        forecast = requests.get(forecast_url).json()
        return forecast["properties"]["periods"]
    
    def get_historical_temps(self, station_id, start_date, end_date):
        """Fetch historical data from NOAA ISD"""
        # Requires ISD station ID (e.g., 724695 for Denver)
        # Can use NCEI API or local weather station data
        pass
```

#### 2. **PRISM Climate Data (Oregon State University)**
```
Data: Daily temperature, precipitation (high resolution)
Resolution: 4km grid
Coverage: Entire USA including Colorado
URL: https://prism.oregonstate.edu/
Format: GeoTIFF, NetCDF
Lag: 2-3 day delay for daily data
Historical: 1895-present

Great for:
- County-level climate analysis
- Historical trend detection
- Comparing current conditions to 130-year baseline
```

**Python access**:
```python
import xarray as xr

# Load PRISM data
temp_data = xr.open_dataset(
    "https://prism.oregonstate.edu/dist/products/ppt/early_yr/PRISM_ppt_early_4km_*/2026*/PRISM_*.nc"
)
```

#### 3. **USGS Water Resources - SNOTEL**
```
Data: Snowpack, soil moisture, temperature
Sites: 100+ Colorado monitoring stations
URL: https://wcc.nrcs.usda.gov/nwcc/site
Format: CSV, JSON available
Real-time: Yes
Historical: 40+ years

Critical for:
- Spring snowmelt prediction
- Spring water availability
- Tick emergence correlation with snowmelt
```

#### 4. **NASA POWER** (Already in AEDES)
```
Data: Temperature, humidity, solar radiation, precipitation
Coverage: 0.5° grid globally
URL: https://power.larc.nasa.gov/api/v1/
Advantages: Free, global, 40-year historical record
```

### B. Phenology Data

#### **USGS National Phenology Network**
```
Data: First leaf, first bloom dates for plants
Coverage: USA-wide citizen science
URL: https://www.usgs.gov/faqs/what-leaf-out-index
API: https://www.usanpn.org/api/v0/

Relevance:
- Early leaf-out = tick hosts (deer, rodents) more active
- Plant phenology predicts vector activity
```

#### **BirdCast Migration Forecasts**
```
Data: Bird migration intensity and timing
URL: https://birdcast.info/
API: https://birdcast.info/api/
Real-time: Daily during migration season

Spring migration (March-May):
- Correlates with tick nymph emergence
- Ticks travel on bird hosts

Fall migration (Aug-Oct):
- WNV and infected birds moving south
- Peak WNV transmission timing
```

### C. Disease Case Data

#### **CDC NNDSS via CDC Wonder**
```
Already integrated in AEDES

Data: Confirmed cases by week, state, county
Lag: 1-2 weeks
Historical: 5+ years

New queries to run:
- Time series correlation: cases vs. temperature
- Seasonal pattern detection: when does risk spike?
```

---

## Part 4: Climate-Disease Correlation Framework

### Step 1: Collect Aligned Data

```python
# Collect daily for 5+ years:
# - Max/min temperature
# - Precipitation
# - GDD accumulation
# - Disease cases (lagged by 7-14 days for reporting delay)

data = {
    "date": [],
    "temp_max": [],
    "temp_min": [],
    "precip": [],
    "gdd": [],
    "disease_cases": [],
    "cases_lagged_7d": [],
    "cases_lagged_14d": []
}
```

### Step 2: Identify Leads & Lags

```
Question: Does temperature predict cases 1-4 weeks ahead?

Climate → Tick/Mosquito Development → Cases

Expected lag:
- Lyme: Temperature change → nymph behavior change (1-2 weeks)
- WNV: Temperature → mosquito population growth → human cases (2-4 weeks)

Analysis:
- Correlate temp at t=0 with cases at t=7, t=14, t=21, t=28
- Find maximum correlation lag
```

### Step 3: Build Predictive Model

```python
from sklearn.linear_model import LinearRegression
import numpy as np

class ClimateDiseasePredictor:
    def __init__(self):
        self.model = LinearRegression()
    
    def fit(self, climate_data, disease_cases, lag_weeks=2):
        """
        Fit model: disease_cases ~ f(temperature, gdd, precip at lag_weeks prior)
        """
        X = climate_data[["temp_max", "temp_min", "precip", "gdd"]].values[:-lag_weeks*7]
        y = disease_cases[lag_weeks*7:].values
        
        self.model.fit(X, y)
        return self.model.score(X, y)  # R² score
    
    def forecast_4weeks(self, latest_climate_data):
        """Predict cases 2-4 weeks ahead based on current climate"""
        prediction = self.model.predict(latest_climate_data)
        return prediction
```

### Step 4: Translate to Early Warnings

```
Climate Signal → Early Warning

Example: Lyme Disease

Signal: GDD accumulation 50+ days ahead of historical average
→ Early nymph emergence expected
→ Alert: "Elevated nymph risk April 15-May 30"

Signal: Minimum winter temp >-5°C two winters running
→ Reduced winter tick mortality
→ Alert: "Expected tick population increase; adjust prevention messaging"

Signal: Spring precipitation +50% above normal
→ Enhanced mosquito habitat
→ Alert: "West Nile monitoring elevated June 1-August 31"
```

---

## Part 5: Regional Climate-Disease Dynamics

### Colorado-Specific Considerations

#### **Front Range (Denver Metro, Boulder)**
```
Climate trend: Warming rapidly (+3°F since 1990)
Elevation: 5,280-6,000 ft
Winter low: -10 to 0°C (marginal for Ixodes survival)
Status: Becoming suitable for year-round Ixodes, especially on Front Range

Current risk: Moderate
Projected 2050: High (Lyme endemic; WNV amplified)
```

#### **Western Slope (Glenwood, Grand Junction)**
```
Climate trend: Moderate warming (+2°F since 1990)
Elevation: 4,000-6,000 ft
Winter low: -5 to +5°C (already marginal)
Status: Already hosts year-round Ixodes in protected areas

Current risk: High
Projected 2050: Very High (extended seasons; year-round transmission)
```

#### **Mountains (Elevation >8,000 ft)**
```
Climate trend: Slower warming than lower elevations
Winter: Still cold enough for seasonal patterns
Status: High altitude protection; tick season = summer only

Current risk: Seasonal high (summer peak)
Projected 2050: Extended season (spring/fall activity increases)
```

### Neighboring State Coordination

**New Mexico & Arizona** (south):
- Warmer winters → earlier WNV season
- Risk spreads north by June 1 (wind/bird transport)
- Monitor for early WNV in NM → predict CO timing +2-3 weeks

**Wyoming & Montana** (north):
- Cold winters still robust but shortening
- Northward tick range expansion continuing
- Delayed freeze dates extend fall season

**Kansas & Nebraska** (east):
- Prairie states warming rapidly
- Expanding Ixodes range from east
- Monitor for "invasion" westward along front
- Alternate animal hosts (prairie dogs, rodents)

---

## Part 6: Interpretation Examples

### Example 1: Predicting Early Lyme Season

```
Observation (March 2026):
- Winter 2025-26 minimum: -8°C (vs. historical -15°C average)
- February temperatures: 8°F above normal
- GDD accumulation: 50 GDD by March 15 (normally 0-10)

Interpretation:
1. Mild winter → 50-70% more ticks survive to spring
2. Rapid GDD accumulation → nymphs emerge 2 weeks early
3. Early season + larger population = HIGH RISK

Early Warning (March 20):
"Lyme disease nymph activity expected April 20-30 (typically May 10-20). Tick 
prevention season begins 2-3 weeks early. Recommend early outdoor safety 
messaging."

Verification (May 2026):
- Nymph emergence confirmed April 22
- Peak nymph activity May 1-15
- Cases surge June 1-15 (lagged from May emergence)
```

### Example 2: Predicting WNV Epidemic Year

```
Observation (June 2026):
- Spring 2026 precipitation: +60% above normal (wet year)
- Summer temperatures trending 2-3°F above normal
- iNaturalist robin sightings: +40% vs. historical average (early arrival)
- First Culex mosquitoes detected June 8 (vs. historical June 20)

Interpretation:
1. Abundant spring rain → maximum breeding habitat for Culex
2. Early warm temps → faster larval development
3. Early mosquitoes emerging + warm forecast = rapid population growth
4. Early robin arrival = early WNV amplification (birds are "super-spreader" hosts)

Risk Assessment (June 15):
"Conditions favoring major West Nile outbreak: wet spring (breeding habitat) + 
warm forecast (rapid development) + early mosquitoes + early birds (amplification). 
Predict epidemic-level transmission July-September 2026. Recommend enhanced 
surveillance and public warnings."

Verification (August 2026):
- July-August 2026: 45 cases in Colorado (vs. typical 15-20)
- Peak in August confirms prediction
- Model validated
```

### Example 3: Atmospheric Transport Alert

```
Observation (July 2026):
- New Mexico: 60 WNV cases detected in week 28 (southern NM near CO border)
- Colorado wind forecast: Southwest 12-18 mph for 5 days
- Colorado temperature: 85-90°F (optimal for WNV transmission)

Interpretation:
1. Outbreak in upwind region (NM SW)
2. Prevailing wind direction points from NM to CO
3. Optimal temperature for mosquito flight + virus replication
4. Atmospheric transport conditions favorable

Transport Risk Alert (July 18):
"Southwest wind pattern with upstream New Mexico outbreak creates elevated 
West Nile risk for southwestern Colorado (San Juan region) July 20-25. Infected 
mosquitoes may be wind-dispersed. Recommend enhanced mosquito surveillance in 
border counties."

Verification (August 2026):
- First CO cases detected in San Juan County July 27
- Genetic sequencing shows match to NM outbreak strain
- Alert successfully predicted transport event
```

---

## Part 7: Integration with AEDES

### Data Pipeline Addition

```python
# scripts/fetch_climate_data.py (NEW)

def fetch_noaa_temps(locations, days_back=365):
    """Fetch historical temps from NOAA"""
    
def fetch_prism_climate(bbox, start_date, end_date):
    """Fetch high-res climate data from PRISM"""

def calculate_gdd(temp_max, temp_min, base=10):
    """Calculate growing degree days"""

def correlate_climate_disease(climate_df, disease_df, lags=[7, 14, 21]):
    """Correlate climate variables with lagged disease cases"""
```

### Dashboard Update

```html
<!-- docs/index.html additions -->

<div class="card">
    <h3>🌡️ Climate-Disease Risk Forecast</h3>
    <div id="gdd-progress"></div>
    <p>Growing Degree Days: <span id="gdd-current"></span> 
       (vs. historical avg: <span id="gdd-historical"></span>)</p>
    <p>Early Season Status: <span id="season-status"></span></p>
    <div id="climate-forecast-chart"></div>
</div>

<div class="card">
    <h3>⚠️ Climate Risk Alerts</h3>
    <ul id="climate-alerts"></ul>
</div>
```

### Jupyter Notebook

```
notebooks/04_climate_disease_correlation.ipynb
- Load historical climate + disease data
- Visualize correlations
- Build predictive models
- Generate 4-week forecast
- Display early warning signals
```

---

## Part 8: Future Expansion: Scenario Planning

### 2050 Projections (RCP 4.5 scenario)

```
Lyme Disease (Ixodes scapularis):
- Range: Expanded northward by ~200 miles (into Montana, Wyoming uplands)
- Front Range: Year-round activity (no winter shutdown)
- Season: March-December (10 months vs. 6 currently)
- Cases: 50-100% increase by 2050

West Nile Virus:
- Season: May-November (7 months vs. 4 currently)
- Peak: Shifted to July-August (earlier than current Aug-Sept)
- Amplitude: 25-50% increase in epidemic years

Rocky Mountain Spotted Fever:
- Range: Extended upward in elevation (currently limited to <8,000 ft)
- Season: April-November (extended spring/fall)
- Incidence: Stable to slightly increasing

Key uncertainties:
- Precipitation patterns (wetter or drier Southwest?)
- Extreme heat events (>100°F days)
- Vector adaptation to new climates
```

---

## References

1. **Thermal Biology**:
   - Mordecai et al. 2019. "Thermal biology of mosquito-borne disease" (*Ecology Letters*)
   - Eisen et al. 2016. "County-scale distribution of ticks" (*Journal of Medical Entomology*)

2. **Climate Data**:
   - PRISM Climate Group: https://prism.oregonstate.edu/
   - NOAA National Centers for Environmental Information: https://www.ncei.noaa.gov/

3. **Phenology**:
   - USGS National Phenology Network: https://www.usgs.gov/faqs/what-leaf-out-index
   - BirdCast: https://birdcast.info/

4. **Epidemic Forecasting**:
   - Ryan et al. 2019. "Global expansion of Aedes-borne viruses with climate change" (*PLOS NTD*)
   - Reisen 2010. "Landscape epidemiology of vector-borne diseases" (*Annual Review of Entomology*)

---

## Quick Start: Using This Guide

**For epidemiologists**: 
- Jump to Part 1 (thermal thresholds) and Part 4 (correlation framework)
- Use Part 6 examples to build interpretation protocols

**For data scientists**: 
- Reference Part 3 (data sources) and Part 7 (integration)
- Build predictive models using Part 4 methodology

**For public health officials**: 
- Focus on Part 5 (regional dynamics) and Part 6 (interpretation examples)
- Use Part 8 projections for long-term planning

**For communication/outreach**: 
- Use Part 6 examples for explaining climate-disease linkages
- Reference Part 8 for public messaging about future risk

---

*Last updated: May 18, 2026*  
*Version: 1.0*  
*Maintainer: AEDES Climate Tracking Team*
