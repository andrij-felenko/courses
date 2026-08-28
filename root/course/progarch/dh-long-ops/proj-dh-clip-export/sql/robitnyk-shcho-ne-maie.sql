-- Claim: атомарно забрати задачу й поставити СВІЖИЙ жетон оренди $2.
UPDATE operations SET
  status           = 'running',
  lease_id         = $2,                          -- новий жетон на кожен забір (фенс на майбутнє)
  lease_expires_at = now() + ($3 || ' seconds')::interval,
  attempt          = attempt + 1
WHERE id = (
  SELECT id FROM operations
   WHERE status = 'queued'
      OR (status = 'running' AND lease_expires_at < now())   -- перехопити мертвого робітника
   ORDER BY created_at
   FOR UPDATE SKIP LOCKED                          -- перестрибнути вже взяті іншими
   LIMIT 1)
RETURNING id, request, attempt, lease_id, user_id;
