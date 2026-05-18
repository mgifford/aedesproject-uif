# AEDES Project Agent Skills

This directory contains skill definitions and configurations for the AEDES project. Skills guide development practices, code quality standards, and accessibility compliance.

## Quick Start

**Active Skills:**
- `python-code-style` — Code style, linting, type checking (ruff, mypy, pytest)
- `charts-graphs` — Accessible data visualizations (HIGH PRIORITY)
- `image-alt-text` — Alt text for static images
- `tables` — Accessible data table patterns
- `plain-language` — Clear writing standards
- `color-contrast` — Colorblind-safe palettes and contrast ratios

**Configuration:**
- Registered skills: `skills-lock.json`
- Accessibility standards: `ACCESSIBILITY.md`
- Workflow documentation: `../AGENTS.md`

## Using Skills

### 1. Data Visualization Accessibility

**When:** Creating charts, plots, heatmaps in Jupyter notebooks or dashboards

**Steps:**
1. Review [`.agents/ACCESSIBILITY.md`](.agents/ACCESSIBILITY.md) patterns
2. For Plotly: Use descriptive titles, add data tables, test with colorblind palette
3. For Matplotlib: Include grid, patterns (not just color), export data
4. Test with [Coblis Color Blind Simulator](https://www.color-blindness.com/coblis-color-blindness-simulator/)

**Example (Plotly):**
```python
import plotly.express as px

fig = px.line(df, x='week', y='cases',
    title='West Nile Virus Cases (2026)',
    labels={'cases': 'Confirmed Cases'})

# Add description as reference
description = "Line chart of weekly WNV cases. Peak: weeks 30-35. Total: 847 cases."
fig.write_html('chart.html')
# Include description in notebook markdown cell
```

### 2. Code Style & Quality

**When:** Writing Python code in `src/`, `scripts/`, or `tests/`

**Steps:**
1. Format: `ruff format <file_or_dir>`
2. Check types: `mypy <file_or_dir>`
3. Lint: `ruff check <file_or_dir>`

**Example:**
```bash
ruff format src/aedesproject_uif/
mypy src/aedesproject_uif/
ruff check src/aedesproject_uif/
```

### 3. Testing & Coverage

**When:** Adding new code or fixing bugs

**Steps:**
1. Write tests in `tests/` directory
2. Run: `pytest tests/ -v`
3. With coverage: `pytest tests/ --cov=src/aedesproject_uif --cov-report=html`

### 4. Documentation Standards

**When:** Writing markdown files, docstrings, comments

**Principles (from plain-language skill):**
- Short sentences (<20 words)
- Active voice: "Cases increased 40%" not "A 40% increase was observed"
- Define terms: "GDD (Growing Degree Days)" not just "GDD"
- Use bullet points for lists
- Headers show document structure

## Documentation Files

| File | Purpose |
|------|---------|
| `ACCESSIBILITY.md` | Complete accessibility standards for data visualizations (WCAG 2.1 AA) |
| `../AGENTS.md` | Skills registry, GitHub Actions workflows, development workflow |
| `../JUPYTER_ENVIRONMENT.md` | Jupyter execution, data management, troubleshooting |
| `skills-lock.json` | Configuration of active skills and dependencies |

## References

- **Accessibility Skills Source:** [mgifford/accessibility-skills](https://github.com/mgifford/accessibility-skills)
- **Python Style Guide:** [wshobson/agents](https://github.com/wshobson/agents)
- **WCAG 2.1:** https://www.w3.org/WAI/WCAG21/quickref/
- **Color Blind Simulator:** [Coblis](https://www.color-blindness.com/coblis-color-blindness-simulator/)

---

**Last Updated:** May 18, 2026  
**Maintainers:** AEDES Project Team
