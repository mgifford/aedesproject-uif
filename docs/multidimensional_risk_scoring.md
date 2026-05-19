# ---
title: "Multidimensional Risk Scoring"
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
# Multidimensional Risk Scoring

Dengue fever, a mosquito-borne viral infection, poses a significant public health challenge, affecting millions of people worldwide. Effective management of the dengue crisis requires a comprehensive understanding of various risk factors, which can be complex and multidimensional. The INFORM (Index for Risk Management) framework offers a robust methodology for assessing such risks by considering multiple dimensions, including hazards, vulnerabilities, and lack of coping capacities (Promentilla, 2020; UNISDR, 2019). This paper presents a modified INFORM framework tailored for dengue crisis risk assessment, incorporating a wide array of variables and utilizing Sparse Principal Component (SPC) regression to handle high-dimensionality in the data.

The INFORM framework's multidimensional risk assessment can guide decision-makers in allocating resources more effectively, prioritizing interventions, and implementing preventive measures. For instance, areas with high vulnerability scores may benefit from targeted public health campaigns, while those with low coping capacities might require strengthened healthcare infrastructures.

## Data Sources
The target outcome considered for the pilot implementation is **year-to-date (YTD)** case fatality rate, computed as the ratio of YTD number of deaths to YTD number of cases.  On the other hand, the predictor variables for this model are derived from various reputable sources, including meteorological data, remote sensing data, and map places of interest (POIs). These variables are categorized into three risk dimensions: Hazard, Vulnerability, and Lack of Coping Capacity, as inspired by the INFORM framework (UNISDR, 2019).

Below is a table of predictors included in the model:


|   Data Source   |   Hazard   |   Vulnerability   |   Lack of Coping Capacity   |
|-----------------|------------|-------------------|-----------------------------|
|   Department of Health | Cases|        |          |   
|   NASA AppEEARS   |   Normalized Difference Vegetation Index (NDVI), Normalized Difference Water Index (NDWI)   |   Normalized Difference Built-up Index (NDBI)   |      |
|   NASA POWER   |   Earth Skin Temperature (C), Temperature at 2 Meters (C), Specific Humidity at 2 Meters (g/kg), Relative Humidity at 2 Meters (%), Dew/Frost Point at 2 Meters (C), Wet Bulb Temperature at 2 Meters (C), Surface Soil Wetness (1), Temperature at 2 Meters Maximum (C), Temperature at 2 Meters Minimum (C), Profile Soil Moisture (1), Root Zone Soil Wetness (1), SYN1deg Cloud Amount (%), Temperature at 2 Meters Range (C), Precipitation Corrected (mm/day), SYN1deg All Sky Surface Longwave Downward Irradiance (W/m^2)   |      |      |
|   OpenStreetMap   |   Number of Rivers, Number of Ponds, Number of Reservoirs, Number of Basins, Number of Lakes, Number of Streams, Number of Lagoons, Number of Fishponds, Number of Moats, Number of Oxbows, Number of Canals, Number of Ditches, Number of Creeks, Number of Shallows, Number of Stream Pools, Number of Wastewaters, Number of Swimming Pools, Number of Tidals, Number of Pala-Isdaans, Number of Toilets, Number of Waste Disposals, Number of Waste Transfer Stations   |   Number of schools, Number of universities, Number of colleges, Number of kindergartens, Number of childcares, Number of prep schools, Number of dormitories, Number of nursing homes, Number of quarantine facilities, Number of birthing centres, Number of residential buildings   |   Number of Hospitals, Number of Clinics, Number of Health Posts, Number of Healthcares, Number of Pharmacies, Number of Doctors, Number of Rescues, Number of Community Centres, Number of Social Centres, Number of Social Facilities, Number of Emergency Services   |
|   Meta Data for Good   |      |   Total Population Density, Children under 5 y.o. Population Density, Elderly 60+ y.o. Population Density, Youth 15-24 y.o. Population Density, Average Relative Wealth Index   |      |

* **Hazard:** The remote sensing and meteorological indices considered generally measure environmental conditions that may contribute to the proliferation of the dengue mosquito vector. For instance, high vegetation (NDVI) and water indices (NDWI) can indicate potential breeding grounds, while high temperatures and certain precipitation levels can enhance mosquito survival and reproduction.  Count of places of interest (POIs) that can possibly become mosquito breeding sites or promote human-mosquito interactions are also included.
* **Vulnerability:** These indices generally measure conditions that make an area more susceptible to a dengue outbreak. For instance, built-up and densely populated areas (NDBI, Population Density) can facilitate human-mosquito contact.  Count of POIs where vulnerable population might frequent or live were also added.
* **Lack of coping capacity:** For this dimension, POIs that can provide resources for response or might stress existing resources during an outbreak are examined. 

## Methodological Framework
### Sparse Principal Component Analysis (SPCA)
Given the high-dimensionality of the data (p >> n), traditional principal component analysis (PCA) may not be effective. Sparse PCA (SPCA) offers a solution by producing principal components with sparse loadings, making them easier to interpret and more suitable for regression models (Zou, Hastie, & Tibshirani, 2006).

### Bayesian Optimization for Hyperparameter Tuning
Objective Function: Explained Variance with Penalty
The objective function in Bayesian optimization is designed to maximize the explained variance of the model while incorporating a penalty term for model complexity. Specifically, the objective **f(x)** is defined as:

```math
f(x)=Explained Variance − λ × Model Complexity
```

Here, "Explained Variance" measures how well the model accounts for the variability of the response data, and "Model Complexity" is quantified using the number of non-zero coefficients in the sparse PCA loadings. The penalty term, controlled by **λ**, ensures that the model does not overfit by becoming too complex. This objective function allows for a balanced trade-off between model accuracy and simplicity [Snoek et al. (2012)].

Bayesian optimization offers several advantages over traditional hyperparameter tuning methods like random and grid search, making it particularly well-suited for high-dimensional and complex models. First, it is computationally more efficient than grid search, which exhaustively explores all possible combinations of hyperparameters [Brochu et al. (2010)]. Second, it aims for global optimization of the objective function, ensuring a more accurate and reliable model compared to the random search, which may miss the optimal set of hyperparameters [Snoek et.al (2012)]. Lastly, Bayesian optimization employs a probabilistic model to predict the objective function's value for different hyperparameters, allowing for more informed decisions about which hyperparameters to test next. This reduces the number of iterations needed to find the optimal set, thereby enhancing the efficiency of the model tuning process (Shahriari et al., 2016).

By employing Bayesian optimization, this study ensures a more efficient and effective hyperparameter tuning process, which is crucial for handling the high-dimensionality and complexity inherent in dengue risk assessment models.

### Recursive Feature Elimination (RFE)
For models where the number of principal components is one, the raw variables are fed into the linear regression instead and Recursive Feature Elimination (RFE) is performed for feature selection.  Initially proposed by Guyon et al. (2002), RFE has been widely adopted in various domains, including healthcare and sentiment analysis, for its effectiveness in eliminating irrelevant and redundant features [Lamba et al. (2022), Mohd Nafis & Awang (2021)]. The algorithm iteratively evaluates and ranks features based on their importance, thus providing a more refined feature set for model training [Lin et al., (2022)]. 

# References
Promentilla, M. A. B. (2020). Coronavirus: The Story of Risk and Resilience (Part 2). Medium. https://medium.com/@mpromentilla/coronavirus-the-story-of-risk-and-resilience-part-2-de2c23cd5c55

UNISDR. (2019). INFORM Epidemic Risk Index Technical Report. United Nations Office for the Coordination of Humanitarian Affairs. https://www.unisdr.org/preventionweb/files/62241_informepidemicriskindextechnicalrep.pdf

Zou, H., Hastie, T., & Tibshirani, R. (2006). Sparse principal component analysis. Journal of computational and graphical statistics, 15(2), 265-286.

Snoek, J., Larochelle, H., & Adams, R. P. (2012). Practical Bayesian optimization of machine learning algorithms. In Advances in neural information processing systems (pp. 2951-2959).

Brochu, E., Cora, V. M., & de Freitas, N. (2010). A tutorial on Bayesian optimization of expensive cost functions, with application to active user modeling and hierarchical reinforcement learning. arXiv preprint arXiv:1012.2599.

Shahriari, B., Swersky, K., Wang, Z., Adams, R. P., & de Freitas, N. (2016). Taking the Human Out of the Loop: A Review of Bayesian Optimization. Proceedings of the IEEE, 104(1), 148-175.

Guyon, I., Weston, J., Barnhill, S., & Vapnik, V. (2002). Gene selection for cancer classification using support vector machines. Machine Learning, 46(1-3), 389-422.

Lamba, R., Gulati, T., & Jain, A. (2022). A Hybrid Feature Selection Approach for Parkinson’s Detection Based on Mutual Information Gain and Recursive Feature Elimination. Arabian Journal for Science and Engineering, 47, 1-14. DOI: 10.1007/s13369-021-06544-0

Mohd Nafis, N. S., & Awang, S. (2021). An Enhanced Hybrid Feature Selection Technique Using Term Frequency-Inverse Document Frequency and Support Vector Machine-Recursive Feature Elimination for Sentiment Classification. IEEE Access, 9, 3069001. DOI: 10.1109/ACCESS.2021.3069001

Lin, H., Xue, Y., Chen, K., Zhong, S., & Chen, L. (2022). Acute coronary syndrome risk prediction based on gradient boosted tree feature selection and recursive feature elimination: A dataset-specific modeling study. PLOS ONE, 17(1), e0278217. DOI: 10.1371/journal.pone.0278217
