# Data quality report

Source: IBM HR Analytics Employee Attrition & Performance (Kaggle).

- Rows: 1470, Columns: 35
- Missing values: 0
- Duplicate EmployeeNumber IDs: 0
- Constant (zero-information) columns: ['EmployeeCount', 'Over18', 'StandardHours']
- Rows with internally inconsistent tenure fields: 0
- PerformanceRating only takes values 3 and 4 — no low performers recorded, so it has almost no discriminative value.
- Single cross-sectional snapshot (synthetic, IBM-generated): no dates, so the 16.1% attrition is treated as an annualized rate for costing.

## Cleaning applied
- Dropped constant columns (EmployeeCount, StandardHours, Over18).
- Relabelled 'Research & Development' as 'Engineering' and mapped lab/research titles to tech equivalents (labels only).
- Added derived fields: AttritionFlag, TenureBand, IncomeQuartile.