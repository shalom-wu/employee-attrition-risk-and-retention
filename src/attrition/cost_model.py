"""Component-based cost-of-attrition model.

Each departure is costed from four components, expressed relative to the
departing employee's own salary (MonthlyIncome x 12), with multipliers
tiered by job level:

  1. Recruiting & hiring   20% of annual salary
     Agency fees for professional/tech roles run 20-25% of first-year
     salary; internal sourcing + interview loop time is comparable
     (SHRM cost-per-hire studies).
  2. Onboarding & training 10% of annual salary
     Equipment, formal training, manager/buddy time in the first weeks.
  3. Vacancy cost          months vacant x monthly salary x 1.0
     SHRM average time-to-fill ~44 days; tech roles typically 50-70+
     days, longer for senior levels. A vacant seat is valued at 1.0x
     salary — conservative, since output value usually exceeds salary.
  4. Ramp-up cost          ramp months x monthly salary x 50%
     New hires average ~50% productivity over a 3-6 month ramp.

Sanity anchor: totals land at ~55% of annual salary for junior roles and
~88% for executives (~6.5-11 months of salary), inside the SHRM rule of
thumb (6-9 months for direct replacement) and at the conservative end of
Gallup's one-half-to-two-times-salary range for fully loaded cost. Soft
costs (knowledge loss, morale, customer damage) are deliberately excluded
so every dollar traces to an explicit assumption.
"""

import pandas as pd

ASSUMPTIONS = pd.DataFrame(
    {
        "JobLevel": [1, 2, 3, 4, 5],
        "recruiting_pct_of_salary": [0.20] * 5,
        "onboarding_pct_of_salary": [0.10] * 5,
        "months_vacant": [1.5, 2.0, 2.5, 3.0, 4.0],
        "ramp_months": [3, 3, 4, 6, 6],
        "ramp_productivity_loss": [0.5] * 5,
    }
)

COST_COMPONENTS = ["cost_recruiting", "cost_onboarding", "cost_vacancy", "cost_ramp"]


def apply_cost_model(df: pd.DataFrame,
                     assumptions: pd.DataFrame = ASSUMPTIONS) -> pd.DataFrame:
    """Return df with per-employee replacement-cost columns appended.

    `replacement_cost` is what it would cost to replace each employee if
    they left; summing it over actual leavers gives the annual attrition
    cost.
    """
    out = df.merge(assumptions, on="JobLevel", how="left")
    out["annual_salary"] = out["MonthlyIncome"] * 12
    out["cost_recruiting"] = out["annual_salary"] * out["recruiting_pct_of_salary"]
    out["cost_onboarding"] = out["annual_salary"] * out["onboarding_pct_of_salary"]
    out["cost_vacancy"] = out["MonthlyIncome"] * out["months_vacant"]
    out["cost_ramp"] = (
        out["MonthlyIncome"] * out["ramp_months"] * out["ramp_productivity_loss"]
    )
    out["replacement_cost"] = out[COST_COMPONENTS].sum(axis=1)
    out["replacement_cost_pct_salary"] = out["replacement_cost"] / out["annual_salary"]
    return out


def unit_economics(df_costed: pd.DataFrame) -> pd.DataFrame:
    """Replacement cost per departure by job level (whole population)."""
    unit = df_costed.groupby("JobLevel").agg(
        headcount=("MonthlyIncome", "count"),
        median_annual_salary=("annual_salary", "median"),
        avg_replacement_cost=("replacement_cost", "mean"),
    )
    unit["cost_as_pct_of_salary"] = (
        df_costed.groupby("JobLevel")["replacement_cost_pct_salary"].mean() * 100
    )
    return unit.round(0)


def annual_cost_summary(df_costed: pd.DataFrame) -> dict:
    """Headline cost numbers for the leavers in the snapshot year."""
    leavers = df_costed[df_costed["AttritionFlag"] == 1]
    total = leavers["replacement_cost"].sum()
    return {
        "leavers": len(leavers),
        "total_annual_cost": round(total),
        "avg_cost_per_departure": round(leavers["replacement_cost"].mean()),
        "avg_cost_pct_of_salary": round(
            leavers["replacement_cost_pct_salary"].mean(), 3
        ),
        "cost_pct_of_payroll": round(total / df_costed["annual_salary"].sum() * 100, 1),
    }


def segment_cost(df_costed: pd.DataFrame, mask: pd.Series) -> dict:
    """Attrition economics for an arbitrary employee segment."""
    seg = df_costed[mask]
    seg_leavers = seg[seg["AttritionFlag"] == 1]
    all_leaver_cost = df_costed.loc[
        df_costed["AttritionFlag"] == 1, "replacement_cost"
    ].sum()
    return {
        "headcount": len(seg),
        "leavers": len(seg_leavers),
        "attrition_rate_pct": round(seg["AttritionFlag"].mean() * 100, 1),
        "annual_cost": round(seg_leavers["replacement_cost"].sum()),
        "pct_of_total_cost": round(
            seg_leavers["replacement_cost"].sum() / all_leaver_cost * 100, 1
        ),
    }
