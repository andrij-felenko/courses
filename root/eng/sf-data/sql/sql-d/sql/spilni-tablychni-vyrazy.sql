WITH DepartmentStats AS (
    SELECT department_id,
           AVG(salary) AS avg_dept_salary,
           COUNT(*) AS staff_count
    FROM employees
    GROUP BY department_id
),
HighSalaryEmployees AS (
    SELECT e.employee_id, e.first_name, e.salary, e.department_id
    FROM employees e
    WHERE e.salary > 80000
)
SELECT h.first_name, h.salary, d.avg_dept_salary, d.staff_count
FROM HighSalaryEmployees h
JOIN DepartmentStats d ON h.department_id = d.department_id;
