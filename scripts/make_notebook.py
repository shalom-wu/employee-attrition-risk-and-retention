"""Generate and execute notebooks/attrition_analysis.ipynb.

The notebook is the guided walkthrough of the analysis; all heavy lifting
lives in src/attrition so the notebook stays readable. Executing it here
embeds the outputs so the rendered notebook is self-contained on GitHub.
"""

from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "notebooks" / "attrition_analysis.ipynb"

nb = nbf.v4.new_notebook()
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell

cells = [
md("""# Employee attrition: cost, drivers, and retention economics

A 1,470-employee tech company loses 16.1% of its staff a year. This notebook
walks through the three questions the project answers:

1. **What does that attrition actually cost?** (component-based cost model)
2. **Where is it concentrated, and what drives it?** (EDA + predictive models)
3. **Which interventions pay for themselves?** (segment economics)

Data: [IBM HR Analytics Employee Attrition & Performance]\
(https://www.kaggle.com/datasets/pavansubhash/ibm-hr-analytics-attrition-dataset)
— a public, synthetic dataset; see `data/README.md` for source and caveats.
The reusable logic lives in `src/attrition/`; this notebook is the guided tour."""),

code("""import pandas as pd

from attrition import data as adata
from attrition import cost_model as cm
from attrition import modeling as am
from attrition import viz

viz.apply_style()
pd.set_option("display.width", 120)"""),

md("""## 1. Data quality

The dataset is clean by construction (it's synthetic), but three columns are
constant, `PerformanceRating` only takes two values, and there are no dates —
which shapes what we can and can't claim later."""),

code("""raw = adata.load_raw()
for note in adata.quality_report(raw):
    print("-", note)

df = adata.clean(raw)
overall = df["AttritionFlag"].mean()
print(f"\\nAfter cleaning: {df.shape[0]} rows x {df.shape[1]} cols | "
      f"attrition {overall:.1%}")"""),

md("""## 2. Where attrition concentrates

Attrition is not diffuse — it stacks up in overtime workers, first-year
employees, junior levels, and the bottom pay quartile."""),

code("""for col in ["Department", "OverTime", "TenureBand", "JobLevel", "IncomeQuartile"]:
    print(f"=== {col} ===")
    print(adata.attrition_table(df, col, sort_by_rate=False).to_string(index=False))
    print()"""),

code("""import matplotlib.pyplot as plt

pivot = (df.pivot_table(index="JobLevel", columns="OverTime",
                        values="AttritionFlag", aggfunc="mean") * 100)
fig, ax = plt.subplots(figsize=(8, 4.2))
pivot.plot(kind="bar", ax=ax, color=[viz.NAVY, viz.CORAL], width=0.75)
for container in ax.containers:
    ax.bar_label(container, fmt="%.0f%%", fontsize=9, fontweight="bold")
ax.set_ylabel("Attrition rate (%)")
ax.set_xlabel("Job level (1 = junior IC)")
ax.set_title("Overtime multiplies junior attrition", loc="left", pad=12)
ax.legend(title="Overtime")
plt.setp(ax.get_xticklabels(), rotation=0)
plt.show()"""),

md("""The headline interaction: **junior (L1) employees working overtime leave at
52.6%** — 82 of the company's 237 annual departures from 156 people (11% of
headcount)."""),

md("""## 3. What a departure costs

Each departure is costed from four explicit components (recruiting 20% of
salary, onboarding 10%, vacancy months x salary, ramp months at 50%
productivity), tiered by job level. Full assumptions and benchmark anchors:
`src/attrition/cost_model.py`."""),

code("""df = cm.apply_cost_model(df)
print(cm.unit_economics(df).to_string())
print()
summary = cm.annual_cost_summary(df)
print(f"Total annual attrition cost: ${summary['total_annual_cost']:,} "
      f"({summary['cost_pct_of_payroll']}% of payroll)")
print(f"Average per departure: ${summary['avg_cost_per_departure']:,} "
      f"= {summary['avg_cost_pct_of_salary']:.0%} of salary "
      f"(~{summary['avg_cost_pct_of_salary']*12:.1f} months)")"""),

md("""Sanity check: ~59% of salary ≈ 7.1 months sits inside the SHRM 6–9-month
replacement rule of thumb and at the conservative end of Gallup's 0.5–2×
range — the model is defensible and, if anything, understates the loss.

Cost concentration in the risk segments:"""),

code("""segments = {
    "All overtime employees": df["OverTime"] == "Yes",
    "First-year employees": df["YearsAtCompany"] <= 1,
    "Junior + overtime core": (df["JobLevel"] == 1) & (df["OverTime"] == "Yes"),
}
print(pd.DataFrame(
    [{"segment": k, **cm.segment_cost(df, m)} for k, m in segments.items()]
).to_string(index=False))"""),

md("""## 4. Predictive models

Logistic regression baseline vs XGBoost, stratified 75/25 split with 5-fold
CV. Given the 16% positive class we evaluate on ROC-AUC / PR-AUC and pick an
operating threshold that catches ≥70% of leavers (false positives are cheap
— a manager conversation; misses cost ~$37K)."""),

code("""result = am.train_and_evaluate(df.drop(columns=[
    c for c in df.columns
    if c.startswith("cost_") or c in (
        "annual_salary", "replacement_cost", "replacement_cost_pct_salary",
        "recruiting_pct_of_salary", "onboarding_pct_of_salary",
        "months_vacant", "ramp_months", "ramp_productivity_loss")
]))
result["metrics"][["model", "roc_auc", "pr_auc", "cv_roc_auc_mean",
                   "cv_roc_auc_std", "recall_at_op", "precision_at_op",
                   "flagged_employees"]]"""),

md("""The simpler model wins on this small, clean tabular dataset — reported
as-is rather than forcing the fancier model to look better. Both agree on
the drivers:"""),

code("""print("Top drivers, logistic regression (odds ratio per 1 SD):")
print(am.logreg_odds_ratios(result).head(10).to_string(index=False))"""),

code("""import shap

explainer = shap.TreeExplainer(result["models"]["XGBoost"])
shap_values = explainer.shap_values(result["X_test"])
shap.summary_plot(shap_values, result["X_test"], max_display=12)"""),

md("""One finding only the model surfaces: **years since last promotion raises
attrition risk (OR ≈ 1.6 per SD) once tenure is controlled for.** The raw
segment cut hides this because long-tenured employees have both stale
promotion dates and low attrition.

## 5. Takeaways

- Attrition costs **$8.67M/yr (7.6% of payroll)**; over half sits with the
  416 overtime employees.
- The recommended package (targeted overtime reduction + first-year
  experience program) projects **≈$1.25M/yr savings for ~$420K/yr cost** —
  see `reports/strategy_deck.md` for options, tradeoffs, and the pilot plan.
- A broad bottom-quartile pay raise does **not** pay for itself on
  replacement cost alone (−$640K/yr net) — the counterintuitive result that
  shapes the recommendation.

**Caveats** (full list in `outputs/model_report.md`): synthetic
cross-sectional data, correlation ≠ causation, no voluntary/involuntary
split, no market comp benchmarks. Intervention effect sizes are stated
assumptions to be validated by pilot, not model outputs."""),
]

nb.cells = cells
nb.metadata["kernelspec"] = {
    "name": "python3", "display_name": "Python 3", "language": "python",
}

client = NotebookClient(nb, timeout=600, kernel_name="python3",
                        resources={"metadata": {"path": str(NB_PATH.parent)}})
client.execute()
nbf.write(nb, NB_PATH)
print(f"Executed and wrote {NB_PATH}")
