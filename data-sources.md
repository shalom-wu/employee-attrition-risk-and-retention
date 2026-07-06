# Data Sources

## IBM HR Analytics Employee Attrition & Performance

- **Source page:** https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset
- **Original publisher/creator:** IBM data scientists, published as a fictional sample dataset.
- **Hosting platform:** Kaggle, user `pavansubhasht`.
- **Kaggle metadata checked:** 2026-07-06.
- **License returned by Kaggle metadata:** `DbCL-1.0`.
- **Local raw file:** `data/WA_Fn-UseC_-HR-Employee-Attrition.csv`
- **Rows/columns used:** 1,470 rows x 35 source columns.
- **Dataset type:** Synthetic/fictional sample data. It should not be described as private company HR data.

## Fields Used

The analysis uses employee demographics, role, compensation, overtime, tenure, satisfaction scores, business travel, and the `Attrition` label. The Python pipeline adds `AttritionFlag`, `TenureBand`, `IncomeQuartile`, cost-model fields, and replacement-cost estimates.

## Transformations

The raw file is included in the repo. Python scripts under `scripts/` and reusable modules under `src/attrition/` create the processed outputs in `outputs/`. The SQL layer reads the included raw and processed CSVs, validates row counts and key fields, and exports dashboard-ready tables to `data/powerbi/`.

## Limitations

This is a synthetic, cross-sectional HR sample. The model is useful for demonstrating attrition analytics, cost framing, and retention-prioritization logic, but it cannot prove causal turnover drivers or represent a specific employer.
