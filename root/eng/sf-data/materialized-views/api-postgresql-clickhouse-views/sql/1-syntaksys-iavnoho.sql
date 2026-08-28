-- 1. Цільова фізична таблиця для збереження агрегованих сум
CREATE TABLE analytics.daily_sales_dest (
    event_date Date,
    category_id UInt32,
    total_amount SimpleAggregateFunction(sum, Float64),
    order_count SimpleAggregateFunction(sum, UInt64)
) ENGINE = SummingMergeTree()
PRIMARY KEY (event_date, category_id)
ORDER BY (event_date, category_id);

-- 2. Матеріалізоване представлення-конвеєр
CREATE MATERIALIZED VIEW analytics.mv_daily_sales
TO analytics.daily_sales_dest
AS SELECT
    toDate(created_at) AS event_date,
    category_id,
    sum(amount) AS total_amount,
    count() AS order_count
FROM raw_data.orders
GROUP BY event_date, category_id;
