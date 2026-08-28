SELECT 
    schemaname,
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    n_live_tup AS live_tuples,
    n_dead_tup AS dead_tuples,
    round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 2) AS dead_tuple_percent,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables
WHERE n_dead_tup > 500
ORDER BY n_dead_tup DESC;
