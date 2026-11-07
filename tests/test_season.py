"""Tests for aedesproject_uif.surveillance.season (in-season comparison with earlier seasons)."""
import pytest

from aedesproject_uif.surveillance.season import as_alert_metrics, cumulative_at_week, season_pace


def rows_for(year, cumulative_by_week):
    return [{"year": year, "week": w, "cumulative": c} for w, c in cumulative_by_week.items()]


ROWS = (
    rows_for(2024, {30: 0, 31: 0, 32: 10})
    + rows_for(2025, {30: 20, 31: 30, 32: 40})
    + rows_for(2026, {30: 5, 31: None})  # week 31 unavailable
)


class TestCumulativeAtWeek:
    def test_uses_latest_available_value_at_or_before_week(self):
        assert cumulative_at_week(ROWS, 2026, 31) == 5  # week 31 is None, so week 30 is used
        assert cumulative_at_week(ROWS, 2025, 31) == 30

    def test_returns_none_when_nothing_is_available(self):
        assert cumulative_at_week(ROWS, 2026, 10) is None
        assert cumulative_at_week(ROWS, 2030, 30) is None


class TestSeasonPace:
    def test_compares_with_earlier_seasons_at_the_same_week(self):
        pace = season_pace(ROWS, 2026)
        assert pace["week"] == 30
        assert pace["ytd"] == 5
        assert pace["prior"] == {2024: 0, 2025: 20}
        assert pace["prior_median"] == 10
        assert pace["status"] == "within_recent_range"

    @pytest.mark.parametrize("ytd, status", [(0, "within_recent_range"), (25, "above_recent_range")])
    def test_status_against_range(self, ytd, status):
        rows = ROWS[:-2] + rows_for(2026, {30: ytd})
        assert season_pace(rows, 2026)["status"] == status

    def test_below_range(self):
        rows = rows_for(2025, {30: 20}) + rows_for(2026, {30: 3})
        assert season_pace(rows, 2026)["status"] == "below_recent_range"

    def test_no_current_data_is_reported_as_no_data_not_zero(self):
        pace = season_pace(ROWS, 2027)
        assert pace["status"] == "no_data"
        assert pace["ytd"] is None

    def test_no_earlier_seasons(self):
        pace = season_pace(rows_for(2026, {30: 5}), 2026)
        assert pace["status"] == "no_baseline"
        assert pace["ytd"] == 5


class TestAsAlertMetrics:
    def test_keys_used_by_notebook_06(self):
        metrics = as_alert_metrics(season_pace(ROWS, 2026))
        assert metrics["ytd_cases"] == 5
        assert metrics["expected_at_week"] == 10
        assert metrics["deviation_pct"] == pytest.approx(-50.0)
        assert metrics["alert_level"] == "Within the range of recent seasons"
        assert metrics["recent_range"] == (0, 20)
        assert metrics["recent_years"] == [2024, 2025]

    def test_missing_values_stay_none(self):
        metrics = as_alert_metrics(season_pace([], 2026))
        assert metrics["ytd_cases"] is None
        assert metrics["expected_at_week"] is None
        assert metrics["deviation_pct"] is None
        assert metrics["alert_level"] == "No in-season data"
