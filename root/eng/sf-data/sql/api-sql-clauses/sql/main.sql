/* Варіант A: Умова в секції ON */
SELECT c.id, c.name, o.total
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id AND o.status = 'completed';

/* Варіант B: Умова в секції WHERE */
SELECT c.id, c.name, o.total
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.status = 'completed';
