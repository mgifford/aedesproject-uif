# 2026 Season Review: What the Dashboard Showed and What Happened

- Review date: 2026-11-07
- Data as of: CDC NNDSS provisional counts through MMWR week 43 of 2026 (retrieved 2026-11-07); CDC ArboNET final counts through 2025 (retrieved 2026-11-06)
- Status: **draft, AI-assisted, not reviewed by an epidemiologist or vector ecologist**
- Reproduce: `git fetch origin gh-pages && python scripts/season_review.py --year 2026 --out docs/season-review-2026` (outputs are committed in [`docs/season-review-2026/`](season-review-2026/))

## Summary

1. **The dashboard did not make a projection that 2026 can test.** Its West Nile virus (WNV) risk index followed the 14-day mean temperature almost exactly (Pearson r = 0.975 over 170 days), so it would rise and fall in the same way every summer.
2. **Its in-season alert could not work.** It reported WNV as "LOW" on all 174 published days. The season file it read was last updated in May, so it compared zero recorded cases with a pace based on an incorrect baseline.
3. **2026 was a small, late WNV season.** Colorado reported 72 cases, 5 of them fatal (provisional), against a 2010 to 2025 median of 120. Most were reported in September and October.
4. **The warmest summer at the dashboard's weather point did not bring a large season.** Across 2010 to 2025, none of seven temperature or precipitation measures at that point was associated with annual neuroinvasive cases.
5. **For 2027 the data support a base rate, not a forecast.** In-season mosquito surveillance is the documented early signal in Colorado and is the most useful thing to add next.

There is no outcome data to test the tick-borne disease outputs against (section 3).

## 1. What the dashboard published

The values below were recovered from the daily deploys on the `gh-pages` branch: one deploy per day from 2026-05-18 to 2026-11-07, 174 days in all (see [`published_values.csv`](season-review-2026/published_values.csv)).

| Month | WNV index range | WNV label (days) | Tick index range |
|---|---|---|---|
| May | 0.18 to 0.22 | LOW (10) | 0.16 to 0.61 |
| June | 0.27 to 0.36 | MODERATE (23), LOW (7) | 0.15 to 0.44 |
| July | 0.43 to 0.49 | MODERATE (31) | 0.00 to 0.14 |
| August | 0.44 to 0.49 | MODERATE (31) | 0.00 to 0.03 |
| September | 0.31 to 0.39 | MODERATE (30) | 0.03 to 0.17 |
| October | 0.17 to 0.24 | LOW (31) | 0.19 to 0.45 |
| November (to 7th) | 0.16 to 0.17 | LOW (7) | 0.13 to 0.32 |

Notes:

- The index values were shown as percentages ("MODERATE (47.6%)") until 2026-11-05, when they were relabelled as an experimental index on a 0 to 1 scale. The numbers are the same.
- The tick index formula was rewritten on 2026-05-20; the May maximum of 0.61 is that single day.
- From 2026-05-21 to 2026-11-05 the tick index used 200 iNaturalist "tick" records a day that were in fact flies (wrong taxon ID; see issue #13 and the [scientific audit](SCIENTIFIC-AUDIT.md)).
- The season-monitoring notebook's WNV alert read "LOW" on every one of the 174 days.

## 2. What was reported

### West Nile virus

Colorado reported **72 WNV disease cases, 5 of them fatal**, according to both CDPHE's WNV data dashboard and CDC NNDSS provisional data (week 43). These counts include neuroinvasive and non-neuroinvasive disease and will rise somewhat as late reports arrive: in 2022 to 2025, between 2% and 8% of each season's cases were reported after week 43 (`share_reported_after_latest_week`).

Cumulative cases reported to CDC by MMWR week, as published at the time ([`summary.json`](season-review-2026/summary.json), `pace`):

| Week of report | 2022 | 2023 | 2024 | 2025 | 2026 | 2026 compared with 2022 to 2025 |
|---|---|---|---|---|---|---|
| 30 (late July) | 1 | 5 | 0 | 2 | 2 | within range |
| 34 (late August) | 28 | 101 | 0 | 74 | 14 | within range |
| 38 (mid-September) | 139 | 438 | 59 | 220 | 52 | below all four |
| 43 (late October) | 200 | 584 | 70 | 278 | 72 | within range (just above 2024) |

Colorado's 2024 count stayed at 0 until week 36 and rose to 59 by week 38, which suggests a batch of reports. That makes 2024 look artificially low at weeks 30 to 36 and widens the "range" in those weeks.

### Tick-borne diseases

There is no outcome data to compare the tick index with:

- CDC's NNDSS weekly data has no Colorado rows for Lyme disease or spotted fever rickettsiosis.
- Colorado tick fever is not nationally notifiable. CDC reports a national median of 7 cases a year (range 3 to 37) for 2003 to 2022, too few for any statistical comparison.
- Tularemia: 6 cases in 2026 to week 43, against 9 in all of 2025 (NNDSS). Tularemia has several routes of exposure besides ticks, so it is not a tick indicator on its own.

## 3. Comparing what was shown with what happened

**WNV index.** The index rose to MODERATE in June, peaked on 2026-07-29 (0.49) and fell through September. Reported cases came mostly in September and October. Because the index tracks temperature, this timing would look much the same in any year; it is the seasonal calendar, not a forecast.

On magnitude, the index points the wrong way. By the temperature measures that drive it, 2026 had the warmest summer at the dashboard's Denver point since 2010 (June to August mean 22.8 C) and by far the warmest winter (mean 2.0 C), yet reported cases were below the median. 2023, the largest season since 2003 (634 cases), had one of the coolest summers and the wettest summer in the period.

Across 2010 to 2025 (n = 16), none of these measures at the Denver point was associated with annual neuroinvasive cases (Spearman correlation; exploratory, no correction for multiple comparisons):

| Measure | rho | p |
|---|---|---|
| June to August mean temperature | -0.12 | 0.67 |
| July mean temperature | 0.17 | 0.52 |
| Highest 14-day mean temperature | 0.09 | 0.73 |
| Days with 14-day mean above 18 C (January to September) | -0.14 | 0.59 |
| Preceding winter mean temperature | 0.09 | 0.75 |
| March to May precipitation | 0.19 | 0.48 |
| June to August precipitation | 0.19 | 0.49 |

This does not show that temperature is unimportant for WNV. It shows that one modelled weather point near Denver does not explain year-to-year differences in Colorado's case counts, so an index built on it cannot either.

**In-season alert.** The alert's "expected" count assumed cases build up evenly through the year (week / 52 x median), when in Colorado 74% to 100% of each season's cases in 2022 to 2025 were reported after week 34, in late August (`share_reported_after_week_34`). Its WNV median was 12, taken from a hardcoded "2024 baseline" that was itself wrong. It also defaulted to LOW when there was no data.

**Simple baselines.** All of them overestimated 2026 (`baselines_vs_season`): last year's total (285), the 2010 to 2025 median (120), the mean (163) and the median of the last five years (206). This is consistent with the lack of year-to-year persistence described below.

**Tick index.** It was built partly on fly records, and it rose again in October and November. CDC states that most Colorado tick fever cases occur in spring or summer.

## 4. What the data support for 2027

**Reference expectation, not a forecast.** From CDC ArboNET, 2010 to 2025, Colorado's annual reported WNV cases had:

- a median of 120, with half of years between 80 and 183;
- a range of 7 (2011) to 634 (2023);
- 4 of 16 years above 200 (2013, 2022, 2023, 2025).

That is the reference this project will compare 2027 against: first with NNDSS provisional counts at the end of the 2027 season, then with the ArboNET final count when CDC publishes it.

**One season says little about the next.** For 2010 to 2025, the correlation between one year's total and the next is about zero (Spearman rho = -0.01, n = 15; an earlier calculation over 2004 to 2025 gave +0.08, n = 22). A small 2026 does not make 2027 small or large.

**Where the earlier signal is.** In northeastern Colorado, Bolling et al. (2009) found that the abundance of *Culex tarsalis* females was strongly associated with WNV case onsets 4 to 7 weeks later, and the vector index (abundance of infected females) with onsets 1 to 2 weeks later. That study covered 2006 and 2007, and 2007 was an intense season. The authors also recorded no WNV-infected *Culex* at sites above 1,600 m, roughly Denver's elevation. Mosquito trap and vector-index data from CDPHE and county programmes would give earlier and more local information than the climate index.

**Ticks.** Nothing in the data held by this project supports a 2027 statement for tick-borne disease.

## 5. What changed as a result

- The dashboard now fetches CDC NNDSS provisional weekly WNV counts and compares the current season with the same week in 2022 to 2025 (notebooks 06 and 08). Missing data is shown as "No in-season data", not as LOW. This comparison of reported counts is not a risk estimate; see section 11 of the [scientific audit](SCIENTIFIC-AUDIT.md).
- Earlier fixes (PR 1 and PR 2) corrected the iNaturalist taxon IDs, the historical WNV counts and the labels on the composite index.

Still to do before the 2027 season:

1. Find mosquito surveillance data (trap counts, pool results, vector index) from CDPHE or counties, and check the terms of use.
2. Reframe the WNV composite index as a temperature seasonality indicator, or retire it.
3. Ask CDPHE about tick submission records and county counts for Colorado tick fever and spotted fever.

## 6. Limitations

- Climate measures come from one NASA POWER point (latitude 39.74, longitude -104.99). These are modelled values, not station observations.
- The correlations use 16 years and seven measures, with no correction for multiple comparisons; they are exploratory.
- 2026 counts are provisional and by week of report, not week of illness onset.
- NNDSS weekly data starts in 2022, so only four earlier seasons are available for the in-season comparison, one of which (2024) shows batch reporting.
- The published values were recovered by reading text from rendered pages; days without a value are left blank, not filled in.
- CDPHE's dashboard was read only at the top level (case count and deaths). Its mosquito data was not available in a form this review could use.

## Sources

- CDC NNDSS Weekly Data, data.cdc.gov dataset x9gk-5huc: https://data.cdc.gov/NNDSS/NNDSS-Weekly-Data/x9gk-5huc (retrieved 2026-11-07)
- CDC West Nile virus historic data (ArboNET): https://www.cdc.gov/west-nile-virus/data-maps/historic-data.html (retrieved 2026-11-06; "All data are finalized as of September 16, 2026")
- CDPHE West Nile virus data: https://cdphe.colorado.gov/animal-related-diseases/west-nile-virus/west-nile-virus-data (CSV export of the embedded dashboard, retrieved 2026-11-07: 72 cases, 5 deaths)
- CDC, Data and Maps for Colorado Tick Fever: https://www.cdc.gov/colorado-tick-fever/data-maps/index.html
- Bolling BG, Barker CM, Moore CG, Pape WJ, Eisen L. Seasonal patterns for entomological measures of risk for exposure to Culex vectors and West Nile virus in relation to human disease cases in northeastern Colorado. J Med Entomol. 2009;46(6):1519-1531. doi:10.1603/033.046.0641. https://pmc.ncbi.nlm.nih.gov/articles/PMC2802831/
- NASA POWER daily point API: https://power.larc.nasa.gov/

## AI assistance

This review was drafted with Claude (Anthropic, model `claude-opus-5-5`) in Claude Code, under the direction of the repository maintainer. Every number comes from the committed outputs of `scripts/season_review.py` or from the sources listed above, except the CDPHE death count, the tularemia counts and the national Colorado tick fever figures, which were read from the cited pages. The interpretation has not been reviewed by a domain expert.
