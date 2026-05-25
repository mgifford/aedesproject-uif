#!/usr/bin/env python3
"""
Generate the HTML landing page (index.html) for the AEDES surveillance dashboard.

Scans _site/notebooks/ for converted notebook HTML files and builds
a navigation index linking to each analysis page.
"""

import os
import glob
import datetime
import json

SITE_DIR = os.path.join(os.path.dirname(__file__), "..", "_site")
NOTEBOOKS_DIR = os.path.join(SITE_DIR, "notebooks")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "surveillance")
TODAY = datetime.date.today().strftime("%B %d, %Y")

# Metadata for each notebook (filename stem → display info)
# data_recency: "live" = current season + live feeds, "historical" = finalized data through 2024
NOTEBOOK_META = {
    "06_current_season_monitoring": {
        "title": "2026 Season Monitoring",
        "icon": "📅",
        "description": "Real-time 2026 season tracking with weekly case counts, baseline comparisons, and early-warning alert levels.",
        "disease": "WNV / Lyme / RMSF",
        "vector": "Live monitoring",
        "data_recency": "live",
    },
    "01_west_nile_virus_surveillance": {
        "title": "West Nile Virus Surveillance",
        "icon": "🦟",
        "description": "Current-season WNV risk, 90-day climate conditions, iNaturalist vector observations, and early warning signals. Historical trends (2010–2024) available below.",
        "disease": "West Nile Virus",
        "vector": "Culex tarsalis",
        "data_recency": "live",
    },
    "02_tick_disease_surveillance": {
        "title": "Tick-Borne Disease Surveillance",
        "icon": "🕷️",
        "description": "Current tick activity, iNaturalist tick observations, and seasonal risk calendar for Colorado. Historical Lyme trends (2015–2024) available below.",
        "disease": "Lyme / RMSF / CTF",
        "vector": "Ixodes / Dermacentor",
        "data_recency": "live",
    },
    "07_regional_tracking": {
        "title": "Regional County Tracking",
        "icon": "🗺️",
        "description": "County-level breakdown for Colorado — choropleth map, Front Range hotspot analysis, and per-county iNaturalist vector observations.",
        "disease": "WNV / Lyme / RMSF",
        "vector": "County-level",
        "data_recency": "live",
    },
    "04_climate_disease_correlation": {
        "title": "Climate–Disease Correlation",
        "icon": "🌡️",
        "description": "Feature engineering with Growing Degree Days, winter survival risk, and correlation between climate variables and disease incidence.",
        "disease": "WNV / Lyme",
        "vector": "Climate-driven",
        "data_recency": "historical",
    },
    "05_climate_change_impact_analysis": {
        "title": "Climate Change Impact Analysis",
        "icon": "📈",
        "description": "Long-term climate trends, projected vector range expansion, and future risk scoring under warming scenarios.",
        "disease": "WNV / Lyme / RMSF",
        "vector": "Multi-vector",
        "data_recency": "historical",
    },
}

# Notebooks whose CDC case data ends at 2024 and lack a current-season feed
# are moved to the "Historical Archive" section on the dashboard.
HISTORICAL_ARCHIVE_STEMS = {
    "03_multi_disease_dashboard",
    "04_climate_disease_correlation",
    "05_climate_change_impact_analysis",
    "08_comprehensive_surveillance_dashboard",
    "09_model_validation_report",
}


def get_last_fetched() -> str:
    sentinel = os.path.join(DATA_DIR, "wnv_colorado.json")
    if os.path.exists(sentinel):
        try:
            with open(sentinel) as f:
                data = json.load(f)
            return data.get("fetched", TODAY)
        except (json.JSONDecodeError, KeyError):
            pass
    return TODAY


def get_reliability_report() -> dict | None:
    report_path = os.path.join(DATA_DIR, "reliability_report.json")
    if not os.path.exists(report_path):
        return None
    try:
        with open(report_path) as f:
            report = json.load(f)
        if isinstance(report, dict):
            return report
    except json.JSONDecodeError:
        pass
    return None


def build_reliability_section(report: dict | None) -> str:
    if not report:
        return """
  <div class=\"reliability\">
    <h3>Pipeline Reliability Status</h3>
    <p>No reliability report found for this run yet.</p>
  </div>
"""

    run_mode = str(report.get("run_mode", "unknown")).lower()
    generated_at = report.get("generated_at", "unknown")
    mode_label = {
        "normal": "Normal",
        "degraded": "Degraded",
        "blocked": "Blocked",
    }.get(run_mode, "Unknown")

    sources = report.get("sources", [])
    rows: list[str] = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        source_id = source.get("source_id", "unknown")
        status = source.get("status", "unknown")
        status_reason = source.get("status_reason", "n/a")
        last_success_at = source.get("last_success_at") or "n/a"
        fallback_used = "Yes" if source.get("fallback_used", False) else "No"
        rows.append(
            f"<tr><td>{source_id}</td><td>{status}</td><td>{fallback_used}</td><td>{last_success_at}</td><td>{status_reason}</td></tr>"
        )

    rows_html = "\n".join(rows) if rows else "<tr><td colspan='5'>No source status data available.</td></tr>"

    return f"""
  <div class=\"reliability\">
    <h3>Pipeline Reliability Status</h3>
    <p><strong>Run mode:</strong> {mode_label} &nbsp;|&nbsp; <strong>Generated:</strong> {generated_at}</p>
    <table>
      <thead>
        <tr>
          <th>Source</th>
          <th>Status</th>
          <th>Fallback Used</th>
          <th>Last Success</th>
          <th>Reason</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </div>
"""


def _build_card(html_path: str, archive: bool = False) -> str:
    stem = os.path.splitext(os.path.basename(html_path))[0]
    meta = NOTEBOOK_META.get(stem, {
        "title": stem.replace("_", " ").title(),
        "icon": "📊",
        "description": "Surveillance analysis notebook.",
        "disease": "Unknown",
        "vector": "Unknown",
        "data_recency": "historical",
    })
    rel_path = f"notebooks/{os.path.basename(html_path)}"
    archive_badge = '<span class="archive-badge">📂 Historical data (through 2024)</span>' if archive else ""
    return f"""
        <div class="card{'  card-archive' if archive else ''}">
          <div class="card-icon">{meta['icon']}</div>
          <div class="card-body">
            <h2><a href="{rel_path}">{meta['title']}</a></h2>
            <p class="meta">Disease: <strong>{meta['disease']}</strong> &nbsp;|&nbsp; Vector: <strong>{meta['vector']}</strong></p>
            {archive_badge}
            <p>{meta['description']}</p>
            <a href="{rel_path}" class="btn">View Analysis →</a>
          </div>
        </div>"""


def build_notebook_cards(html_files: list[str]) -> tuple[str, str]:
    """Return (current_cards_html, archive_cards_html) as a tuple."""
    if not html_files:
        empty = "<p class='no-data'>No analyses available yet. Check back after the first workflow run.</p>"
        return empty, ""

    # Determine sort order: NOTEBOOK_META key order defines priority within each group
    meta_order = list(NOTEBOOK_META.keys())

    def sort_key(path: str) -> tuple[int, int]:
        stem = os.path.splitext(os.path.basename(path))[0]
        is_archive = stem in HISTORICAL_ARCHIVE_STEMS
        try:
            pos = meta_order.index(stem)
        except ValueError:
            pos = 999
        return (1 if is_archive else 0, pos)

    current_cards: list[str] = []
    archive_cards: list[str] = []

    for html_path in sorted(html_files, key=sort_key):
        stem = os.path.splitext(os.path.basename(html_path))[0]
        is_archive = stem in HISTORICAL_ARCHIVE_STEMS
        card = _build_card(html_path, archive=is_archive)
        if is_archive:
            archive_cards.append(card)
        else:
            current_cards.append(card)

    return "\n".join(current_cards), "\n".join(archive_cards)


def build_index() -> None:
    os.makedirs(SITE_DIR, exist_ok=True)
    html_files = glob.glob(os.path.join(NOTEBOOKS_DIR, "*.html"))
    current_cards_html, archive_cards_html = build_notebook_cards(html_files)
    last_fetched = get_last_fetched()
    reliability_html = build_reliability_section(get_reliability_report())

    archive_section = ""
    if archive_cards_html:
        archive_section = f"""
  <section aria-label="Historical analysis archive">
    <details class="archive-section">
      <summary>
        <h2 class="archive-heading">📂 Historical Analysis Archive (data through 2024)</h2>
      </summary>
      <p class="archive-note">
        These notebooks use CDC finalized annual case data, which is published with a 12–18 month lag.
        The most recent finalized year is <strong>2024</strong>.
        They are preserved here for historical context and methodological reference.
      </p>
      <div class="grid">
        {archive_cards_html}
      </div>
    </details>
  </section>
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AEDES — Colorado Vector-Borne Disease Surveillance</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f4f7fb;
      color: #2d3748;
      line-height: 1.6;
    }}

    header {{
      background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
      color: white;
      padding: 2.5rem 2rem 2rem;
    }}
    header h1 {{ font-size: 1.9rem; font-weight: 700; }}
    header p  {{ opacity: 0.85; margin-top: 0.4rem; font-size: 1rem; }}
    .badge {{
      display: inline-block;
      background: rgba(255,255,255,0.15);
      border: 1px solid rgba(255,255,255,0.3);
      border-radius: 20px;
      padding: 0.25rem 0.75rem;
      font-size: 0.8rem;
      margin-top: 0.75rem;
    }}

    .container {{ max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; }}

    .alert {{
      background: #ebf8ff;
      border-left: 4px solid #3182ce;
      border-radius: 4px;
      padding: 0.9rem 1.2rem;
      margin-bottom: 2rem;
      font-size: 0.9rem;
    }}

    .data-note {{
      background: #fffbeb;
      border-left: 4px solid #d69e2e;
      border-radius: 4px;
      padding: 0.9rem 1.2rem;
      margin-bottom: 2rem;
      font-size: 0.88rem;
    }}

    .section-heading {{
      font-size: 1.15rem;
      font-weight: 600;
      color: #2d3748;
      margin: 2rem 0 1rem;
      padding-bottom: 0.4rem;
      border-bottom: 2px solid #e2e8f0;
    }}

    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 1.5rem; }}

    .card {{
      background: white;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
      display: flex;
      gap: 1rem;
      padding: 1.5rem;
      transition: box-shadow 0.2s;
    }}
    .card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.13); }}
    .card-archive {{ opacity: 0.88; border: 1px solid #e2e8f0; box-shadow: none; }}
    .card-icon {{ font-size: 2.5rem; flex-shrink: 0; line-height: 1; }}
    .card-body h2 {{ font-size: 1.1rem; margin-bottom: 0.3rem; }}
    .card-body h2 a {{ color: #2b6cb0; text-decoration: none; }}
    .card-body h2 a:hover {{ text-decoration: underline; }}
    .card-body .meta {{ font-size: 0.8rem; color: #718096; margin-bottom: 0.5rem; }}
    .card-body p {{ font-size: 0.9rem; color: #4a5568; margin-bottom: 0.75rem; }}
    .archive-badge {{
      display: inline-block;
      background: #faf5e4;
      border: 1px solid #d69e2e;
      border-radius: 12px;
      padding: 0.15rem 0.6rem;
      font-size: 0.78rem;
      color: #744210;
      margin-bottom: 0.5rem;
    }}
    .btn {{
      display: inline-block;
      background: #2b6cb0;
      color: white;
      padding: 0.35rem 0.9rem;
      border-radius: 5px;
      font-size: 0.85rem;
      text-decoration: none;
    }}
    .btn:hover {{ background: #2c5282; }}

    .no-data {{ color: #718096; font-style: italic; padding: 1rem 0; }}

    .archive-section {{
      margin-top: 2.5rem;
      background: white;
      border-radius: 10px;
      padding: 1.5rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }}
    .archive-section summary {{
      cursor: pointer;
      list-style: none;
      padding: 0.25rem 0;
    }}
    .archive-section summary::-webkit-details-marker {{ display: none; }}
    .archive-section summary::before {{
      content: '▶ ';
      font-size: 0.8em;
      color: #718096;
    }}
    .archive-section[open] summary::before {{ content: '▼ '; }}
    .archive-heading {{
      display: inline;
      font-size: 1rem;
      font-weight: 600;
      color: #4a5568;
    }}
    .archive-note {{
      font-size: 0.85rem;
      color: #718096;
      margin: 0.75rem 0 1.25rem;
    }}

    .disease-key {{
      margin-top: 2.5rem;
      background: white;
      border-radius: 10px;
      padding: 1.5rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }}
    .reliability {{
      margin-top: 1.5rem;
      background: white;
      border-radius: 10px;
      padding: 1.2rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
      font-size: 0.88rem;
    }}
    .reliability h3 {{ font-size: 1rem; margin-bottom: 0.5rem; color: #4a5568; }}
    .reliability table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; }}
    .reliability th {{ background: #edf2f7; text-align: left; padding: 0.45rem 0.6rem; }}
    .reliability td {{ padding: 0.4rem 0.6rem; border-bottom: 1px solid #edf2f7; }}
    .disease-key h3 {{ font-size: 1rem; font-weight: 600; margin-bottom: 1rem; color: #4a5568; }}
    .disease-key table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
    .disease-key th {{ background: #edf2f7; text-align: left; padding: 0.5rem 0.75rem; }}
    .disease-key td {{ padding: 0.45rem 0.75rem; border-bottom: 1px solid #edf2f7; }}

    footer {{
      text-align: center;
      padding: 2rem;
      font-size: 0.8rem;
      color: #a0aec0;
      margin-top: 2rem;
    }}
    footer a {{ color: #718096; }}
  </style>
</head>
<body>

<header>
  <div class="container" style="padding-top:0; padding-bottom:0;">
    <h1>🦟 AEDES Colorado Surveillance Dashboard</h1>
    <p>Advanced Early Disease Prediction and Exploration Service — Vector-Borne Disease Monitoring</p>
    <span class="badge">🕐 Data last fetched: {last_fetched}</span>
    <span class="badge">📍 Colorado, USA</span>
  </div>
</header>

<div class="container">

  <div class="alert">
    <strong>About this dashboard:</strong> Automatically updated daily using CDC surveillance data,
    NASA POWER climate records, and iNaturalist citizen-science observations. Each analysis notebook
    includes trend charts, seasonal risk indicators, and early warning signals.
    Built on the <a href="https://github.com/mgifford/aedesproject-uif">AEDES framework</a>,
    originally developed for dengue surveillance in the Philippines (Ligot &amp; Toledo, 2021).
  </div>

  <div class="data-note">
    <strong>ℹ️ About CDC data recency:</strong>
    CDC's finalized annual case counts are published approximately 12–18 months after the end of each
    calendar year, so the most recent <em>finalized</em> data is <strong>2024</strong>.
    Current-season (2026) provisional weekly counts are available in the live monitoring reports below.
    Reports that rely exclusively on finalized historical data are grouped in the
    <em>Historical Archive</em> section at the bottom of this page.
  </div>

  <h2 class="section-heading">🔴 Current Season Reports (2026)</h2>
  <div class="grid">
    {current_cards_html}
  </div>

  {archive_section}

  {reliability_html}

  <div class="disease-key">
    <h3>Colorado Vector-Borne Disease Quick Reference</h3>
    <table>
      <thead>
        <tr>
          <th>Disease</th>
          <th>Vector</th>
          <th>Peak Season</th>
          <th>CFR</th>
          <th>Reportable</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>West Nile Virus</td><td>Culex tarsalis</td><td>Jul–Sep</td><td>~10% (neuroinvasive)</td><td>Yes</td></tr>
        <tr><td>Lyme Disease</td><td>Ixodes scapularis</td><td>May–Aug</td><td>&lt;1%</td><td>Yes</td></tr>
        <tr><td>Rocky Mountain Spotted Fever</td><td>Dermacentor andersoni</td><td>Mar–Aug</td><td>5–20%</td><td>Yes</td></tr>
        <tr><td>Colorado Tick Fever</td><td>Dermacentor andersoni</td><td>May–Aug</td><td>&lt;1%</td><td>CO only</td></tr>
        <tr><td>Tularemia</td><td>Dermacentor / rabbit contact</td><td>Jun–Sep</td><td>&lt;2% treated</td><td>Yes</td></tr>
        <tr><td>Hantavirus (HPS)</td><td>Deer mouse (airborne)</td><td>Apr–Sep</td><td>~38%</td><td>Yes</td></tr>
        <tr><td>Plague</td><td>Flea / prairie dog contact</td><td>Jun–Sep</td><td>10–15% treated</td><td>Yes</td></tr>
      </tbody>
    </table>
  </div>

</div>

<footer>
  <p>
    AEDES — Advanced Early Disease Prediction and Exploration Service &nbsp;|&nbsp;
    <a href="https://github.com/mgifford/aedesproject-uif">GitHub</a> &nbsp;|&nbsp;
    Built with Jupyter, nbconvert, and GitHub Actions &nbsp;|&nbsp;
    Data: CDC NNDSS, NASA POWER, iNaturalist &nbsp;|&nbsp;
    Generated: {TODAY}
  </p>
  <p style="margin-top:0.5rem;">
    Original AEDES methodology: Ligot &amp; Toledo (2021). Academia Letters, Article 2956.
  </p>
</footer>

</body>
</html>
"""

    out_path = os.path.join(SITE_DIR, "index.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"Dashboard index written → {out_path}")
    print(f"  Linked {len(html_files)} notebook(s)")


if __name__ == "__main__":
    build_index()
