"""Tests for the pure functions in scripts/season_review.py."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import season_review as sr  # noqa: E402


class TestIndexValue:
    def test_reads_percentage_format_used_before_2026_11_05(self):
        assert sr.index_value("- Integrated risk: MODERATE (47.6%) 95% CI") == ("MODERATE", pytest.approx(0.476))

    def test_reads_scale_format_used_after_2026_11_05(self):
        text = "- Experimental composite index: LOW (0.16 on a 0-1 scale; not a probability)"
        assert sr.index_value(text) == ("LOW", pytest.approx(0.16))

    def test_missing_value_is_none(self):
        assert sr.index_value("no index here") == (None, None)


class TestOutputText:
    def test_keeps_output_and_drops_code(self):
        page = (
            '<div class="jp-InputArea"><pre>print("hidden code")</pre></div>'
            '<div class="jp-RenderedText jp-OutputArea-output"><pre>WNV cases YTD: <b>3</b></pre></div>'
        )
        assert sr.output_text(page).strip() == "WNV cases YTD: 3"


class TestClimateByYear:
    def test_summaries_from_daily_values(self):
        days = pd.date_range("2019-12-01", "2020-12-31", freq="D")
        daily = pd.DataFrame({"T2M": 10.0, "PRECTOTCORR": 1.0}, index=days)
        daily.loc[daily.index.month == 7, "T2M"] = 25.0
        daily.loc[(daily.index.month == 12) & (daily.index.year == 2019), "T2M"] = -5.0

        row = sr.climate_by_year(daily, 2020, 2020).loc[2020]
        assert row["july_mean_c"] == 25.0
        assert row["summer_mean_c"] == pytest.approx((30 * 10 + 31 * 25 + 31 * 10) / 92)
        assert row["winter_mean_c"] == pytest.approx((31 * -5 + 31 * 10 + 29 * 10) / 91)
        assert row["spring_precip_mm"] == 92.0
        assert row["max_14day_mean_c"] == 25.0

    def test_missing_values_are_ignored_not_counted_as_zero(self):
        days = pd.date_range("2019-12-01", "2020-12-31", freq="D")
        daily = pd.DataFrame({"T2M": 20.0, "PRECTOTCORR": 1.0}, index=days)
        daily.loc["2020-07-01":"2020-07-10", "T2M"] = np.nan
        assert sr.climate_by_year(daily, 2020, 2020).loc[2020, "july_mean_c"] == 20.0
