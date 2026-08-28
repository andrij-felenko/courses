-- Створення представлення з жорсткою прив'язкою до схеми
CREATE VIEW dbo.vw_category_sales
WITH SCHEMABINDING
AS
SELECT
    category_id,
    COUNT_BIG(*) AS total_items,
    SUM(ISNULL(amount, 0)) AS total_revenue
FROM dbo.order_items
GROUP BY category_id;
GO

-- Фізична матеріалізація через кластеризований індекс
CREATE UNIQUE CLUSTERED INDEX idx_vw_category_sales
ON dbo.vw_category_sales (category_id);
