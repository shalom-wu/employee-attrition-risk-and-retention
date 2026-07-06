# Data Manifest

This repo is self-contained for review: the raw IBM HR sample, processed outputs, SQL queries, and Power BI-ready exports are included.

| File | Type | Shape / size | Used by | Notes |
|---|---|---:|---|---|
| `WA_Fn-UseC_-HR-Employee-Attrition.csv` | Synthetic raw sample | 1,470 x 35, 222.6 KB | Python, tests, SQL | Kaggle metadata checked 2026-07-06; IBM fictional sample hosted by `pavansubhasht`; license `DbCL-1.0`. |
| `powerbi/fact_employees.csv` | Derived | 1,470 x 17, 188.6 KB | Power BI, SQL review | Employee-level dashboard fact table from `outputs/hr_data_with_costs.csv`. |
| `powerbi/kpi_attrition_overview.csv` | Derived aggregate | 1 x 6, <1 KB | Power BI | Headcount, leavers, attrition rate, and replacement-cost summary. |
| `powerbi/kpi_attrition_by_department.csv` | Derived aggregate | 3 x 5, <1 KB | Power BI | Department attrition and cost view. |
| `powerbi/kpi_attrition_by_job_role.csv` | Derived aggregate | 9 x 5, <1 KB | Power BI | Job-role attrition and cost view. |
| `powerbi/kpi_attrition_by_overtime.csv` | Derived aggregate | 2 x 5, <1 KB | Power BI | Overtime risk split. |
| `powerbi/kpi_attrition_by_tenure_band.csv` | Derived aggregate | 5 x 4, <1 KB | Power BI | Tenure-band attrition view. |
| `powerbi/kpi_cost_by_department.csv` | Derived + assumed | 3 x 4, <1 KB | Power BI | Replacement cost exposure by department. Cost assumptions are in `outputs/cost_model_assumptions.csv`. |
| `powerbi/flight_risk_segments.csv` | Derived segment table | 5 x 5, <1 KB | Power BI | Targetable retention segments from the Python analysis. |

The raw dataset is synthetic and redistributable subject to the Kaggle-listed `DbCL-1.0` license. The cost outputs are derived from the synthetic employee file plus documented assumptions; they should be described as planning estimates, not observed company financials.
