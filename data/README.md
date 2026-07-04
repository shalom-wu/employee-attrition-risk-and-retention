# Data source

**IBM HR Analytics Employee Attrition & Performance** — a public, widely
used sample dataset created by IBM data scientists. It is **synthetic**
(fictional employees) and is included here because it is freely
redistributed by IBM itself.

- Kaggle listing: https://www.kaggle.com/datasets/pavansubhash/ibm-hr-analytics-attrition-dataset
- File in this repo was fetched from IBM's public mirror:
  https://raw.githubusercontent.com/IBM/employee-attrition-aif360/master/data/emp_attrition.csv
  (repository: [IBM/employee-attrition-aif360](https://github.com/IBM/employee-attrition-aif360), Apache-2.0)
- Verified identical to the canonical Kaggle file: 1,470 rows × 35 columns,
  237 leavers (16.12% attrition rate).

## Caveats that follow from the source

- **Synthetic and cross-sectional**: one snapshot, no hire/exit dates. The
  16.1% attrition is treated as an annualized rate; survival analysis and
  time-based validation are not possible.
- Salary levels (median ≈ $59K/yr) are below current tech-market rates; all
  dollar findings scale linearly with payroll.
- For narrative purposes this project frames the company as a mid-size
  tech/SaaS firm: the "Research & Development" department is relabelled
  "Engineering" and lab/research job titles are mapped to tech equivalents.
  **Labels only — no values are changed** (enforced by a unit test).
