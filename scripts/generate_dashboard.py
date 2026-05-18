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
NOTEBOOK_META = {
    "01_west_nile_virus_surveillance": {
        "title": "West Nile Virus Surveillance",
        "icon": "🦟",
        "description": "Annual case trends, seasonal patterns, and climate correlates for WNV in Colorado.",
        "disease": "West Nile Virus",
        "vector": "Culex tarsalis",
    },
    "02_tick_disease_surveillance": {
        "title": "Tick-Borne Disease Surveillance",
        "icon": "🕷️",
        "description": "Lyme disease trends, iNaturalist tick observations, and seasonal risk calendar for Colorado.",
        "disease": "Lyme / RMSF / CTF",
        "vector": "Ixodes / Dermacentor",
    },
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


def build_notebook_cards(html_files: list[str]) -> str:
    if not html_files:
        return "<p class='no-data'>No analyses available yet. Check back after the first workflow run.</p>"

    cards = []
    for html_path in sorted(html_files):
        stem = os.path.splitext(os.path.basename(html_path))[0]
        meta = NOTEBOOK_META.get(stem, {
            "title": stem.replace("_", " ").title(),
            "icon": "📊",
            "description": "Surveillance analysis notebook.",
            "disease": "Unknown",
            "vector": "Unknown",
        })
        rel_path = f"notebooks/{os.path.basename(html_path)}"
        cards.append(f"""
        <div class="card">
          <div class="card-icon">{meta['icon']}</div>
          <div class="card-body">
            <h2><a href="{rel_path}">{meta['title']}</a></h2>
            <p class="meta">Disease: <strong>{meta['disease']}</strong> &nbsp;|&nbsp; Vector: <strong>{meta['vector']}</strong></p>
            <p>{meta['description']}</p>
            <a href="{rel_path}" class="btn">View Analysis →</a>
          </div>
        </div>""")
    return "\n".join(cards)


def build_index() -> None:
    os.makedirs(SITE_DIR, exist_ok=True)
    html_files = glob.glob(os.path.join(NOTEBOOKS_DIR, "*.html"))
    cards_html = build_notebook_cards(html_files)
    last_fetched = get_last_fetched()

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
    .card-icon {{ font-size: 2.5rem; flex-shrink: 0; line-height: 1; }}
    .card-body h2 {{ font-size: 1.1rem; margin-bottom: 0.3rem; }}
    .card-body h2 a {{ color: #2b6cb0; text-decoration: none; }}
    .card-body h2 a:hover {{ text-decoration: underline; }}
    .card-body .meta {{ font-size: 0.8rem; color: #718096; margin-bottom: 0.5rem; }}
    .card-body p {{ font-size: 0.9rem; color: #4a5568; margin-bottom: 0.75rem; }}
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

    .disease-key {{
      margin-top: 2.5rem;
      background: white;
      border-radius: 10px;
      padding: 1.5rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }}
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

  <div class="grid">
    {cards_html}
  </div>

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
