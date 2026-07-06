# Data Model

Load these files from `data/powerbi/`:

| Table | File | Grain |
|---|---|---|
| `fact_employees` | `fact_employees.csv` | One row per employee. |
| `kpi_attrition_overview` | `kpi_attrition_overview.csv` | One-row executive KPI table. |
| `kpi_attrition_by_department` | `kpi_attrition_by_department.csv` | One row per department. |
| `kpi_attrition_by_job_role` | `kpi_attrition_by_job_role.csv` | One row per job role. |
| `kpi_attrition_by_overtime` | `kpi_attrition_by_overtime.csv` | One row per overtime flag. |
| `kpi_attrition_by_tenure_band` | `kpi_attrition_by_tenure_band.csv` | One row per tenure band. |
| `kpi_cost_by_department` | `kpi_cost_by_department.csv` | One row per department. |
| `flight_risk_segments` | `flight_risk_segments.csv` | One row per analyst-defined risk segment. |

Relationships are optional because most dashboard pages can use the pre-aggregated tables directly. If you want slicers from `fact_employees`, relate department/job role dimensions only after creating separate dimension tables to avoid ambiguous relationships.
