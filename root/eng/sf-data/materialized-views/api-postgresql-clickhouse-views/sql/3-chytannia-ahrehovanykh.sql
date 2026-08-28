SELECT
    event_date,
    device_type,
    uniqMerge(unique_users) AS active_users,
    quantileMerge(0.95)(latency_p95) AS p95,
    quantileMerge(0.99)(latency_p99) AS p99
FROM analytics.user_metrics_dest
WHERE event_date >= today() - INTERVAL 7 DAY
GROUP BY event_date, device_type
ORDER BY event_date, device_type;
