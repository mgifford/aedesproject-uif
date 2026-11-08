"""Tests for scripts/build_season_review_pages.py."""
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_season_review_pages as srp  # noqa: E402

SAMPLE = """# 2030 Season Review: Test

- Evidence: [`season-review-2030/`](season-review-2030/)
- Source: https://data.cdc.gov/example

## Summary

See the [audit](SCIENTIFIC-AUDIT.md#limits) and the [data](season-review-2030/summary.json).

| A | B |
|---|---|
| 1 | <script>alert(1)</script> |

## Summary

A second heading with the same text.
"""


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.hrefs.append(attrs["href"])


def _collect(page: str) -> _Collector:
    collector = _Collector()
    collector.feed(page)
    return collector


class TestRewriteUrl:
    @pytest.mark.parametrize("url, expected", [
        ("SCIENTIFIC-AUDIT.md", f"{srp.REPO_URL}/blob/main/docs/SCIENTIFIC-AUDIT.md"),
        ("SCIENTIFIC-AUDIT.md#limits", f"{srp.REPO_URL}/blob/main/docs/SCIENTIFIC-AUDIT.md#limits"),
        ("../AGENTS.md", f"{srp.REPO_URL}/blob/main/AGENTS.md"),
        ("season-review-2026/", f"{srp.REPO_URL}/tree/main/docs/season-review-2026"),
        ("season-review-2026/summary.json", "season-review-2026/summary.json"),
        ("https://www.cdc.gov/page.md", "https://www.cdc.gov/page.md"),
        ("#summary", "#summary"),
    ])
    def test_rewrites_only_docs_markdown_and_folders(self, url, expected):
        assert srp.rewrite_url(url) == expected


class TestRenderReview:
    page = srp.render_review(SAMPLE, "2030-SEASON-REVIEW.md", built="2030-11-01")

    def test_page_landmarks_and_title(self):
        assert '<html lang="en">' in self.page
        assert "<title>2030 Season Review: Test | AEDES Colorado</title>" in self.page
        assert '<main id="main">' in self.page
        assert '<a class="skip-link" href="#main">' in self.page
        assert 'href="index.html"' in self.page

    def test_heading_ids_are_unique_and_listed_on_the_page(self):
        found = _collect(self.page)
        assert {"summary", "summary-2"} <= found.ids
        assert '<nav class="toc" aria-label="On this page">' in self.page
        assert "#summary" in found.hrefs and "#summary-2" in found.hrefs

    def test_tables_are_keyboard_reachable_labelled_regions(self):
        assert '<div class="table-scroll" role="region" tabindex="0" aria-labelledby="summary">' in self.page

    def test_raw_html_in_markdown_is_escaped(self):
        assert "<script>" not in self.page
        assert "&lt;script&gt;" in self.page

    def test_links_are_rewritten(self):
        hrefs = _collect(self.page).hrefs
        assert f"{srp.REPO_URL}/blob/main/docs/SCIENTIFIC-AUDIT.md#limits" in hrefs
        assert f"{srp.REPO_URL}/tree/main/docs/season-review-2030" in hrefs
        assert "season-review-2030/summary.json" in hrefs
        assert f"{srp.REPO_URL}/blob/main/docs/2030-SEASON-REVIEW.md" in hrefs

    def test_bare_urls_become_links_as_on_github(self):
        assert "https://data.cdc.gov/example" in _collect(self.page).hrefs


class TestBuildReviewPages:
    def test_builds_page_and_copies_evidence(self, tmp_path):
        docs, site = tmp_path / "docs", tmp_path / "_site"
        (docs / "season-review-2030").mkdir(parents=True)
        (docs / "season-review-2030" / "summary.json").write_text("{}")
        (docs / "2030-SEASON-REVIEW.md").write_text(SAMPLE)
        (docs / "DRAFT-SEASON-REVIEW.md").write_text("# Not a dated review")

        pages = srp.build_review_pages(docs, site)

        assert pages == [site / "2030-season-review.html"]
        assert (site / "season-review-2030" / "summary.json").exists()
        assert not (site / "DRAFT-season-review.html").exists()

    def test_committed_reviews_have_no_broken_links(self, tmp_path):
        """Every relative link and in-page anchor in the real reviews resolves on the built site."""
        pages = srp.build_review_pages(ROOT / "docs", tmp_path)
        assert tmp_path / "2026-season-review.html" in pages
        for page in pages:
            found = _collect(page.read_text(encoding="utf-8"))
            for href in found.hrefs:
                if href.startswith(("http://", "https://", "mailto:")) or href == "index.html":
                    continue
                if href.startswith("#"):
                    assert href[1:] in found.ids, f"{page.name}: missing anchor {href}"
                else:
                    assert (tmp_path / href).exists(), f"{page.name}: broken link {href}"
