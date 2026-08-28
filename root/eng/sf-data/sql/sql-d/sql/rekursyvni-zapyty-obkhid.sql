WITH RECURSIVE OrgHierarchy AS (
    /* Базова частина (Anchor Member): починаємо з генерального директора */
    SELECT employee_id, manager_id, first_name, 1 AS depth
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    /* Рекурсивна частина (Recursive Member): приєднуємо підлеглих */
    SELECT e.employee_id, e.manager_id, e.first_name, o.depth + 1
    FROM employees e
    JOIN OrgHierarchy o ON e.manager_id = o.employee_id
)
SELECT employee_id, manager_id, first_name, depth
FROM OrgHierarchy
ORDER BY depth, employee_id;
