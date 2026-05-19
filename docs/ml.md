# ---
title: "Machine Learning"
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
# Machine Learning

## Overview

This section covers the various modules used for machine learning in aedesproject-uif. These modules handle the 
training of forecasting and risk models.

---


## auto-ts

### Description

This module handles auto time-series modeling pipeline in aedesproject-uif.

### Main Functions


#### Function Name

`train_fcast_model(iso_country_code, adm, target, fcst_length, n_ar, freq, n_fold, m)`

#### Description

Main function used for auto time-series modeling.  It includes automatic selection of optimal transformation, tuning, model fitting, evaluation, and best model selection.

#### Parameters

- `iso_country_code`: ISO code of a country.
- `adm`: Subregion name for which to train the forecasting model.
- `target`: Target outcome to forecast.
- `fcst_length`: Length of forecast horizon.  Equivalent to number of steps ahead to forecast.
- `n_ar`: Number of autoregressive (AR) terms to include in the model fitting.
- `freq`: Frequency of the dates in the data being modelled.  Refer to this [link](https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases) for the valid values.
- `n_fold`: Number of folds to be used in cross-validation.
- `m`: Number of observations that counts one seasonal step. For Hourly: 24, Weekly: 52, Monthly: 12, Quarterly: 4.


### Usage

```python
from aedesproject_uif.ml.auto-ts import train_fcast_model
train_fcast_model("PHL", "Zamboanga del Sur", "cases", 4, 12, 'W', 5, 52)
```

---


## hotspot_detection

### Description

This module handles hotspot detection pipeline in aedesproject-uif.

### Main Functions


#### Function Name

`detect_hotspots(iso_country_code, subregion, start_date, end_date, duration_threshold)`

#### Description

Main function used for hotspot detection.  This detects potential stagnant water based on varying thresholds of Normalized Difference Water Index (NDWI) across different levels of Normalized Difference Vegetation Index (NDVI).

#### Parameters

- `iso_country_code`: ISO code of a country.
- `subregion`: Subregion in which to detect potential stagnant water bodies.
- `start_date`: Start date of analysis window (in 'dd/mm/yyyy'). 
- `end_date`: End date of analysis window (in 'dd/mm/yyyy'). 
- `duration_threshold`: Number of consecutive times a pixel is detected as water body to be definitively considered as 
stagnant water.


### Usage

```python
from aedesproject_uif.ml.hotspot_detection import detect_hotspots
detect_hotspots("PHL", "Zamboanga Sibugay", '18/03/2023', '18/06/2023', 8)
```

---


## risk_model_dev

### Description

This module handles hazard, vulnerability, lack of coping capacity, and consolidated risk model development in aedesproject-uif.

### Main Functions


#### Function Name

`1. train_risk_model(ISO_COUNTRY_CODE, TARGET_VAR, risk_dimension)`

#### Description

Main function used for building the hazard, vulnerability, and lack of coping capacity scoring model.

#### Parameters

- `ISO_COUNTRY_CODE`: ISO code of a country.
- `TARGET_VAR`: Target outcome with which one wants the risk score to be correlated.
- `risk_dimension`: Risk Dimension.  Valid values = {"Hazard", "Vulnerability", "Lack of Coping Capacity"}

### Usage

```python
from aedesproject_uif.ml.risk_model_dev import train_risk_model
train_risk_model("PHL", "CFR", "Hazard")
train_risk_model("PHL", "CFR", "Vulnerability")
train_risk_model("PHL", "CFR", "Lack of Coping Capacity")
```

#### Function Name

`2. train_final_risk_model(ISO_COUNTRY_CODE, TARGET_VAR)`

#### Description

Main function used for building the final risk scoring model based on hazard, vulnerability, and lack of coping capacity scores.  Note that the individual risk dimension scores from *train_risk_model()* should exist before fitting the final risk model.

#### Parameters

- `ISO_COUNTRY_CODE`: ISO code of a country.
- `TARGET_VAR`: Target outcome with which one wants the risk score to be correlated.

### Usage

```python
from aedesproject_uif.ml.risk_model_dev import train_final_risk_model
train_final_risk_model("PHL", "CFR")
```

---

