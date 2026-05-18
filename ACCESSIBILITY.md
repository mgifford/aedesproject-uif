# AEDES Project Accessibility Guidelines

## Overview

This document provides accessibility guidelines for the AEDES project's web dashboards and interfaces. These guidelines are based on the [mgifford/accessibility-skills](https://github.com/mgifford/accessibility-skills) repository and are tailored to the specific needs of geospatial health data visualization.

## Quick Start

Skills from the accessibility-skills repository have been selected for relevance to AEDES dashboards:

- **maps** - Critical for geospatial visualization
- **charts-graphs** - Essential for data visualization
- **color-contrast** - Vital for readability
- **keyboard** - Required for navigation accessibility
- **content-design** - For clear, understandable content
- **forms** - For user input accessibility
- **plain-language** - For clear documentation and messaging

## Dashboard Components: Accessibility Checklist

### 1. Maps & Geospatial Visualization

**Critical for**: All dashboards with geospatial data (DPGA, SAT Browser, Space Apps)

**Accessibility Requirements**:
- ✅ Provide text alternative describing the map and its purpose
- ✅ Use ARIA labels for map controls (zoom, pan, etc.)
- ✅ Ensure all map features are keyboard accessible
- ✅ Provide alternative data representations (tables, CSV exports)
- ✅ Use sufficient color contrast (WCAG AA minimum: 4.5:1)
- ✅ Don't rely solely on color to convey information
- ✅ Include legend with sufficient text labels

**Implementation File**: `dashboards/*/js/rendermap.js`

**Example**:
```html
<div id="map-container" role="application" aria-label="Dengue risk map for region selection">
  <div id="map" aria-live="polite"></div>
  <div class="map-controls" role="toolbar" aria-label="Map controls">
    <button aria-label="Zoom in">+</button>
    <button aria-label="Zoom out">-</button>
  </div>
  <div aria-label="Map legend" class="legend">
    <!-- Legend content -->
  </div>
</div>
```

### 2. Charts & Graphs

**Critical for**: Forecast dashboards, INFORM risk scoring, hotspot detection

**Accessibility Requirements**:
- ✅ Provide text summary of key findings
- ✅ Use sufficient contrast between chart elements
- ✅ Include a data table as alternative to visual chart
- ✅ Use patterns/textures in addition to colors
- ✅ Label all axes clearly
- ✅ Provide accessible descriptions of trends
- ✅ Make charts keyboard accessible if interactive

**Implementation Location**: `dashboards/*/dashboard/` JavaScript files

**Example**:
```html
<figure role="img" aria-label="Monthly dengue cases trend">
  <div id="chart-container"></div>
  <figcaption>
    Chart shows 23% increase in dengue cases from January to March 2024.
    <a href="#data-table-cases">View data table</a>
  </figcaption>
  <table id="data-table-cases" class="data-export">
    <!-- Alternative table representation -->
  </table>
</figure>
```

### 3. Color Contrast

**Applies to**: All UI elements

**WCAG AA Standards** (minimum):
- Normal text: 4.5:1 ratio
- Large text (18pt+): 3:1 ratio
- UI components: 3:1 ratio

**Files to Review**:
- `dashboards/dpga_enhancement/css/main.css`
- `dashboards/*/resources/css/*`

**Testing Tools**:
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Chrome DevTools Lighthouse
- Axe DevTools Browser Extension

**Example CSS Update**:
```css
/* Before: Poor contrast */
.risk-label-low { color: #90ee90; }

/* After: Better contrast */
.risk-label-low { color: #006600; background: white; }
```

### 4. Keyboard Navigation

**Required for**: All interactive dashboards

**Accessibility Requirements**:
- ✅ All functionality available via keyboard
- ✅ Logical tab order through elements
- ✅ Visible focus indicators
- ✅ Skip navigation links
- ✅ No keyboard traps
- ✅ Keyboard shortcuts documented

**Implementation**:
```javascript
// Add skip navigation link to all pages
<a href="#main-content" class="skip-link">Skip to main content</a>

// Ensure interactive elements are focusable
<button onclick="handleZoom(1)" aria-label="Zoom in">+</button>

// Provide keyboard shortcut help
document.addEventListener('keydown', function(e) {
  if (e.key === '?') showKeyboardHelpDialog();
});
```

### 5. Content Design & Plain Language

**Critical for**: All user-facing text, labels, and instructions

**Accessibility Requirements**:
- ✅ Clear, concise language
- ✅ Define technical terms on first use
- ✅ Use bullet points and lists
- ✅ Short paragraphs (3-4 sentences max)
- ✅ Meaningful link text (not "click here")
- ✅ Clear headings hierarchy

**Example**:
```html
<!-- Before: Unclear -->
<p>Execute the parameterized geospatial aggregation module to generate choropleth visualizations.</p>

<!-- After: Clear -->
<p>Click the "Generate Map" button to view dengue risk by region.</p>
```

### 6. Forms & User Input

**For**: Data entry interfaces, filters, searches

**Accessibility Requirements**:
- ✅ Associated labels for all form fields
- ✅ Grouped related inputs with `<fieldset>`
- ✅ Error messages clearly associated with fields
- ✅ Helpful hint text
- ✅ Required field indicators
- ✅ Success messages for submissions

**Implementation**:
```html
<form>
  <fieldset>
    <legend>Date Range Filter</legend>
    <div class="form-group">
      <label for="start-date">Start Date <span aria-label="required">*</span></label>
      <input type="date" id="start-date" required 
             aria-describedby="date-hint" aria-invalid="false">
      <small id="date-hint">Format: YYYY-MM-DD</small>
    </div>
  </fieldset>
</form>
```

## Specific Dashboard Improvements

### DPGA Enhancement Dashboard
**Location**: `dashboards/dpga_enhancement/`
- [ ] Add ARIA labels to map features
- [ ] Update color scheme for better contrast
- [ ] Provide CSV data export
- [ ] Add keyboard navigation documentation

### SAT Browser Dashboard
**Location**: `dashboards/sat_browser/`
- [ ] Add alt text to satellite imagery
- [ ] Improve layer selection accessibility
- [ ] Add keyboard shortcuts for common tasks
- [ ] Provide data table alternatives for maps

### Space Apps Demo
**Location**: `dashboards/space_apps/demo/`
- [ ] Enhance form accessibility
- [ ] Add ARIA live regions for dynamic updates
- [ ] Provide accessible forecast display
- [ ] Add help dialog documentation

## Testing for Accessibility

### Automated Testing
```bash
# Install axe DevTools
npm install --save-dev @axe-core/react

# Run accessibility audit in CI/CD
npx axe check https://dashboard-url
```

### Manual Testing Checklist
- [ ] Navigate site using only keyboard (Tab, Enter, Escape, Arrow keys)
- [ ] Use screen reader (NVDA, JAWS, or VoiceOver)
- [ ] Check color contrast with contrast checker
- [ ] Verify all images have meaningful alt text
- [ ] Check heading hierarchy (h1 → h2 → h3, no skipping)
- [ ] Test forms with keyboard and screen reader
- [ ] Check link text is descriptive

### Browser Tools
- Chrome/Edge: Lighthouse (Accessibility audit)
- Chrome/Edge: Axe DevTools
- Firefox: WAVE Firefox Extension
- All browsers: Web Accessibility Evaluation Tool (WAVE)

## Resources & References

### Accessibility Skills from mgifford/accessibility-skills
The following skills are most relevant for AEDES dashboards:

1. **maps** - Geospatial data visualization accessibility
2. **charts-graphs** - Data visualization patterns
3. **color-contrast** - Color accessibility standards
4. **keyboard** - Keyboard navigation requirements
5. **content-design** - Clear, accessible content
6. **forms** - Form accessibility patterns
7. **plain-language** - Clear communication
8. **aria-live-regions** - Dynamic content accessibility

### Install Accessibility Skills
```bash
# Install all relevant skills
npx skills add mgifford/accessibility-skills --skill maps
npx skills add mgifford/accessibility-skills --skill charts-graphs
npx skills add mgifford/accessibility-skills --skill color-contrast
npx skills add mgifford/accessibility-skills --skill keyboard
npx skills add mgifford/accessibility-skills --skill content-design
npx skills add mgifford/accessibility-skills --skill forms

# Or install all at once
npx skills add mgifford/accessibility-skills
```

### WCAG Standards
- [WCAG 2.1 Overview](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM](https://webaim.org/)
- [A11ycasts by Google Chrome](https://www.youtube.com/playlist?list=PLNYkxOF6rcICWx0C9Xc-RgEzwLvePng7V)

### Health Data Visualization
- [CDC Data Visualization Standards](https://www.cdc.gov/DataVisualization/)
- [WHO Accessible Data Visualization](https://www.who.int/news-room/fact-sheets/detail/data-visualization-for-health)

## Implementation Priority

### Phase 1 (High Priority)
- [ ] Fix color contrast issues in all dashboards
- [ ] Add keyboard navigation to maps
- [ ] Add skip navigation links
- [ ] Add form labels

### Phase 2 (Medium Priority)
- [ ] Add ARIA labels to interactive elements
- [ ] Create accessible chart alternatives
- [ ] Update navigation structure
- [ ] Add help documentation

### Phase 3 (Lower Priority)
- [ ] Implement advanced ARIA patterns
- [ ] Add animation/motion preferences
- [ ] Create comprehensive testing suite
- [ ] User accessibility feedback loop

## Maintenance & Monitoring

1. **Automated Checks**: Run axe-core in CI/CD pipeline
2. **Regular Audits**: Quarterly accessibility reviews
3. **User Feedback**: Collect feedback from users with disabilities
4. **Training**: Team training on accessibility best practices
5. **Standards**: Stay updated with WCAG guidelines

## Contact & Questions

For accessibility questions or issues, please open an issue with the `accessibility` label in the project repository.

---

**Last Updated**: 2024
**Based On**: [mgifford/accessibility-skills](https://github.com/mgifford/accessibility-skills)
**Standard**: WCAG 2.1 Level AA
