# Manual Build Instructions

1. Run `python scripts/run_sql.py` from the project root.
2. Open Power BI Desktop.
3. Get Data -> Text/CSV and load all files from `data/powerbi/`.
4. Create the DAX measures in `dax_measures.md`.
5. Build three pages:
   - Executive KPI: cards for headcount, leavers, attrition rate, replacement cost; bar charts by department and overtime.
   - Attrition Diagnostics: bar charts by job role and tenure band; slicers for department, overtime, job level, and income quartile.
   - Retention Decision Support: table of `flight_risk_segments`, replacement cost by department, and a short caveat text box.
6. Add footer text: `Source: IBM HR Analytics fictional sample via Kaggle; cost outputs use documented assumptions.`
7. Save as `power-bi/attrition_retention_strategy.pbix`.

The files in `screenshots/` are static mockups to guide layout. They are not Desktop screenshots.
