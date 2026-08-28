-- КОРОТКИЙ claim: атомарно вихопити одну готову задачу й позначити своєю.
-- SKIP LOCKED усередині підзапиту → двоє воркерів беруть РІЗНІ рядки, ніхто не чекає.
UPDATE jobs
   SET status = 'running', locked_by = $1, locked_at = now()
 WHERE id = (
   SELECT id FROM jobs
    WHERE status = 'ready'
    ORDER BY id
    LIMIT 1
    FOR UPDATE SKIP LOCKED
 )
RETURNING id, type, payload;
