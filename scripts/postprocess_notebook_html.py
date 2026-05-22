#!/usr/bin/env python3
"""
Post-process exported notebook HTML pages:
- Collapse code input cells behind Show/Hide toggles
- Inject notebook navigation (Home + Previous/Next notebook links)
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

NOTEBOOK_ORDER = [
    "01_west_nile_virus_surveillance",
    "02_tick_disease_surveillance",
    "03_multi_disease_dashboard",
    "04_climate_disease_correlation",
    "05_climate_change_impact_analysis",
    "06_current_season_monitoring",
    "07_regional_tracking",
    "08_comprehensive_surveillance_dashboard",
    "09_model_validation_report",
]


def notebook_sort_key(stem: str) -> tuple[int, int | str]:
    if stem in NOTEBOOK_ORDER:
        return (0, NOTEBOOK_ORDER.index(stem))
    return (1, stem)


def notebook_title(stem: str) -> str:
    no_prefix = re.sub(r"^\d+_", "", stem)
    return no_prefix.replace("_", " ").title()


def build_nav_html(current_stem: str, available_stems: list[str]) -> str:
    ordered = sorted(available_stems, key=notebook_sort_key)
    current_idx = ordered.index(current_stem)
    prev_stem = ordered[current_idx - 1] if current_idx > 0 else None
    next_stem = ordered[current_idx + 1] if current_idx < len(ordered) - 1 else None

    prev_link = (
        f'<a class="aedes-nav-link" href="{prev_stem}.html" rel="prev">← Previous</a>'
        if prev_stem
        else '<span class="aedes-nav-link is-disabled">← Previous</span>'
    )
    next_link = (
        f'<a class="aedes-nav-link" href="{next_stem}.html" rel="next">Next →</a>'
        if next_stem
        else '<span class="aedes-nav-link is-disabled">Next →</span>'
    )

    return f"""
    <!-- AEDES_NOTEBOOK_NAV_START -->
    <nav class="aedes-notebook-nav" aria-label="Notebook navigation">
      <a class="aedes-skip-link" href="#notebook-content-start">Skip to notebook content</a>
      <a class="aedes-nav-link aedes-home-link" href="../index.html">🏠 Home</a>
      {prev_link}
      <span class="aedes-nav-current" aria-current="page">{notebook_title(current_stem)}</span>
      {next_link}
    </nav>
    <div id="notebook-content-start" tabindex="-1" role="region" aria-label="Notebook content"></div>
    <!-- AEDES_NOTEBOOK_NAV_END -->
    """


def build_head_snippet() -> str:
    return """
<!-- AEDES_NOTEBOOK_HEAD_START -->
<style>
.aedes-notebook-nav {
  position: sticky;
  top: 0;
  z-index: 1000;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  margin-bottom: 0.75rem;
  border-bottom: 1px solid #d0d7de;
  background: #ffffff;
}
.aedes-nav-link,
.aedes-nav-current {
  display: inline-block;
  padding: 0.25rem 0.55rem;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  font-size: 0.84rem;
  line-height: 1.2;
}
.aedes-nav-link {
  text-decoration: none;
  background: #f6f8fa;
  color: #24292f;
}
.aedes-nav-link:hover { background: #eef2f6; }
.aedes-nav-link:focus-visible {
  outline: 2px solid #2b6cb0;
  outline-offset: 2px;
}
.aedes-skip-link {
  position: absolute;
  left: -9999px;
  top: auto;
}
.aedes-skip-link:focus {
  position: static;
  left: auto;
  top: auto;
  padding: 0.25rem 0.55rem;
  border: 1px solid #2b6cb0;
  border-radius: 6px;
  background: #ffffff;
  color: #2b6cb0;
}
.aedes-home-link { font-weight: 600; }
.aedes-nav-current {
  border-color: #2b6cb0;
  color: #2b6cb0;
  background: #ebf8ff;
}
.aedes-nav-link.is-disabled {
  color: #57606a;
  background: #f6f8fa;
}

.code-toggle-btn {
  margin: 0.4rem 0 0.2rem;
  padding: 0.25rem 0.55rem;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  background: #f6f8fa;
  color: #24292f;
  font-size: 0.82rem;
  cursor: pointer;
}
.code-toggle-btn:hover { background: #eef2f6; }
.jp-InputArea.jp-Cell-inputArea.collapsed-query { display: none; }
</style>
<script>
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.jp-CodeCell').forEach(function (cell, index) {
    const input = cell.querySelector('.jp-InputArea.jp-Cell-inputArea');
    if (!input) return;

    if (!input.id) {
      const baseId = cell.getAttribute('id') || cell.getAttribute('data-cell-id') || String(index);
      const safeId = String(baseId).replace(/[^a-zA-Z0-9_-]/g, '-');
      input.id = 'aedes-query-' + safeId;
    }
    input.classList.add('collapsed-query');

    const button = document.createElement('button');
    button.className = 'code-toggle-btn';
    button.type = 'button';
    button.textContent = 'Show query';
    button.setAttribute('aria-expanded', 'false');
    button.setAttribute('aria-controls', input.id);

    button.addEventListener('click', function () {
      const isCollapsed = input.classList.contains('collapsed-query');
      if (isCollapsed) {
        input.classList.remove('collapsed-query');
        button.textContent = 'Hide query';
        button.setAttribute('aria-expanded', 'true');
      } else {
        input.classList.add('collapsed-query');
        button.textContent = 'Show query';
        button.setAttribute('aria-expanded', 'false');
      }
    });

    input.parentNode.insertBefore(button, input);
  });
});
</script>
<!-- AEDES_NOTEBOOK_HEAD_END -->
"""


def inject_ui(html: str, current_stem: str, available_stems: list[str]) -> str:
    head_snippet = build_head_snippet()
    nav_html = build_nav_html(current_stem, available_stems)

    if "AEDES_NOTEBOOK_HEAD_START" not in html and "</head>" in html:
        html = html.replace("</head>", f"{head_snippet}\n</head>", 1)

    nav_pattern = re.compile(
        r"<!-- AEDES_NOTEBOOK_NAV_START -->.*?<!-- AEDES_NOTEBOOK_NAV_END -->",
        flags=re.DOTALL,
    )
    if "AEDES_NOTEBOOK_NAV_START" in html:
        html = nav_pattern.sub(nav_html.strip(), html, count=1)
    else:
        body_match = re.search(r"<body[^>]*>", html, flags=re.IGNORECASE)
        if body_match:
            insertion_point = body_match.end()
            html = f"{html[:insertion_point]}\n{nav_html}\n{html[insertion_point:]}"
    return html


def process_directory(directory: str | Path) -> int:
    out_dir = Path(directory)
    if not out_dir.exists():
        print(f"Directory not found: {out_dir}")
        return 0

    html_paths = sorted(out_dir.glob("*.html"))
    available_stems = [path.stem for path in html_paths]
    updated_count = 0

    for html_path in html_paths:
        html = html_path.read_text(encoding="utf-8")
        updated = inject_ui(html, current_stem=html_path.stem, available_stems=available_stems)
        if updated != html:
            html_path.write_text(updated, encoding="utf-8")
            updated_count += 1
            print(f"Updated {html_path}")
    return updated_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Inject nav + collapsible code UI into notebook HTML.")
    parser.add_argument(
        "--directory",
        default="_site/notebooks",
        help="Directory containing notebook HTML files (default: _site/notebooks)",
    )
    args = parser.parse_args()
    process_directory(args.directory)


if __name__ == "__main__":
    main()
