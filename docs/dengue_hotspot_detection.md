# ---
title: "Dengue Hotspot Detection"
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
# Detecting Stagnant Water as Dengue Hotspots

Dengue fever, a mosquito-borne viral infection, poses significant public health risks, particularly in tropical and subtropical regions (Gubler, 1998). One of the primary breeding grounds for the Aedes aegypti mosquito, the vector for dengue, is stagnant water bodies. Traditional methods of identifying these hotspots often involve labor-intensive field surveys, which are not scalable and may lack temporal relevance. Remote sensing technologies offer a more efficient, scalable, and timely approach to identifying these critical areas (Wood et al., 2017). This paper outlines a comprehensive methodology for detecting stagnant water bodies as potential dengue hotspots using a threshold-based method applied on satellite images.

## Data Sources
The methodology employs NDVI for vegetation detection and NDWI for water body identification, both of which are widely recognized in the remote sensing community for their reliability.  Both are calculated from spectral data of Harmonized Landsat and Sentinel-2 satellite images.

The use of remote sensing indices like the Normalized Difference Water Index (NDWI) and the Normalized Difference Vegetation Index (NDVI) has gained prominence in environmental monitoring, particularly in the detection of surface water and vegetation cover. NDWI is highly effective in identifying water bodies, as it is sensitive to changes in liquid water content of leaves and can differentiate between water bodies and other land cover types [McFeeters (2013)].  This makes NDWI a reliable tool for detecting stagnant water, which is a potential breeding ground for mosquitoes.

Moreover, NDVI is traditionally used for vegetation monitoring but has also been employed to distinguish water bodies, especially in complex terrains [Olayemi et al. (2019)]. The combination of NDWI and NDVI can provide a more comprehensive understanding of the environmental conditions conducive to mosquito breeding. For instance, while NDWI can identify the presence of water, NDVI can help in understanding the vegetation around it, which can also be a factor in mosquito breeding [Chua (n.d.), Ligot and Toledo (2021)].

Stagnant water bodies are likely to exhibit less variance in spectral characteristics over time compared to flowing water bodies. Hence, temporal range is included as a parameter to understand the seasonality of these potential hotspots.

## Vegetation Classification and Water Detection
The methodology employs a three-tiered classification of vegetation—sparse, moderate, and dense—based on NDVI values. Specifically, each pixel of NDVI satellite images is classified into the three levels of vegetation using percentile-based thresholds (less than the 2nd percentile, between the 2nd and 98th percentile, and greater than the 98th percentile for sparse, moderate, and dense vegetation, respectively).  Within each category, water bodies are detected using the values of the pixels of NDWI images (greater than the 98th percentile).  This acknowledges that high-NDVI areas (dense vegetation) will have different NDWI characteristics than low-NDVI areas (sparse or no vegetation).  

## NDWI Variability and Stagnant Water Detection
To distinguish between transient and stagnant water bodies, a stagnancy duration is required to ensure that only water bodies that have been stagnant for a significant period are flagged as potential hotspots.  The methodology also includes the standard deviation of NDWI values across time as a criterion in detection.  High variability might suggest that a water body is more likely to be transient, such as a puddle that forms after a rain event and then dries up, whereas low variability might suggest that a water body is more likely to be stagnant.


# References
Gubler, D. J. (1998). Dengue and dengue hemorrhagic fever. Clinical microbiology reviews, 11(3), 480-496.

Wood, B. L., Beck, L. R., Washino, R. K., Palchick, S. M., & Sebesta, P. D. (2017). Spectral and spatial characterization of rice field mosquito habitat. International Journal of Remote Sensing, 18(1), 137-156.

McFeeters, S. K. (2013). Using the Normalized Difference Water Index (NDWI) within a Geographic Information System to Detect Swimming Pools for Mosquito Abatement: A Practical Approach. Remote Sensing, 5(7), 3544-3561. DOI: 10.3390/rs5073544

Olayemi, I. K., Ande, A. T., Danlami, G., & Abdullahi, U. (2019). An Assessment of Surface Water Detection Methods for Water Resource Management in the Nigerien Sahel. Sensors, 20(2), 431. DOI: 10.3390/s20020431

Chua, W. (n.d.). Project Still Water: A Free Workshop Aimed at Combating Dengue Using Satellite Data [PowerPoint slides].  https://github.com/docligot/aedesproject/blob/master/literature/Stagnant%20Water%20Maps%20from%20Satellite%20Infrared%20Data.pdf

Ligot, D.V., Toledo, M. (2021). Advanced Early Dengue Prediction and Exploration Service (AEDES). Academia Letters, Article 2956. https://doi.org/10.20935/AL2956 , Available at SSRN: https://ssrn.com/abstract=3902598 or http://dx.doi.org/10.2139/ssrn.3902598

