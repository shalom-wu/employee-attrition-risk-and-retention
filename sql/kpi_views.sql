-- KPI definitions used by the README and Power BI handoff.

CREATE OR REPLACE VIEW v_attrition_overview AS
SELECT
    COUNT(*) AS headcount,
    SUM(attrition_flag) AS leavers,
    ROUND(AVG(attrition_flag) * 100, 1) AS attrition_rate_pct,
    ROUND(SUM(CASE WHEN attrition_flag = 1 THEN replacement_cost ELSE 0 END), 0) AS estimated_replacement_cost,
    ROUND(AVG(CASE WHEN attrition_flag = 1 THEN replacement_cost END), 0) AS avg_cost_per_leaver,
    ROUND(AVG(replacement_cost_pct_salary) * 100, 1) AS avg_replacement_cost_pct_salary
FROM v_fact_employees;

CREATE OR REPLACE VIEW v_attrition_by_department AS
SELECT
    department,
    COUNT(*) AS headcount,
    SUM(attrition_flag) AS leavers,
    ROUND(AVG(attrition_flag) * 100, 1) AS attrition_rate_pct,
    ROUND(SUM(CASE WHEN attrition_flag = 1 THEN replacement_cost ELSE 0 END), 0) AS estimated_replacement_cost
FROM v_fact_employees
GROUP BY 1
ORDER BY attrition_rate_pct DESC, headcount DESC;

CREATE OR REPLACE VIEW v_attrition_by_job_role AS
SELECT
    job_role,
    COUNT(*) AS headcount,
    SUM(attrition_flag) AS leavers,
    ROUND(AVG(attrition_flag) * 100, 1) AS attrition_rate_pct,
    ROUND(SUM(CASE WHEN attrition_flag = 1 THEN replacement_cost ELSE 0 END), 0) AS estimated_replacement_cost
FROM v_fact_employees
GROUP BY 1
ORDER BY attrition_rate_pct DESC, headcount DESC;

CREATE OR REPLACE VIEW v_attrition_by_overtime AS
SELECT
    overtime,
    COUNT(*) AS headcount,
    SUM(attrition_flag) AS leavers,
    ROUND(AVG(attrition_flag) * 100, 1) AS attrition_rate_pct,
    ROUND(SUM(CASE WHEN attrition_flag = 1 THEN replacement_cost ELSE 0 END), 0) AS estimated_replacement_cost
FROM v_fact_employees
GROUP BY 1
ORDER BY attrition_rate_pct DESC;

CREATE OR REPLACE VIEW v_attrition_by_tenure_band AS
SELECT
    tenure_band,
    COUNT(*) AS headcount,
    SUM(attrition_flag) AS leavers,
    ROUND(AVG(attrition_flag) * 100, 1) AS attrition_rate_pct
FROM v_fact_employees
GROUP BY 1
ORDER BY
    CASE tenure_band
        WHEN '<=1 yr' THEN 1
        WHEN '2-3 yrs' THEN 2
        WHEN '4-6 yrs' THEN 3
        WHEN '7-10 yrs' THEN 4
        ELSE 5
    END;

CREATE OR REPLACE VIEW v_cost_by_department AS
SELECT
    department,
    ROUND(SUM(CASE WHEN attrition_flag = 1 THEN replacement_cost ELSE 0 END), 0) AS estimated_replacement_cost,
    ROUND(AVG(CASE WHEN attrition_flag = 1 THEN replacement_cost END), 0) AS avg_cost_per_leaver,
    SUM(attrition_flag) AS leavers
FROM v_fact_employees
GROUP BY 1
ORDER BY estimated_replacement_cost DESC;

CREATE OR REPLACE VIEW v_flight_risk_segments AS
SELECT *
FROM read_csv_auto('outputs/flight_risk_segments.csv', HEADER = TRUE);
