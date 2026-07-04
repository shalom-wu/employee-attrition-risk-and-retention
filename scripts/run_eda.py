"""Descriptive analysis: data quality report, attrition-rate tables by cut,
flight-risk segments, and the EDA figures used in the deck and README.

Outputs: outputs/*.csv, outputs/data_quality_report.md, reports/figures/*.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from attrition import data as adata
from attrition import viz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = ROOT / "reports" / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

viz.apply_style()

raw = adata.load_raw()
notes = adata.quality_report(raw)
df = adata.clean(raw)
df.to_csv(OUT / "clean_hr_data.csv", index=False)
overall = df["AttritionFlag"].mean()

# ---------------------------------------------------------------------------
# Attrition-rate tables and bar charts by cut
# ---------------------------------------------------------------------------
CUTS = {
    # name: (column, keep natural order?, x-rotation)
    "department": ("Department", False, 0),
    "jobrole": ("JobRole", False, 30),
    "joblevel": ("JobLevel", True, 0),
    "tenureband": ("TenureBand", True, 0),
    "overtime": ("OverTime", False, 0),
    "jobsatisfaction": ("JobSatisfactionLabel", True, 0),
    "incomequartile": ("IncomeQuartile", True, 0),
    "businesstravel": ("BusinessTravel", False, 0),
    "maritalstatus": ("MaritalStatus", False, 0),
}
TITLES = {
    "department": "Attrition rate by department",
    "jobrole": "Attrition rate by job role",
    "joblevel": "Attrition rate by job level (1 = junior IC)",
    "tenureband": "Attrition rate by tenure at company",
    "overtime": "Attrition rate by overtime status",
    "jobsatisfaction": "Attrition rate by job satisfaction score",
    "incomequartile": "Attrition rate by monthly income quartile",
    "businesstravel": "Attrition rate by business travel frequency",
    "maritalstatus": "Attrition rate by marital status",
}
for name, (col, natural, rot) in CUTS.items():
    t = adata.attrition_table(df, col, sort_by_rate=not natural)
    t.to_csv(OUT / f"attrition_by_{name}.csv", index=False)
    viz.rate_barplot(t, col, TITLES[name], FIG / f"attrition_by_{name}.png",
                     company_avg=overall, rotate=rot)
    print(f"\n=== {TITLES[name]} ===")
    print(t.to_string(index=False))

print(f"\nOverall attrition: {overall:.1%} ({df['AttritionFlag'].sum()} of {len(df)})")

# ---------------------------------------------------------------------------
# The headline interaction: job level x overtime
# ---------------------------------------------------------------------------
pivot = (
    df.pivot_table(index="JobLevel", columns="OverTime",
                   values="AttritionFlag", aggfunc="mean") * 100
)
fig, ax = plt.subplots(figsize=(8, 4.4))
pivot.plot(kind="bar", ax=ax, color=[viz.NAVY, viz.CORAL], width=0.75)
for container in ax.containers:
    ax.bar_label(container, fmt="%.0f%%", fontsize=9, fontweight="bold",
                 color="#232946", padding=2)
ax.set_ylabel("Attrition rate (%)")
ax.set_xlabel("Job level (1 = junior IC)")
ax.set_ylim(0, pivot.values.max() * 1.15)
ax.set_title("Overtime multiplies junior attrition", loc="left", pad=12)
ax.legend(title="Overtime", loc="upper right")
plt.setp(ax.get_xticklabels(), rotation=0)
fig.tight_layout()
fig.savefig(FIG / "attrition_joblevel_x_overtime.png")
plt.close(fig)

# Income distribution: leavers vs stayers
fig, ax = plt.subplots(figsize=(8, 4.2))
sns.kdeplot(data=df, x="MonthlyIncome", hue="Attrition", fill=True,
            common_norm=False, ax=ax, palette=[viz.NAVY, viz.CORAL])
ax.set_title("Leavers skew low-income", loc="left", pad=12)
ax.set_xlabel("Monthly income ($)")
ax.set_xlim(left=0)
fig.tight_layout()
fig.savefig(FIG / "income_distribution.png")
plt.close(fig)

# ---------------------------------------------------------------------------
# Flight-risk segments (rule-based, from the descriptive patterns)
# ---------------------------------------------------------------------------
segments = {
    "A. Burned-out juniors (JobLevel 1 + OverTime)":
        (df["JobLevel"] == 1) & (df["OverTime"] == "Yes"),
    "B. Early-tenure hires (<=1 yr at company)":
        df["YearsAtCompany"] <= 1,
    "C. Overtime sales reps":
        (df["JobRole"] == "Sales Representative") & (df["OverTime"] == "Yes"),
    "D. Stalled mid-tenure (4+ yrs since promotion, JobLevel 1-2)":
        (df["YearsSinceLastPromotion"] >= 4) & (df["JobLevel"] <= 2),
    "E. Low satisfaction + low income":
        (df["JobSatisfaction"] == 1) & (df["IncomeQuartile"] == "Q1 (lowest)"),
}
rows = []
for name, mask in segments.items():
    sub = df[mask]
    rows.append({
        "segment": name,
        "headcount": len(sub),
        "leavers": int(sub["AttritionFlag"].sum()),
        "attrition_rate_pct": round(sub["AttritionFlag"].mean() * 100, 1),
        "share_of_all_leavers_pct": round(
            sub["AttritionFlag"].sum() / df["AttritionFlag"].sum() * 100, 1),
    })
seg_df = pd.DataFrame(rows)
seg_df.to_csv(OUT / "flight_risk_segments.csv", index=False)
print("\n=== Flight-risk segments ===")
print(seg_df.to_string(index=False))

# ---------------------------------------------------------------------------
# Data quality report
# ---------------------------------------------------------------------------
report = ["# Data quality report", "",
          "Source: IBM HR Analytics Employee Attrition & Performance (Kaggle).", ""]
report += [f"- {n}" for n in notes]
report += ["", "## Cleaning applied",
           "- Dropped constant columns (EmployeeCount, StandardHours, Over18).",
           "- Relabelled 'Research & Development' as 'Engineering' and mapped "
           "lab/research titles to tech equivalents (labels only).",
           "- Added derived fields: AttritionFlag, TenureBand, IncomeQuartile."]
(OUT / "data_quality_report.md").write_text("\n".join(report), encoding="utf-8")
print("\nWrote outputs/ and reports/figures/.")
