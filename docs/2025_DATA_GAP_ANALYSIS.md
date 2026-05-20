# 2025 Data Gap Analysis

**Date:** May 20, 2026  
**Question:** Why don't the surveillance CSV reports contain 2025 data?

---

## Executive Summary

The CSV files in `notebooks/*.csv` contain only data through **2024** because they are generated from **static reference/fallback data**, not live CDC feeds. These built-in JSON files (`data/surveillance/wnv_colorado.json`, `data/surveillance/lyme_colorado.json`) were last updated with finalized 2024 data and have not been refreshed with 2025 results.

---

## Root Cause

### 1. Static Reference Data Architecture

The surveillance module uses a **two-tier data strategy**:

```
Tier 1 (Primary):   Live CDC ArboNET API calls
                    └─ Fetch current-year (2026) YTD data
                    └─ May fail if API unavailable

Tier 2 (Fallback):  Built-in JSON reference files
                    └─ data/surveillance/wnv_colorado.json  (2010-2024)
                    └─ data/surveillance/lyme_colorado.json (2015-2024)
                    └─ Static, finalized historical years only
```

### 2. Current Data Coverage

| File | Years | Type | Status |
|------|-------|------|--------|
| `wnv_colorado.json` | 2010–2024 | Reference | **Last updated: 2024 finalization** |
| `lyme_colorado.json` | 2015–2024 | Reference | **Last updated: 2024 finalization** |
| Generated CSVs | 2010–2024* | Output | Derived from JSON files above |

*CSV year ranges now explicitly shown in filenames:
- `nb08_wnv_annual-2010-2024.csv`
- `nb08_lyme_annual-2015-2024.csv`
- `wnv_annual_trend-2010-2024.csv`
- `lyme_trend-2015-2024.csv`

### 3. Why 2025 Data Is Not Included

✗ **2025 is missing because:**
- JSON reference files contain **finalized years only** (2010–2024)
- 2025 data has not been fetched from CDC ArboNET and added to the JSON files
- Notebooks fallback to these static files when live API calls fail or are unavailable
- Static reference data is intentionally conservative (confirmed/final data only)

✓ **2025 data SHOULD exist** because:
- Today is May 20, **2026** — 2025 is a complete, finalized year
- CDC ArboNET publishes annual summaries by early 2026
- 2025 is NOT provisional data — it's fully reported

---

## How to Fix: Add 2025 Data

### Step 1: Fetch 2025 Data from CDC ArboNET

```python
# Option A: Use CDC NNDSS API directly
# https://www.cdc.gov/surveillance/nndss/

# Option B: Use existing data_extraction module
from aedesproject_uif.data_extraction.disease_surveillance import CDCArboNetFetcher

fetcher = CDCArboNetFetcher()
wnv_2025 = fetcher.fetch_annual_data('wnv', year=2025, state='Colorado')
lyme_2025 = fetcher.fetch_annual_data('lyme', year=2025, state='Colorado')
```

### Step 2: Update JSON Reference Files

Add 2025 records to `data/surveillance/wnv_colorado.json`:

```json
{
  "year": 2025,
  "state": "Colorado",
  "neuroinvasive": <cases>,
  "deaths": <deaths>
}
```

Add 2025 records to `data/surveillance/lyme_colorado.json`:

```json
{
  "year": 2025,
  "state": "Colorado",
  "confirmed": <confirmed>,
  "probable": <probable>
}
```

### Step 3: Re-execute Notebooks

Once JSON files are updated, re-run notebooks to regenerate CSVs with 2025 data:

```bash
cd notebooks
jupyter nbconvert --execute --inplace 08_comprehensive_surveillance_dashboard.ipynb
```

CSV files will auto-regenerate with year ranges `2010-2025` and `2015-2025`.

---

## File Naming Convention (Updated)

**Historic/Finalized Data:**
```
{name}-{YYYY}-{YYYY}.csv
├─ wnv_annual_trend-2010-2024.csv    (finalized 2010–2024 only)
├─ lyme_trend-2015-2024.csv          (finalized 2015–2024 only)
└─ nb08_wnv_annual-2010-2024.csv     (historical reference)
```

**Live/Current Data:**
```
{name}_ytd.csv or {name}_provisional.csv
├─ wnv_ytd_2026.csv                  (current year YTD)
└─ lyme_ytd_2026.csv                 (current year YTD)
```

*This naming avoids confusion between static reference data and live surveillance data.*

---

## Impact on Notebooks

| Notebook | Uses JSON Fallback | Status | Action |
|----------|-------------------|--------|--------|
| NB01: WNV Surveillance | ✓ Yes | Shows 2010–2024 historical | Update JSON to add 2025 |
| NB08: Comprehensive Dashboard | ✓ Yes | Shows 2010–2024 historical | Update JSON to add 2025 |
| NB09: Model Validation | ✓ Yes (baseline) | Compares against 2010–2024 | Can validate 2025 once added |

---

## Recommendation

**Immediate:** CSV files now correctly labeled with year ranges to clarify they are **not** live data.

**Short-term (1-2 weeks):**
1. Fetch 2025 finalized data from CDC ArboNET
2. Update `data/surveillance/wnv_colorado.json` and `data/surveillance/lyme_colorado.json`
3. Re-execute notebooks to regenerate CSVs with 2025 included
4. Verify year ranges in filenames (should show `2010-2025`, `2015-2025`, etc.)

**Long-term (future enhancement):**
- Implement automated CDC API refresh monthly
- Separate live/provisional data from finalized reference data
- Add CI/CD pipeline to auto-fetch and update reference JSON files quarterly

---

## Related Files

- Source data: `data/surveillance/wnv_colorado.json`, `data/surveillance/lyme_colorado.json`
- Data loader: `src/aedesproject_uif/surveillance/data_loader.py`
- CDC API docs: https://www.cdc.gov/surveillance/nndss/
- Notebook using data: `notebooks/08_comprehensive_surveillance_dashboard.ipynb`
