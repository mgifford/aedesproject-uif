# Quality Assurance Report

**Generated**: 2026-05-18T14:59:26.905123

## Data Source Verification

| Source | Status | Records | Date Range | Notes |
|--------|--------|---------|------------|-------|
| Climate (NOAA) | ✓ | 365 | 2023-01-01 to 2023-12-31 | Complete daily data |
| Disease (CDC NNDSS) | ✓ | 365 | 2023-01-01 to 2023-12-31 | Reported cases |

## Schema Validation

### Climate Data
- ✓ PASS: required_columns
- ✓ PASS: date_is_datetime
- ✓ PASS: temp_is_numeric
- ✓ PASS: precip_is_numeric
- ✓ PASS: no_null_dates
- ✓ PASS: low_null_temps
- ✓ PASS: low_null_precip
- ✓ PASS: temp_range_reasonable
- ✓ PASS: temp_min_lt_max
- ✓ PASS: precip_non_negative

### Disease Data
- ✓ PASS: required_columns
- ✓ PASS: date_is_datetime
- ✓ PASS: cases_non_negative
- ✓ PASS: cases_are_integers

## Summary Statistics

### Climate
- Mean temperature: 12.0°C
- Temperature range: -15.1°C to 41.1°C
- Total precipitation: 832 mm
- Frost-free days: 255

### Disease
- Total Lyme cases: 2214
- Total WNV cases: 1544
- Peak Lyme day: 2023-06-30
- Peak WNV day: 2023-10-12
