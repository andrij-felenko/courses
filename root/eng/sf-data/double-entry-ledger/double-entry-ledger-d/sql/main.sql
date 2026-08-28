   WITH latest_snapshot AS (
       SELECT sequence_num, balance
       FROM balance_snapshots
       WHERE account_id = 42
       ORDER BY sequence_num DESC
       LIMIT 1
   )
   SELECT 
       COALESCE(s.balance, 0) + COALESCE(SUM(p.amount), 0) AS current_balance
   FROM latest_snapshot s
   LEFT JOIN postings p ON p.account_id = 42 AND p.sequence_num > s.sequence_num;
