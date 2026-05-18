[![codecov](https://codecov.io/gh/Cirrolytix/aedesproject-uif/graph/badge.svg?token=GL2XS3XT5W)](https://codecov.io/gh/Cirrolytix/aedesproject-uif)

[![Test Coverage](https://github.com/Cirrolytix/aedesproject-uif/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/Cirrolytix/aedesproject-uif/actions/workflows/test-coverage.yml)

# Project AEDES Unicef Innovation Repository

## What is AEDES?

**Advanced Early Dengue Prediction and Exploration Service (AEDES)** aims to achieve a sustainable future for humanity by **advancing innovations in risk management**. We strive to improve risk identification and mitigation through 4IR technologies such as big data, AI, robotics, and IoT. Through big data, we enhance root cause analysis, design, planning, and monitoring to achieve positive outcomes and minimize harms to humanity. Our mission is to **empower the public sector and non-profit organizations** with **multimodal, multidimensional dashboards** that inform sustainable risk interventions towards quantifiable impacts on society.

### Dengue Crisis in the Philippines

The dengue situation in the Philippines has been a persistent public health concern. In 2019, the country reported over 146,062 cases and 622 deaths due to dengue, making it the nation with the most number of dengue cases in Southeast Asia for that year [[Paris, J. (2019)]](https://www.rappler.com/nation/237340-philippines-has-most-dengue-cases-southeast-asia-2019/). In 2022, the situation escalated further with approximately 221,000 recorded cases, marking an 182% increase compared to the same period in the previous year [[Statista Research Department (2019)]](https://www.statista.com/statistics/1120319/philippines-number-dengue-cases/). As of July 15, 2023, the Philippines Department of Health (DOH) has reported a total of 80,318 dengue fever cases, with 14 of the 17 regions in the country experiencing an increase in cases over the past month [["Philippines dengue tally" (2023)]](https://outbreaknewstoday.com/philippines-dengue-tally-eclipses-80000-in-2023-to-date-92506/#:~:text=The%20Philippines%20Department%20of%20Health,cases%20over%20the%20past%20month.).

### Global Dengue Situation

In 2023, the global dengue situation is alarming. As of August 23, over 3.7 million cases and more than 2,000 dengue-related deaths have been reported from 70 countries/territories. The Americas are particularly hard-hit, with over 3 million new infections recorded so far. Countries like Brazil, Peru, and Bolivia are among the most affected, experiencing severe outbreaks that have strained their healthcare systems [["Dengue Worldwide Overview" (2023)]](https://www.ecdc.europa.eu/en/dengue-monthly).

### The Need for a Big Data Dengue Risk Surveillance Portal

The escalating numbers of dengue cases, both in the Philippines and globally, make a compelling case for the urgent need for a big data dengue risk surveillance portal. Such a system could offer advanced warnings of potential outbreaks to public health agencies and local governments, enabling them to allocate resources more effectively and implement targeted interventions.

### Our Solution

AEDES for Dengue is an automated information portal that correlates dengue cases and deaths with various non-traditional data, giving an advance indicator of when dengue will emerge and potential dengue hotspot locations.

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

## Documentation

For detailed information on how to use and leverage the full potential of aedesproject-uif please refer to the documentation available at:

https://cirrolytix.github.io/aedesproject-uif/ 📚

## Awards
Global Award for Best Use of Data, [2019 NASA Space Apps Challenge](https://2019.spaceappschallenge.org/challenges/living-our-world/smash-your-sdgs/teams/aedes-project/project)  
2020 Earth Observation for the Sustainable Development Goals (GEO SDG) Award, [Group on Earth Observations](https://www.earthobservations.org/geo_blog_obs.php?id=472)
Digital Public Good Status, [UNICEF Philippines, UNICEF Office of Global Innovation, and Digital Public Goods Alliance](https://digitalpublicgoods.net/blog/unicef-philippines-announces-its-first-digital-public-good-pathfinding-pilot/)
Highly Commended, Resilience, safety, resource quality & protection of life Category, [Geovation International Geospatial Innovation Awards 2023](https://geovation.uk/insights/introducing-our-award-winners/)

## Licenses

Project AEDES uses the following open licenses:

- [MIT License](https://github.com/Cirrolytix/aedesproject-uif/blob/main/MIT.md)  
- [Creative Commons Attribution Share Alike 4.0 International](https://github.com/Cirrolytix/aedesproject-uif/blob/main/CC%20BY-SA%204.0.md)

## About

Project AEDES is in active development and continously maintained by [**Cirrolytix Research Services**](https://cirrolytix.com/).  

#### Team Members:
- [Dominic Ligot](https://www.linkedin.com/in/docligot/), Founder and Chief Executive Officer
- [Emily Jo Vizmonte](https://www.linkedin.com/in/emily-jo-vizmonte-b7a09380/), Analytics Consultant
- [Claire Tayco](https://www.linkedin.com/in/claire-san-juan-tayco-81361828/), Managing Consultant and Chief Data Scientist
- [Cricket Soong](https://www.linkedin.com/in/cricketeer/), Chief of Operations

## Get Involved

Whether you're here to contribute to our Python package or to collaborate and use our web-based risk portal, we are excited to have you on board.

#### For Python Package Contributors

We are always on the lookout for enthusiastic developers to help us improve our Python package. Whether you are fixing bugs, adding new features, or improving documentation, your contributions are highly valued.

- **Getting Started:** Check out our [**Contributing Guidelines**](Contributing.md) to understand how you can start contributing.
- **Code of Conduct:** We believe in fostering an inclusive and welcoming environment. Please read our [**Code of Conduct**](CODE_OF_CONDUCT.md) to understand our community's values and expectations.

#### For App Collaborators

If you are here to use our risk portal and explore the visualizations, welcome! Our app is designed to provide actionable insights and we hope it serves your needs.

- **Getting Started:** Navigate to the app's main page and explore the various features and visualizations available.
- **Feedback:** Your feedback is invaluable. If you have suggestions, improvements, or find any issues, please raise them in the issues section.
- **Code of Conduct:** We aim to create a positive experience for all our users. Familiarize yourself with our [**Code of Conduct**](CODE_OF_CONDUCT.md) to understand the community's expectations.

If you have other questions or feedback, contact us via email at support@aedesproject.org.

#### Stay Connected

Follow our social media channels to stay updated with the latest information, news, and community discussions.

**Twitter:** [@aedes_ai](https://twitter.com/aedes_ai)
**Facebook:** [@aedesproject.org](https://web.facebook.com/aedesproject.org?_rdc=1&_rdr)
**LinkedIn:** [company/project-aedes](https://www.linkedin.com/company/30893221/admin/feed/posts/)

## Citation

If you use this software, please cite it using the following metadata.

#### APA:
```    
Ligot, D.V., Tayco, F.C., Soong, G.K., and Vizmonte, E.J.. aedesproject-uif (Version 4.0.0) [Computer software]
```

#### BibTeX:

```
@software{aedesproject-uif,
author = {Ligot, Dominic Vincent, Tayco, Frances Claire, Soong, Gabriel Kristopher, and Vizmonte, Emily Jo},
license = {MIT License},
month = {9},
title = {{aedesproject-uif}},
version = {4.0.0},
year = {2023}
}


```


©️ 2019-2023, [Cirrolytix Research Services](https://www.cirrolytix.com/)
