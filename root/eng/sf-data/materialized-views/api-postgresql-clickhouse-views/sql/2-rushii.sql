-- Таблиця агрегації перцентилів та унікальних користувачів
CREATE TABLE analytics.user_metrics_dest (
    event_date Date,
    device_type LowCardinality(String),
    unique_users AggregateFunction(uniq, UInt64),
    latency_p95 AggregateFunction(quantile(0.95), Float32),
    latency_p99 AggregateFunction(quantile(0.99), Float32)
) ENGINE = AggregatingMergeTree()
PRIMARY KEY (event_date, device_type)
ORDER BY (event_date, device_type);

-- Матеріалізоване в'ю накопичення станів
CREATE MATERIALIZED VIEW analytics.mv_user_metrics
TO analytics.user_metrics_dest
AS SELECT
    toDate(timestamp) AS event_date,
    device_type,
    uniqState(user_id) AS unique_users,
    quantileState(0.95)(latency_ms) AS latency_p95,
    quantileState(0.99)(latency_ms) AS latency_p99
FROM raw_data.access_logs
GROUP BY event_date, device_type;
