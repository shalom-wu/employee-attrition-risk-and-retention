-- High-signal checks for a cross-sectional synthetic HR dataset.

SELECT '01 raw row count' AS check_name, COUNT(*)::VARCHAR AS result
FROM raw_hr_employees;

SELECT '02 processed row count matches raw' AS check_name,
       CASE WHEN (SELECT COUNT(*) FROM raw_hr_employees) = (SELECT COUNT(*) FROM hr_employees)
            THEN 'pass' ELSE 'fail' END AS result;

SELECT '03 duplicate employee numbers' AS check_name,
       COUNT(*)::VARCHAR AS result
FROM (
    SELECT EmployeeNumber
    FROM hr_employees
    GROUP BY 1
    HAVING COUNT(*) > 1
);

SELECT '04 attrition flag valid' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'pass' ELSE 'fail' END AS result
FROM hr_employees
WHERE AttritionFlag NOT IN (0, 1);

SELECT '05 missing key fields' AS check_name,
       COUNT(*)::VARCHAR AS result
FROM hr_employees
WHERE Department IS NULL
   OR JobRole IS NULL
   OR MonthlyIncome IS NULL
   OR Attrition IS NULL;

SELECT '06 negative income or replacement cost' AS check_name,
       COUNT(*)::VARCHAR AS result
FROM hr_employees
WHERE MonthlyIncome < 0 OR replacement_cost < 0;

SELECT '07 source is synthetic sample data' AS check_name,
       'documented in data-sources.md and data/data_manifest.md' AS result;
