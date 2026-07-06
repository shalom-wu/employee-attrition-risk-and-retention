# DAX Measures

Create these measures on `fact_employees`:

```DAX
Headcount = COUNTROWS(fact_employees)

Leavers = SUM(fact_employees[attrition_flag])

Attrition Rate = DIVIDE([Leavers], [Headcount])

Estimated Replacement Cost =
SUMX(
    FILTER(fact_employees, fact_employees[attrition_flag] = 1),
    fact_employees[replacement_cost]
)

Average Cost per Leaver = DIVIDE([Estimated Replacement Cost], [Leavers])

Avg Monthly Income = AVERAGE(fact_employees[monthly_income])
```

Format `Attrition Rate` as percentage, cost measures as currency, and counts as whole numbers. The SQL exports are the reference; the DAX should reconcile to `kpi_attrition_overview.csv`.
