# Data Dictionary: Climate and Disease Surveillance

## Climate Variables

| Variable | Unit | Description | Source |
|----------|------|-------------|--------|
| date | ISO 8601 | Date of observation | NOAA |
| temp_max_c | °C | Daily maximum temperature | NOAA |
| temp_min_c | °C | Daily minimum temperature | NOAA |
| temp_mean_c | °C | Mean temperature = (max + min) / 2 | Derived |
| precip_mm | mm | Daily precipitation | NOAA |
| gdd_base10 | degree-days | Growing Degree Days (base 10°C) | Derived |
| thermal_risk_lyme | 0-1 index | Thermal suitability for *Ixodes* activity | Derived |
| thermal_risk_wnv | 0-1 index | Thermal suitability for West Nile transmission | Derived |

## Disease Variables

| Variable | Unit | Description | Source |
|----------|------|-------------|--------|
| lyme_cases | count/day | Laboratory-confirmed Lyme disease cases | CDC NNDSS |
| wnv_cases | count/day | Laboratory-confirmed West Nile Virus neuroinvasive cases | CDC NNDSS |
