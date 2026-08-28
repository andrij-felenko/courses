SELECT 
    pid,
    usename,
    client_addr,
    state,
    backend_xid,
    backend_xmin,
    now() - xact_start AS transaction_age,
    now() - state_change AS state_age,
    query
FROM pg_stat_activity
WHERE backend_xmin IS NOT NULL OR backend_xid IS NOT NULL
ORDER BY transaction_age DESC;
