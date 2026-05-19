# ---
title: "Changelog"
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
# Changelog

## [Version 1.0.0](https://github.com/docligot/aedesproject)
- Initial release.  NASA Space Apps Challenge 2019 version.  Datasets used were admin 1 level monthly cases from Department of Health's website, weather data from PAGASA, Google Trends of dengue-related keywords, and Sentinel-2 images via QGIS.  Forecasting methodology was stepwise regression.  Dashboard includes dengue hotspot map and alerts

## [Version 2.0.0](https://github.com/cirrolytix/aedes_dpg)
- Included additional locations. ARIMA added as a forecasting method for comparison.

## [Version 3.0.0](https://github.com/cirrolytix/aedes_unicef_2022)
- Additional datasets: remote sensing indices from Google Earth Engine, places of interest from OpenStreetMaps.  Admin level 2 weekly cases are now available.  PyPI library (https://pypi.org/project/aedes/).  Uploaded data to HDX (https://data.humdata.org/organization/cirrolytix)

## [Version 4.0.0](https://github.com/cirrolytix/aedesproject-uif)
- Automated data extraction, preparation, machine learning, and prediction.  Changed data sources: remote sensing indices from NASA AppEEARS, satellite images from NASA Worldview, weather data from NASA POWER.  Additional data sources: administrative boundaries from www.geoboundaries.org, location latitude and longitude from geocode.maps.co, population density and relative wealth index from Meta Data for Good.  Dashboard includes multidimensional risk scores inspired by European Commission's Joint Research Centre.  Locations analyzed were provinces in the Zamboanga Peninsula region.
