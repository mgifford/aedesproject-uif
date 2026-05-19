# ---
title: "Data Extraction"
nav:
	- Home: index.md
	- Prerequisites: prerequisites.md
	- Initialization: initialization.md
	- Data Extraction: data_extraction.md
	- Data Preparation: data_preparation.md
	- Machine Learning: ml.md
	- Prediction: predict.md
	- Dengue Forecasting: dengue_forecasting.md
	- Dengue Hotspot Detection: dengue_hotspot_detection.md
	- Multidimensional Risk Scoring: multidimensional_risk_scoring.md
	- Changelog: changelog.md
# ---
# Data Extraction

## Overview

This section covers the various modules used for data extraction in aedesproject-uif. 
The modules handle different sources and types of data relevant to early dengue detection 
and exploration services. These include geographical, meteorological, demographic, search interest, and various 
other types of data.

---

## admin_boundaries

### Description

This module is used for extracting administrative boundaries data. It fetches geographical data 
and provides it in a format suitable for further analysis.

### Main Function

#### Function Name

`fetch_geoboundaries(iso_country_code, admin_level)`

#### Description

Fetches geographical boundaries from www.geoboundaries.org based on the ISO country code and administrative level.

#### Parameters

- `iso_country_code`: ISO code of the country.
- `admin_level`: Administrative level for which the boundaries are fetched.

### Usage

```python
from aedesproject_uif.data_extraction.admin_boundaries import save_admin_regions
save_admin_regions("PHL", 2)
```

---

## demographics

### Description

The `demographics` module is responsible for fetching demographic data, including indices like 
relative wealth, population density, and other relevant metrics.

### Main Functions

#### Function Name

1.  `fetch_relative_wealth_index(country, iso_country_code)`

#### Description

Fetches the relative wealth index for a given country.

#### Parameters

- `country`: Name of the country.
- `iso_country_code`: ISO code of the country.

#### Function Name

2. `fetch_population_density(country, iso_country_code, segment)`

#### Description

Fetches the population density data for a given country.

#### Parameters

- `country`: Name of the country.
- `iso_country_code`: ISO code of the country.
- `segment`: Valid values = {'general', 'children_under_five', 'elderly_60_plus', 'youth_15_24'}

### Usage

```python
from aedesproject_uif.data_extraction.demographics import fetch_population_density, fetch_relative_wealth_index
fetch_population_density("Philippines", "PHL", "general")
fetch_relative_wealth_index("Philippines", "PHL")
```

---

## google_trends

### Description

This module allows you to fetch data from Google Trends, focusing on keywords and search queries 
related to dengue.

### Main Function

#### Function Name

`fetch_google_trends(iso_country_code, start_date, end_date)`

#### Description

Fetches Google Trends data for a given country and time range.

#### Parameters

- `iso_country_code`: ISO code of the country.
- `start_date`: Start date for fetching data (in 'yyyy-mm-dd').
- `end_date`: End date for fetching data (in 'yyyy-mm-dd').

### Usage

```python
from aedesproject_uif.data_extraction.google_trends import fetch_google_trends
fetch_google_trends('PHL', '2016-01-10', '2021-01-10')
```

---

## meteorological

### Description

The `meteorological` module handles the extraction of weather-related data. This includes 
temperature, humidity, and other meteorological factors.

### Main Function

#### Function Name

`fetch_weather_data(iso_country_code, start, end)`

#### Description

Fetches weather data for a given country and year range.

#### Parameters

- `iso_country_code`: ISO code of the country.
- `start`: Start year for fetching data (in yyyy).
- `end`: End year for fetching data (in yyyy).

### Usage

```python
from aedesproject_uif.data_extraction.meteorological import fetch_weather_data
fetch_weather_data("PHL", 2016, 2021)
```

---

## nasa_appeears

### Description

This module interacts with NASA Application for Extracting and Exploring Analysis Ready Samples (AρρEEARS)'s API to fetch various types of remote sensing data.  The AρρEEARS API requires a NASA Earthdata Login.  Register for NASA EarthData login [here](https://urs.earthdata.nasa.gov/users/new?client_id=ZAQpxSrQNpk342OR77kisA&redirect_uri=https%3A%2F%2Fappeears.earthdatacloud.nasa.gov%2Flogin&response_type=code&state=%2F).

### Main Functions

#### Function Name

1.  get_earthdata_token()

#### Description

Prompts the user to enter their NASA Earthdata Login Username and Password. It then sends a POST request to authenticate the user.  If authentication is successful, it returns an authorization header containing a Bearer token.  If the authentication fails, an error message is logged, and None is returned.

#### Parameters

`None`

#### Function Name

2.  `fetch_nasa_appeears(headers, iso_country_code, subregion, adm_lvl, start_date, end_date)`

#### Description

Fetches spectral band layers of Harmonized Landsat and Sentinel-2 Land Surface Reflectance images from NASA AρρEEARS' API within a specified date range.

#### Parameters

- `headers`: Bearer token from get_earthdata_token().
- `iso_country_code`: ISO code of the country.
- `subregion`: Name of a particular subregion in the country.
- `adm_lvl`: Administrative boundary level of the subregion selected.
- `start_date`: Start date for fetching data (in 'mm-dd-yyyy')
- `end_date`: End date for fetching data (in 'mm-dd-yyyy')


### Usage

```python
from aedesproject_uif.data_extraction.nasa_appeears import get_earthdata_token, fetch_nasa_appeears
headers = get_earthdata_token()
fetch_nasa_appeears(headers, "PHL", "Zamboanga Sibugay", 2, '01-01-2021', '01-10-2021')
```

---

## nasa_worldview

### Description

`nasa_worldview` is used for extracting Earth imaging data from NASA's Worldview service.

### Main Function

#### Function Name

`fetch_nasa_worldview(iso_country_code, subregion, region, start_date, end_date, interval)`

#### Description

Fetches Earth imaging data for a given subregion in a country within a specified date range.

#### Parameters

- `iso_country_code`: ISO code of the country.
- `subregion`: Name of a particular subregion in the country.
- `region`: Name of the region under which the selected subregion falls.
- `start_date`: Start date for fetching data (in 'yyyy-mm-dd')
- `end_date`: End date for fetching data (in 'yyyy-mm-dd')
- `interval`: Valid values = {'D' = daily, 'W' = weekly, 'M' = monthly, 'Q' = quarterly} 


### Usage

```python
from aedesproject_uif.data_extraction.nasa_worldview import fetch_nasa_worldview
fetch_nasa_worldview("PHL", "Zamboanga Sibugay", "Zamboanga Peninsula", "2016-01-10", "2021-01-10", "W")
```

---

## osm

### Description

The `osm` module is used for fetching data from OpenStreetMap, including Points of Interest (POIs) 
and other geographical data.

### Main Function

#### Function Name

`fetch_osm(iso_country_code, admin_level)`

#### Description

Fetches OpenStreetMap places of interest (POI) data of all subregions of a given country.

#### Parameters

- `iso_country_code`: ISO code of the country.
- `admin_level`: Administrative boundary level to fetch data for.

### Usage

```python
from aedesproject_uif.data_extraction.osm import fetch_osm
fetch_osm("PHL", 2)
```

---
