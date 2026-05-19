# ---
title: "Home"
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
# Advanced Early Disease Prediction and Exploration Service (AEDES)

## Introduction

Welcome to the AedesProject-UIF documentation! This Python package is designed for advanced early disease prediction and exploration, supporting surveillance of multiple vector-borne diseases across different geographic contexts.

> **Original work**: AEDES was originally developed as the *Advanced Early **Dengue** Prediction and Exploration Service* under the UNICEF Innovation Fund, focused on dengue surveillance in the Philippines.

### Dengue Crisis in the Philippines

The dengue situation in the Philippines has been a persistent public health concern. In 2019, the country reported over 146,062 cases and 622 deaths due to dengue, making it the nation with the most number of dengue cases in Southeast Asia for that year [[Paris, J. (2019)]](https://www.rappler.com/nation/237340-philippines-has-most-dengue-cases-southeast-asia-2019/). In 2022, the situation escalated further with approximately 221,000 recorded cases, marking an 182% increase compared to the same period in the previous year [[Statista Research Department (2019)]](https://www.statista.com/statistics/1120319/philippines-number-dengue-cases/). As of July 15, 2023, the Philippines Department of Health (DOH) has reported a total of 80,318 dengue fever cases, with 14 of the 17 regions in the country experiencing an increase in cases over the past month [["Philippines dengue tally" (2023)]](https://outbreaknewstoday.com/philippines-dengue-tally-eclipses-80000-in-2023-to-date-92506/#:~:text=The%20Philippines%20Department%20of%20Health,cases%20over%20the%20past%20month.).

### Global Dengue Situation

In 2023, the global dengue situation is alarming. As of August 23, over 3.7 million cases and more than 2,000 dengue-related deaths have been reported from 70 countries/territories. The Americas are particularly hard-hit, with over 3 million new infections recorded so far. Countries like Brazil, Peru, and Bolivia are among the most affected, experiencing severe outbreaks that have strained their healthcare systems [["Dengue Worldwide Overview" (2023)]](https://www.ecdc.europa.eu/en/dengue-monthly).

### The Need for a Big Data Dengue Risk Surveillance Portal

The escalating numbers of dengue cases, both in the Philippines and globally, make a compelling case for the urgent need for a big data dengue risk surveillance portal. Such a system could offer advanced warnings of potential outbreaks to public health agencies and local governments, enabling them to allocate resources more effectively and implement targeted interventions.

#### Advanced Early Detection and Exploration Service (AEDES)

AEDES is an automated information portal that correlates dengue cases and deaths with various non-traditional data, giving an advance indicator of when dengue will emerge and potential dengue hotspot locations.

This service relies on 5 data sets:
1. Satellite Data: Satellite imaging data from NASA Worldview and AppEEARS
2. Meteorological Data: from NASA POWER
3. Google Data: Search trends for 'dengue' and related terms
4. Places of Interest (POIs): Buildings, amenities, and water bodies from OpenStreetMap
5. Demographic Data: Population density and relative wealth index from Meta Data for Good

To populate the information portal, AEDES runs on three models:
1. Dengue cases prediction from climate and search data
2. Likely stagnant water detection (dengue hotspots) from satellite data
3. Assessment the risk of dengue crisis by examining the hazard, vulnerability, and lack of coping capacity of localities

By doing this, AEDES is addressing 2 key challenges for public health and local government officials:

- Get ahead of the lagged delay of dengue reporting by using real-time information (e.g., climate, searches) to infer if dengue cases are about to spike.
- Precisely anticipate areas that may be affected by dengue to prioritize health aid, supplies, and proactive fumigation to prevent the outbreaks.

## Installation

User must have `Python>=3.8` and `pip` ready to use.  To install the package, run the following command:

```bash
pip install git+https://github.com/Cirrolytix/aedesproject-uif.git
```