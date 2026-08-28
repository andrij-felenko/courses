-- Атомарна заміна партиції в Apache Iceberg
INSERT OVERWRITE gold_db.daily_user_revenue
PARTITION (partition_date = '2026-08-20')
SELECT 
    user_id,
    SUM(amount_cents) AS raw_total_cents,
    SUM(discounted_amount) AS discounted_total_cents,
    COUNT(1) AS events_count,
    MAX(update_time) AS updated_at
FROM stage_prepared_events
WHERE event_date = '2026-08-20'
GROUP BY user_id;
