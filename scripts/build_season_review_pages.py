#!/usr/bin/env python3
"""Render season reviews (docs/<year>-SEASON-REVIEW.md) as pages on the dashboard site.

Each review becomes _site/<year>-season-review.html. The review's evidence folder,
docs/season-review-<year>/, is copied next to it so relative links to the data files
keep working. Links to other Markdown files and folders in docs/ point to GitHub.
"""

from __future__ import annotations

import datetime
import html
import posixpath
import re
import shutil
from pathlib import Path

import mistune

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
SITE_DIR = ROOT / "_site"
REPO_URL = "https://github.com/mgifford/aedesproject-uif"
REVIEW_FILE = re.compile(r"^(\d{4})-SEASON-REVIEW\.md$")

PAGE_CSS = """
  *, *::before, *::after { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         line-height: 1.6; color: #1a202c; background: #fff; }
  a { color: #2b6cb0; overflow-wrap: anywhere; }
  a:focus-visible, .table-scroll:focus-visible { outline: 3px solid #1a365d; outline-offset: 2px; }
  .skip-link { position: absolute; left: -9999px; }
  .skip-link:focus { left: 1rem; top: 1rem; background: #fff; padding: 0.5rem; z-index: 1; }
  .site-header, main, footer { max-width: 52rem; margin: 0 auto; padding: 1rem 1.25rem; }
  .site-header { border-bottom: 1px solid #cbd5e0; }
  h1 { font-size: 1.8rem; line-height: 1.25; }
  h2 { margin-top: 2.5rem; border-bottom: 1px solid #e2e8f0; }
  nav.toc { background: #f7fafc; border: 1px solid #e2e8f0; padding: 0.5rem 1.25rem; margin: 1.5rem 0; }
  .table-scroll { overflow-x: auto; margin: 1rem 0; }
  table { border-collapse: collapse; width: 100%; font-size: 0.95rem; }
  th, td { border: 1px solid #cbd5e0; padding: 0.4rem 0.6rem; text-align: left; vertical-align: top; }
  th { background: #edf2f7; }
  code { background: #edf2f7; padding: 0 0.2rem; overflow-wrap: anywhere; }
  footer { border-top: 1px solid #cbd5e0; font-size: 0.9rem; color: #4a5568; }
"""


def slugify(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", "", text)).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "section"


def rewrite_url(url: str) -> str:
    """Point relative links to Markdown files or folders in docs/ at GitHub."""
    if re.match(r"^([a-z][a-z0-9+.-]*:|#|/)", url, re.IGNORECASE):
        return url
    path, sep, fragment = url.partition("#")
    target = posixpath.normpath(posixpath.join("docs", path))
    if path.endswith("/"):
        return f"{REPO_URL}/tree/main/{target}"
    if path.endswith(".md"):
        return f"{REPO_URL}/blob/main/{target}{sep}{fragment}"
    return url


class _ReviewRenderer(mistune.HTMLRenderer):
    """HTML renderer that adds heading ids and rewrites relative links."""

    def __init__(self) -> None:
        super().__init__()
        self.headings: list[tuple[int, str, str]] = []

    def heading(self, text: str, level: int, **attrs) -> str:
        base = slug = slugify(text)
        used = {h[1] for h in self.headings}
        n = 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        self.headings.append((level, slug, text))
        return f'<h{level} id="{slug}">{text}</h{level}>\n'

    def link(self, text: str, url: str, title: str | None = None) -> str:
        return super().link(text, rewrite_url(url), title)


def _wrap_tables(body: str) -> str:
    """Let wide tables scroll on narrow screens, as keyboard-reachable labelled regions."""
    heading_ids = [(m.start(), m.group(1)) for m in re.finditer(r'<h[1-6] id="([^"]+)"', body)]

    def wrap(match: re.Match) -> str:
        label = next((hid for pos, hid in reversed(heading_ids) if pos < match.start()), None)
        name = f'aria-labelledby="{label}"' if label else 'aria-label="Table"'
        return f'<div class="table-scroll" role="region" tabindex="0" {name}>\n{match.group(0)}</div>'

    return re.sub(r"<table>.*?</table>", wrap, body, flags=re.DOTALL)


def render_review(markdown_text: str, source_name: str, built: str | None = None) -> str:
    renderer = _ReviewRenderer()
    body = mistune.create_markdown(renderer=renderer, plugins=["table", "url"])(markdown_text)
    body = _wrap_tables(body)

    h1 = next((text for level, _, text in renderer.headings if level == 1), "Season review")
    title = html.unescape(re.sub(r"<[^>]+>", "", h1))
    sections = [(slug, text) for level, slug, text in renderer.headings if level == 2]
    if sections:
        items = "\n".join(f'    <li><a href="#{slug}">{text}</a></li>' for slug, text in sections)
        toc = f'<nav class="toc" aria-label="On this page">\n  <ul>\n{items}\n  </ul>\n</nav>\n'
        body = body.replace("<h2", toc + "<h2", 1)

    built = built or datetime.date.today().isoformat()
    source_url = f"{REPO_URL}/blob/main/docs/{source_name}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} | AEDES Colorado</title>
  <style>{PAGE_CSS}</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to the review</a>
<header class="site-header">
  <nav aria-label="Site">
    <a href="index.html">AEDES Colorado Surveillance Dashboard</a>
  </nav>
</header>
<main id="main">
{body}
</main>
<footer>
  <p>Source: <a href="{source_url}">docs/{source_name}</a> on GitHub. Page built {built}.</p>
  <p><a href="index.html">Back to the dashboard</a></p>
</footer>
</body>
</html>
"""


def build_review_pages(docs_dir: Path = DOCS_DIR, site_dir: Path = SITE_DIR) -> list[Path]:
    site_dir.mkdir(parents=True, exist_ok=True)
    pages = []
    for md_path in sorted(docs_dir.glob("*-SEASON-REVIEW.md")):
        match = REVIEW_FILE.match(md_path.name)
        if not match:
            continue
        year = match.group(1)
        out = site_dir / f"{year}-season-review.html"
        out.write_text(render_review(md_path.read_text(encoding="utf-8"), md_path.name), encoding="utf-8")
        evidence = docs_dir / f"season-review-{year}"
        if evidence.is_dir():
            shutil.copytree(evidence, site_dir / evidence.name, dirs_exist_ok=True)
        pages.append(out)
        print(f"Season review written: {out}")
    return pages


if __name__ == "__main__":
    build_review_pages()
