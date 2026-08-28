-- 1. Створення журналу змін над базовою таблицею
CREATE MATERIALIZED VIEW LOG ON sales_orders
WITH ROWID, PRIMARY KEY (order_id, category_id),
SEQUENCE (amount, quantity)
INCLUDING NEW VALUES;

-- 2. Створення матеріалізованого представлення з підтримкою FAST REFRESH
CREATE MATERIALIZED VIEW mv_sales_summary
BUILD IMMEDIATE
REFRESH FAST ON COMMIT
ENABLE QUERY REWRITE
AS SELECT
    category_id,
    COUNT(*) AS total_orders,
    SUM(amount) AS total_revenue
FROM sales_orders
GROUP BY category_id;
