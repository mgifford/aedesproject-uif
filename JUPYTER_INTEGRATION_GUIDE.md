# Jupyter Notebooks + GitHub Pages: Integration Options Summary

## Quick Answer

**For AEDES Colorado, use OPTION 3: GitHub Actions + nbconvert** ← Recommended

This gives you:
- ✅ Automatic daily updates
- ✅ Beautiful HTML on GitHub Pages
- ✅ No manual conversion needed
- ✅ Real-time surveillance dashboard
- ✅ Perfect for 2-3 week early warning system

---

## All Integration Options Explained

### Option 1: Commit Directly + nbviewer Links ⭐ Simplest
**Setup**: 5 minutes | **Updates**: Manual

```
Your workflow:
notebooks/*.ipynb → git push → GitHub repo
                     ↓
              Users click nbviewer link
```

**Use when**: Quick sharing, ad-hoc analysis  
**Example link**: https://nbviewer.org/github/Cirrolytix/aedesproject-uif/blob/main/notebooks/01_lyme_analysis.ipynb

---

### Option 2: nbconvert → Static HTML ⭐⭐ Professional
**Setup**: 15 minutes | **Updates**: Manual

```
notebooks/*.ipynb → jupyter nbconvert → docs/analysis/*.html → GitHub Pages
                                           ↓
                                    Served as static site
```

**Use when**: Beautiful documentation, professional look  
**Workflow**:
```bash
jupyter nbconvert --to html --execute notebooks/*.ipynb --output-dir=docs/analysis
git add docs/
git push
```

---

### Option 3: GitHub Actions Automation ⭐⭐⭐ Recommended
**Setup**: 30 minutes | **Updates**: Automatic

```
notebooks/*.ipynb → GitHub Actions workflow → Convert to HTML → Deploy to Pages
     ↑                                           (on schedule)
  Every day                                    (auto-generated)
  at 6 AM UTC
  
  Fetches fresh data → Reruns notebooks → Publishes results
```

**Best for AEDES Colorado** because:
- Daily CDPHE case data updates
- Weekly surveillance trends
- Real-time bird flu monitoring
- Automatic without manual intervention

**Workflow file** (.github/workflows/build-notebooks.yml):
```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  push:
    paths: ['notebooks/**']
```

---

### Option 4: Jupyter Book (Full Documentation) ⭐⭐⭐⭐ Comprehensive
**Setup**: 45 minutes | **Updates**: Automatic

```
├── notebooks/ (as chapters)
├── markdown/ (for methods, reference)
└── _toc.yml, _config.yml (navigation)
    ↓
    Jupyter Book builds professional docs site
    ↓
    GitHub Pages
```

**Use when**: Complete documentation needed  
**Structure**:
- Chapter 1: Methods
- Chapter 2: Lyme Disease Analysis (notebook)
- Chapter 3: West Nile Trends (notebook)
- Chapter 4: Bird Flu Surveillance (notebook)
- Chapter 5: References

---

## Integration Comparison Table

| Feature | Option 1 | Option 2 | Option 3 | Option 4 |
|---------|----------|----------|----------|----------|
| **Setup Time** | 5 min | 15 min | 30 min | 45 min |
| **Beautiful Output** | ⭐ Limited | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Automation** | Manual | Manual | Automatic | Automatic |
| **Update Frequency** | Manual | Manual | Daily/Weekly | On schedule |
| **Interactivity** | Static | Static | Static | Static + Search |
| **Cost** | Free | Free | Free | Free |
| **Best For** | Quick share | Pretty docs | **Surveillance** | Full docs |
| **AEDES Use** | Fallback | Foundation | **PRIMARY** | Reference |

---

## Recommended Hybrid Approach for AEDES Colorado

**Start with Option 3, expand to Option 4:**

```
Week 1:  Option 3 setup (30 min)
         └─ Dashboard auto-updates daily with surveillance data
         
Week 2-4: Build notebooks with real data
         └─ Lyme disease
         └─ West Nile Virus
         └─ Bird flu monitoring
         
Month 2: Add Option 4 documentation
         └─ Methods & data source reference
         └─ Methodology explanations
         
Month 3+: Expand disease coverage
         └─ Rocky Mountain Spotted Fever
         └─ Multi-disease risk assessment
```

---

## How It Works: The Workflow

### Daily Cycle (Option 3):

```
6:00 AM UTC (1:00 AM Mountain Time)
│
├─ GitHub Actions triggers
│
├─ Fetch fresh surveillance data
│  ├─ CDPHE cases (Lyme, WNV, RMSF)
│  ├─ NOAA weather
│  ├─ iNaturalist observations
│  └─ USGS bird detections
│
├─ Run notebooks with new data
│  ├─ 01_lyme_disease_analysis.ipynb
│  ├─ 02_west_nile_virus_trends.ipynb
│  ├─ 03_bird_flu_surveillance.ipynb
│  └─ 04_integrated_risk_dashboard.ipynb
│
├─ Convert to HTML (nbconvert)
│  └─ Save to docs/analysis/
│
└─ Auto-deploy to GitHub Pages
   └─ Live at: cirrolytix.github.io/aedesproject-uif/

9:00 AM (Mountain Time)
Public health officials check dashboard with latest data
```

---

## Repository Structure

```
aedesproject-uif/
├── README.md (← Add Option 1 links here)
├── docs/
│   ├── index.html (main page, links to analysis)
│   ├── analysis/
│   │   ├── 01_lyme_disease_analysis.html (Option 2/3)
│   │   ├── 02_west_nile_virus_trends.html
│   │   ├── 03_bird_flu_surveillance.html
│   │   └── 04_integrated_risk_dashboard.html
│   └── reference/ (Option 4 - later)
│       ├── methods.md
│       ├── data_sources.md
│       └── _toc.yml
│
├── notebooks/
│   ├── 01_lyme_disease_analysis.ipynb
│   ├── 02_west_nile_virus_trends.ipynb
│   ├── 03_bird_flu_surveillance.ipynb
│   └── 04_integrated_risk_dashboard.ipynb
│
├── scripts/
│   ├── fetch_cdphe_data.py
│   ├── fetch_weather.py
│   ├── fetch_inat_ticks.py
│   └── convert_notebooks.py
│
└── .github/workflows/
    └── build-notebooks.yml ← GitHub Actions here
```

---

## Implementation Steps (Option 3 - Recommended)

### Step 1: Create the GitHub Actions Workflow (10 min)

Create `.github/workflows/build-notebooks.yml`:

```yaml
name: Build and Deploy Notebooks

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  push:
    paths: ['notebooks/**']
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install jupyter nbconvert pandas matplotlib plotly
    
    - name: Fetch surveillance data
      run: |
        python scripts/fetch_cdphe_data.py
        python scripts/fetch_weather.py
    
    - name: Convert notebooks
      run: |
        mkdir -p docs/analysis
        jupyter nbconvert --to html --execute \
          notebooks/*.ipynb --output-dir=docs/analysis
    
    - name: Deploy to GitHub Pages
      uses: actions/deploy-pages@v1
```

### Step 2: Enable GitHub Pages (5 min)

Go to repository Settings > Pages:
- Source: "Deploy from a branch"
- Branch: "main"
- Folder: "/docs"

### Step 3: Push and Monitor (5 min)

```bash
git add .github/workflows/build-notebooks.yml
git commit -m "Add GitHub Actions notebook build"
git push origin main
```

Check Actions tab to see first run ✅

### Step 4: Verify Deployment (5 min)

- Wait 5-10 minutes for first run
- Go to: https://cirrolytix.github.io/aedesproject-uif/
- Click "analysis/" folder
- See your converted notebooks

---

## Key Advantages for AEDES Colorado

1. **Early Warning System**
   - Notebooks run daily with fresh data
   - Catch case spikes 2-3 weeks before official reports
   - Same proven approach as Philippines dengue

2. **Multi-Disease Tracking**
   - Lyme disease (tick-borne)
   - West Nile Virus (mosquito-borne)
   - Bird flu spillover risk (migratory)
   - All in one dashboard

3. **Occupational Health**
   - Monitor wildlife handlers
   - Track poultry worker exposures
   - Alert on high-risk periods

4. **Automated Efficiency**
   - No manual conversion needed
   - Updates every day automatically
   - Free hosting on GitHub Pages

5. **Professional Presentation**
   - Beautiful HTML output
   - Plotly visualizations
   - Integrated with your GitHub repo

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| **GitHub Pages not working** | Source not set to /docs | Go to Settings > Pages, select "Deploy from branch" → main → /docs |
| **Notebooks won't convert** | Missing dependencies | Add `pip install jupyter nbconvert` to workflow |
| **Slow builds** | Large data downloads | Cache data or use `--to html --no-input` |
| **Wrong URL paths** | Base URL configuration | Add `html.baseurl:` to Jupyter Book config |

---

## Next Steps

1. **Read**: See the full notebook `JUPYTER_GITHUB_PAGES_INTEGRATION.ipynb` for detailed examples
2. **Review**: Check `GITHUB_PAGES_SETUP.md` (Section 3 has GitHub Actions template)
3. **Implement**: Copy `.github/workflows/build-notebooks.yml` and customize
4. **Test**: Run locally first with `jupyter nbconvert`
5. **Deploy**: Push to GitHub and monitor Actions tab
6. **Iterate**: Add more notebooks and data sources

---

## Resources

- **Jupyter Notebooks**: https://jupyter.org/
- **nbconvert**: https://nbconvert.readthedocs.io/
- **Jupyter Book**: https://jupyterbook.org/
- **GitHub Pages**: https://pages.github.com/
- **GitHub Actions**: https://github.com/features/actions

---

## Decision Matrix

**Choose your path:**

```
Quick sharing? → Option 1 (5 min)
   ↓
Pretty docs? → Option 2 (15 min)
   ↓
Auto updates? → Option 3 (30 min) ← PICK THIS
   ↓
Full documentation? → Option 4 (45 min)
```

**For AEDES Colorado surveillance: Start with Option 3, add Option 4 later.**

---

**Questions?** See troubleshooting in the Jupyter Notebook: `JUPYTER_GITHUB_PAGES_INTEGRATION.ipynb`

**Ready to implement?** Follow steps in `GITHUB_PAGES_SETUP.md` Section 3 (GitHub Actions)
