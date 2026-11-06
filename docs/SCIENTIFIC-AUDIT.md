# Scientific Audit: Colorado AEDES (Phase 0)

- Audit date: 2026-11-05
- Repository revision audited: `ed2d720` (branch `main`)
- Published site audited: https://mgifford.github.io/aedesproject-uif/ (generated 2026-11-05)
- Upstream: https://github.com/Cirrolytix/aedesproject-uif (no commits since 2023-10-09; this fork is 116 commits ahead)
- Status of this document: **draft, AI-assisted, not reviewed by an epidemiologist or vector ecologist.**
- Updated 2026-11-05 for PR 1 (correctness and labels) and 2026-11-06 for PR 2 (provenance). Sections 9 and 10 list what each changed.

## How this audit was done

This audit was drafted with Claude (Anthropic, model `claude-opus-5-5`) in Claude Code, working under the direction of the repository maintainer. Every factual claim below is either:

1. read directly from code or data in this repository (file and line given), or
2. checked against a named external source on the audit date (URL given), or
3. explicitly marked **unverified**.

No new citations were introduced without checking that they resolve. Scientific judgements (for example, whether an indicator is "unsupported") are the author's reading of the evidence and need expert review before they are treated as settled.

A passing test suite does not establish scientific validity. Every chart in the published site executes without error; several still publish incorrect or synthetic data.

---

## 1. Priority findings

Ranked by the harm a reader could suffer from trusting the published output.

### P0: published data that is wrong or not what it claims to be

| # | Finding | Evidence | Status in this branch |
|---|---|---|---|
| 1 | **"Tick observations" contain no ticks; "mosquito observations" query a fish genus.** The iNaturalist fetch used taxon `47822` (order Diptera, true flies) for ticks and `53522` (genus *Synbranchus*, swamp eels) for mosquitoes. All 200 cached "tick" records (2026-09-18 to 2026-11-01) are flies, mainly drone flies and hover flies. Mosquito results are always empty. These counts feed NB02, NB07 and the county table. This is the root cause of issue #13. | `scripts/fetch_surveillance_data.py` (before this branch); `data/surveillance/inaturalist_ticks_colorado.json`; `https://api.inaturalist.org/v1/taxa/47822` returns Diptera, `/53522` returns *Synbranchus*, `/51672` returns Ixodida, `/52134` returns Culicidae | **Fixed in code** (constants `INAT_TAXON_TICKS = 51672`, `INAT_TAXON_MOSQUITOES = 52134`, with regression tests). Cached data is corrected by the next scheduled fetch. |
| 2 | **Colorado West Nile virus counts are wrong for every year 2010 to 2024.** `fetch_cdc_wonder_wnv()` does not fetch anything; it writes a hardcoded table and stamps it `"fetched": TODAY`. Compared with CDC ArboNET state data, the hardcoded neuroinvasive counts differ in all 15 years. The largest error is 2023: the repo shows 6 neuroinvasive cases and 0 deaths; CDC reports 316 neuroinvasive and 634 total cases, Colorado's largest season since 2003. CDC also already publishes 2025 (143 neuroinvasive, 285 total). | `scripts/fetch_surveillance_data.py` `fetch_cdc_wonder_wnv()`; CDC file `https://www.cdc.gov/wcms/vizdata/live/ncezid_dvbd/WNV/wnv_hum_historic - Historic Sta.csv` (from https://www.cdc.gov/west-nile-virus/data-maps/historic-data.html). Comparison table in Appendix A. | **Fixed in PR 2**: fetched from the CDC ArboNET state file with source URL, retrieval date and latest year recorded; 2010 to 2025 now match CDC. |
| 3 | **NB05 "Climate Change Impact Analysis" is built entirely on random synthetic data, but the published page names NOAA and CDC as its data sources.** Climate and case series come from `generate_synthetic_climate_data()` and `generate_synthetic_disease_data()` (`np.random`). The word "synthetic" appears only in collapsed code, not in any visible text on the published page. | `notebooks/05_climate_change_impact_analysis.ipynb` cell 6; published page `notebooks/05_climate_change_impact_analysis.html` (visible text checked on 2026-11-05) | Visible "SYNTHETIC DATA: demonstration only" notice added and data-source list corrected. Unpublishing still needs a maintainer decision. |
| 4 | **NB04 "Climate-Disease Correlation" trains its forecasting model on synthetic case counts.** WNV weekly cases are generated with `np.random.poisson` from the same climate features the model then "predicts". Climate data also falls back silently to random values if the real file is missing. Any reported accuracy is circular. | `notebooks/04_climate_disease_correlation.ipynb` cells 7 and 13 | Visible synthetic-data notice added and data-source list corrected. Unpublishing still needs a maintainer decision. |
| 5 | **NB09 "Model Validation" does not validate anything yet.** Correction to the first draft of this audit: the live page does not show the 426 and 455 totals as "2026 YTD". Those figures (sums of the hardcoded 2010 to 2024 WNV and 2015 to 2024 Lyme tables) appear only in the stale committed file `notebooks/nb09_validation_report.json`, dated 2026-05-20. The live page labels both baselines "2010-2025" although the data cover 2010 to 2024 and 2015 to 2024, and its module output is `integrated risk=nan`. | `notebooks/09_model_validation_report.ipynb` cells 5 and 9; published `09_model_validation_report.html` (checked 2026-11-05); `notebooks/nb09_validation_report.json` | Year ranges fixed (computed from the data); experimental banner added. `nan` output and stale JSON not changed. |
| 6 | **The reliability report certifies hardcoded data as fresh.** `cdc_wnv` and `cdc_lyme` are reported `ok / fresh_data` every day because the static tables are re-stamped with today's date. `regional_counties_2026.json` gets `fetched: TODAY` daily although its case columns are seed values. The report's own `run_mode` is `blocked` (regional file fails schema), yet the site publishes anyway. | `scripts/fetch_surveillance_data.py` `update_regional_data()`, `generate_reliability_report()`; `data/surveillance/reliability_report.json`; dashboard "Pipeline Reliability Status" | **Fixed in PR 2**: static tables are reported as `static`, sources not updated in a run as `stale`, and the Lyme and county files are no longer re-stamped. The report still does not stop publication. |

### P1: misleading interpretation

| # | Finding | Evidence |
|---|---|---|
| 7 | **"Probabilistic risk" outputs are not probabilities.** `ProbabilisticRiskScorer` combines habitat scores with fixed weights (0.7/0.3, 0.6/0.4, then 0.2/0.3/0.3/0.2). It assumes a default 50% "prior probability of pathogen in vector population". Its "confidence intervals" are a fixed fraction of `1 - p`, not a statistical interval. Vector presence enters the integrated score twice (directly and through transmission). None of the coefficients has a cited source or a fit to data. Categories LOW/MODERATE/HIGH use cut-points 0.3 and 0.7 with no stated basis. | `src/aedesproject_uif/surveillance/risk_scorer.py` lines 55 to 316 |
| 8 | **Lyme disease vector stated as *Ixodes scapularis* for Colorado** in the README and in the dashboard "Quick Reference" table. NB02 cell 15 lists Lyme with *I. scapularis* and *I. pacificus* as "Colorado-relevant". The registry says local risk is "via *I. pacificus* (western slope, rare)". Elsewhere the code says, correctly, that *I. scapularis* is not established in Colorado. No evidence is cited for *I. pacificus* in Colorado. CDPHE's tick-borne illness page names American dog ticks, Rocky Mountain wood ticks and brown dog ticks as the ticks found in Colorado. | `README.md`; published index "Colorado Vector-Borne Disease Quick Reference"; `notebooks/02_...ipynb` cell 15; `src/aedesproject_uif/surveillance/registry.py` line 184; https://cdphe.colorado.gov/child-care-school-settings/tick-borne |
| 9 | **Lyme counts are unverified and not comparable across 2022.** The hardcoded series rises almost every year (35 to 65 confirmed). The README separately says "2023: 42 reported cases", which contradicts the script (61 confirmed plus 49 probable). The national Lyme surveillance case definition changed in 2022, so a single 2015 to 2024 trend line mixes definitions. **Unverified**: CDC's Lyme surveillance page did not expose state-level data in a machine-readable form during this audit. | `scripts/fetch_surveillance_data.py` `fetch_cdc_wonder_lyme()`; `README.md` |
| 10 | **"Automatically updated daily using CDC surveillance data" is not true.** No CDC endpoint is queried. `ingest_cdc_provisional.py --fetch` is a stub that always returns `None`. `2026_season_ytd.json` holds two rows, last dated 2026-05-18, with `next_update: 2026-05-25`. The "2026 Season Monitoring" report is therefore six months stale. The dashboard also says 2024 is the most recent finalized year, but CDC publishes 2025 WNV data. | `scripts/ingest_cdc_provisional.py` lines 87 to 111; `data/surveillance/2026_season_ytd.json`; published index text |
| 11 | **Notebooks count table rows as cases.** `len(df)` counts records, not the case column. Found in NB01 (WNV and Lyme YTD, which also feed the composite index), NB02 (Lyme YTD and prior year) and NB03 (YTD for every disease). **Fixed in PR 1**: the case column is summed, and NB01 says when the source has no current-year records instead of showing a bare 0. | `notebooks/01_...ipynb` cell 6; `02_...ipynb` cell 3; `03_...ipynb` cell 4 |
| 12 | **iNaturalist counts are truncated and mis-geocoded.** Requests use `per_page=200` with no pagination, so `count` is "first 200", not a total. County is parsed from free-text `place_guess` (for example "Colorado, US", "S Race St, Denver, CO, US"), so many records cannot be assigned to a county or are assigned wrongly. Observation counts are opportunistic, effort-biased presence records, not abundance. | `scripts/fetch_surveillance_data.py` `fetch_inaturalist_*`, `update_regional_data()` |
| 13 | **"Hotspot" and "high-risk county" labels** in NB07 come from a static list of counties and from county case counts that are seed values. No spatial statistic is computed. | `notebooks/07_regional_tracking.ipynb` cells 2, 19 |
| 14 | **A single Denver point stands in for "Colorado" climate.** NASA POWER and Open-Meteo are queried at one coordinate (about 39.74 N, 104.99 W). Colorado spans more than 3,000 m of elevation; Denver conditions do not represent the Western Slope or the mountains where *Dermacentor andersoni* is active. | `scripts/fetch_surveillance_data.py` `fetch_nasa_power_colorado()`, `fetch_open_meteo_colorado()` |

### P2: documentation, governance, accessibility

| # | Finding | Evidence |
|---|---|---|
| 15 | Root directory holds about 20 overlapping status and summary documents (`FINAL_REPORT.md`, `REVIEW_SUMMARY.md`, `DEPLOYMENT_STATUS.md`, `VALIDATION_CHECKLIST.md`, `COLORADO_COMPLETE.md`, and more). Several state completion or validation that the code does not support. | repository root |
| 16 | `AGENTS.md` says the pipeline fetches "CDC WNV/Lyme data (annual summaries from CDC NNDSS + weekly YTD provisional)" and that "60/60 tests" pass. The first is not true (see 2 and 10). | `AGENTS.md` |
| 17 | README badges and the documentation link point at the upstream Cirrolytix repository. The relative `Contributing.md` link was broken (the file is `CONTRIBUTING.md`; **fixed in PR 1**). Correction to the first draft: the `MIT.md` link is absolute and resolves on upstream, where that file exists. | `README.md` |
| 18 | Dashboard footer cites "Ligot & Toledo (2021). Academia Letters, Article 2956". **Unverified**: a web search on 2026-11-05 did not find it. The README's own citation block lists different authors. | published index footer |
| 19 | Five files under `.venv/` are committed (interpreter symlinks and `pyvenv.cfg`); `.venv` is not in `.gitignore`. The committed venv has no packages, so it cannot run the tests. | `git ls-files .venv` |
| 20 | Dashboard index accessibility (axe-core 4.10.2, WCAG 2.0/2.1/2.2 A and AA plus best practice): 15 `color-contrast` failures (serious), `landmark-one-main` (no `<main>`), and 6 `region` violations. Decorative emoji are used as headings and icons. Not tested: notebook pages, keyboard flow, screen reader output, zoom and reflow, forced colours. | run in browser on https://mgifford.github.io/aedesproject-uif/ |
| 21 | The quick-reference table puts reservoirs and exposures in the "Vector" column (for example deer mouse for hantavirus). Its case-fatality and reportability figures are uncited. **Unverified.** | published index |

### Upstream site (https://www.aedesproject.org/)

Out of scope for code changes here, but relevant to upstream contribution:

- Content has not been updated since 2021 (footer "2019-2021").
- It claims "For every single day we can reduce the lag in response time we save: 5 lives, 1,130 cases" without a method or source.
- It states "We are able to accurately model dengue cases" with no published validation linked.
- Its 2019 Philippine dengue figures (271,000 cases, 1,100 deaths) differ from this repository's README (146,062 cases, 622 deaths). **Unverified**: neither figure was checked against Philippine Department of Health data.
- Accessibility, from DOM inspection only (axe not run on the third-party site): no `lang` attribute, all 9 images lack an `alt` attribute, no `h1`, the carousel repeats the same `h2` four times, and there is no `main` landmark.

---

## 2. Inventory of data sources

| Source (as named in repo) | What the code actually does | Real fetch? | Observation type | Notes |
|---|---|---|---|---|
| CDC ArboNET WNV (`wnv_colorado.json`) | Downloads and validates the CDC state-level CSV (PR 2; previously a hardcoded table) | Yes | Human reported cases by state of residence | No state-level deaths in the file (recorded as null). |
| Lyme table (`lyme_colorado.json`) | Writes a static 2015 to 2024 table, marked `static` (PR 2) | No | Human reported cases (claimed) | Unverified; case definition changed in 2022. |
| CDC provisional weekly (`2026_season_ytd.json`) | Stub; manual `workflow_dispatch` inputs only | No | Human provisional cases | Two rows, last 2026-05-18. |
| County seed file (`regional_counties_2026.json`) | Seed file marked `static`; only iNaturalist counts are updated (PR 2) | No (cases) | Human cases by county (claimed) | Case columns are seed values of undocumented origin. |
| NASA POWER daily, 90 days | Live API at Denver point; filters `-999` sentinels | Yes | Modelled (reanalysis-based) | Single point. |
| Open-Meteo, 30 days | Live API at Denver point | Yes | Modelled forecast and reanalysis | Single point. |
| Google Trends, Colorado | `pytrends`; currently failing | Attempted | Search interest index | `degraded` in every recent report. |
| iNaturalist ticks | Live API, research grade, CO bounding box | Yes, wrong taxon until this branch | Opportunistic presence | First 200 only. |
| iNaturalist mosquitoes | Live API, research grade | Yes, wrong taxon until this branch | Opportunistic presence | Always empty until this branch. |
| `data_loader.load_mosquito_pool_data`, `load_tick_surveillance_data`, `load_usgs_ecological_data` | Look for local files that do not exist; return empty frames | No | Pool testing, tick drags, USGS | Code paths exist with no data behind them. |
| Philippine dengue, NASA, OSM, INFORM data under `data/` | Upstream historical files | n/a | Mixed | Upstream functionality; not audited here. |

## 3. Inventory of models and indicators

Status values: Observed, Derived, Modelled, Experimental, Unsupported, Synthetic.

| Indicator (as shown) | Where | Actual calculation | Source | Time / space | Evidence cited | Validation | Status | Action |
|---|---|---|---|---|---|---|---|---|
| WNV annual neuroinvasive cases | NB01, NB06, NB08, NB09 | CDC ArboNET state file (PR 2) | CDC ArboNET | Annual / state of residence | n/a | Values checked against CDC on 2026-11-06 | Observed | Keep; deaths shown as not published |
| Lyme confirmed and probable | NB02, NB08, NB09 | Hardcoded table | Unverified | Annual / state | None | None | Unsupported (unverified) | Verify; split at 2022; label as residence, not exposure |
| 2026 season weekly counts | NB06 | Two manual rows | Manual entry | Weekly / state | None | None | Stale | Show last observation date; stop calling it live |
| County cases and "hotspots" | NB07 | Seed values plus static hotspot list | Seed file | YTD / county | None | None | Unsupported | Remove "hotspot" wording until a method exists |
| Tick observations | NB02, NB07 | Count of iNaturalist records | iNaturalist | 365 days / point | n/a | n/a | Observed (after fix); was invalid | Label as opportunistic presence, show species, paginate |
| Mosquito observations | NB01, NB07 | As above | iNaturalist | As above | n/a | n/a | Observed (after fix); was always empty | As above; distinguish *Culex tarsalis* and *Cx. pipiens* |
| 90-day temperature and precipitation | NB01, NB04 | Daily values at one point | NASA POWER | Daily / point | n/a | n/a | Observed (modelled reanalysis) | Rename to "Denver area"; add regional points |
| GDD and tick activity multiplier | NB02 | GDD with base 10 C, scaled to a multiplier | Open-Meteo | Daily / point | None cited | None | Experimental | Cite thresholds or label as illustrative |
| Vector presence "probability" | `risk_scorer.py`, NB01 to NB03 | `0.7*habitat + 0.3*min(conf, 0.9)` | Derived | n/a | None | None | Unsupported as probability | Rename to experimental index; document formula |
| Transmission "probability" | as above | `vector * 0.5`, then blended with case flag | Derived | n/a | None (50% prior is arbitrary) | None | Unsupported | As above |
| Integrated risk score and LOW/MODERATE/HIGH | NB01 to NB03, NB08 | Weighted sum 0.2/0.3/0.3/0.2, cut at 0.3/0.7 | Derived | n/a | None | None | Unsupported | Relabel as "experimental composite index (not validated)" |
| "Uncertainty bands" | as above | `p plus or minus k*(1-p)` | Derived | n/a | None | None | Unsupported | Remove interval wording or replace with real uncertainty |
| Climate-to-cases forecast | NB04 | Model trained on synthetic Poisson cases | Synthetic | Weekly | None | Circular | Synthetic | Label as demonstration or unpublish |
| Climate change impact | NB05 | All inputs random | Synthetic | Daily | None | None | Synthetic | Label as demonstration or unpublish |
| Model validation | NB09 | Baselines against mislabelled totals | Hardcoded | Annual | n/a | Invalid | Unsupported | Fix inputs; use rolling-origin evaluation |
| Pipeline reliability | index | File presence, schema keys, static flag and retrieval date; reports latest observation (PR 2) | Pipeline | Daily | n/a | n/a | Software check only | Add a publication gate |

The table covers the headline indicators. Chart-by-chart entries for NB01, NB02, NB03, NB06 to NB08 still need to be completed. Several charts reuse the indicators above.

## 4. Restricted terms found in published output

The terms below appear in the published notebooks. None is backed by a validated model in this repository.

| Term | Notebooks | Supported? |
|---|---|---|
| "probability", "probabilistic risk" | 01, 02, 03, 08, 09 | No (see finding 7) |
| "early warning" | 01, 02, 04, 05, 06 | No validated lead time |
| "forecast", "predict" | 01, 02, 03, 04, 05, 06, 09 | NB04 and NB05 are synthetic |
| "outbreak" | 01, 02, 04, 08, 09 | No outbreak definition or threshold |
| "hotspot", "high-risk county" | 01, 02, 07 | No spatial method |
| "expansion", "climate-driven" | 01, 02, 04 | No long-term trend or distribution analysis |

## 5. Tests and CI assessment

- `Tests` workflow runs pytest on push and pull request with Python 3.11. It last ran 2026-05-25. Locally on this branch: 184 passed, 11 skipped (AGENTS.md still says 60/60). Daily data commits use `[skip ci]`, so data changes are never tested.
- The tests check file structure, schema keys and fallback behaviour. No test checks that a fetched record is the taxon requested, that a value matches its stated source, or that a published page contains no synthetic data. That is why findings 1 to 6 passed CI.
- `Constitution Policy Check` checks PR body text only. Its one run failed.
- `Surveillance Dashboard` publishes even when the reliability report says `blocked`.
- `tests/test_notebooks.py` has an `integration` marker for executing notebooks; CI does not run it.

## 6. Prioritized implementation plan

Each step is a separate, reviewable PR, following the brief's PR strategy.

1. **PR 1, correctness and labels (small):** taxon ID fix (done on this branch), NB09 mislabel, NB01 row count, *Ixodes* statements in README, NB02 and the quick reference, and visible "SYNTHETIC DATA: demonstration only" banners on NB04 and NB05 (or unpublishing them, if the maintainer prefers). Relabel "probability" and "risk" outputs as "experimental index, not validated".
2. **PR 2, provenance:** replace hardcoded WNV with the CDC ArboNET state CSV, including source URL and retrieval time. Separate `retrieved_at` from `latest_observation`. Stop re-stamping static files. Add `config/data-sources.yaml`. Make the reliability report distinguish "static", "fresh" and "stale".
3. **PR 3, disease boundaries:** `config/diseases/` for WNV, CTF, RMSF, tularemia, TBRF and Lyme (as travel-associated), each with vectors and references verified by a domain expert.
4. **PR 4, validation:** rolling-origin evaluation of seasonal and persistence baselines on corrected CDC data, before any model is called predictive.
5. **PR 5, accessibility:** fix the axe findings on the index, then audit the notebook pages.
6. **PR 6 and 7:** climate trend work and upstream extraction, per the brief.

## 7. Safe to change now

These changes correct facts or labels without removing functionality:

- iNaturalist taxon IDs (done on this branch).
- NB09 "2026 YTD" label and NB01 `len()` bug.
- README, NB02 cell 15 and quick-reference vector statements for Lyme.
- Visible synthetic-data banners on NB04 and NB05.
- README broken links (`Contributing.md`, `MIT.md`).
- Add `.venv/` to `.gitignore` and untrack the committed venv files.

These need a maintainer decision because they remove or replace published output:

- Unpublishing NB04 and NB05.
- Removing or renaming the integrated risk score and its categories.
- Replacing the hardcoded WNV and Lyme tables (this changes every historical chart).

## 8. Questions that need scientific expertise or external evidence

1. Is there any documented established population of *Ixodes scapularis* or *I. pacificus* in Colorado (for example in CDC tick surveillance county records)? If not, should Lyme stay on the Colorado dashboard only as a travel-associated indicator?
2. Which Colorado sources publish mosquito trap counts and WNV-positive pools by county or district? Under what licence can they be redistributed? CDPHE and some local districts publish weekly WNV mosquito surveillance during the season; the format and terms need checking.
3. For Colorado tick fever and RMSF, what is the defensible environmental signal? *D. andersoni* is reported at 4,000 to 10,000 feet (CDC); a single Denver weather point cannot represent that range.
4. Should rodent-borne and flea-borne conditions (hantavirus, plague) remain in a "vector-borne" dashboard, and if so under what framing?
5. Which case-fatality and reportability figures in the quick reference are correct, and from which source?
6. Is the composite risk index worth keeping as a documented experimental index, or should it be retired until there is data to fit it?
7. What is the source for "Ligot & Toledo (2021)"?

---

## Appendix A: Colorado WNV, repository versus CDC ArboNET

Source: CDC, "Historic Data (1999-2025)", state-level CSV used by https://www.cdc.gov/west-nile-virus/data-maps/historic-data.html, retrieved 2026-11-05. Repository values from `data/surveillance/wnv_colorado.json` (`neuroinvasive` field).

| Year | Repo neuroinvasive | CDC neuroinvasive | CDC all cases |
|---|---|---|---|
| 2010 | 51 | 26 | 81 |
| 2011 | 20 | 2 | 7 |
| 2012 | 130 | 62 | 131 |
| 2013 | 14 | 90 | 322 |
| 2014 | 43 | 46 | 118 |
| 2015 | 72 | 57 | 101 |
| 2016 | 14 | 59 | 149 |
| 2017 | 5 | 29 | 68 |
| 2018 | 15 | 52 | 96 |
| 2019 | 10 | 52 | 122 |
| 2020 | 10 | 17 | 35 |
| 2021 | 8 | 101 | 175 |
| 2022 | 16 | 131 | 206 |
| 2023 | 6 | 316 | 634 |
| 2024 | 12 | 40 | 77 |
| 2025 | (not present) | 143 | 285 |

ArboNET counts are reported by state of residence and may be revised. They undercount true infections, especially non-neuroinvasive ones.

## Appendix B: Sources consulted

- iNaturalist taxa API: https://api.inaturalist.org/v1/taxa/47822, /53522, /51672, /52134
- CDC West Nile virus historic data: https://www.cdc.gov/west-nile-virus/data-maps/historic-data.html
- CDPHE tick-borne illness: https://cdphe.colorado.gov/child-care-school-settings/tick-borne
- CDC Colorado tick fever, causes and spread: https://www.cdc.gov/colorado-tick-fever/causes-and-spread/index.html
- CDC Tickborne Diseases of the United States (2025 manual): https://www.cdc.gov/ticks/media/pdfs/2025/03/tickborne-diseases-manual-508.pdf
- Project AEDES site: https://www.aedesproject.org/

## 9. PR 1 changes (correctness and labels)

What PR 1 changed, and why. Nothing was removed from the published site; NB04 and NB05 are still published, now with a visible notice.

| Change | Files | Why |
|---|---|---|
| iNaturalist taxon IDs corrected to Ixodida (51672) and Culicidae (52134), with regression tests | `scripts/fetch_surveillance_data.py`, `tests/test_scripts.py` | Finding 1, issue #13 |
| "SYNTHETIC DATA: demonstration only" notice in the first cell; data-source lists corrected | NB04, NB05 | Findings 3 and 4 |
| "Experimental index, not validated" notice in the first cell, with links to CDPHE and CDC guidance | NB01, NB02, NB03, NB08, NB09 | Finding 7 |
| Index values printed on a 0 to 1 scale instead of as percentages; "95% CI" relabelled as a fixed-formula band; chart titles and axis labels say "experimental index, not a probability"; method sections marked as planned | NB01, NB02, NB03, NB08 | Finding 7 |
| Case counts summed instead of counting rows | NB01, NB02, NB03 | Finding 11 |
| Baseline year ranges computed from the data | NB09 | Finding 5 |
| Lyme described as travel-associated; *Ixodes* vectors not documented as established in Colorado; RMSF vector corrected to *Dermacentor*; Colorado tick fever added | `README.md`, NB02, dashboard quick reference | Finding 8 |
| WNV 2023 figure in README corrected to CDC ArboNET (634 cases, 316 neuroinvasive) | `README.md` | Finding 2 |
| Colorado tick fever elevation corrected from "1,200 to 1,400 m" to about 1,200 to 3,000 m (4,000 to 10,000 ft), per CDC | NB02 | CDC Colorado tick fever page |
| Dashboard "About" text no longer says CDC data is fetched daily; card descriptions drop "real-time", "early warning" and "hotspot"; the provisional-count note says counts are entered manually | `scripts/generate_dashboard.py` | Findings 10 and 13 |
| "Dashboard Features" in the README marked as planned | `README.md` | Finding 10 |
| AGENTS.md pipeline description and test-count claim corrected | `AGENTS.md` | Finding 16 |
| Guard tests: a notebook that generates synthetic data, or shows the composite index, must carry the matching notice in its first cell | `tests/test_notebooks.py` | Prevents findings 3, 4 and 7 from recurring |

### Not changed in PR 1

- The hardcoded WNV and Lyme tables (finding 2): replacing them changes every historical chart; this is PR 2.
- The composite index formula and its LOW/MODERATE/HIGH cut-points: only the labels changed.
- `registry.py` still says local Lyme risk is "via *I. pacificus* (western slope, rare)"; this needs a source or removal (PR 3).
- The footer citation "Ligot & Toledo (2021)" is unverified and left as is (question 7).
- Dashboard accessibility: on a local build, axe-core 4.10.2 reports the same rule types as the live site (`color-contrast`, `landmark-one-main`, `region`). The contrast failures are in existing styles (`.meta` text `#718096` on white, 4.01:1; footer link 3.73:1), not in text PR 1 added.

### New findings from the PR 1 pass

- NB08 draws its "Moderate" and "High" lines at 0.25 and 0.60, while `categorize_risk()` uses 0.3 and 0.7, so a chart and its category label can disagree.
- NB02 sets the transmission component to 0.45 next to a comment saying the Colorado tick fever infection rate in *D. andersoni* is "~14%"; neither value is sourced.
- CDPHE runs a "Submit a tick" programme (linked from its tick-borne diseases page), a candidate source of verified tick records for PR 3 and Phase 4.
- Running the notebook integration tests (`pytest -m integration`, or any run where `nbclient` is installed) executes the notebooks in `notebooks/` and overwrites tracked outputs there and under `processed/`, and creates `_site/`. CI is unaffected, but local runs dirty the working tree.

### Verification for PR 1

- `pytest tests/ --ignore=tests/test_geoboundaries.py --ignore=tests/test_nasa_worldview.py --ignore=tests/test_osm.py`: 216 passed, including the 11 notebook-execution integration tests.
- The new disclosure tests fail on the `main` versions of NB01 to NB05, NB08 and NB09 and pass on this branch.
- All seven edited notebooks executed with `jupyter nbconvert --execute` in an isolated copy; the rendered HTML shows the new notices and labels.
- Live iNaturalist queries with the corrected IDs for the past year in the Colorado bounding box return 7 tick records (*Dermacentor andersoni*, *D. variabilis*) and 7 mosquito records (including *Culex tarsalis*).
- Not verified: screen-reader output, keyboard flow, zoom and reflow on the notebook pages; the matplotlib chart images in NB03 were not inspected visually.

## 10. PR 2 changes (data provenance)

| Change | Files | Why |
|---|---|---|
| West Nile virus counts fetched from the CDC ArboNET state-level CSV, validated (expected columns, complete years, neuroinvasive not above total, no negative counts) and saved with source URL, documentation page, retrieval time and latest year | `scripts/fetch_surveillance_data.py`, `data/surveillance/wnv_colorado.json` | Finding 2 |
| If the CDC download or validation fails, the previous file is kept and reported as `stale`; no built-in numbers are substituted | `scripts/fetch_surveillance_data.py` | Brief Phase 3.2; finding 2 |
| WNV deaths recorded as `null` (not published at state level in the CDC file) instead of being filled with zeros | script, NB01 | Brief Phase 3.2 |
| Lyme table renamed to `write_lyme_static_table()`, marked `static`, no longer stamped with the run date | script, `lyme_colorado.json` | Finding 6 |
| County seed file marked `static`; its unsupported "aggregated from CDPHE weekly reports" note replaced; only the iNaturalist columns and `inaturalist_counts_updated` change on each run | script, `regional_counties_2026.json` | Finding 6 |
| Reliability report schema 1.1: adds `kind` and `latest_observation`, and the statuses `static` and `stale`; reads county records from `county_ytd`, so the county file is no longer reported as invalid | script | Finding 6 |
| Dashboard reliability table shows kind and latest observation, and explains both | `scripts/generate_dashboard.py` | Brief Phase 3.1 |
| Where a file does not state its latest observation, the report takes the newest record date (for example NASA POWER's newest day was 2026-10-30 in a file retrieved 2026-11-05) | script | Brief Phase 3.1: show observation date, not run date |
| Machine-readable source registry, checked by tests against the reliability report | `config/data-sources.yaml`, `tests/test_data_sources.py` | Brief Phase 3 |
| NB01 historical WNV load rewritten: the loader path counted rows per year (every year showed 1 case) and the fallback was a second copy of the wrong table; the cell now shows the source and latest year, and an empty table skips the charts | NB01 | New finding |
| NB01 alt text computed from the data; the uncited claim that peak years "correlate with warm, wet springs" removed | NB01 | Brief Phase 5 |
| NB08 panel 8 fixed: it summed the `state` column (the text "Colorado") instead of case counts, and drew Lyme (from 2015) on the WNV (from 2010) x positions | NB08 | New finding |
| NB06 bars relabelled from "Annual Total" to "Neuroinvasive cases"; year ranges in NB01, NB06 and NB08 computed from the data | NB01, NB06, NB08 | Data now run to 2025 |
| `pyyaml` added to the test workflow install (already in `requirements.txt`) | `.github/workflows/test-coverage.yml` | Registry tests |

### Not changed in PR 2

- The reliability report still does not stop publication when the run mode is `blocked` (brief Phase 10.4).
- `2026_season_ytd.json` and the provisional-ingestion stub are unchanged; the 2026 season view is still months out of date.
- The Lyme table is still unverified. No machine-readable state-level Lyme source was found during this audit.
- iNaturalist pagination and county parsing are unchanged.

### New findings from the PR 2 pass

- CDC returns HTTP 403 to the project's custom User-Agent `AEDES-Surveillance/2.0`, while the standard Python and curl client headers receive the file. The CDC request now sends the standard Python header. This is a judgement call for the maintainer: it does not disguise the client as a browser, but it does change the header CDC sees.
- CDC also publishes a county-level yearly WNV file (`wnv_hist_hum_nonhum_yearly.csv`, linked from the same page) with human and neuroinvasive cases by county FIPS code. It could replace the county seed values for WNV in a later PR.
- CDC's public WNV files give deaths only as national totals.
- CDC's page states that non-neuroinvasive counts should not be compared between places or over time, so the dashboard should keep using neuroinvasive counts for trends.
- NB06 and NB08 publish none of their Plotly charts: the live pages contain no Plotly output (checked 2026-11-06), while NB02 publishes five. The cells run without error, so the figures are dropped silently. Only the matplotlib panels in NB08 appear.
- Five PNG files tracked in `notebooks/` (for example `wnv_annual_trend.png`, which still shows the old "2012 outbreak, 130 cases" table) are stale. They are not published, because the deploy copies only `_site/`, but they are misleading to anyone browsing the repository.
- NB08 panel 8 draws WNV in a light green from the viridis palette, which appears to fall well below the 3:1 non-text contrast WCAG 2.2 requires for chart graphics (SC 1.4.11). Not measured; for PR 5.

