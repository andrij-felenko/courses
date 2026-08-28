-- Так воркер у проді забирає пачку готових задач БЕЗ гонки за рядок.
-- FOR UPDATE бере рядок під блокування; SKIP LOCKED каже «зайняте іншим — не чекай, пропусти».
UPDATE jobs
   SET state = 'running', locked_by = $worker, locked_at = now()
 WHERE id IN (
     SELECT id FROM jobs
      WHERE state = 'ready' AND run_after <= now()
      ORDER BY id
      FOR UPDATE SKIP LOCKED           -- Postgres 9.5+ (2016): пропустити вже зайняті рядки
      LIMIT $batch
 )
RETURNING id, cls, payload, key;
