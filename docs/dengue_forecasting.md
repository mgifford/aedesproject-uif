# ---
title: "Dengue Forecasting"
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
# Forecasting Dengue Cases

The increasing incidence of dengue fever across various geographical regions necessitates the development of robust forecasting models to aid in public health planning and intervention. Accurate and timely forecasts can significantly contribute to the effective allocation of resources and implementation of preventive measures. In this context, AEDES aims to provide a comprehensive forecasting pipeline for predicting dengue cases. Utilizing a multi-faceted approach that incorporates advanced statistical methods and machine learning algorithms, the pipeline is designed to optimize the accuracy and reliability of the forecasts. Specifically, the pipeline is built upon the Scalecast Python package [[Keith (2021)]](https://github.com/mikekeith52/scalecast), a versatile time series forecasting tool that includes automated model selection, model optimization, pipelines, visualization, and reporting. This methodology section elucidates the rationale behind the choice of data sources, preprocessing steps, and machine learning models.

## Exogenous Variables
The use of meteorological data like temperature, humidity, and precipitation is based on their proven correlation with the breeding patterns of Aedes mosquitoes, the primary vectors of dengue [Van Hau et al. (2022), Li and Dong (2022), Ligue and Ligue (2022), de Almeida et al. (2022),  Chen et al. (2022), Methiyothin and Ahn (2022), Ceballos-Arroyo et al. (2020), Jain et al. (2019), Ruangudomsakul et al. (2018), Link et al. (2018)]. Google Trends data provides insights into public awareness and concern about dengue, which has been shown to correlate with actual case numbers [Methiyothin et al. (2022), Puengpreeda et al. (2020), Rangarajan et al. (2019), Yeh (2019), Tang and Subramanian (2019), Anggraeni and Aristiani (2016), Gluskin et al. (2014)].

## Data Preprocessing

### Outlier Detection and Correction
The initial phase of the pipeline involves data preprocessing, a critical step that significantly influences the quality of the subsequent modeling. Outliers can introduce noise and lead to misleading forecasts [Fu et al. (2023), Shiyuan et al. (2021), Ranjan et al. (2020), Wang et al. (2019), Sankaran et al. (2019), Karthika et al. (2017)].  

Outlier detection and correction using the Lowess Smoother algorithm is employed. This non-parametric method is chosen for its flexibility in capturing complex relationships in the data. The smoother operates with a smooth fraction of 0.25 and one iteration to identify and correct outliers.

### Variable Selection
As there are several exogenous variables (including their lags) being considered initially, there is a need to perform dimension reduction prior to time-series modeling [Ghysels et al. (2016), Fujita et al. (2007)]. The Granger causality test is often employed to identify which variables in a multivariate time series have a predictive relationship with a target variable. Applying Granger causality tests can help in eliminating variables that do not have a causal relationship with the target variable, thereby simplifying the model.  This not only reduces the dimensionality of the model but also improves its interpretability.   


## Model Training and Tuning
### Model Selection
The pipeline incorporates a variety of machine learning models, including MLR, Lasso, Ridge, ElasticNet, XGBoost, LightGBM, KNN, Catboost, and GBT.  Linear models like MLR, Lasso, Ridge, and ElasticNet are used for their suitability in capturing linear trends in the data [Marigmen et al. (2022), Patil and Pandya (2021), Olmoguez et al. (2019)]. On the other hand, gradient boosting models like XGBoost, LightGBM, Catboost, and GBT are included for their ability to capture complex non-linear relationships [Nascimento et al. (2023), Panda and Mohanty (2023), Methiyothin and Ahn (2022)]. KNN is also employed for its effectiveness in capturing local patterns in the data [Tajmouati et al. (2021)].

The models' performances are evaluated using RMSE and R-squared metrics on both in-sample and out-of-sample data.

Hyperparameter Tuning
The pipeline includes an automated hyperparameter tuning step, which is essential for optimizing the performance of the machine learning models. This is achieved through cross-validation and dynamic tuning methods.

Data Transformation and Reversion
The pipeline also includes steps for optimal data transformation and reversion, which are crucial for improving model performance. These steps are automated and are part of the [Scalecast package](https://scalecast-examples.readthedocs.io/en/latest/misc/introduction/Introduction2.html#Fully-Automated-Pipelines), upon which the pipeline is built.


# References
Ceballos-Arroyo, A. M., Maldonado-Perez, D., Mesa-Yepes, H., Pérez, L., Ciuoderis, K., Comach, G., & Branch-Bedoya, J. W. (2020). Towards a machine learning-based approach to forecasting Dengue virus outbreaks in Colombian cities: a case-study: Medellin, Antioquia. DOI: 10.1117/12.2547001

Ruangudomsakul, C., Duangsin, A., Kerdprasop, K., & Kerdprasop, N. (2018). Application of Remote Sensing Data for Dengue Outbreak Estimation Using Bayesian Network. DOI: 10.18178/ijmlc.2018.8.4.718

Link, H. E., Richter, S. N., Leung, V., Brost, R., Phillips, C., & Staid, A. (2018). Statistical Models of Dengue Fever. DOI: 10.1007/978-981-13-6661-1_14

Van Hau, N., Tuyet Hanh, T. T., Mulhall, J., Minh, H., Duong, T., Van Chien, N., & Viet Hung, N. Q. (2022). Deep learning models for forecasting dengue fever based on climate data in Vietnam. DOI: 10.1371/journal.pntd.0010509

Li, Z., & Dong, J. (2022). Big Geospatial Data and Data-Driven Methods for Urban Dengue Risk Forecasting: A Review. DOI: 10.3390/rs14195052

Ligue, K. D. B., & Ligue, K. J. B. (2022). Deep Learning Approach to Forecasting Dengue Cases in Davao City Using Long Short-term Memory (LSTM). DOI: 10.56899/151.03.01

de Almeida, M. L., & de Souza, F. T. (2022). The use of Predictive Models as a Tool to Fight Dengue and to Improve Public Health. DOI: 10.22161/ijaers.912.40

Jain, R., Sontisirikit, S., Iamsirithaworn, S., & Prendinger, H. (2019). Prediction of dengue outbreaks based on disease surveillance, meteorological and socio-economic data. DOI: 10.1186/s12879-019-3874-x

Chen, J.-W., Ding, R.-L., Liu, K., Xiao, H., Hu, G., Xiao, X., & Dong, G.-H. (2022). Collaboration between meteorology and public health: Predicting the dengue epidemic in Guangzhou, China, by meteorological parameters. DOI: 10.3389/fcimb.2022.881745

Methiyothin, T., & Ahn, I. (2022). Forecasting Dengue Fever in France and Thailand using XGBoost. DOI: 10.23919/APSIPAASC55919.2022.9979936

Rangarajan, P., Mody, S. K., & Marathe, M. (2019). Forecasting dengue and influenza incidences using a sparse representation of Google trends, electronic health records, and time series data. PLOS Computational Biology, 15(11), e1007518. DOI: 10.1371/journal.pcbi.1007518

Yeh, F.-C. (2019). Forecasting mortality using Google trend. arXiv preprint arXiv:1901.09692. Link

Tang, S. L., & Subramanian, P. (2019). Review on Nowcasting using Least Absolute Shrinkage Selector Operator (LASSO) to Predict Dengue Occurrence in San Juan and Iquitos as Part of Disease Surveillance System. Periodicals of Engineering and Natural Sciences, 7(2), 442. DOI: 10.21533/PEN.V7I2.442

Anggraeni, W., & Aristiani, L. (2016). Using Google Trend data in forecasting number of dengue fever cases with ARIMAX method case study: Surabaya, Indonesia. 2016 International Conference on Information & Communication Technology and Systems (ICTS). DOI: 10.1109/ICTS.2016.7910283

Puengpreeda, A., Yhusumrarn, S., & Sirikulvadhana, S. (2020). Weekly Forecasting Model for Dengue Hemorrhagic Fever Outbreak in Thailand. Epidemiology, 24(3), 71. DOI: 10.4186/ej.2020.24.3.71

Gluskin, R., Johansson, M., Santillana, M., & Brownstein, J. (2014). Evaluation of Internet-Based Dengue Query Data: Google Dengue Trends. PLOS Neglected Tropical Diseases, 8(2), e2713. DOI: 10.1371/journal.pntd.0002713

Fu, W., Fu, Y., Li, B., Zhang, H., Zhang, X. & Liu. J (2023). A compound framework incorporating improved outlier detection and correction, VMD, weight-based stacked generalization with enhanced DESMA for multi-step short-term wind speed forecasting. Applied Energy, 2023. DOI: 10.1016/j.apenergy.2023.121587

Wang, J., Du, P., Hao, Y., Ma, X., Niu, T. & Yang. W. (2019). An innovative hybrid model based on outlier detection and correction algorithm and heuristic intelligent optimization algorithm for daily air quality index forecasting. Journal of Environmental Management, 2019. DOI: 10.1016/j.jenvman.2019.109855

Ranjan, K.G., Tripathy, D.S., Prusty, B. & Jena, D. (2020). An improved sliding window prediction‐based outlier detection and correction for volatile time‐series. International Journal of Numerical Modelling: Electronic Networks, Devices and Fields, 2020. DOI: 10.1002/jnm.2816

Shiyuan, H., Jinliang, G., Zhong, D., Liqun, D., Ou, C. & Xin, P. (2021). An Innovative Hourly Water Demand Forecasting Preprocessing Framework with Local Outlier Correction and Adaptive Decomposition Techniques. Water, 2021. DOI: 10.3390/W13050582

Karthika, S., Margaret, V. & Balaraman, K. (2017). Hybrid short term load forecasting using ARIMA-SVM. 2017 Innovations in Power and Advanced Computing Technologies (i-PACT). DOI: 10.1109/IPACT.2017.8245060

Sankaran, G., Sasso, F., Kepczynski, R. & Chiaraviglio, A. (2019). Custom Method to Forecast Seasonal Products. DOI: 10.1007/978-3-030-05381-9_4

Ghysels, E., Hill, J. B., & Motegi, K. (2016). Simple Granger Causality Tests for Mixed Frequency Data. This paper presents Granger causality tests based on a dimension reduction technique for regression models, particularly useful for causality with a large time lag. DOI: 10.2139/ssrn.2616736

Fujita, A., Sato, J., Garay-Malpartida, H. M., Yamaguchi, R., Miyano, S., Sogayar, M., & Ferreira, C. (2007). Modeling gene expression regulatory networks with the sparse vector autoregressive model. The paper discusses the use of Granger causality to infer partial causalities in gene regulatory networks, effectively reducing the dimensionality of the model. DOI: 10.1186/1752-0509-1-39

Patil, S., & Pandya, S. (2021). Forecasting Dengue Hotspots Associated With Variation in Meteorological Parameters Using Regression and Time Series Models. Frontiers in Public Health. DOI: 10.3389/fpubh.2021.798034

Marigmen, J. L. D. C., & Addawe, R. (2022). Forecasting and on the Influence of Climatic Factors on Rising Dengue Incidence in Baguio City, Philippines. Journal of Computational and Theoretical Nanoscience. DOI: 10.32890/jcia2022.1.1.3

Olmoguez, I. L. G., Catindig, M. A. C., Amongos, M. F. L., & Lazan, F. G. (2019). Developing a Dengue Forecasting Model: A Case Study in Iligan City. International Journal of Advanced Computer Science and Applications. DOI: 10.14569/ijacsa.2019.0100936

Nascimento, D. V., Sousa, R. T., Silva, D. F. C., Pagotto, D. D. P., Coelho, C., & Filho, A. R. G. (2023). Live Birth Forecasting in Brazillian Health Regions with Tree-based Machine Learning Models. DOI: 10.1109/CBMS58004.2023.00197

Panda, S.K. and Mohanty, S. N. (2023). "Time Series Forecasting and Modeling of Food Demand Supply Chain Based on Regressors Analysis," in IEEE Access, vol. 11, pp. 42679-42700, 2023, doi: 10.1109/ACCESS.2023.3266275.

Tajmouati, S., Wahbi, B., Bedoui, A., Abarda, A. and Dakkon, M. (2021). Applying k-nearest neighbors to time series forecasting: two new approaches. https://doi.org/10.48550/arXiv.2103.14200
