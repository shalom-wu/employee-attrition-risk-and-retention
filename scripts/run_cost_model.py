"""Cost-of-attrition estimates: unit economics by level, annual totals,
and cost concentration in the flight-risk segments.

Assumptions and benchmark anchors are documented in src/attrition/cost_model.py.

Outputs: outputs/cost_*.csv, outputs/annual_attrition_cost.csv,
         outputs/hr_data_with_costs.csv, reports/figures/cost_by_department.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from attrition import cost_model as cm
from attrition import data as adata
from attrition import viz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = ROOT / "reports" / "figures"

viz.apply_style()

df = cm.apply_cost_model(adata.clean(adata.load_raw()))
df.to_csv(OUT / "hr_data_with_costs.csv", index=False)
cm.ASSUMPTIONS.to_csv(OUT / "cost_model_assumptions.csv", index=False)

unit = cm.unit_economics(df)
unit.to_csv(OUT / "cost_per_departure.csv")
print("=== Replacement cost per departure, by job level ===")
print(unit.to_string())

summary = cm.annual_cost_summary(df)
print(f"\nLeavers: {summary['leavers']}")
print(f"Total annual attrition cost: ${summary['total_annual_cost']:,}")
print(f"Average cost per departure:  ${summary['avg_cost_per_departure']:,} "
      f"({summary['avg_cost_pct_of_salary']:.0%} of salary)")
print(f"Cost as % of payroll: {summary['cost_pct_of_payroll']}%")

# Cost by department and by flight-risk segment
leavers = df[df["AttritionFlag"] == 1]
by_dept = (
    leavers.groupby("Department")["replacement_cost"]
    .agg(leavers="count", annual_cost="sum")
    .round(0)
    .sort_values("annual_cost", ascending=False)
    .reset_index()
    .rename(columns={"Department": "segment"})
)
by_dept["pct_of_total_cost"] = (
    by_dept["annual_cost"] / summary["total_annual_cost"] * 100
).round(1)

seg_masks = {
    "All overtime employees": df["OverTime"] == "Yes",
    "First-year employees": df["YearsAtCompany"] <= 1,
    "Junior + overtime core (L1 + OT)":
        (df["JobLevel"] == 1) & (df["OverTime"] == "Yes"),
}
seg_rows = [{"segment": k, **cm.segment_cost(df, m)} for k, m in seg_masks.items()]
seg_df = pd.DataFrame(seg_rows)[
    ["segment", "leavers", "annual_cost", "pct_of_total_cost"]
]
pd.concat([by_dept, seg_df]).to_csv(OUT / "annual_attrition_cost.csv", index=False)
print("\n=== Annual attrition cost by department / segment ===")
print(pd.concat([by_dept, seg_df]).to_string(index=False))

# Figure: annual cost by department, stacked by component
comp = leavers.groupby("Department")[cm.COST_COMPONENTS].sum()
comp.columns = ["Recruiting", "Onboarding", "Vacancy", "Ramp-up"]
comp = comp.loc[comp.sum(axis=1).sort_values(ascending=False).index]
fig, ax = plt.subplots(figsize=(8, 4.4))
comp.plot(kind="bar", stacked=True, ax=ax,
          color=[viz.NAVY, "#7A8BC4", viz.CORAL, "#F0A05A"], width=0.7)
ax.set_ylabel("Annual replacement cost")
ax.set_xlabel("")
ax.yaxis.set_major_formatter(lambda x, _: f"${x/1e6:.1f}M")
total = summary["total_annual_cost"]
ax.set_title(f"Annual cost of attrition by department (total ${total/1e6:.1f}M)",
             loc="left", pad=12)
ax.legend(loc="upper right")
plt.setp(ax.get_xticklabels(), rotation=0)
fig.tight_layout()
fig.savefig(FIG / "cost_by_department.png")
plt.close(fig)
print("\nWrote cost outputs.")
