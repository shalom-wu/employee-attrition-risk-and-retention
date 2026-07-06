# Refresh Instructions

## Regenerate inputs

```bash
python scripts/run_eda.py
python scripts/run_cost_model.py
python scripts/run_modeling.py
python scripts/run_sql.py
```

## Refresh Power BI

Open the `.pbix` after it is manually built, confirm each query points to the local `data/powerbi/` folder, then use Home -> Refresh.

If the folder path changes after cloning, use Transform data -> Data source settings -> Change Source.
