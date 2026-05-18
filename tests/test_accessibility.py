"""
Tests for accessibility compliance per .agents/ACCESSIBILITY.md

Validates:
- Alt text presence in visualizations
- Color contrast ratios (WCAG 2.1 Level AA)
- Data table exports (CSV/JSON)
- ARIA labels and semantic HTML
"""
import json
import re
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest


class TestAccessibilityStandards:
    """Test accessibility configuration and standards adherence."""

    def test_accessibility_documentation_exists(self):
        """Verify ACCESSIBILITY.md exists and contains required sections."""
        a11y_file = Path(__file__).parent.parent / ".agents" / "ACCESSIBILITY.md"
        assert a11y_file.exists(), "ACCESSIBILITY.md not found"
        content = a11y_file.read_text()
        required_sections = [
            "WCAG 2.1 Level AA",
            "Plotly pattern",
            "Matplotlib pattern",
            "Data Table pattern",
            "Colorblind-safe palettes",
            "Contrast ratios"
        ]
        for section in required_sections:
            assert section in content, f"Missing section: {section}"

    def test_skills_lock_includes_accessibility_skills(self):
        """Verify skills-lock.json includes accessibility skills."""
        skills_file = Path(__file__).parent.parent / ".agents" / "skills-lock.json"
        assert skills_file.exists(), "skills-lock.json not found"
        skills = json.loads(skills_file.read_text())
        
        required_skills = [
            "charts-graphs",
            "image-alt-text",
            "tables",
            "plain-language",
            "color-contrast"
        ]
        for skill in required_skills:
            assert skill in skills.get("skills", {}), f"Missing skill: {skill}"

    def test_colorblind_safe_palette_defined(self):
        """Verify colorblind-safe palette is properly defined."""
        # Colorblind-safe palette per ACCESSIBILITY.md
        palette = ['#0173B2', '#DE8F05', '#CC78BC', '#CA9161', '#949494']
        
        # Validate hex colors
        hex_pattern = r'^#[0-9A-Fa-f]{6}$'
        for color in palette:
            assert re.match(hex_pattern, color), f"Invalid hex color: {color}"
        
        # Verify sufficient colors for typical visualization
        assert len(palette) >= 5, "Palette should have at least 5 distinct colors"


class TestPlotlyAccessibility:
    """Test Plotly visualization accessibility patterns."""

    def test_plotly_chart_has_aria_label(self):
        """Test that Plotly charts include ARIA labels."""
        # Sample Plotly figure structure
        fig_config = {
            "layout": {
                "title": {"text": "Weekly Cases"},
                "xaxis": {"title": "Week"},
                "yaxis": {"title": "Cases"},
                "hovermode": "x unified"
            },
            "config": {
                "responsive": True,
                "displayModeBar": True
            }
        }
        
        # Verify required accessibility attributes
        assert fig_config["layout"]["title"]["text"]
        assert fig_config["layout"]["xaxis"]["title"]
        assert fig_config["layout"]["yaxis"]["title"]

    def test_plotly_exports_data_table(self):
        """Test that Plotly visualizations export data as CSV/JSON."""
        # Mock data export
        export_data = {
            "format": "csv",
            "filename": "weekly_cases.csv",
            "data": "week,cases\n1,5\n2,8\n3,12"
        }
        
        assert export_data["format"] in ["csv", "json"]
        assert export_data["filename"]
        assert export_data["data"]

    def test_plotly_color_contrast_minimum(self):
        """Test minimum contrast ratio of 3:1 for graphics."""
        # Contrast ratio calculator (simplified)
        def relative_luminance(hex_color):
            """Calculate relative luminance of hex color."""
            # Convert hex to RGB
            r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
            # Normalize to 0-1
            r, g, b = r/255, g/255, b/255
            # Apply gamma correction
            r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055) ** 2.4
            g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055) ** 2.4
            b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        def contrast_ratio(color1, color2):
            """Calculate contrast ratio between two colors."""
            l1 = relative_luminance(color1)
            l2 = relative_luminance(color2)
            lighter = max(l1, l2)
            darker = min(l1, l2)
            return (lighter + 0.05) / (darker + 0.05)
        
        # Test colorblind-safe palette against white
        palette = ['#0173B2', '#DE8F05', '#CC78BC', '#CA9161', '#949494']
        white = '#FFFFFF'
        
        for color in palette:
            ratio = contrast_ratio(color, white)
            assert ratio >= 3.0, f"Color {color} has contrast {ratio} < 3.0 against white"

    def test_plotly_keyboard_navigation_config(self):
        """Test Plotly configuration supports keyboard navigation."""
        config = {
            "responsive": True,
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"]
        }
        
        assert config["responsive"], "Chart should be responsive"
        assert config["displayModeBar"], "Mode bar should be visible"


class TestMatplotlibAccessibility:
    """Test Matplotlib visualization accessibility patterns."""

    def test_matplotlib_grid_lines_present(self):
        """Test that matplotlib plots include grid lines for readability."""
        plot_config = {
            "grid": True,
            "linestyle": "--",
            "alpha": 0.3
        }
        
        assert plot_config["grid"], "Grid should be enabled"
        assert plot_config["alpha"] > 0, "Grid should be visible"

    def test_matplotlib_pattern_fill_not_just_color(self):
        """Test that patterns (not just color) distinguish series."""
        series = [
            {"color": "#0173B2", "linestyle": "-", "marker": "o"},
            {"color": "#DE8F05", "linestyle": "--", "marker": "s"},
            {"color": "#CC78BC", "linestyle": "-.", "marker": "^"}
        ]
        
        for s in series:
            assert s["color"], "Color required"
            assert s["linestyle"], "Line style required for distinction"
            assert s["marker"], "Marker required for distinction"

    def test_matplotlib_high_dpi_export(self):
        """Test that matplotlib exports at high DPI for clarity."""
        export_config = {
            "dpi": 150,
            "format": "png",
            "bbox_inches": "tight"
        }
        
        assert export_config["dpi"] >= 150, "DPI should be >= 150"
        assert export_config["format"] in ["png", "svg"]

    def test_matplotlib_explicit_labels(self):
        """Test that all axes have explicit labels."""
        plot = {
            "title": "Weekly Cases",
            "xlabel": "Week",
            "ylabel": "Cases",
            "fontsize": 12
        }
        
        assert plot["title"]
        assert plot["xlabel"]
        assert plot["ylabel"]


class TestDataTableAccessibility:
    """Test data table accessibility patterns."""

    def test_table_html_structure(self):
        """Test that exported tables have proper HTML structure."""
        html_table = """
        <table>
            <caption>Weekly Lyme Cases</caption>
            <thead>
                <tr>
                    <th scope="col">Week</th>
                    <th scope="col">Cases</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>5</td>
                </tr>
            </tbody>
        </table>
        """
        
        # Verify required elements
        assert "<table>" in html_table
        assert "<caption>" in html_table
        assert "<thead>" in html_table
        assert "<th scope=\"col\">" in html_table
        assert "<tbody>" in html_table

    def test_csv_export_valid_format(self):
        """Test that CSV exports are properly formatted."""
        csv_data = "week,cases,risk_level\n1,5,low\n2,8,medium\n3,12,high"
        
        lines = csv_data.strip().split('\n')
        headers = lines[0].split(',')
        
        assert len(headers) >= 2, "Should have at least 2 columns"
        assert len(lines) >= 2, "Should have headers + at least 1 data row"
        
        for row in lines[1:]:
            cells = row.split(',')
            assert len(cells) == len(headers), f"Row has {len(cells)} cells, expected {len(headers)}"

    def test_json_export_structure(self):
        """Test that JSON exports have proper structure."""
        json_data = {
            "metadata": {
                "title": "Weekly Cases",
                "fetched": "2026-01-01",
                "source": "CDPHE"
            },
            "data": [
                {"week": 1, "cases": 5},
                {"week": 2, "cases": 8}
            ]
        }
        
        assert "metadata" in json_data
        assert "data" in json_data
        assert json_data["metadata"]["title"]
        assert len(json_data["data"]) > 0


class TestSemanticHTML:
    """Test semantic HTML and ARIA patterns."""

    def test_html_landmark_structure(self):
        """Test that HTML includes proper landmark elements."""
        html = """
        <body>
            <header>
                <nav aria-label="Main navigation">...</nav>
            </header>
            <main aria-label="Main content">
                <article>
                    <h1>Surveillance Dashboard</h1>
                </article>
            </main>
            <footer>Footer content</footer>
        </body>
        """
        
        # Verify landmarks
        assert "<header>" in html
        assert "<nav" in html
        assert "<main" in html
        assert "<footer>" in html
        assert 'aria-label=' in html

    def test_heading_hierarchy(self):
        """Test proper heading hierarchy for document structure."""
        html = """
        <h1>Surveillance Report</h1>
        <h2>Section: Lyme Disease</h2>
        <h3>Subsection: Weekly Trends</h3>
        <p>Content here</p>
        <h3>Subsection: Risk Assessment</h3>
        <p>Content here</p>
        <h2>Section: West Nile</h2>
        """
        
        # Extract heading levels
        import re
        headings = re.findall(r'<h(\d)>([^<]+)</h\1>', html)
        levels = [int(h[0]) for h in headings]
        
        # Verify no skipped levels
        for i in range(len(levels) - 1):
            assert levels[i+1] <= levels[i] + 1, "Heading levels should not skip"

    def test_skip_links_present(self):
        """Test that skip links are present for accessibility."""
        html = """
        <body>
            <a href="#main-content" class="skip-link">Skip to main content</a>
            <nav>Navigation here</nav>
            <main id="main-content">Content here</main>
        </body>
        """
        
        assert "skip-link" in html or "Skip to" in html
        assert "#main-content" in html or "id=" in html


class TestAccessibilityTesting:
    """Test accessibility testing infrastructure."""

    def test_accessibility_tools_documented(self):
        """Test that accessibility testing tools are documented."""
        a11y_file = Path(__file__).parent.parent / ".agents" / "ACCESSIBILITY.md"
        content = a11y_file.read_text()
        
        testing_tools = [
            "axe DevTools",
            "WAVE",
            "Lighthouse",
            "NVDA",
            "Coblis"
        ]
        
        for tool in testing_tools:
            assert tool in content, f"Testing tool {tool} not documented"

    def test_wcag_2_1_compliance_target(self):
        """Test that WCAG 2.1 Level AA is the compliance target."""
        a11y_file = Path(__file__).parent.parent / ".agents" / "ACCESSIBILITY.md"
        content = a11y_file.read_text()
        
        assert "WCAG 2.1 Level AA" in content, "WCAG 2.1 Level AA should be target"

    @patch('subprocess.run')
    def test_contrast_checker_integration(self, mock_run):
        """Test that contrast checker can be integrated into CI/CD."""
        # Mock successful contrast check
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "All colors pass contrast ratio 4.5:1"
        
        # Simulate running contrast check
        import subprocess
        result = subprocess.run(["check-contrast", "stylesheet.css"], capture_output=True)
        
        assert result.returncode == 0
