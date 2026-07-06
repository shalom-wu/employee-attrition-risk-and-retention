-- DuckDB local views over the included raw and processed HR data.
-- Run from the project root through scripts/run_sql.py.

CREATE OR REPLACE VIEW raw_hr_employees AS
SELECT *
FROM read_csv_auto('data/WA_Fn-UseC_-HR-Employee-Attrition.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW hr_employees AS
SELECT *
FROM read_csv_auto('outputs/hr_data_with_costs.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_fact_employees AS
SELECT
    EmployeeNumber::INTEGER AS employee_number,
    Age::INTEGER AS age,
    Department AS department,
    JobRole AS job_role,
    JobLevel::INTEGER AS job_level,
    BusinessTravel AS business_travel,
    OverTime AS overtime,
    MaritalStatus AS marital_status,
    Gender AS gender,
    MonthlyIncome::DOUBLE AS monthly_income,
    YearsAtCompany::INTEGER AS years_at_company,
    TenureBand AS tenure_band,
    IncomeQuartile AS income_quartile,
    JobSatisfactionLabel AS job_satisfaction_label,
    AttritionFlag::INTEGER AS attrition_flag,
    replacement_cost::DOUBLE AS replacement_cost,
    replacement_cost_pct_salary::DOUBLE AS replacement_cost_pct_salary
FROM hr_employees;
