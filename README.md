# Project AEDES: Exploring Transferable Disease Surveillance Methods

**An open-source research project examining whether approaches to vector-borne disease surveillance can be adapted across diseases, climates, and geographic regions.**

**Project status: Experimental research. Predictive models have not been validated for public-health use.**

[Explore the Colorado research dashboard](https://mgifford.github.io/aedesproject-uif/) | [Read the 2026 season review](https://mgifford.github.io/aedesproject-uif/2026-season-review.html) | [Scientific audit](docs/SCIENTIFIC-AUDIT.md) | [Original AEDES project](https://github.com/Cirrolytix/aedesproject-uif)

## Important: How to interpret the results

**This project is not a reliable disease-risk indicator, forecasting service, or public-health early-warning system.**

Any predictions, projections, composite risk indices, or estimates published here are experimental. They have not been demonstrated to predict disease outbreaks reliably.

**Any projections developed for the 2027 season are intended solely as hypotheses to be evaluated against actual 2027 surveillance results when those results become available.**

They must not be used to:

- Assess an individual's risk of infection.
- Make medical or clinical decisions.
- Determine whether an area is safe from vector-borne disease.
- Allocate public-health resources.
- Trigger or cancel vector-control interventions.
- Issue public-health warnings.
- Substitute for official disease surveillance or advice from public-health authorities.

A prediction may appear plausible because it follows seasonal temperature patterns. That does not mean it predicts disease incidence.

The purpose of publishing experimental projections is to make their assumptions visible, record what they predict *before outcomes are known*, and test whether they perform better than simple historical baselines.

A failed prediction is a useful research result. It must not be reinterpreted afterward as a successful forecast.

For official disease information in the United States, consult the [Centers for Disease Control and Prevention](https://www.cdc.gov/) and the relevant state or local public-health authority.

## What is Project AEDES?

Project AEDES began as the **Advanced Early Dengue Prediction and Exploration Service**, developed by [Cirrolytix Research Services](https://github.com/Cirrolytix/aedesproject-uif).

The original project explored combining dengue case records, climate observations, geospatial information, and other data sources to investigate dengue patterns in the Philippines.

This repository is an independent experimental fork of that work.

It investigates a related but different question:

**Can the software architecture, data collection methods, and analytical approaches developed for dengue surveillance be transferred to other vector-borne diseases and geographic regions?**

The initial adaptation focuses on Colorado, United States.

It examines West Nile virus, tick-borne diseases, and associated environmental and ecological observations.

The fork also considers broader One Health surveillance questions, including zoonotic diseases and wildlife health. These are related research interests but are not necessarily vector-borne diseases.

### Research objectives

The project aims to determine:

1. Which parts of the original AEDES architecture can be reused across regions.
2. Which data sources must be replaced or adapted for different public-health systems.
3. How climate, geography, vector species, and disease ecology affect the usefulness of collected signals.
4. Whether environmental and observational data provide useful information beyond established seasonal patterns.
5. What data quality and scientific validation are required before any predictive capability could be considered reliable.
6. How open-source, accessible, and reproducible reporting can help researchers evaluate these questions.

The objective is to understand what transfers successfully, what fails, and what additional evidence is needed.

It is not to assume that a dengue forecasting model developed for one region will work for another disease or location.

## From the Philippines to Colorado

### Original AEDES: Dengue surveillance in the Philippines

The original [Cirrolytix AEDES repository](https://github.com/Cirrolytix/aedesproject-uif) provides the foundation for this work.

Its architecture combines several forms of evidence:

- Historical disease surveillance data.
- Weather and climate observations.
- Satellite and geospatial datasets.
- Population and demographic information.
- Search-interest data.
- Statistical analysis and modelling.
- Geographic visualization and reporting.

These are potentially reusable technical methods.

However, successful data integration is not equivalent to demonstrated forecasting accuracy.

Claims about predictive performance require independent evaluation against observations that were not used to develop or tune the model.

The original project's documentation and historical research remain available through its upstream repository.

### Colorado: Testing whether the approach transfers

Colorado provides a substantially different research environment.

Its climate, geography, public-health infrastructure, and relevant vector species differ from those associated with dengue transmission in the Philippines.

The fork therefore concentrates initially on:

**West Nile virus:** A mosquito-borne disease with established seasonal transmission in Colorado.

**Tick-borne diseases:** Diseases involving locally relevant tick species, including Colorado tick fever and spotted fever rickettsioses.

**Lyme disease:** Primarily a travel-associated surveillance concern in Colorado. Reported cases among Colorado residents must not be interpreted as evidence of locally acquired transmission.

**Associated environmental signals:** Temperature, precipitation, vector observations, seasonality, and other available ecological information.

The project also contains research material concerning avian influenza and wildlife disease.

Avian influenza is not ordinarily classified as vector-borne. That work should be understood as a separate One Health research direction rather than part of the validated scope of the vector-borne surveillance experiment.

## Explore the Colorado research

The [Colorado dashboard](https://mgifford.github.io/aedesproject-uif/) brings together available surveillance and environmental observations.

It includes several notebooks and reports that illustrate different parts of the research.

| Research area | What it provides | Interpretation |
|---|---|---|
| Current-season West Nile virus monitoring | Reported cases compared with corresponding weeks in previous seasons | Descriptive surveillance comparison, not a forecast |
| Historical West Nile virus surveillance | CDC case histories and annual comparisons | Recorded disease burden, subject to source limitations |
| Tick observations | Community-science observations of ticks in Colorado | Opportunistic occurrence records, not population abundance or infection risk |
| Environmental monitoring | Temperature, precipitation, and other environmental variables | Contextual data, not direct evidence of disease transmission |
| Experimental composite indices | Calculated indicators combining environmental and other inputs | Unvalidated research measures |
| Climate-disease analysis | Exploratory associations and modelling demonstrations | Requires appropriate outcome data and scientific validation |
| Historical season reviews | Comparison of published indicators against later observations | Retrospective evaluation of model performance and limitations |

Some archived notebooks use synthetic or static demonstration data. Those outputs must not be interpreted as observed disease cases or validated projections.

The dashboard's purpose is to make the available evidence inspectable and support questions about the transferability of surveillance methods.

## What we learned from the 2026 season

The [2026 season review](docs/2026-SEASON-REVIEW.md) is an important part of the project.

It evaluates what the Colorado dashboard published during 2026 and compares those outputs with subsequently reported West Nile virus observations.

The review is AI-assisted and has not been reviewed by an epidemiologist or vector ecologist.

### The experimental risk index did not demonstrate predictive value

The earlier West Nile virus index closely followed seasonal temperature.

Its movement could largely be explained by changing temperature throughout the summer.

That did not establish a reliable relationship with the eventual number of reported cases.

The review found that environmental measurements from one location near Denver were insufficient to explain differences in disease burden across years.

### The original in-season alert failed

The dashboard's earlier in-season West Nile virus alert reported LOW throughout the evaluated period, even as cases accumulated.

Investigation identified problems in its underlying data and comparison methodology.

The alert was subsequently replaced with a comparison of provisional reported cases against equivalent reporting weeks in previous seasons.

This comparison provides descriptive context. It does not predict future disease burden.

### Data errors were discovered and corrected

The [scientific audit](docs/SCIENTIFIC-AUDIT.md) also identified significant data problems.

These included:

- Incorrect iNaturalist taxon identifiers, causing supposed tick observations to contain flies.
- Historical West Nile virus case values that did not match CDC records.
- Static data incorrectly presented as newly fetched.
- Unverified disease case tables.
- Experimental indices described using probabilistic terminology without statistical validation.
- Synthetic datasets presented without sufficiently prominent disclosure.

Several of these problems were corrected in subsequent pull requests.

Other limitations remain documented and unresolved.

The experience demonstrates why code tests, successful workflows, and visually convincing charts cannot substitute for validation of underlying scientific claims.

### What the review established

The 2026 evaluation did not establish a successful forecasting model.

It established a clearer understanding of the data, exposed incorrect assumptions, corrected important errors, and provided a basis for more disciplined experiments.

That is a legitimate research outcome.

[Read the 2026 season review and its supporting evidence](https://mgifford.github.io/aedesproject-uif/2026-season-review.html).

## The 2027 evaluation

**The next research objective is to evaluate explicitly documented hypotheses against the 2027 season.**

This is not a commitment to deliver an operational forecasting system in 2027.

It is a commitment to testing whether experimental approaches provide meaningful information when compared with subsequent observations.

### What may be evaluated

Potential research questions include:

- Can a seasonal environmental index distinguish a year with relatively high West Nile virus activity from one with relatively low activity?
- Do locally observed mosquito abundance or infection measures provide useful information earlier than human case reports?
- Do geographic differences in weather and ecology improve the interpretation of surveillance data?
- Does a model perform better than simply using historical seasonal averages?
- Can the approach identify when data are insufficient to make a meaningful projection?

These are hypotheses, not established capabilities.

### Establish expectations before observing the outcomes

Any proposed 2027 prediction must be recorded before the period it is intended to predict.

A reproducible evaluation should include:

1. The prediction or hypothesis and the date it was made.
2. The disease, geographic area, and time period.
3. The data available when the prediction was made.
4. The exact model version, parameters, and calculation.
5. The expected outcome or prediction interval, where scientifically justified.
6. A simple baseline against which the model will be compared.
7. The official data source that will be used to evaluate the result.
8. The method for handling reporting delays, revisions, and missing observations.

Predictions should be preserved as immutable historical records.

Later model changes must not silently rewrite previously published predictions.

### Historical reference ranges are not reliable forecasts

The 2026 season review calculated descriptive ranges from earlier Colorado West Nile virus seasons.

These provide context for assessing subsequent outcomes.

They do not establish that the next season will fall within a particular range, or that the model can anticipate whether a season will be unusually severe.

A historical median is a baseline. It is not, by itself, a validated disease prediction.

### Evaluate after the season

When the 2027 observations become available, the project should:

- Compare the original recorded expectations with actual reported outcomes.
- Document the dates and revisions of the surveillance data used.
- Calculate appropriate errors and uncertainty measures.
- Compare performance against simple historical and seasonal baselines.
- Identify cases where the model failed or where evidence was insufficient.
- Preserve the original predictions and the evaluation results.
- Document any changes proposed for subsequent experiments.

Provisional and final public-health surveillance data should be distinguished.

The project should not claim successful prediction based only on observations selected after the outcome is known.

### Scientific review

Any interpretation of model performance intended for broader public-health use requires review by appropriately qualified epidemiologists, vector ecologists, statisticians, and public-health specialists.

Until such review and independent validation occur, the models remain experimental.

**Even a successful comparison with one season would not establish a generally reliable disease indicator.**

## Data sources and their limitations

The Colorado implementation combines datasets with different scientific meanings and levels of reliability.

The [data source registry](config/data-sources.yaml) records source URLs, geographic and temporal coverage, observation types, freshness, verification status, and known limitations.

| Source | What it provides | Key limitation |
|---|---|---|
| [CDC ArboNET](https://www.cdc.gov/west-nile-virus/data-maps/historic-data.html) | Historical reported West Nile virus cases | Surveillance underreporting and differences between place of residence and exposure |
| [CDC NNDSS](https://data.cdc.gov/NNDSS/NNDSS-Weekly-Data/x9gk-5huc) | Provisional weekly West Nile virus reports | Reporting delays, revisions, and incomplete current-season data |
| [NASA POWER](https://power.larc.nasa.gov/) | Modelled climate and meteorological information | Current implementation uses a Denver-area point, not comprehensive statewide conditions |
| [Open-Meteo](https://open-meteo.com/) | Weather and environmental observations or model outputs | Spatial resolution and local ecological relevance vary |
| [iNaturalist](https://www.inaturalist.org/) | Community-science tick and mosquito occurrence records | Observations are affected by participation, sampling effort, identification quality, and geographic bias |
| Google Trends | Relative search interest for selected disease-related terms | Search interest is not disease incidence; availability can be unreliable |
| Historical Lyme case table | Static reference values currently retained in the repository | Original source remains unverified; not suitable for reliable epidemiological conclusions |

### Observations are not interchangeable

Human case reports, vector observations, environmental variables, and search trends measure different things.

For example:

- A tick observation does not establish that the tick carries a pathogen.
- The number of iNaturalist observations does not measure tick population density.
- Warmer temperatures do not automatically imply higher disease incidence.
- Search activity may reflect publicity rather than infections.
- Reported cases may not identify where exposure occurred.
- Missing data are not equivalent to zero cases.

A model combining these datasets must justify how each input relates to the outcome being studied.

The repository must distinguish **observed, modelled, derived, static, synthetic, experimental, and unverified** information.

### Data availability and reliability

The automated pipeline may continue producing a dashboard when individual data requests fail.

A successful dashboard build does not establish that all sources were successfully refreshed.

Readers should consult the source dates, reliability information, and documented limitations before interpreting any figures.

Static or stale data must not be represented as newly collected observations.

## Can AEDES be adapted to other regions?

This is the main research question behind the fork.

The original Philippine dengue implementation and the Colorado experiment provide different environments for investigating transferability.

### Potentially reusable components

Several parts of the architecture may be reusable:

- Modular data ingestion.
- Source provenance and validation.
- Historical case-data processing.
- Environmental data collection.
- Geographic analysis.
- Reproducible notebooks.
- Accessible charts, tables, and reports.
- Automated publishing through GitHub Actions.
- Retrospective evaluation of experimental models.

These are software and research methods. Their transferability does not depend on assuming that disease models themselves are transferable.

### Components requiring local adaptation

Each region may require different:

- Disease surveillance sources and case definitions.
- Vector species and relevant pathogens.
- Environmental variables.
- Seasonal assumptions.
- Geographic boundaries and spatial resolution.
- Reporting delays and data availability.
- Public-health institutions.
- Data access and reuse arrangements.
- Statistical models and validation datasets.

A method useful for dengue in the Philippines may not be useful for West Nile virus in Colorado.

Conversely, experience collecting and validating Colorado surveillance data may help improve the original Philippine implementation.

### Potential future contexts

Future research could investigate whether similar approaches are useful in:

- Other US states and Canadian provinces.
- Thailand and Indonesia.
- Other countries with dengue surveillance programmes.
- Regions where changing climate conditions may affect vector distributions.

These are possible future research directions, not active deployments or validated capabilities.

Any new regional implementation should begin by establishing local scientific relevance and identifying appropriate public-health data.

## Research principles

The project follows several principles intended to make experimental results useful and trustworthy.

### Reproducible evidence

Data sources, transformations, assumptions, and analytical methods should be documented sufficiently for independent review.

### Scientific uncertainty is explicit

Do not present experimental indices as probabilities, forecasts, or risk levels unless the statistical interpretation has been demonstrated and validated.

### No synthetic data presented as surveillance data

Synthetic or illustrative datasets must be clearly labelled in the visible report, not only in source code or collapsed notebook cells.

### Preserve unsuccessful results

Failed predictions, incorrect assumptions, and model limitations are part of the scientific record.

They should be documented rather than removed or reframed.

### Compare against simple baselines

A complex model should demonstrate useful performance beyond a seasonal average, historical median, or another appropriate baseline before claims of predictive improvement are made.

### Accessible and inspectable reports

Charts and maps should include meaningful explanations, source references, and accessible alternatives such as data tables.

### Responsible use of resources

Data collection and computational work should be proportional to the research value they provide.

Prefer existing public datasets, efficient processing, and reusable evidence over unnecessary repeated collection.

## Current implementation

The fork includes:

- Python data collection and analysis modules.
- Jupyter notebooks for surveillance and environmental analysis.
- A GitHub Pages dashboard.
- Scheduled GitHub Actions workflows.
- Data source reliability reporting.
- Automated tests.
- Scientific audit and historical season review documentation.

The Colorado dashboard is updated through scheduled workflows, with different frequencies for the active and quieter seasons.

Its continued publication should not be interpreted as an operational disease warning service.

### Running tests

Clone the repository:

```bash
git clone https://github.com/mgifford/aedesproject-uif.git
cd aedesproject-uif
```

Install the package and test dependencies:

```bash
python -m pip install -e . --no-deps
python -m pip install pytest pytest-cov pytest-mock
```

Run the standard tests, excluding the optional geospatial integration tests:

```bash
python -m pytest tests/ \
  --ignore=tests/test_geoboundaries.py \
  --ignore=tests/test_nasa_worldview.py \
  --ignore=tests/test_osm.py \
  -v
```

Some additional functionality requires optional geospatial and remote-data dependencies.

Passing software tests does not establish that scientific conclusions or experimental models are valid.

See [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md) for development guidance.

## Contributing

Contributions are welcome from developers, public-health researchers, epidemiologists, vector ecologists, statisticians, data scientists, and accessibility specialists.

Particularly useful contributions include:

- Reviewing scientific assumptions and disease-specific parameters.
- Identifying reliable surveillance datasets.
- Improving data provenance and reliability checks.
- Correcting misleading indicators or labels.
- Evaluating model performance against historical outcomes.
- Improving support for different geographic contexts.
- Testing accessible data visualizations.
- Separating reusable software from location-specific assumptions.
- Reviewing source licenses and data reuse requirements.
- Improving documentation of uncertainty and research limitations.

Scientific corrections and negative findings are as valuable as new features.

[Open an issue in this fork](https://github.com/mgifford/aedesproject-uif/issues).

## Upstream project and attribution

This repository is derived from the original AEDES project developed by Cirrolytix Research Services.

**Original project:** [Cirrolytix/aedesproject-uif](https://github.com/Cirrolytix/aedesproject-uif)

The original AEDES work focused on dengue surveillance in the Philippines.

This fork adapts and extends that foundation to investigate surveillance methods in Colorado and their potential transferability to other contexts.

The original contributors retain attribution for their work. Changes made in this fork should not be presented as accomplishments of the original project without appropriate evidence.

Where improvements are generally applicable, contributors are encouraged to consider whether they can also benefit the upstream project.

This repository does not represent an official public-health authority or a validated operational deployment of AEDES.

## Documentation

### Scientific evidence and evaluation

- [Scientific Audit](docs/SCIENTIFIC-AUDIT.md): Evidence review, data-quality problems, model limitations, and corrective work.
- [2026 Season Review](docs/2026-SEASON-REVIEW.md): Retrospective comparison of dashboard outputs with reported observations.
- [2026 Review Evidence](docs/season-review-2026/): Supporting datasets and reproducible calculations.
- [Data Source Registry](config/data-sources.yaml): Source provenance, reliability, licensing, and limitations.

### Disease and regional research

- [Colorado Adaptation](COLORADO_ADAPTATION.md): Research into adapting the AEDES framework to Colorado.
- [Tick-Borne Disease Surveillance](TICK.md): Tick species, associated diseases, ecology, and surveillance approaches.
- [Mosquito-Borne Disease Surveillance](MOSQUITO.md): Mosquito species, diseases, seasonal patterns, and possible monitoring methods.
- [Avian Influenza Surveillance](BIRD_FLU_SURVEILLANCE.md): Separate One Health and zoonotic surveillance research.

These research documents include proposed functionality and scientific assumptions that have not all been implemented or verified.

### Development and governance

- [Contributing](CONTRIBUTING.md).
- [Accessibility Guidelines](ACCESSIBILITY.md).
- [Project Charter](CHARTER.md).
- [Development Instructions](AGENTS.md).
- [Changelog](CHANGELOG.md).

Historical status reports elsewhere in the repository may describe earlier project plans and should not be treated as more authoritative than the current scientific audit and data source registry.

## Licensing

The software is distributed under the [MIT License](LICENSE), retaining the original Cirrolytix copyright and license notice.

Certain documentation and other materials are distributed under [Creative Commons Attribution-ShareAlike 4.0](CC%20BY-SA%204.0.md).

External datasets may have separate licensing and reuse conditions. Consult their original sources before redistributing data or incorporating it into another application.

## Research status and public-health disclaimer

**AEDES is experimental research software.**

Its current indicators and models have not been independently validated as reliable measures of present or future disease risk.

Any projections concerning 2027 are intended to test hypotheses against subsequently observed surveillance results. They are not dependable predictions of disease incidence, outbreak timing, or individual exposure.

Do not use this project to make medical, public-health, environmental management, or emergency-response decisions.

The project's value lies in transparent data collection, reproducible experimentation, recognition of uncertainty, and the willingness to evaluate and correct its own assumptions.
