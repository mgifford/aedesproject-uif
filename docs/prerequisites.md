# ---
title: "Prerequisites"
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
# Prerequisites

Before running the data extraction, preparation, machine learning, and prediction on country and subregions of interest, make sure to perform the following steps first:

1.  Set up the required project directory structure in your chosen working directory.  Refer to the [Initialization](./initialization.md) section for the detailed instructions on how to do this.
2.  Make sure that you have the following files in the `data` folder in your chosen working directory:

	- `Admin_Boundaries_{iso_country_code}.csv`: Where iso_country_code is the 3-letter ISO code of the country of interest.  This file has the columns **Subregion** (which may be any administrative level 2 or 3 location name) and **Region** (which may be any administrative level 1 or 2 location name).
	- `Subdivision_{iso_country_code}`: Where iso_country_code is the 3-letter ISO code of the country of interest.  This file has the columns **ISO 3166-2** (which are the ISO codes of the subregions in the country of interest) and **Region** (which are the subregion names in the country of interest).  
