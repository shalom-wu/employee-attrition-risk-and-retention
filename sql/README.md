# SQL Layer - Validation and KPI Reference

This folder adds a DuckDB validation layer on top of the included IBM HR sample data and the processed outputs created by the Python pipeline.

Run it from the project root:

```bash
python scripts/run_sql.py
```

Files run in order:

| File | Purpose |
|---|---|
| `create_tables.sql` | Creates local DuckDB views over the included raw CSV and the processed cost-model output. |
| `data_quality_checks.sql` | Checks row counts, duplicate employee IDs, valid attrition flags, missing key fields, and negative cost values. |
| `kpi_views.sql` | Defines the attrition, segment, tenure, overtime, and replacement-cost KPIs used by Power BI. |
| `analysis_queries.sql` | Prints the reviewer-facing checks and headline KPI cuts. |

The SQL layer is not a second model. It is the reproducible counting and aggregation layer. Python remains responsible for the cost model, classifier, and charts; SQL makes the dashboard inputs easy to audit.

Exports written to `data/powerbi/`:

- `fact_employees.csv`
- `kpi_attrition_overview.csv`
- `kpi_attrition_by_department.csv`
- `kpi_attrition_by_job_role.csv`
- `kpi_attrition_by_overtime.csv`
- `kpi_attrition_by_tenure_band.csv`
- `kpi_cost_by_department.csv`
- `flight_risk_segments.csv`
