# ---
title: "Prediction"
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
# Prediction

## Overview

This section covers the modules used for prediction in aedesproject-uif. These modules handle the generation of forecasts and risk scores based on the trained models.  The model pickles of the final models from the **ml.risk_model_dev** module should be present in the **model** folder.

---


## generate_forecasts

### Description

This module generates forecasts by applying trained models on new data.

### Main Function

#### Function Name

`forecast_data(iso_country_code, adm, target, n_ar, freq)`

#### Description

Main function used for generating forecasts.

#### Parameters

- `iso_country_code`: ISO code of a country.
- `adm`: Subregion for which to generate forecasts.
- `target`: Target outcome to be forecasted.
- `n_ar`: Number of AR to be included in the initialization of the forecaster.  This should be equal to the number used in model training.
- `freq`: Frequency of the dates in the training data.  Refer to this [link](https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases) for the valid values.

### Usage

```python
from aedesproject_uif.predict.generate_forecasts import forecast_data
forecast_data("PHL", "Zamboanga del Norte", "cases", 12, "W")
```

---


## generate_risk_scores

### Description

This module generates hazard, vulnerability, lack of coping capacity, and consolidated risk scores in the aedesproject-uif.

### Main Function

#### Function Name

`risk_score_data(ISO_COUNTRY_CODE)`

#### Description

Main function used for generating the individual and consolidated risk scores.

#### Parameters

- `ISO_COUNTRY_CODE`: ISO code of a country.

### Usage

```python
from aedesproject_uif.predict.generate_risk_scores import risk_score_data
risk_score_data('PHL')
```

---

