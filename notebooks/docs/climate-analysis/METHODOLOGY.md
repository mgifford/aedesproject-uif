# Methodology: Climate-Disease Correlation Analysis

## Thermal Risk Index Calculation

### Lyme Disease (Ixodes scapularis)

**Formula**:
$$\text{Lyme Risk} = \begin{cases}
0 & \text{if } T < 7°C \\
\frac{T - 7}{6} \times 0.3 & \text{if } 7 ≤ T < 13°C \\
0.3 + \frac{T - 13}{7} \times 0.5 & \text{if } 13 ≤ T < 20°C \\
0.8 + \frac{T - 20}{5} \times 0.2 & \text{if } 20 ≤ T < 25°C \\
0.7 & \text{if } T ≥ 25°C
\end{cases}$$

**Interpretation**:
- **T < 7°C**: No tick activity (dormant)
- **7-13°C**: Emerging/low activity
- **13-20°C**: Active period (ramping risk)
- **20-25°C**: Peak activity (0.8-1.0)
- **T > 25°C**: Heat stress, reduced activity (0.7)

### West Nile Virus (Culex mosquito)

**Formula**:
$$\text{WNV Risk} = \begin{cases}
0 & \text{if } T < 13°C \\
0.1 & \text{if } 13 ≤ T < 18°C \\
0.3 & \text{if } 18 ≤ T < 20°C \\
0.6 + \frac{T - 20}{8} \times 0.3 & \text{if } 20 ≤ T < 28°C \\
0.7 & \text{if } T ≥ 28°C
\end{cases}$$

**Basis**: Virus only replicates above 18°C; extrinsic incubation period shortens with temperature.

## Growing Degree Days (GDD)

**Formula**:
$$GDD = \max\left(0, \frac{T_{max} + T_{min}}{2} - T_{base}\right)$$

where $T_{base} = 10°C$ for *Ixodes* tick development.

**Cumulative GDD** from March 1 predicts phenological timing:
- 500 GDD = Nymph emergence (typically May-June)
- 800 GDD = Peak nymph activity
- 1500 GDD = Winter dormancy

## Time Lag Analysis

Disease cases lag behind climate conditions due to:
1. **Vector development time** (2-3 weeks for nymphs)
2. **Human exposure and infection** (variable)
3. **Incubation period** (3-30 days for Lyme)
4. **Laboratory confirmation and reporting** (7-14 days)

**Typical lags**:
- Lyme: 14-21 days (temperature → peak nymph → cases)
- WNV: 21-28 days (temperature → mosquito development → cases)

## Anomaly Calculation

**Temperature anomaly**:
$$\Delta T = T_{observed} - \bar{T}_{climatology}$$

where $\bar{T}_{climatology}$ is the 1991-2020 long-term average for that calendar date.

Early season signals (GDD advance >50) indicate potential for earlier disease peaks.
