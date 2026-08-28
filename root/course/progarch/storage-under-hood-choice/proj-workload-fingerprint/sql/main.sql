-- A. Один рядок на таблицю: модифікації рядків, сканування, кеш купи, розмір.
--    Лічильники КУМУЛЯТИВНІ від останнього reset — тому знімемо двічі (див. Python).
SELECT s.relname                          AS tbl,
       s.n_tup_ins                        AS ins,        -- вставок
       s.n_tup_upd                        AS upd,        -- оновлень
       s.n_tup_del                        AS del,        -- видалень
       s.seq_scan + s.idx_scan            AS scans,      -- усього сканувань
       s.seq_tup_read + s.idx_tup_fetch   AS rows_read,  -- рядків віддано читанням
       s.n_dead_tup                       AS dead,       -- мертвих рядків (мусор)
       io.heap_blks_read                  AS disk_blks,  -- сторінок купи з ДИСКА
       io.heap_blks_hit                   AS cache_blks, -- сторінок купи з КЕШУ
       pg_table_size(s.relid)             AS size_bytes  -- фізичний розмір
FROM       pg_stat_user_tables   s
JOIN       pg_statio_user_tables io USING (relid)
WHERE s.relname = ANY (%(tables)s);

-- B. Тиск запису в БАЙТАХ WAL і форма читань (рядків на виклик).
--    Грубе зіставлення з таблицею за текстом нормалізованого запиту (див. пастки).
SELECT t.tbl,
       sum(s.calls)      AS calls,
       sum(s.rows)       AS rows,
       sum(s.wal_bytes)  AS wal_bytes
FROM   pg_stat_statements s
JOIN   unnest(%(tables)s) AS t(tbl) ON s.query ILIKE '%' || t.tbl || '%'
GROUP  BY t.tbl;

-- C. Розкид провідної колонки ключа: кореляція фізичного й логічного порядку.
--    ≈ ±1 → вставки лягають упорядковано (дописування в правий край дерева);
--    ≈ 0  → вставки розкидані по всій таблиці (дорогий випадковий запис).
SELECT tablename AS tbl, attname AS key_col, correlation AS corr
FROM   pg_stats
WHERE (tablename, attname) IN (('measurement', 'device_id'),   -- провідна PK телеметрії
                               ('device',      'id'));          -- PK реєстру
