import pandas as pd

from aedesproject_uif.surveillance import ProbabilisticRiskScorer


def test_compute_integrated_risk_score_aligns_mismatched_indexes_by_position():
    scorer = ProbabilisticRiskScorer()
    dt_index = pd.date_range("2026-05-01", periods=3, freq="D")

    vector_prob = pd.Series([0.2, 0.4, 0.6], index=dt_index)
    transmission_prob = pd.Series([0.1, 0.3, 0.5], index=pd.RangeIndex(3))
    exposure_prob = pd.Series([0.2, 0.2, 0.2], index=pd.RangeIndex(3))
    outbreak_prob = pd.Series([0.0, 0.1, 0.2], index=pd.RangeIndex(3))

    risk, low_ci, high_ci = scorer.compute_integrated_risk_score(
        vector_prob=vector_prob,
        transmission_prob=transmission_prob,
        exposure_prob=exposure_prob,
        outbreak_prob=outbreak_prob,
    )

    # Weighted sum using default weights from ProbabilisticRiskScorer:
    # 0.2*vector + 0.3*transmission + 0.3*exposure + 0.2*outbreak
    expected = pd.Series([0.13, 0.25, 0.37], index=dt_index)

    pd.testing.assert_series_equal(risk, expected)
    assert not risk.isna().any()
    assert not low_ci.isna().any()
    assert not high_ci.isna().any()


def test_compute_integrated_risk_score_uses_vector_index_for_output():
    scorer = ProbabilisticRiskScorer()
    dt_index = pd.date_range("2026-05-01", periods=2, freq="D")

    vector_prob = pd.Series([0.3, 0.5], index=dt_index)
    transmission_prob = pd.Series([0.2, 0.4], index=[10, 11])
    exposure_prob = pd.Series([0.3, 0.3], index=[10, 11])
    outbreak_prob = pd.Series([0.1, 0.1], index=[10, 11])

    risk, _, _ = scorer.compute_integrated_risk_score(
        vector_prob=vector_prob,
        transmission_prob=transmission_prob,
        exposure_prob=exposure_prob,
        outbreak_prob=outbreak_prob,
    )

    assert risk.index.equals(dt_index)
