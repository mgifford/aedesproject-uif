# AEDES Project Agents & Skills

This document describes the agents, skills, and automation workflows available for the AEDES project. These tools support code quality, surveillance data pipelines, testing, and climate-disease analysis.

## Skills Registry

Skills are reusable capabilities that guide development practices and coding standards. They are sourced from the `.agents/skills/` directory and referenced in `skills-lock.json`.

### Python Code Style

**Location:** [`.agents/skills/python-code-style/SKILL.md`](.agents/skills/python-code-style/SKILL.md)

**Description:** Python code style, linting, formatting, naming conventions, and documentation standards.

**Use When:**
- Setting up linting and formatting for a new module
- Writing or reviewing docstrings
- Establishing team coding standards
- Configuring ruff, mypy, or pyright
- Reviewing code for style consistency
- Creating project documentation

**Key Tools:**
- `ruff` — Fast Python linter and formatter (PEP 8, modern conventions)
- `mypy` — Static type checker with strict mode support
- `pytest` — Testing framework with coverage reporting

**Reference:** [wshobson/agents](https://github.com/wshobson/agents) — Source repository

### Data Visualization Accessibility

**Location:** [`mgifford/accessibility-skills` — charts-graphs](https://github.com/mgifford/accessibility-skills/tree/main/skills/charts-graphs)

**Description:** Accessible data visualization patterns for charts, graphs, dashboards, and infographics using Plotly, Matplotlib, D3.js, and web technologies.

**Use When:**
- Creating data visualizations (charts, graphs, plots, heatmaps)
- Building interactive dashboards with Plotly
- Designing infographics or data-driven presentations
- Generating surveillance monitoring displays
- Publishing analysis notebooks with visual output

**Key Patterns:**
- Text alternatives to charts (descriptions, summaries)
- Data tables alongside visualizations
- Color contrast and colorblind-friendly palettes
- SVG accessibility for custom graphics
- Canvas + ARIA patterns for complex visualizations
- Keyboard navigation for interactive charts

**Related Skills:**
- **Image Alt Text** — Describe charts, diagrams, and visual elements
- **Tables** — Provide data table alternatives to charts
- **SVG Graphics** — Accessible patterns for SVG-based visualizations
- **Plain Language** — Write chart descriptions clearly

**AEDES Application:**
- Plotly charts in Notebooks 01-06: trending data, risk assessment visuals
- Surveillance dashboards with accessible color schemes
- Climate-disease correlation heatmaps
- Weekly case count visualizations
- Risk scoring indicators (🟢🟡🟠🔴 color patterns)
- Semantic anchor links (`#summary`, `#annual-trends`, `#early-warning`) for direct section linking
- Collapsible query cells (Show/Hide code toggle) focusing on results over query mechanics

**Reference:** [mgifford/accessibility-skills](https://github.com/mgifford/accessibility-skills) — Source repository

---

## GitHub Actions Workflows

Automation workflows in [`.github/workflows/`](.github/workflows/) run scheduled tasks, CI/CD tests, and surveillance data pipelines.

### Surveillance Dashboard

**File:** [`.github/workflows/surveillance-dashboard.yml`](.github/workflows/surveillance-dashboard.yml)

**Purpose:** Daily automated data fetch, notebook execution, and GitHub Pages deployment.

**Schedule:** 6 AM UTC daily (or manual trigger)

**Triggers:**
- Daily cron schedule: `0 6 * * *` (6 AM UTC)
- Push to `notebooks/` or `scripts/` directories
- Manual workflow dispatch via GitHub Actions UI

**Pipeline Steps:**
1. Fetch CDC WNV/Lyme data (annual summaries from CDC NNDSS + weekly YTD provisional)
2. Fetch NASA POWER climate data (90-day rolling window for Colorado, excluding sentinel values)
3. Fetch iNaturalist tick/mosquito observations (real-time)
4. Execute Jupyter notebooks (`.ipynb` → `.html`) with executable Python cells
5. Post-process HTML: inject CSS/JS to collapse query cells by default, add Show/Hide toggles
6. Generate dashboard landing page with accessible navigation
7. Deploy to GitHub Pages (`gh-pages` branch)

**Output:** Evergreen surveillance dashboard with:
- Semantic section anchors for direct linking
- Collapsible code cells (results-first presentation)
- Current-year (2026) YTD focus with historical context (2010–2024)
- Validated climate data (sentinel value filtering: `-999` excluded)
- Accessible at GitHub Pages URL with keyboard navigation support

**Key Scripts:**
- `scripts/fetch_surveillance_data.py` — Data ingestion from public APIs (CDC, NASA POWER, iNaturalist)
- `scripts/generate_dashboard.py` — Dashboard HTML generation with notebook cards and index
- Workflow step: Post-processing HTML injection for collapsible query cells (universal JS/CSS toggle)

---

### Test Coverage

**File:** [`.github/workflows/test-coverage.yml`](.github/workflows/test-coverage.yml)

**Purpose:** Continuous integration testing with coverage reporting.

**Schedule:** On every push or pull request to `main` branch

**Triggers:**
- `push` to `main` branch
- `pull_request` targeting `main` branch

**Pipeline Steps:**
1. Set up Python 3.11 environment
2. Install project dependencies (`pip install -e . --no-deps`)
3. Run pytest test suite with coverage analysis
4. Generate coverage reports (terminal, XML, HTML)
5. Upload coverage metrics to Codecov

**Test Configuration:**
- Framework: `pytest 9.0.3`
- Coverage: `pytest-cov` with terminal + XML reporting
- Ignored optional tests: `test_geoboundaries.py`, `test_nasa_worldview.py`, `test_osm.py` (require external deps)
- Passes: 60/60 tests (4 test modules, shared `conftest.py` fixtures)

**Key Test Files:**
- `tests/test_demographics.py` — Admin boundary and population data
- `tests/test_google_trends.py` — Google search trend fetching
- `tests/test_meteorological.py` — NASA POWER and NOAA weather
- `tests/test_nasa_appeears.py` — NASA AppEEARS satellite data
- `tests/test_scripts.py` — Data fetch and dashboard generation scripts

---

## Custom Agents & Prompts

### Prompt Templates

Custom prompts stored in: `{{VSCODE_USER_PROMPTS_FOLDER}}`

Currently available:
- **Data Pipeline Agent** — Orchestrates surveillance data ingestion and validation
- **Climate-Disease Analysis Agent** — Correlates climate variables with vector-borne disease spread
- **Forecast & Risk Scoring Agent** — Generates early warning signals and risk briefings

---

## Skill Dependencies

```
skills-lock.json
├── python-code-style (wshobson/agents)
│   ├── ruff (formatting + linting)
│   ├── mypy (type checking)
│   └── pytest (testing framework)
│
├── charts-graphs (mgifford/accessibility-skills) [HIGH PRIORITY]
│   ├── Color contrast & colorblind-safe palettes
│   ├── Text alternatives (descriptions + data tables)
│   ├── SVG accessibility patterns
│   └── Keyboard navigation for interactive charts
│
├── Supporting Accessibility Skills (mgifford/accessibility-skills)
│   ├── image-alt-text
│   ├── tables
│   ├── plain-language
│   ├── color-contrast
│   └── svg (for custom diagrams)
```

**Configuration:** See [`.agents/ACCESSIBILITY.md`](.agents/ACCESSIBILITY.md) for detailed accessibility standards and implementation patterns.

---

## Development Workflow with Agents

### 0. Move to Spec-Kitty-Driven Development

- Move to spec-kitty-driven development by defining or refining the spec before implementation.
- Reference: https://docs.spec-kitty.ai/

### 1. Writing New Code

Use the **Python Code Style** skill:
```bash
# Format code
ruff format src/aedesproject_uif/

# Check types
mypy src/aedesproject_uif/

# Lint
ruff check src/aedesproject_uif/
```

### 2. Running Tests Locally

```bash
# All tests (excluding optional geospatial deps)
pytest tests/ --ignore=tests/test_geoboundaries.py --ignore=tests/test_nasa_worldview.py --ignore=tests/test_osm.py -v

# With coverage
pytest tests/ ... --cov=src/aedesproject_uif --cov-report=html
```

### 3. CI/CD Validation

- Push to `main` → **Test Coverage** workflow runs automatically
- All 60 tests must pass before PR merge
- Coverage report uploaded to Codecov

### 4. Data Pipeline Execution

- Manual trigger via GitHub Actions UI, or
- Automated daily at 6 AM UTC via **Surveillance Dashboard** workflow
- Fresh data available in `/data/surveillance/` within 30 minutes

### 5. Notebook-Based Analysis

- Notebooks in `/notebooks/` are executed during surveillance dashboard build
- Output HTML served on GitHub Pages
- Supports climate-disease correlation, risk forecasting, regional surveillance

---

## Adding New Skills

To add a new skill to the project:

1. **Lock skill in registry:**
   ```bash
   # Update skills-lock.json with new skill source
   ```

2. **Document the skill:**
   ```bash
   # Add SKILL.md to .agents/skills/<skill-name>/
   ```

3. **Reference in development:**
   - Update `.agents/` directory structure
   - Document in this file under "Skills Registry"
   - Update CI/CD if new tools are needed

---

## References

- **Skills Source:** [wshobson/agents GitHub](https://github.com/wshobson/agents)
- **GitHub Actions:** [GitHub Actions Documentation](https://docs.github.com/en/actions)
- **Testing:** [pytest Documentation](https://docs.pytest.org/)
- **Code Quality:** [Ruff Documentation](https://docs.astral.sh/ruff/)
- **Type Checking:** [Mypy Documentation](https://mypy.readthedocs.io/)

---

**Last Updated:** May 18, 2026  
**Maintained By:** AEDES Project Team  
**License:** CC BY-SA 4.0 (see [CC BY-SA 4.0.md](CC%20BY-SA%204.0.md))
