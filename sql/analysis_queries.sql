-- Business-facing spot checks and review queries.

SELECT *
FROM v_attrition_overview;

SELECT *
FROM v_attrition_by_department;

SELECT *
FROM v_attrition_by_overtime;

SELECT *
FROM v_cost_by_department;

SELECT *
FROM v_flight_risk_segments;

SELECT
    'Overtime attrition lift' AS metric,
    ROUND(
        (SELECT attrition_rate_pct FROM v_attrition_by_overtime WHERE overtime = 'Yes')
        -
        (SELECT attrition_rate_pct FROM v_attrition_by_overtime WHERE overtime = 'No'),
        1
    ) AS value_pct_points;
