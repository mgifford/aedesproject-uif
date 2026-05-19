# ---
title: "Initialization"
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
# Initialization

## Overview

This section covers the utility function to set up the project structure required by the aedesproject-uif Python package to work properly in the user's current working directory. 

---

## setup_project_structure

### Description

This function sets up the project structure by downloading and extracting certain directories from the aedesproject-uif GitHub repository.  There will be **model** and **processed** directories, which will be empty, and a **data** directory, which will only contain the **INFORM_DF_Variables.csv** file.

### Function Name

`setup_project_structure(destination_path)`

### Parameters

- `destination_path`: The path where the project structure will be set up.

### Usage

```python
from aedesproject_uif import setup_project_structure
setup_project_structure(r"C:\USERS\USER123\Documents\aedes")
```

### Important Note:
First, create a subfolder in the *destination_path* for the \*.py or \*.ipynb file that you will run (e.g. a subfolder named **src**).  Create the Python file or Jupyter notebook that will perform the project structure setup in that subfolder, then run it.  

Ensure that all Python files or Jupyter notebooks that contain the codes that run the processes in aedesproject-uif are saved and ran from that code subfolder.
