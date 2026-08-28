     -- Псевдокод внутрішнього порівняння PostgreSQL:
     SELECT diff.* FROM (
         SELECT 'INSERT' AS op, t.* FROM temp_table t
         LEFT JOIN matview m ON m.unique_key = t.unique_key
         WHERE m.unique_key IS NULL
         UNION ALL
         SELECT 'DELETE' AS op, m.* FROM matview m
         LEFT JOIN temp_table t ON t.unique_key = m.unique_key
         WHERE t.unique_key IS NULL
         UNION ALL
         SELECT 'UPDATE' AS op, t.* FROM temp_table t
         JOIN matview m ON m.unique_key = t.unique_key
         WHERE t.* IS DISTINCT FROM m.*
     ) diff;
