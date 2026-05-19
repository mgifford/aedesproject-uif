# ---
title: "Data Preparation"
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
# Data Preparation

## Overview

This section covers the various modules used for data preparation in aedesproject-uif. The modules handle the preparation 
and processing of data after extraction, making it ready for further analysis and modeling.

---


## demographic_data

### Description

This module processes and prepares demographic data for further analysis.

### Main Function

#### Function Name

`process_demogs(iso_country_code, adm_level)`

#### Description

Main function used for processing high resolution population density maps from Meta Data for Good and for calculating population counts, densities, and relative wealth indices.

#### Parameters

- `iso_country_code`: ISO code of the country.
- `adm_level`: Administrative level for which the population counts, densities, and relative wealth indices are computed.

### Usage

```python
from aedesproject_uif.data_preparation.demographic_data import process_demogs
process_demogs("PHL", 2)
```

---


## dengue_data

### Description

This module processes and prepares dengue data for further analysis.

### Main Function

#### Function Name

`process_dengue_data(iso_country_code, adm_level, end_date)`

#### Description

Main function used for processing dengue data and calculating year-to-date (YTD) numbers.

#### Parameters

- `iso_country_code`: ISO code of the country.
- `adm_level`: Administrative level for which the population counts, densities, and relative wealth indices are computed.
- `end_date`: End date for which to base the YTD computation on (in 'yyyy-mm-dd')

### Usage

```python
from aedesproject_uif.data_preparation.dengue_data import process_dengue_data
process_dengue_data("PHL", 2, "2019-12-29")
```

---


## forecasting_data

### Description

This module processes and prepares forecasting data for further analysis.  This combines the Google Trends data and meteorological or weather data for a particular subregion within a country.  This requires the file Admin_Boundaries_{iso_country_code}.csv in the **data** folder.

### Main Function

#### Function Name

`process_fcast_data(iso_country_code, adm, flnm)`

#### Description

Main function used for processing forecasting data data.

#### Parameters

- `iso_country_code`: ISO code of the country.
- `adm`: Subregion name to get Google Trends and weather data on.
- `flnm`: Filename of the dengue data. The file should be saved in the 'Dengue/{iso_country_code}' subfolder in 'data'. It should have the following columns: [loc = subnational area name (all caps), cases = number of dengue cases, deaths = number of dengue deaths, Region = regional area name (all caps)]


### Usage

```python
from aedesproject_uif.data_preparation.forecasting_data import process_fcast_data
iso_country_code = "PHL"
adm = "Zamboanga Sibugay"
process_fcast_data(iso_country_code, adm, "PHL.xlsx")
```

---


## poi_data

### Description

This module processes and prepares places of interest (POI) data from OpenStreetMap for further analysis.  

### Main Function

#### Function Name

`process_osm_data(iso_country_code, adm_level)`

#### Description

Main function used for processing the POI data.  This filters only the POIs that will be used in the multidimensional risk scoring.

#### Parameters

- `iso_country_code`: ISO code of the country
- `adm_level`: Administrative level for which the POI-related indicators are to be obtained.

### Usage

```python
from aedesproject_uif.data_preparation.poi_data import process_osm_data
process_osm_data("PHL", 2)
```

---


## remote_sensing_data

### Description

This module processes and prepares remote sensing data for further analysis.  

### Main Function

#### Function Name

`process_remote_sensing_data(iso_country_code, end_date_str)`

#### Description

Main function used for processing remote sensing data.  This computes for the averages of Normalized Difference Vegetation Index (NDVI), Normalized Difference Water Index (NDWI), and Normalized Difference Built-up Index (NDBI) from the satellite images as of the closest date to the end date that will be specified by the user.

#### Parameters

- `iso_country_code`: ISO code of the country
- `end_date_str`: End date for computing the averages (in 'dd/mm/yyyy').

### Usage

```python
from aedesproject_uif.data_preparation.remote_sensing_data import process_remote_sensing_data
process_remote_sensing_data("PHL", '29/12/2019')
```

---


## remote_sensing_indices_images

### Description

This module generates the images for various remote sensing indices from the spectral band layers of the Harmonized Landsat and Sentinel-2 (HLS) Land Surface reflectance images, for further analysis.

### Main Function

#### Function Name

`hls_to_indices(iso_country_code, subregion, index_func, start_date_str, end_date_str)`

#### Description

Main function used for processing HLS images.

#### Parameters

- `iso_country_code`: ISO code of a country.
- `subregion`: Subregion name for which to process the HLS images.
- `index_func`: Callable.  Valid values = {calculate_ndvi, calculate_ndwi, calculate_ndbi}.
- `start_date_str`: Start date for processing images (in 'dd/mm/yyyy').
- `end_date_str`: End date for processing images (in 'dd/mm/yyyy').

### Usage

```python
from aedesproject_uif.data_preparation.remote_sensing_indices_images import hls_to_indices
iso_code = "PHL"  # Example ISO country code for Philippines
subregion_name = "Zamboanga Sibugay"  # Example subregion
hls_to_indices(iso_code, subregion_name, calculate_ndvi, '01/12/2019', '18/06/2023')
hls_to_indices(iso_code, subregion_name, calculate_ndwi, '01/12/2019', '18/06/2023')
hls_to_indices(iso_code, subregion_name, calculate_ndbi, '01/12/2019', '18/06/2023')
hls_to_indices(iso_code, subregion_name, calculate_fpar, '01/12/2019', '18/06/2023')
```

---


## risk_data_consolidation

### Description

This module processes and prepares risk data consolidation for further analysis.

### Main Function

#### Function Name

`combine_inform_data(iso_country_code, end_date)`

#### Description

Main function used for processing risk data consolidation data.  This merges the meteorological or weather data, remote sensing averages data, filtered POIs data, and demographic data for subsequent use in multidimensional risk modeling and scoring.

#### Parameters

- `iso_country_code`: ISO code of a country.
- `end_date`: End date for the report (in 'dd/mm/yyyy')

### Usage

```python
from aedesproject_uif.data_preparation.risk_data_consolidation import combine_inform_data
combine_inform_data("PHL", "29/12/2019")
```

---


## weather_data

### Description

This module processes and prepares weather data for further analysis.

### Main Function

#### Function Name

`process_weather_data(iso_country_code, end_date)`

#### Description

Main function used for processing weather data.  This computes for the 3-month average values of moisture, humidity, precipitation, and temperature data.

#### Parameters

- `iso_country_code`: ISO code of a country.
- `end_date`: End date for the report (in 'yyyy-mm-dd')

### Usage

```python
from aedesproject_uif.data_preparation.weather_data import process_weather_data
process_weather_data("PHL", '2019-12-29')
```

---

