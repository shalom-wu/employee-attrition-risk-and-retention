"""Tests for the cost-of-attrition model: internal consistency and
agreement with published benchmark ranges."""

import pandas as pd
import pytest

from attrition import cost_model as cm
from attrition import data as adata


@pytest.fixture(scope="module")
def costed():
    return cm.apply_cost_model(adata.clean(adata.load_raw()))


def test_replacement_cost_is_sum_of_components(costed):
    recomputed = costed[cm.COST_COMPONENTS].sum(axis=1)
    pd.testing.assert_series_equal(
        recomputed, costed["replacement_cost"], check_names=False
    )


def test_cost_within_published_benchmark_band(costed):
    """SHRM: ~6-9 months of salary for direct replacement; Gallup: one-half
    to two times annual salary fully loaded. Our per-level averages must sit
    inside the union of those bands (0.5x-2.0x salary)."""
    pct = costed.groupby("JobLevel")["replacement_cost_pct_salary"].mean()
    assert (pct >= 0.50).all()
    assert (pct <= 2.00).all()


def test_cost_increases_with_seniority(costed):
    """Senior roles take longer to fill and ramp, so cost as a % of salary
    must be non-decreasing in job level."""
    pct = costed.groupby("JobLevel")["replacement_cost_pct_salary"].mean()
    assert pct.is_monotonic_increasing


def test_headline_totals(costed):
    summary = cm.annual_cost_summary(costed)
    assert summary["leavers"] == 237
    # Regression guard on the headline numbers quoted in the README/deck.
    assert summary["total_annual_cost"] == 8_674_901
    assert summary["avg_cost_per_departure"] == 36_603
    assert 5.0 < summary["cost_pct_of_payroll"] < 12.0


def test_segment_cost_partitions_total(costed):
    """Complementary segments must partition leavers and cost exactly."""
    ot = cm.segment_cost(costed, costed["OverTime"] == "Yes")
    no_ot = cm.segment_cost(costed, costed["OverTime"] == "No")
    assert ot["leavers"] + no_ot["leavers"] == 237
    total = cm.annual_cost_summary(costed)["total_annual_cost"]
    # Segment costs are rounded independently of the total, so allow $1 slack.
    assert abs(ot["annual_cost"] + no_ot["annual_cost"] - total) <= 1
