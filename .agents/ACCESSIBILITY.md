# AEDES Accessibility Skills & Standards

This document outlines accessibility requirements and best practices for the AEDES project, with emphasis on data visualizations and surveillance dashboards.

## Core Principle

**All surveillance data visualizations must be accessible to all users**, including those with:
- Visual impairments (color blindness, low vision, blindness)
- Motor impairments (keyboard-only navigation)
- Cognitive differences (plain language, clear structure)
- Assistive technology users (screen readers)

## Applicable Accessibility Skills

Source: [mgifford/accessibility-skills](https://github.com/mgifford/accessibility-skills)

### 1. Charts & Graphs (Primary Skill)

**Applies to:** All visualizations in Notebooks 01-06, dashboards, interactive plots

**Key Requirements:**

#### Text Alternatives
- Every chart must have a text alternative (description or data table)
- Descriptions should follow this pattern:
  ```
  [Chart Type]: [Title]
  [Key Finding/Trend]
  [Data Range/Time Period]
  ```
- Examples:
  - Line chart: "West Nile Virus Cases (2024-2026) show peak incidence in weeks 30-35"
  - Heatmap: "Climate suitability by county and month shows highest risk July-September"

#### Data Tables
- Provide data tables alongside charts whenever possible
- For `<table>` HTML in notebooks:
  - Use proper `<thead>`, `<tbody>`, `<th>` tags
  - Include `scope="col"` on header cells
  - For complex tables, use `<caption>` element

#### Color & Contrast
- Never rely on color alone to convey information
- Use patterns, labels, or hatching in addition to color
- Maintain 4.5:1 contrast ratio for text; 3:1 for graphics
- Test with ColorBlind Web Page Filter or Sim Daltonism

#### Plotly-Specific Patterns
```python
import plotly.express as px
import plotly.graph_objects as go

# 1. Add descriptive title and subtitle
fig = px.line(df, x='week', y='cases',
    title='West Nile Virus Weekly Cases (2026)',
    labels={'cases': 'Case Count', 'week': 'Week of Year'})

# 2. Include alt text in chart
fig.update_layout(
    title_font_size=16,
    hovermode='x unified',
    xaxis_title='Week of Year',
    yaxis_title='Confirmed Cases'
)

# 3. Add data table reference
description = """
Line chart showing weekly West Nile Virus cases across 2026.
Peak weeks: 30-35 (late summer/early fall).
Total cases YTD: [number]
Data source: CDC NNDSS Provisional Reports
"""

# 4. Colorblind-safe palette
safe_colors = ['#0173B2', '#DE8F05', '#CC78BC', '#CA9161', '#949494']
fig.update_traces(marker_color=safe_colors[0])
```

#### Matplotlib-Specific Patterns
```python
import matplotlib.pyplot as plt
import numpy as np

# 1. Use colorblind-safe palettes
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['#0173B2', '#DE8F05', '#CC78BC'])

# 2. Add patterns to distinguish lines/bars
fig, ax = plt.subplots()
ax.plot(x, y, linestyle='-', linewidth=2, label='Current Season')
ax.plot(x, y_historical, linestyle='--', linewidth=2, label='Historical Average')
ax.axhline(y=threshold, linestyle=':', color='red', label='Alert Threshold')

# 3. Explicit labels and legend
ax.set_xlabel('Week of Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Case Count', fontsize=12, fontweight='bold')
ax.set_title('2026 West Nile Virus Surveillance', fontsize=14, fontweight='bold')
ax.legend(loc='upper left', framealpha=0.95)

# 4. Grid for readability
ax.grid(True, alpha=0.3, linestyle=':')

# 5. Save with high DPI and accessible size
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 2. Image Alt Text

**Applies to:** Static images, exported plots, infographics

**Pattern:**
```markdown
![Alt text describing the image]
(path/to/image.png "Optional title: more context")
```

**Examples:**
```markdown
![Line graph showing West Nile Virus cases increase from week 25 to peak at week 32, then decline through week 52 in 2026. Total: 847 cases. Source: CDC provisional data](assets/wnv_2026.png "2026 WNV Weekly Surveillance")

![Heatmap of Colorado counties (rows) vs months (columns, Jan-Dec) shading intensity indicating climate suitability for Aedes mosquitoes, with highest suitability shown in dark red for July-September in Front Range counties](assets/climate_suitability.png "Climate suitability for disease vectors by county and month")
```

### 3. Data Tables

**Applies to:** Summary statistics, case counts, baseline data

**HTML Pattern in Notebooks:**
```html
<table>
  <caption>West Nile Virus Cases by County, 2026 YTD</caption>
  <thead>
    <tr>
      <th scope="col">County</th>
      <th scope="col">Confirmed</th>
      <th scope="col">Probable</th>
      <th scope="col">Total</th>
      <th scope="col">Trend</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Denver</td>
      <td>45</td>
      <td>12</td>
      <td>57</td>
      <td>↑ Increasing</td>
    </tr>
    ...
  </tbody>
</table>
```

**Markdown Table Pattern:**
```markdown
| County | Confirmed | Probable | Total | Trend |
|--------|-----------|----------|-------|-------|
| Denver | 45 | 12 | 57 | ↑ Increasing |
| Boulder | 12 | 3 | 15 | → Stable |
| Adams | 28 | 7 | 35 | ↑ Increasing |
```

### 4. SVG Graphics

**Applies to:** Custom diagrams, maps, network visualizations

**Requirements:**
- Use `<title>` and `<desc>` elements
- Ensure text is rendered as text, not paths
- Provide keyboard navigation for interactive SVGs
- Include `role="img"` with `aria-label` for complex graphics

### 5. Plain Language

**Applies to:** Chart descriptions, captions, dashboard text

**Principles:**
- Explain *why* the visualization matters, not just *what* it shows
- Use active voice: "Cases increased 40%" not "A 40% increase was observed"
- Define technical terms: "GDD (Growing Degree Days)" not just "GDD"
- Keep sentences short: aim for <20 words
- Use bullet points for lists

**Example - Before:**
> "Depicted herein is a visualization demonstrating the temporal trajectory of West Nile Virus cases across the state over a 52-week period during the year 2026, with quantitative data stratified by epidemiological classification."

**Example - After:**
> "This chart shows West Nile Virus cases in Colorado each week of 2026. Cases peaked in late summer (weeks 30-35). Most cases were confirmed; some remain probable."

## AEDES Implementation Checklist

### For All Notebooks (01-06)

- [ ] Every chart has a text description or accompanying data table
- [ ] Colorblind-safe color palette used (test with [Color Blind Checker](https://www.color-blindness.com/coblis-color-blindness-simulator/))
- [ ] Color never used as sole indicator (also use labels, patterns, or hatching)
- [ ] Chart titles are descriptive and appear in both visual and text
- [ ] Legends are clear and placed accessibly
- [ ] Axis labels are explicit with units (e.g., "Week of Year (1-52)", "Cases (Count)")
- [ ] Grid lines added for easier reading
- [ ] Data table exported alongside chart (CSV, JSON, or HTML)

### For Interactive Dashboards

- [ ] Keyboard navigation works (Tab, Arrow keys, Enter)
- [ ] Focus indicators are visible (no `outline: none` without replacement)
- [ ] Hover tooltips have keyboard equivalent (focus state)
- [ ] Chart updates announce to screen readers
- [ ] Interactive controls labeled with `aria-label` if visual label missing

### For GitHub Pages Deployment

- [ ] HTML includes WCAG landmark structure (`<nav>`, `<main>`, `<footer>`)
- [ ] Skip link present to bypass navigation
- [ ] Heading hierarchy correct (H1 > H2 > H3, no skipping)
- [ ] Links have descriptive text (not "click here")
- [ ] Images have alt text
- [ ] Forms include `<label>` elements

## Testing & Validation

### Manual Testing
1. **Keyboard-only navigation:** Close trackpad, use Tab and arrow keys exclusively
2. **Screen reader:** Use NVDA (Windows free), JAWS, or VoiceOver (Mac/iOS)
3. **Color blindness:** [Color Blind Simulator](https://www.color-blindness.com/coblis-color-blindness-simulator/)
4. **Zoom:** Browser zoom to 200%, ensure layout doesn't break
5. **Browser DevTools:** Check computed colors for contrast

### Automated Testing
```bash
# Check HTML accessibility
npm install --save-dev axe-core
npx axe check *.html

# Python: Check alt text in generated images
python -c "
from PIL import Image
import json
# Script to validate accessibility metadata
"
```

### Tools
- **axe DevTools:** Chrome/Firefox extension
- **WAVE:** [WebAIM Wave](https://wave.webaim.org/)
- **Lighthouse:** Chrome DevTools built-in
- **NVDA Screen Reader:** [Free Windows tool](https://www.nvaccess.org/)
- **Color Blind Simulator:** [Coblis](https://www.color-blindness.com/coblis-color-blindness-simulator/)

## References & Additional Resources

- **WCAG 2.1 Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/
- **ARIA Authoring Practices:** https://www.w3.org/WAI/ARIA/apg/
- **Accessible Charts Handbook:** [Accessible Dashboard Design](https://www.deque.com/blog/charts-graphs-wcag-accessibility/)
- **Inclusive Data Visualization:** [Harvard Data Science Review](https://hdsr.mitpress.mit.edu/)
- **Colorblind-Safe Palettes:** [ColorBrewer 2.0](https://colorbrewer2.org/)
- **Font Accessibility:** [Dyslexic-friendly fonts](https://www.dyslexiafont.com/)

## Contact & Questions

For accessibility guidance:
1. Consult [`mgifford/accessibility-skills`](https://github.com/mgifford/accessibility-skills/tree/main/skills/charts-graphs)
2. Review WCAG 2.1 Level AA requirements
3. Test with assistive technologies
4. Document accessibility decisions in code comments

---

**Last Updated:** May 18, 2026  
**Compliance Level:** WCAG 2.1 Level AA (minimum)
