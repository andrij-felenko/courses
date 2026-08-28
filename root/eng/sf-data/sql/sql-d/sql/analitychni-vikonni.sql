SELECT employee_id,
       first_name,
       department_id,
       salary,
       /* Сума зарплат по всьому відділу поруч із кожним співробітником */
       SUM(salary) OVER (PARTITION BY department_id) AS dept_payroll,
       /* Порядковий номер співробітника за рівнем зарплати у відділі */
       ROW_NUMBER() OVER (
           PARTITION BY department_id 
           ORDER BY salary DESC
       ) AS salary_rank,
       /* Зарплата попереднього співробітника у відсортованому списку */
       LAG(salary, 1) OVER (
           PARTITION BY department_id 
           ORDER BY salary DESC
       ) AS prev_higher_salary
FROM employees;
