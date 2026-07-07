# Employee Attrition Risk And Retention Strategy

This repository analyzes employee attrition in the public IBM HR Analytics dataset. It combines employee segmentation, a replacement-cost model, interpretable classification, and ROI-based retention planning.

The dataset is synthetic, so the results should be read as a reusable HR analytics framework rather than company-specific evidence.

## Project Summary

| Area | Details |
|---|---|
| Business question | Which employee groups are most at risk of leaving, what does attrition cost, and which retention actions are economically justified? |
| Data | IBM HR Analytics synthetic employee attrition dataset. |
| Methods | Data quality checks, segment analysis, attrition cost modeling, logistic regression, XGBoost, SHAP, intervention ROI modeling. |
| Main outputs | Strategy deck, summary report, model metrics, attrition cost tables, Power BI-ready exports. |
| Tools | Python, pytest, DuckDB SQL, Power BI build documentation. |

## Key Findings

| # | Finding | Evidence |
|---|---|---|
| 1 | Attrition costs about $8.67M per year. | Replacement cost equals about 7.6% of payroll, using recruiting, onboarding, vacancy, and ramp-up assumptions. |
| 2 | Attrition is concentrated in a small high-risk segment. | Junior employees working overtime are 11% of headcount but drive about one-third of all attrition. |
| 3 | The simpler model is the clearest production candidate. | Logistic regression reaches 0.81 ROC-AUC, slightly ahead of XGBoost at 0.79 on this small tabular dataset. |
| 4 | Raw segment cuts miss promotion stagnation. | Once tenure is controlled for, promotion stagnation appears as a material risk factor. |
| 5 | Broad pay raises do not clear the ROI bar. | A targeted overtime and first-year experience program is the stronger economic option under the stated assumptions. |

![Overtime multiplies junior attrition](https://raw.githubusercontent.com/shalom-wu/employee-attrition-risk-and-retention/main/reports/figures/attrition_joblevel_x_overtime.png)

## Data

The project uses the public IBM HR Analytics synthetic employee attrition dataset. Source notes, redistribution details, and caveats are documented in [data-sources.md](data-sources.md) and [data/data_manifest.md](data/data_manifest.md).

Because the data is synthetic and cross-sectional, it should not be used to make claims about a real employer. The value of the project is the workflow: define the business question, quantify cost, model risk, and turn the model into an intervention plan.

## Methodology

1. Clean and profile the employee table, including zero-variance columns and expected schema checks.
2. Analyze attrition by department, role, level, tenure, overtime, satisfaction, pay, and business travel.
3. Estimate replacement cost with recruiting, onboarding, vacancy, and ramp-up components.
4. Train logistic regression and XGBoost models with class-imbalance handling and cross-validation.
5. Explain the model with odds ratios and SHAP, then translate high-risk segments into costed interventions.

## Repository Contents

| Path | Purpose |
|---|---|
| [notebooks/](notebooks) | Executed analysis walkthrough. |
| [src/attrition/](src/attrition) | Data prep, cost model, modeling, and visualization modules. |
| [scripts/](scripts) | Pipeline entry points for EDA, costing, modeling, SQL exports, and notebook execution. |
| [outputs/](outputs) | Data quality, model, and cost outputs. |
| [reports/](reports) | Summary report, strategy deck, and generated figures. |
| [sql/](sql) | DuckDB validation, KPI views, and claim checks. |
| [power-bi/](power-bi) | Power BI dashboard brief, model notes, DAX, refresh steps, and mockups. |
| [tests/](tests) | Data integrity, cost model, and modeling tests. |

## Reproduce

Requires Python 3.11+.

```bash
git clone https://github.com/shalom-wu/employee-attrition-risk-and-retention.git
cd employee-attrition-risk-and-retention
python -m venv .venv
pip install -r requirements.txt
pip install -e .

python scripts/run_eda.py
python scripts/run_cost_model.py
python scripts/run_modeling.py
python scripts/run_sql.py
pytest
```

On Windows, activate the virtual environment with `.venv\Scripts\activate`. On macOS/Linux, use `source .venv/bin/activate`.

## Reporting Layer

SQL is used as the validation layer for row counts, KPI cuts, segment checks, and Power BI-ready exports. Run `python scripts/run_sql.py` to write the dashboard input tables to `data/powerbi/`.

The [power-bi/](power-bi) folder contains the dashboard brief, data model notes, DAX measures, manual build instructions, refresh steps, and mockups. No placeholder `.pbix` file is included.

## Limitations

- The dataset is synthetic and cross-sectional, with no hire or exit dates.
- The analysis is correlational; it cannot prove that changing overtime or pay will reduce attrition.
- There are only 237 positive attrition cases, so small role-level estimates have wide uncertainty.
- The data has no voluntary/involuntary split and no market compensation benchmark.
- Risk scores should be used to prioritize support, not punitive action.

## License And Credit

MIT License. Copyright (c) 2026 Shalom Wu.

Data credit: IBM HR Analytics synthetic employee attrition dataset. See [data-sources.md](data-sources.md) and [data/data_manifest.md](data/data_manifest.md) for source notes and usage caveats.
