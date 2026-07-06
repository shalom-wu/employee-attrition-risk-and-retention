# Power BI Package

No `.pbix` is included for this project yet. Power BI Desktop is installed on this machine, but saving a new `.pbix` requires a manual GUI build step; I did not create a placeholder file.

What is included:

| File/folder | Purpose |
|---|---|
| `../data/powerbi/` | Exact CSV files to load into Power BI. Regenerate with `python scripts/run_sql.py`. |
| `dashboard_brief.md` | Dashboard page plan and audience. |
| `data_model.md` | Tables and relationships. |
| `dax_measures.md` | Measures to create in Power BI Desktop. |
| `manual_build_instructions.md` | Step-by-step rebuild guide. |
| `refresh_instructions.md` | How to regenerate data and refresh the report. |
| `screenshots/page*_mockup.png` | Static mockups generated from the Power BI-ready data, not actual Desktop screenshots. |

Intended pages: Executive KPI, Attrition Diagnostics, and Retention Decision Support.
